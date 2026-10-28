from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import LoginForm, RegistroForm
from .models import Rol
from .permisos import rol_de


class Ingresar(LoginView):
    template_name = "cuentas/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


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
