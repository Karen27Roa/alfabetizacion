"""Casos límite de las Tablas 20 y 21 del documento."""
import pytest

from puntaje.motor import ErrorValidacion, clasificar, color_semaforo, puntaje_total, promedios_por_variable


@pytest.mark.parametrize("total,esperado", [
    (18, "bajo"), (41, "bajo"), (42, "medio"), (65, "medio"), (66, "alto"), (88, "alto"), (90, "alto")])
def test_clasificacion_tabla_20(total, esperado):
    assert clasificar(total) == esperado


@pytest.mark.parametrize("total", [17, 91])
def test_puntaje_fuera_de_rango(total):
    with pytest.raises(ErrorValidacion):
        clasificar(total)


@pytest.mark.parametrize("prom,esperado", [
    (1.0, "verde"), (2.0, "verde"), (2.05, "amarillo"), (2.9, "amarillo"), (3.0, "rojo"), (5.0, "rojo")])
def test_semaforo_tabla_21(prom, esperado):
    assert color_semaforo(prom) == esperado


def test_puntaje_total_valida_cantidad_y_valores():
    assert puntaje_total([1] * 18) == 18 and puntaje_total([5] * 18) == 90
    with pytest.raises(ErrorValidacion):
        puntaje_total([3] * 17)
    with pytest.raises(ErrorValidacion):
        puntaje_total([6] + [3] * 17)


def test_promedios():
    assert promedios_por_variable([("V1", 2), ("V1", 4), ("V2", 5)]) == {"V1": 3.0, "V2": 5.0}
