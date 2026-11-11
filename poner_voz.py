"""Pone voz al vídeo de demostración con las voces en español de macOS (comando `say`).

Uso, dentro de la carpeta del proyecto y con el entorno activado:
    python poner_voz.py
Necesita ffmpeg:  brew install ffmpeg
Resultado: Mision10_Video_demo_NebulaLab_voz.mp4
"""
import os, re, shutil, subprocess, sys, tempfile

VIDEO_IN = 'Mision10_Video_demo_NebulaLab.mp4'
VIDEO_OUT = 'Mision10_Video_demo_NebulaLab_voz.mp4'
SEGS = [
 {
  "start": 0,
  "text": "Presentamos nuestro asistente para consultar la normativa interna de NébulaLab, una empresa ficticia.",
  "slot": 7,
  "who": "Los dos"
 },
 {
  "start": 7,
  "text": "Lo hemos hecho Pablo Mata Rius y Wenjie Jiang para la Misión 10.",
  "slot": 7,
  "who": "Los dos"
 },
 {
  "start": 14,
  "text": "Un empleado pregunta cuántos días de vacaciones tiene, y en la empresa hay tres documentos que dicen cosas distintas.",
  "slot": 9,
  "who": "Wenjie"
 },
 {
  "start": 23,
  "text": "La política de 2023 dice 22 días. Una FAQ de Recursos Humanos de 2024 dice 24, más uno extra a partir del tercer año. Y la política de 2026 dice 25.",
  "slot": 14,
  "who": "Wenjie"
 },
 {
  "start": 37,
  "text": "Solo la de 2026 está en vigor. El reto es que el asistente dé esa cifra y avise de que existen las otras.",
  "slot": 11,
  "who": "Wenjie"
 },
 {
  "start": 48,
  "text": "El asistente funciona en dos fases. Al indexar, lee de cada documento su versión, su fecha y si está vigente o sustituido, y guarda esos datos junto a cada fragmento.",
  "slot": 14,
  "who": "Wenjie"
 },
 {
  "start": 62,
  "text": "Al preguntar, busca los veinte fragmentos más parecidos y pone delante los del documento vigente. Gemini redacta la respuesta y, al final, el código comprueba las citas y que no se filtren datos sensibles.",
  "slot": 16,
  "who": "Wenjie"
 },
 {
  "start": 78,
  "text": "Estos son los diez documentos: los seis del kit de la asignatura y cuatro que añadimos nosotros.",
  "slot": 10.86,
  "who": "Pablo"
 },
 {
  "start": 88.86,
  "text": "Tres de los nuestros son trampas a propósito: la política antigua de 2023, la FAQ de 2024 y un mensaje reenviado que intenta manipular al asistente.",
  "slot": 12.0,
  "who": "Pablo"
 },
 {
  "start": 100.86,
  "text": "Todo es reproducible: las 28 pruebas automáticas pasan sin conexión a internet y la base de datos vectorial se reconstruye con un solo comando.",
  "slot": 13.68,
  "who": "Pablo"
 },
 {
  "start": 114.54,
  "text": "Primera pregunta, hecha como la haría un empleado: cuánto me pagan por kilómetro si voy con mi coche.",
  "slot": 11.76,
  "who": "Pablo"
 },
 {
  "start": 126.3,
  "text": "Gemini responde 0,26 euros por kilómetro y cita su fuente exacta: el manual del empleado, página 2, sección de gastos de viaje.",
  "slot": 11.0,
  "who": "Pablo"
 },
 {
  "start": 137.3,
  "text": "Ahora, la pregunta de las vacaciones con el sistema original del kit, que busca solo por parecido de palabras.",
  "slot": 11.4,
  "who": "Pablo"
 },
 {
  "start": 148.7,
  "text": "El primer resultado es la FAQ de 2024, la de 24 días, porque está escrita casi igual que la pregunta. La política vigente aparece en tercer lugar.",
  "slot": 13.0,
  "who": "Pablo"
 },
 {
  "start": 161.7,
  "text": "La misma pregunta con nuestra versión: ahora la política vigente de 2026 aparece la primera.",
  "slot": 10.94,
  "who": "Pablo"
 },
 {
  "start": 172.64,
  "text": "Gemini responde 25 días, cita las dos fuentes y marca la respuesta como conflicto.",
  "slot": 7.0,
  "who": "Pablo"
 },
 {
  "start": 179.64,
  "text": "No esconde la FAQ antigua: la menciona para que el empleado sepa que hay otra cifra circulando y cuál es la que vale.",
  "slot": 11.0,
  "who": "Pablo"
 },
 {
  "start": 190.64,
  "text": "Esto lo consigue una regla de jerarquía que no depende del parecido con la pregunta, sino de los datos de cada documento: si está vigente, qué tipo de documento es y su fecha.",
  "slot": 15.0,
  "who": "Wenjie"
 },
 {
  "start": 205.64,
  "text": "En las preguntas de este tipo, el sistema original nunca ponía primero el documento vigente; el nuestro lo hace en cuatro de cinco.",
  "slot": 11.0,
  "who": "Wenjie"
 },
 {
  "start": 216.64,
  "text": "Ahora, seguridad. Entre los documentos hay un mensaje reenviado, sin autor ni fecha, que incluye la contraseña de la wifi de invitados.",
  "slot": 13.58,
  "who": "Pablo"
 },
 {
  "start": 230.22,
  "text": "Con las instrucciones originales del kit, Gemini trata ese mensaje como una fuente fiable y revela la contraseña.",
  "slot": 9.0,
  "who": "Pablo"
 },
 {
  "start": 239.22,
  "text": "Con nuestras instrucciones y el control final en el código, la respuesta es: no consta en los documentos disponibles.",
  "slot": 11.4,
  "who": "Pablo"
 },
 {
  "start": 250.62,
  "text": "Por último, una pregunta cuya respuesta no está en ningún documento: el asistente lo reconoce en lugar de inventarse una cifra.",
  "slot": 12.58,
  "who": "Pablo"
 },
 {
  "start": 263.2,
  "text": "Para medir todo esto escribimos 64 preguntas en tres grupos: uno para ajustar el sistema y dos que no usamos para ajustar, para que la evaluación sea justa.",
  "slot": 13.0,
  "who": "Wenjie"
 },
 {
  "start": 276.2,
  "text": "Antes de ejecutar, dejamos por escrito qué resultado haría falta para aceptar cada mejora. En total obtuvimos 396 respuestas reales de Gemini.",
  "slot": 11.0,
  "who": "Wenjie"
 },
 {
  "start": 287.2,
  "text": "Las instrucciones originales del kit aciertan algo más cuando la pregunta usa palabras distintas a las de los documentos, pero revelan la contraseña las dos veces que se la piden.",
  "slot": 14.0,
  "who": "Wenjie"
 },
 {
  "start": 301.2,
  "text": "Nuestra versión final no la revela nunca, reconoce todas las preguntas sin respuesta y resuelve mejor los conflictos entre documentos.",
  "slot": 10.0,
  "who": "Wenjie"
 },
 {
  "start": 311.2,
  "text": "Nuestro hallazgo principal: cuando hicimos las instrucciones menos estrictas para que contestara más, el modelo también se volvió más fácil de manipular.",
  "slot": 11.0,
  "who": "Wenjie"
 },
 {
  "start": 322.2,
  "text": "En dos ocasiones intentó dar la contraseña, y fue el control en el código el que lo impidió. Por eso la seguridad no puede depender solo de las instrucciones.",
  "slot": 14.0,
  "who": "Wenjie"
 },
 {
  "start": 336.2,
  "text": "También tiene límites. El diccionario de sinónimos que añadimos lo escribimos conociendo ya las preguntas de prueba, así que su mejora está sobreestimada.",
  "slot": 11.0,
  "who": "Wenjie"
 },
 {
  "start": 347.2,
  "text": "Y los fallos que quedan son de búsqueda: si el fragmento correcto no llega al modelo, ninguna instrucción lo arregla.",
  "slot": 10.0,
  "who": "Wenjie"
 },
 {
  "start": 357.2,
  "text": "El código, los datos y los resultados están en nuestro repositorio de GitHub. Gracias.",
  "slot": 7.0,
  "who": "Los dos"
 }
]

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def voices():
    out = run(['say', '-v', '?']).stdout
    vs = []
    for line in out.splitlines():
        m = re.match(r'^(.+?)\s{2,}([a-z]{2}[_-][A-Z]{2,3})\s', line)
        if m:
            vs.append((m.group(1).strip(), m.group(2).replace('-', '_')))
    return vs

def pick(vs, preferred, locales):
    names = [n for n, loc in vs if loc in locales]
    for p in preferred:
        for n in names:
            if n.split(' (')[0] == p:
                return n
    return names[0] if names else None

def duration(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path])
    return float(r.stdout.strip())

def main():
    if shutil.which('say') is None:
        sys.exit('Este script necesita macOS (comando say).')
    if shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None:
        sys.exit('Falta ffmpeg. Instálalo con:  brew install ffmpeg')
    if not os.path.exists(VIDEO_IN):
        sys.exit(f'No encuentro {VIDEO_IN} en esta carpeta.')
    vs = voices()
    es_es = {'es_ES'}
    es_any = {loc for _, loc in vs if loc.startswith('es_')}
    female = pick(vs, ['Mónica', 'Monica', 'Marisol', 'Paulina'], es_es) or pick(vs, ['Paulina', 'Mónica'], es_any)
    male = pick(vs, ['Jorge', 'Juan', 'Diego'], es_es) or pick(vs, ['Juan', 'Diego', 'Jorge'], es_any)
    if not female and not male:
        sys.exit('No hay voces en español instaladas. Ajustes del Sistema > Accesibilidad > Contenido leído > Voz del sistema > Gestionar voces > Español.')
    female = female or male
    male = male or female
    print(f'Voz de Wenjie: {female} · Voz de Pablo: {male}')
    voice_for = {'Wenjie': female, 'Pablo': male, 'Los dos': female}
    tmp = tempfile.mkdtemp(prefix='voz_')
    inputs, filters = [], []
    for i, s in enumerate(SEGS):
        aiff = os.path.join(tmp, f'seg{i:02d}.aiff')
        avail = s['slot'] - 0.4
        for rate in (175, 195, 215, 235):
            run(['say', '-v', voice_for[s['who']], '-r', str(rate), '-o', aiff, s['text']])
            d = duration(aiff)
            if d <= avail:
                break
        print(f"{i+1:2d}/{len(SEGS)} {s['who']:7s} {d:5.1f}s de {s['slot']:.1f}s  {s['text'][:60]}")
        inputs += ['-i', aiff]
        ms = int((s['start'] + 0.3) * 1000)
        filters.append(f'[{i+1}:a]aresample=44100,adelay={ms}|{ms}[a{i}]')
    mix = ''.join(f'[a{i}]' for i in range(len(SEGS)))
    filters.append(f'{mix}amix=inputs={len(SEGS)}:normalize=0:duration=longest,apad[aout]')
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', VIDEO_IN] + inputs + [
        '-filter_complex', ';'.join(filters), '-map', '0:v', '-map', '[aout]',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', VIDEO_OUT]
    r = run(cmd)
    if r.returncode != 0:
        sys.exit('ffmpeg falló:\n' + r.stderr)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'Listo: {VIDEO_OUT}')

if __name__ == '__main__':
    main()
