"""Motor de puntaje y clasificación. Python puro: no importa Django ni modelos.
Recibe respuestas y umbrales como datos y devuelve resultados (Tablas 6, 20 y 21)."""
from collections import defaultdict
from typing import Iterable

N_PREGUNTAS = 18
VALOR_MIN, VALOR_MAX = 1, 5
PUNTAJE_MIN = N_PREGUNTAS * VALOR_MIN   # 18
PUNTAJE_MAX = N_PREGUNTAS * VALOR_MAX   # 90

BAJO, MEDIO, ALTO = "bajo", "medio", "alto"
VERDE, AMARILLO, ROJO = "verde", "amarillo", "rojo"


class ErrorValidacion(ValueError):
    """Entrada fuera de los límites posibles del instrumento."""


def puntaje_total(valores: Iterable[int]) -> int:
    valores = list(valores)
    if len(valores) != N_PREGUNTAS:
        raise ErrorValidacion(f"Se esperaban {N_PREGUNTAS} respuestas y llegaron {len(valores)}.")
    if any(not isinstance(v, int) or not VALOR_MIN <= v <= VALOR_MAX for v in valores):
        raise ErrorValidacion("Cada respuesta debe ser un entero entre 1 y 5.")
    return sum(valores)


def clasificar(total: int, bajo_max: int = 41, medio_max: int = 65) -> str:
    if not PUNTAJE_MIN <= total <= PUNTAJE_MAX:
        raise ErrorValidacion(f"El puntaje debe estar entre {PUNTAJE_MIN} y {PUNTAJE_MAX}.")
    if total <= bajo_max:
        return BAJO
    if total <= medio_max:
        return MEDIO
    return ALTO


def color_semaforo(promedio: float, verde_max: float = 2.0, rojo_min: float = 3.0) -> str:
    """Verde si promedio <= verde_max; rojo si >= rojo_min; amarillo en medio (sin vacíos)."""
    if not VALOR_MIN <= promedio <= VALOR_MAX:
        raise ErrorValidacion("El promedio de una variable debe estar entre 1 y 5.")
    if promedio <= verde_max:
        return VERDE
    if promedio >= rojo_min:
        return ROJO
    return AMARILLO


def promedios_por_variable(pares: Iterable[tuple[str, int]]) -> dict[str, float]:
    """pares: (codigo_variable, valor). Devuelve {codigo: promedio}."""
    grupos = defaultdict(list)
    for codigo, valor in pares:
        grupos[codigo].append(valor)
    return {c: sum(v) / len(v) for c, v in grupos.items()}
