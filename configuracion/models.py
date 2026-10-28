from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max


class ConfigRiesgo(models.Model):
    """Versión de rangos, umbrales del semáforo y recomendaciones (RF-08).
    Cada cambio crea una versión nueva; los intentos guardan la versión usada."""
    version = models.PositiveIntegerField(unique=True, editable=False)
    activa = models.BooleanField(default=True)
    bajo_max = models.PositiveSmallIntegerField("Límite máximo de riesgo bajo", default=41)
    medio_max = models.PositiveSmallIntegerField("Límite máximo de riesgo medio", default=65)
    verde_max = models.FloatField("Semáforo: verde si promedio ≤", default=2.0)
    rojo_min = models.FloatField("Semáforo: rojo si promedio ≥", default=3.0)
    rec_bajo = models.TextField("Recomendación (bajo)", default=(
        "Reforzar las buenas prácticas ya adquiridas mediante contenido de refuerzo opcional."))
    rec_medio = models.TextField("Recomendación (medio)", default=(
        "Talleres orientados a la verificación de fuentes y a la validación crítica de "
        "respuestas generadas por inteligencia artificial."))
    rec_alto = models.TextField("Recomendación (alto)", default=(
        "Intervención prioritaria, con acompañamiento docente y formación intensiva en "
        "alfabetización mediática crítica."))
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "configuración de riesgo"
        verbose_name_plural = "configuraciones de riesgo"
        ordering = ["-version"]

    def __str__(self):
        return f"Versión {self.version} ({self.bajo_max}/{self.medio_max})" + (" · activa" if self.activa else "")

    def clean(self):
        if not 18 <= self.bajo_max < self.medio_max <= 89:
            raise ValidationError("Debe cumplirse: 18 ≤ límite de bajo < límite de medio ≤ 89.")
        if not 1.0 <= self.verde_max < self.rojo_min <= 5.0:
            raise ValidationError("Debe cumplirse: 1,0 ≤ umbral verde < umbral rojo ≤ 5,0.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.version is None:
                self.version = (ConfigRiesgo.objects.aggregate(m=Max("version"))["m"] or 0) + 1
            super().save(*args, **kwargs)
            if self.activa:
                ConfigRiesgo.objects.exclude(pk=self.pk).update(activa=False)

    def recomendacion(self, nivel: str) -> str:
        return {"bajo": self.rec_bajo, "medio": self.rec_medio, "alto": self.rec_alto}[nivel]

    @classmethod
    def vigente(cls):
        return cls.objects.filter(activa=True).first() or cls.objects.create()
