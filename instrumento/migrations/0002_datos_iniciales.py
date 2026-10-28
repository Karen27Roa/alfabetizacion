from django.db import migrations

# Variables V1–V10: nombres de la Tabla 13 del documento.
VARIABLES = [
    ("V1", "Verificación de fuentes"), ("V2", "Información falsa"), ("V3", "Argumentación"),
    ("V4", "Consumo rápido"), ("V5", "Compartir sin análisis"), ("V6", "Reacción emocional"),
    ("V7", "Uso de IA sin validación"), ("V8", "Contraste de fuentes"),
    ("V9", "Dependencia de una sola fuente"), ("V10", "Influencia del algoritmo"),
]

# ⚠ BORRADOR: el PDF no incluye el texto de las 18 preguntas ni su asignación a variables
# (dice que se toman del formulario original, sección 3.11). Reemplázalas desde
# /admin/instrumento/pregunta/ con las del formulario de Microsoft Forms.
# Están redactadas de forma que 5 = mayor riesgo.
PREGUNTAS = [
    ("V1", "Comparto contenidos sin comprobar quién los publicó originalmente."),
    ("V1", "Rara vez reviso si una noticia proviene de un medio confiable."),
    ("V2", "Me cuesta distinguir entre una noticia verdadera y una falsa."),
    ("V2", "He creído y difundido información que después resultó ser falsa."),
    ("V3", "Cuando creo que algo es verdadero o falso, no suelo explicar por qué."),
    ("V3", "Acepto una afirmación si la repiten muchas personas, sin pedir pruebas."),
    ("V4", "Me quedo solo con los titulares sin leer el contenido completo."),
    ("V4", "Consumo videos o publicaciones muy rápido, sin detenerme a analizarlos."),
    ("V5", "Reenvío mensajes o publicaciones apenas los recibo."),
    ("V5", "Comparto contenido porque me parece llamativo, aunque no lo haya analizado."),
    ("V6", "Me dejo llevar por contenidos que me generan emociones fuertes (rabia, miedo, indignación)."),
    ("V6", "Reacciono o comento de inmediato a publicaciones que me molestan, sin reflexionar."),
    ("V7", "Uso respuestas de inteligencia artificial sin comprobar si son correctas."),
    ("V7", "Entrego trabajos con información generada por IA sin revisarla."),
    ("V8", "Casi nunca comparo una misma noticia en distintos medios."),
    ("V8", "No busco otras opiniones o puntos de vista sobre un tema."),
    ("V9", "Me informo casi siempre por una sola red social o medio."),
    ("V10", "Creo que lo que me muestran las redes sociales refleja la realidad completa."),
]


def cargar(apps, schema_editor):
    Variable, Pregunta = apps.get_model("instrumento", "Variable"), apps.get_model("instrumento", "Pregunta")
    por_codigo = {c: Variable.objects.create(codigo=c, nombre=n) for c, n in VARIABLES}
    for orden, (codigo, texto) in enumerate(PREGUNTAS, start=1):
        Pregunta.objects.create(orden=orden, texto=texto, variable=por_codigo[codigo])


class Migration(migrations.Migration):
    dependencies = [("instrumento", "0001_initial")]
    operations = [migrations.RunPython(cargar, migrations.RunPython.noop)]
