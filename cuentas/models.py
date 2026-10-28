from django.conf import settings
from django.db import models


class Rol(models.TextChoices):
    ESTUDIANTE = "estudiante", "Estudiante"
    DOCENTE = "docente", "Docente / Coordinador"
    ADMIN = "admin", "Administrador"


class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=12, choices=Rol.choices, default=Rol.ESTUDIANTE)
    codigo_estudiante = models.CharField("Código de estudiante", max_length=20, blank=True)

    def __str__(self):
        return f"{self.usuario} ({self.get_rol_display()})"
