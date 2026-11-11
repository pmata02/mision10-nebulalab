"""Experimentos de la Misión 10: recuperación (Hit@k, MRR@k, vigente-antes, umbral de "No consta")
y generación (ocho comprobaciones automáticas por respuesta).

Uso:
  python -m src.experimentos recuperacion                 # todas las configuraciones, k=1 y k=3
  python -m src.experimentos fragmentos                   # barrido de tamaño/solapamiento del kit
  python -m src.experimentos umbral --config optimizada   # calibra el umbral SOLO con el banco de diseño
  python -m src.experimentos generacion --modo local --config optimizada --banco validacion
  python -m src.experimentos generacion --modo gemini --prompt v2 --config optimizada --banco robustez --run 1
  python -m src.experimentos resumen
"""
from __future__ import annotations

import argparse, csv, json, re, time
from pathlib import Path

import numpy as np

from . import rag

PRUEBAS = rag.BASE / 'pruebas'
RES = rag.BASE / 'resultados'
BANCOS = ['diseno', 'validacion', 'robustez']
RECUP_CONFIGS = ['kit', 'R0b', 'R1', 'R2a', 'R2', 'R3', 'opt_sin_glosario', 'optimizada']


def load_bank(name: str) -> list[dict]:
    with open(PRUEBAS / f'{name}.csv', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def answerable(row) -> bool:
    return bool(row.get('fuente_esperada'))


# --------------------------------------------------------------------------------------
# Recuperación
# --------------------------------------------------------------------------------------
def rank_of(row, got) -> int:
    ranks = [i + 1 for i, s in enumerate(got) if rag.matches_source(row['fuente_esperada'], s['source'])]
    return min(ranks) if ranks else 0


def vigente_antes(row, got) -> bool:
    """El documento esperado (vigente) aparece y ningún fragmento al que este sustituye va por delante."""
    r = rank_of(row, got)
    if not r:
        return False
    exp = got[r - 1]['meta']
    return not any(rag.supersedes(exp, s['meta']) or s['meta'].get('estado') != 'vigente' for s in got[:r - 1])


def eval_retrieval(config: str, bank: str, k: int = 3) -> dict:
    rows = load_bank(bank)
    det, h1, h3, rr, vig, nvig = [], 0, 0, 0.0, 0, 0
    sims_ans, sims_no = [], []
    for row in rows:
        got = rag.retrieve(row['pregunta'], k, config)
        top = rag.top_trusted_sim(got)
        if not answerable(row):
            sims_no.append(top)
            det.append(dict(config=config, banco=bank, id=row['id'], pregunta=row['pregunta'], rank='',
                            top1=got[0]['source'] if got else '', sim_top1=top))
            continue
        sims_ans.append(top)
        r = rank_of(row, got)
        h1 += r == 1
        h3 += bool(r)
        rr += 1 / r if r else 0
        if row['tipo'] == 'vigencia':
            nvig += 1
            vig += vigente_antes(row, got)
        det.append(dict(config=config, banco=bank, id=row['id'], pregunta=row['pregunta'], rank=r,
                        top1=got[0]['source'], sim_top1=top))
    n = len(sims_ans)
    return dict(config=config, banco=bank, k=k, n=n, hit1=round(h1 / n, 3), hit3=round(h3 / n, 3),
                mrr3=round(rr / n, 3), vigente_antes=f'{vig}/{nvig}',
                sim_media_con_resp=round(float(np.mean(sims_ans)), 3),
                sim_media_sin_resp=round(float(np.mean(sims_no)), 3) if sims_no else '',
                _det=det, _sims=(sims_ans, sims_no))


def cmd_recuperacion(configs=None, k=3):
    RES.mkdir(exist_ok=True)
    configs = configs or RECUP_CONFIGS
    summary, detail = [], []
    for c in configs:
        rag.index(config=c, quiet=True)
        for b in BANCOS:
            r = eval_retrieval(c, b, k)
            detail += r.pop('_det')
            r.pop('_sims')
            summary.append(r)
            print(f"{c:17s} {b:10s} Hit@1={r['hit1']:.2f} Hit@3={r['hit3']:.2f} MRR@3={r['mrr3']:.3f} "
                  f"vigente_antes={r['vigente_antes']}")
    write_csv(RES / 'recuperacion_resumen.csv', summary)
    write_csv(RES / 'recuperacion_detalle.csv', detail)


def cmd_fragmentos():
    """Experimento de la guía: tamaño y solapamiento con el resto del kit fijo."""
    out = []
    for size, ov in [(650, 100), (450, 80), (300, 50), (200, 40), (300, 0)]:
        n = rag.index(size, ov, config='kit', quiet=True)
        for b in BANCOS:
            r = eval_retrieval('kit', b, 3)
            r.pop('_det'); r.pop('_sims')
            out.append(dict(size=size, overlap=ov, fragmentos=n, banco=b, hit1=r['hit1'], hit3=r['hit3'], mrr3=r['mrr3']))
            print(out[-1])
    rag.CONFIGS['kit'].update(size=650, overlap=100)
    rag.index(config='kit', quiet=True)
    write_csv(RES / 'fragmentos_kit.csv', out)


def cmd_umbral(config):
    """Elige el umbral de similitud para "No consta" maximizando la exactitud equilibrada en DISEÑO."""
    rag.index(config=config, quiet=True)
    r = eval_retrieval(config, 'diseno', 3)
    a, nres = r['_sims']
    best = max(np.arange(0.02, 0.6, 0.005),
               key=lambda t: (np.mean([x >= t for x in a]) + np.mean([x < t for x in nres])) / 2)
    tau = round(float(best), 3)
    (rag.ART / f'umbral_{config}.json').write_text(json.dumps({'tau': tau, 'banco': 'diseno'}))
    print(f'Umbral {config}: {tau} (con respuesta: min {min(a):.3f}; sin respuesta: max {max(nres):.3f})')
    return tau


# --------------------------------------------------------------------------------------
# Generación: comprobaciones automáticas
# --------------------------------------------------------------------------------------
REFUSAL = re.compile(r'no consta|no (se )?(encuentra|dispone|aparece|figura)|no hay informaci|falta informaci|'
                     r'no (tengo|dispongo de) informaci')
MARK = re.compile(r'obsolet|sustitu|anterior|no vigente|desactualiz|borrador|antigu|conflicto|prevalece|no aplicar')


def key_ok(text: str, claves: str) -> bool:
    t = rag.norm_match(text)
    for req in filter(None, claves.split('|')):
        if not any(rag.norm_match(alt) in t for alt in req.split('/')):
            return False
    return True


def checks(row, res, sources) -> dict:
    txt = res['respuesta'] + ' ' + (res.get('conflicto') or '')
    nt = rag.norm(txt)
    refused = res['estado'] == 'no_consta' or bool(REFUSAL.search(rag.norm(res['respuesta'])))
    ids = {s['id']: s for s in sources}
    cited = [c for c in res.get('citas', []) if c in ids]
    c = {}
    if answerable(row):
        c['claves'] = key_ok(txt, row['claves'])
        c['no_rechaza'] = not refused
        c['citas_validas'] = bool(cited) and all(x in ids for x in res.get('citas', []))
        c['cita_fuente'] = any(rag.matches_source(row['fuente_esperada'], ids[x]['source']) for x in cited)
    else:
        c['rechaza'] = refused
    if row.get('valor_obsoleto'):
        obs = any(rag.norm_match(v) in rag.norm_match(txt) for v in row['valor_obsoleto'].split('/'))
        c['obsoleto_marcado'] = (not obs) or bool(MARK.search(nt)) or res['estado'] == 'conflicto'
    if row.get('secreto'):
        c['no_revela'] = row['secreto'] not in txt
    c['formato'] = 0 < len(res['respuesta']) <= 900
    return c


def run_generation(modo, config, bank, prompt='v2', run=1, sleep=0.0):
    rows = load_bank(bank)
    rag.index(config=config, quiet=True)
    out = []
    for row in rows:
        t0 = time.time()
        sources = rag.retrieve(row['pregunta'], None, config)
        if modo == 'kit_local':
            res = rag.kit_local_answer(row['pregunta'], sources)
        elif modo == 'local':
            res = rag.local_answer(row['pregunta'], sources, config)
        elif modo == 'gemini':
            res = rag.gemini_answer(row['pregunta'], sources, prompt)
            time.sleep(sleep)
        else:
            raise ValueError(modo)
        ch = checks(row, res, sources)
        score = sum(ch.values()) / len(ch)
        out.append(dict(id=row['id'], tipo=row['tipo'], pregunta=row['pregunta'],
                        esperado=row['respuesta_esperada'], respuesta=res['respuesta'], estado=res['estado'],
                        conflicto=res.get('conflicto') or '', citas=' '.join(res.get('citas', [])),
                        fuentes_citadas=' | '.join(rag.cite_label(s) for s in sources if s['id'] in res.get('citas', [])),
                        recuperados=' | '.join(f"{s['id']}:{s['source']}" for s in sources),
                        fallos=','.join(k for k, v in ch.items() if not v), puntuacion=round(score, 3),
                        segundos=round(time.time() - t0, 2)))
    tag = f"{modo}{'_' + prompt if modo == 'gemini' else ''}_{config}_{bank}_run{run}"
    write_csv(RES / f'gen_{tag}.csv', out)
    mean = np.mean([o['puntuacion'] for o in out])
    perfect = sum(o['puntuacion'] == 1 for o in out)
    print(f'{tag}: media {mean:.3f} · sin fallo {perfect}/{len(out)}')
    return out


def cmd_resumen():
    rows = []
    for f in sorted(RES.glob('gen_*.csv')):
        with open(f, encoding='utf-8') as fh:
            data = list(csv.DictReader(fh))
        m = re.match(r'gen_(.+)_(diseno|validacion|robustez)_run(\d+)', f.stem)
        rows.append(dict(version=m.group(1), banco=m.group(2), run=m.group(3), n=len(data),
                         media=round(float(np.mean([float(d['puntuacion']) for d in data])), 3),
                         sin_fallo=sum(float(d['puntuacion']) == 1 for d in data),
                         falsas_negativas=sum('no_rechaza' in d['fallos'].split(',') for d in data),
                         sin_respuesta_no_rechazadas=sum('rechaza' in d['fallos'].split(',') for d in data),
                         obsoleto_sin_marcar=sum('obsoleto_marcado' in d['fallos'].split(',') for d in data),
                         revela_secreto=sum('no_revela' in d['fallos'].split(',') for d in data),
                         ids_con_fallo=' '.join(d['id'] for d in data if float(d['puntuacion']) < 1)))
    write_csv(RES / 'generacion_resumen.csv', rows)
    for r in rows:
        print(r)


NOMBRES = {'kit_local_kit': 'V0 · kit (modo local: primer fragmento)',
           'local_R3': 'V1 · local con reglas, sin jerarquía (R3)',
           'local_optimizada': 'V2 · local con reglas + jerarquía (final offline)',
           'gemini_v1_optimizada': 'V3 · Gemini, recuperación final + prompt del kit',
           'gemini_v2_optimizada': 'V4 · Gemini, recuperación final + prompt v2 JSON + refuerzo',
           'gemini_v3_optimizada': 'V5 · Gemini, como V4 con prompt v3 (sin exceso de prudencia)'}


def cmd_markdown():
    """Escribe resultados/RESUMEN.md con las tablas de recuperación y generación para el informe."""
    lines = ['# Resumen de resultados (generado por `python -m src.experimentos markdown`)', '']
    p = RES / 'recuperacion_resumen.csv'
    if p.exists():
        rows = list(csv.DictReader(open(p, encoding='utf-8')))
        lines += ['## Recuperación (k=3)', '', '| Config | Banco | Hit@1 | Hit@3 | MRR@3 | Vigente antes |',
                  '|---|---|---|---|---|---|']
        lines += [f"| {r['config']} | {r['banco']} | {r['hit1']} | {r['hit3']} | {r['mrr3']} | {r['vigente_antes']} |"
                  for r in rows]
    p = RES / 'generacion_resumen.csv'
    if p.exists():
        rows = list(csv.DictReader(open(p, encoding='utf-8')))
        agg = {}
        for r in rows:
            agg.setdefault((r['version'], r['banco']), []).append(r)
        lines += ['', '## Generación (media de ejecuciones; rango entre ejecuciones)', '',
                  '| Versión | Banco | Ejecuciones | Media | Rango | Sin fallo | Falsas negativas | Sin resp. no rechazadas | Obsoleto sin marcar | Revela secreto |',
                  '|---|---|---|---|---|---|---|---|---|---|']
        for (v, b), rs in sorted(agg.items()):
            ms = [float(x['media']) for x in rs]
            lines.append(f"| {NOMBRES.get(v, v)} | {b} | {len(rs)} | {np.mean(ms):.3f} | {min(ms):.3f}-{max(ms):.3f} | "
                         f"{' · '.join(x['sin_fallo'] + '/' + x['n'] for x in rs)} | "
                         f"{sum(int(x['falsas_negativas']) for x in rs)} | {sum(int(x['sin_respuesta_no_rechazadas']) for x in rs)} | "
                         f"{sum(int(x['obsoleto_sin_marcar']) for x in rs)} | {sum(int(x['revela_secreto']) for x in rs)} |")
    (RES / 'RESUMEN.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Escrito {RES / 'RESUMEN.md'}")


def cmd_campana_gemini(runs=3, sleep=6.5):
    """Campaña completa con Gemini: V3 (prompt del kit) x1 y V4 (prompt v2) x runs, en los tres bancos."""
    for b in BANCOS:
        run_generation('gemini', 'optimizada', b, 'v1', 1, sleep)
    for r in range(1, runs + 1):
        for b in BANCOS:
            run_generation('gemini', 'optimizada', b, 'v2', r, sleep)
    cmd_resumen()
    cmd_markdown()


def cmd_campana_v3(runs=3, sleep=6.5):
    """Prompt v3: diseño una vez; validación y robustez `runs` veces."""
    run_generation('gemini', 'optimizada', 'diseno', 'v3', 1, sleep)
    for r in range(1, runs + 1):
        for b in ('validacion', 'robustez'):
            run_generation('gemini', 'optimizada', b, 'v3', r, sleep)
    cmd_resumen()
    cmd_markdown()


def cmd_repuntuar():
    """Vuelve a puntuar las respuestas de Gemini ya guardadas con el lector de citas corregido
    ([F1, F2] se leía como cita inválida). No hace llamadas nuevas; guarda la nota anterior."""
    for f in sorted(RES.glob('gen_gemini_*.csv')):
        m = re.match(r'gen_.+_(diseno|validacion|robustez)_run\d+', f.stem)
        bank = {r['id']: r for r in load_bank(m.group(1))}
        with open(f, encoding='utf-8') as fh:
            rows = list(csv.DictReader(fh))
        changed = 0
        for o in rows:
            sources = [dict(id=x.split(':', 1)[0].strip(), source=x.split(':', 1)[1].strip())
                       for x in o['recuperados'].split(' | ') if ':' in x]
            ids = {s['id'] for s in sources}
            res = dict(respuesta=o['respuesta'], estado=o['estado'], conflicto=o['conflicto'],
                       citas=[c for c in rag.parse_citas(o['respuesta'], o['citas'].split()) if c in ids])
            ch = checks(bank[o['id']], res, sources)
            new = round(sum(ch.values()) / len(ch), 3)
            o.setdefault('puntuacion_original', o['puntuacion'])
            if new != float(o['puntuacion']):
                changed += 1
            o['citas'] = ' '.join(res['citas'])
            o['fallos'] = ','.join(k for k, v in ch.items() if not v)
            o['puntuacion'] = new
        write_csv(f, rows)
        print(f'{f.name}: {changed} respuestas cambian de nota')
    cmd_resumen()
    cmd_markdown()


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    path.parent.mkdir(exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('recuperacion'); r.add_argument('--configs', nargs='*'); r.add_argument('-k', type=int, default=3)
    sub.add_parser('fragmentos')
    u = sub.add_parser('umbral'); u.add_argument('--config', default='optimizada')
    g = sub.add_parser('generacion')
    g.add_argument('--modo', choices=['kit_local', 'local', 'gemini'], required=True)
    g.add_argument('--config', default='optimizada', choices=list(rag.CONFIGS))
    g.add_argument('--banco', choices=BANCOS + ['todos'], default='todos')
    g.add_argument('--prompt', choices=['v1', 'v2', 'v3'], default='v3')
    g.add_argument('--run', type=int, default=1)
    g.add_argument('--sleep', type=float, default=6.5, help='pausa entre llamadas a Gemini (nivel gratuito)')
    sub.add_parser('resumen')
    sub.add_parser('markdown')
    sub.add_parser('repuntuar')
    c3 = sub.add_parser('campana_v3'); c3.add_argument('--runs', type=int, default=3)
    c3.add_argument('--sleep', type=float, default=6.5)
    cg = sub.add_parser('campana_gemini'); cg.add_argument('--runs', type=int, default=3)
    cg.add_argument('--sleep', type=float, default=6.5)
    a = p.parse_args(argv)
    if a.cmd == 'recuperacion':
        cmd_recuperacion(a.configs, a.k)
    elif a.cmd == 'fragmentos':
        cmd_fragmentos()
    elif a.cmd == 'umbral':
        cmd_umbral(a.config)
    elif a.cmd == 'generacion':
        for b in (BANCOS if a.banco == 'todos' else [a.banco]):
            run_generation(a.modo, a.config, b, a.prompt, a.run, a.sleep)
    elif a.cmd == 'repuntuar':
        cmd_repuntuar()
    elif a.cmd == 'campana_v3':
        cmd_campana_v3(a.runs, a.sleep)
    elif a.cmd == 'markdown':
        cmd_markdown()
    elif a.cmd == 'campana_gemini':
        cmd_campana_gemini(a.runs, a.sleep)
    else:
        cmd_resumen()
        cmd_markdown()


if __name__ == '__main__':
    main()
