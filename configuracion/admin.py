from django.contrib import admin, messages

from .models import ConfigRiesgo


@admin.register(ConfigRiesgo)
class ConfigRiesgoAdmin(admin.ModelAdmin):
    list_display = ("version", "bajo_max", "medio_max", "verde_max", "rojo_min", "activa", "creado")
    readonly_fields = ("version", "creado")

    def save_model(self, request, obj, form, change):
        # Si la versión ya se usó en intentos, no se altera: se crea una versión nueva.
        if change and obj.intentos.exists():
            obj.pk = None
            obj.version = None
            obj.activa = True
            obj._state.adding = True
            messages.info(request, "Esa versión ya tiene intentos; se guardó como una versión nueva.")
        super().save_model(request, obj, form, change)
