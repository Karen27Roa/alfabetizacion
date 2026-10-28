from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]
    list_display = ("username", "first_name", "last_name", "email", "is_active")


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
