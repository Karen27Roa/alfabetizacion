from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import (
    LoginForm,
    NuevaPasswordForm,
    RecuperarPasswordForm,
    RegistroForm,
)
from .models import Rol
from .permisos import rol_de


class Ingresar(LoginView):
    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo iniciar sesión. Por favor, verifica los campos marcados en rojo.")
        return super().form_invalid(form)


class RecuperarPassword(PasswordResetView):
    template_name = "cuentas/password_reset.html"
    email_template_name = "cuentas/password_reset_email.html"
    subject_template_name = "cuentas/password_reset_subject.txt"
    success_url = reverse_lazy("cuentas:password_reset_done")
    form_class = RecuperarPasswordForm

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, ingresa un correo electrónico válido.")
        return super().form_invalid(form)


class ConfirmarPassword(PasswordResetConfirmView):
    template_name = "cuentas/password_reset_confirm.html"
    success_url = reverse_lazy("cuentas:password_reset_complete")
    form_class = NuevaPasswordForm

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo actualizar la contraseña. Revisa los requisitos marcados en rojo.")
        return super().form_invalid(form)


def registro(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistroForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, "¡Cuenta creada! Ya puedes responder el diagnóstico.")
            return redirect("home")
        messages.error(request, "Revisa los campos marcados en rojo.")
    return render(request, "cuentas/registro.html", {"form": form})


def home(request):
    """Redirige según el rol: estudiante → cuestionario, docente/admin → panel."""
    if not request.user.is_authenticated:
        return redirect("cuentas:login")
    if rol_de(request.user) == Rol.ESTUDIANTE:
        return redirect("instrumento:cuestionario")
    return redirect("reportes:dashboard")
