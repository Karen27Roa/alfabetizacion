from collections import defaultdict

from django.db import transaction

from configuracion.models import ConfigRiesgo
from puntaje import motor

from .models import COLOR_SEMAFORO, Intento, Respuesta


@transaction.atomic
def registrar_intento(usuario, semestre: int, respuestas: dict[int, int]) -> Intento:
    """Intento atómico: solo existe si las 18 respuestas llegan completas y válidas."""
    config = ConfigRiesgo.vigente()
    total = motor.puntaje_total(respuestas.values())
    nivel = motor.clasificar(total, config.bajo_max, config.medio_max)
    intento = Intento.objects.create(usuario=usuario, config=config, semestre=semestre,
                                     puntaje_total=total, nivel=nivel)
    Respuesta.objects.bulk_create(
        [Respuesta(intento=intento, pregunta_id=pid, valor=v) for pid, v in respuestas.items()])
    return intento


def semaforo_intento(intento: Intento) -> list[dict]:
    """Promedio por variable de un intento y su color de semáforo."""
    grupos = defaultdict(list)
    for r in intento.respuestas.select_related("pregunta__variable"):
        grupos[r.pregunta.variable].append(r.valor)
    filas = []
    for variable, valores in sorted(grupos.items(), key=lambda kv: kv[0].id):
        prom = sum(valores) / len(valores)
        color = motor.color_semaforo(prom, intento.config.verde_max, intento.config.rojo_min)
        filas.append({"variable": variable, "promedio": prom, "color": color, "bs": COLOR_SEMAFORO[color]})
    return filas
