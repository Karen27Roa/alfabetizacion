from collections import defaultdict

from django.db.models import Avg, Count, Q

from configuracion.models import ConfigRiesgo
from instrumento.models import COLOR_SEMAFORO, Intento, Respuesta
from puntaje import motor

COLORES_NIVEL = {"bajo": "#198754", "medio": "#ffc107", "alto": "#dc3545"}


def filtrar(semestre=None, q=""):
    qs = Intento.objects.select_related("usuario", "config")
    if semestre not in (None, ""):
        qs = qs.filter(semestre=int(semestre))
    if q:
        qs = qs.filter(Q(usuario__first_name__icontains=q) | Q(usuario__last_name__icontains=q)
                       | Q(usuario__username__icontains=q))
    return qs


def resumen(qs) -> dict:
    config = ConfigRiesgo.vigente()
    por_nivel = dict(qs.values_list("nivel").annotate(n=Count("id")))
    distribucion = {n: por_nivel.get(n, 0) for n in ("bajo", "medio", "alto")}

    sem = defaultdict(lambda: {"bajo": 0, "medio": 0, "alto": 0})
    for fila in qs.values("semestre", "nivel").annotate(n=Count("id")):
        sem[fila["semestre"]][fila["nivel"]] = fila["n"]
    semestres = sorted(sem)

    variables = []
    filas = (Respuesta.objects.filter(intento__in=qs.values("pk"))
             .values("pregunta__variable__id", "pregunta__variable__codigo", "pregunta__variable__nombre")
             .annotate(prom=Avg("valor")).order_by("pregunta__variable__id"))
    for f in filas:
        color = motor.color_semaforo(f["prom"], config.verde_max, config.rojo_min)
        variables.append({"codigo": f["pregunta__variable__codigo"], "nombre": f["pregunta__variable__nombre"],
                          "promedio": f["prom"], "color": color, "bs": COLOR_SEMAFORO[color]})

    return {
        "total_intentos": qs.count(),
        "total_estudiantes": qs.values("usuario").distinct().count(),
        "distribucion": distribucion,
        "variables": variables,
        "graficos": {
            "dona": {"labels": ["Bajo", "Medio", "Alto"], "data": list(distribucion.values()),
                     "colors": list(COLORES_NIVEL.values())},
            "barras": {"labels": [f"Sem. {s}" for s in semestres],
                       "series": [{"label": n.capitalize(), "color": COLORES_NIVEL[n],
                                   "data": [sem[s][n] for s in semestres]} for n in ("bajo", "medio", "alto")]},
        },
    }
