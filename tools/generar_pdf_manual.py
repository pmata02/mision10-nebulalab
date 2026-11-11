"""Genera data/10_manual_empleado_2026.pdf (documento ficticio con texto real, no escaneado)."""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

OUT = Path(__file__).resolve().parents[1] / 'data' / '10_manual_empleado_2026.pdf'
CABECERA = 'NébulaLab · Manual del empleado · Uso interno'
PAGINAS = [
    ['DOCUMENTO: Manual del empleado NébulaLab',
     'Versión: 2026-01 | Vigente desde: 2026-01-15 | Responsable: Personas',
     'Sección 1. Horario',
     'La jornada es flexible con una franja de presencia obligatoria de 10:00 a 14:00 de lunes a jueves. '
     'Los viernes de julio y agosto la jornada es intensiva y termina a las 15:00.',
     'Sección 2. Registro de jornada',
     'Cada persona registra su hora de entrada y de salida en la aplicación NébulaTime, también en los días de teletrabajo. '
     'Los olvidos se corrigen en la propia aplicación antes del último día laborable del mes.'],
    ['Sección 3. Gastos de viaje',
     'Los viajes se reservan a través de la agencia corporativa y los billetes se emiten en clase turista. '
     'La dieta es de 55 euros por día en viajes nacionales y de 90 euros por día en viajes internacionales. '
     'El uso del vehículo propio se compensa a 0,26 euros por kilómetro.',
     'Sección 4. Permisos retribuidos',
     'Por matrimonio o registro de pareja de hecho se conceden 15 días naturales. Por traslado de domicilio se concede 1 día. '
     'Por fallecimiento de un familiar de primer grado se conceden 2 días, o 4 si es necesario desplazarse.'],
    ['Sección 5. Equipos y seguridad de la información',
     'El portátil corporativo es personal y no se presta. Se debe bloquear la pantalla al ausentarse del puesto. '
     'La pérdida o el robo de un equipo se comunica a Soporte TI en un plazo máximo de 2 horas.',
     'Sección 6. Canal ético',
     'Las comunicaciones de posibles irregularidades se presentan en el canal ético del portal interno, que admite comunicaciones anónimas.'],
]

def main():
    c = canvas.Canvas(str(OUT), pagesize=A4)
    w, h = A4
    for n, bloques in enumerate(PAGINAS, 1):
        c.setFont('Helvetica', 8); c.drawString(50, h - 30, CABECERA)
        c.drawString(w - 110, 25, f'Página {n} de {len(PAGINAS)}')
        y = h - 70
        for b in bloques:
            titulo = b.startswith('Sección') or b.startswith('DOCUMENTO')
            c.setFont('Helvetica-Bold' if titulo else 'Helvetica', 11 if titulo else 10)
            for line in wrap(b, 95):
                c.drawString(50, y, line); y -= 15
            y -= 8
        c.showPage()
    c.save()
    print('PDF generado:', OUT)

if __name__ == '__main__':
    main()
