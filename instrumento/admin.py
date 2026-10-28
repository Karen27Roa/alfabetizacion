from django.contrib import admin

from .models import Intento, Pregunta, Variable


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ("orden", "texto", "variable")
    list_editable = ("texto", "variable")


@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "semestre", "puntaje_total", "nivel", "config", "fecha")
    list_filter = ("nivel", "semestre")
    def has_change_permission(self, request, obj=None):   # los intentos no se editan
        return False
