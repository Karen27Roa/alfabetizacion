from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from configuracion.models import ConfigRiesgo
from puntaje.motor import ALTO, BAJO, MEDIO

NIVELES = [(BAJO, "Bajo"), (MEDIO, "Medio"), (ALTO, "Alto")]
COLOR_NIVEL = {BAJO: "success", MEDIO: "warning", ALTO: "danger"}   # clases de Bootstrap
COLOR_SEMAFORO = {"verde": "success", "amarillo": "warning", "rojo": "danger"}


class Variable(models.Model):
    codigo = models.CharField(max_length=4, unique=True)   # V1 … V10
    nombre = models.CharField(max_length=80)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"


class Pregunta(models.Model):
    orden = models.PositiveSmallIntegerField(unique=True)
    texto = models.CharField(max_length=300)
    variable = models.ForeignKey(Variable, on_delete=models.PROTECT, related_name="preguntas")

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.orden}. {self.texto[:60]}"


class Intento(models.Model):
    """Un estudiante puede tener varios intentos (RF-09); ninguno se sobrescribe."""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="intentos")
    config = models.ForeignKey(ConfigRiesgo, on_delete=models.PROTECT, related_name="intentos")
    semestre = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    puntaje_total = models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(90)])
    nivel = models.CharField(max_length=6, choices=NIVELES)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        indexes = [models.Index(fields=["semestre", "nivel"]), models.Index(fields=["fecha"])]

    @property
    def color(self):
        return COLOR_NIVEL[self.nivel]

    @property
    def recomendacion(self):
        return self.config.recomendacion(self.nivel)


class Respuesta(models.Model):
    intento = models.ForeignKey(Intento, on_delete=models.CASCADE, related_name="respuestas")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    valor = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["intento", "pregunta"], name="una_respuesta_por_pregunta")]
