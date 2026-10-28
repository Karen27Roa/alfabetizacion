from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.models import Rol
from cuentas.permisos import rol_requerido

from .forms import CuestionarioForm
from .models import Intento, Pregunta
from .services import registrar_intento, semaforo_intento

POR_SECCION = 6   # 18 preguntas en 3 secciones (RNF-01)


@rol_requerido(Rol.ESTUDIANTE)
def cuestionario(request):
    preguntas = list(Pregunta.objects.select_related("variable"))
    if len(preguntas) != 18:
        messages.error(request, "El instrumento no está completo. Avisa al administrador.")
        return render(request, "instrumento/cuestionario.html", {"secciones": []})

    form = CuestionarioForm(request.POST or None, preguntas=preguntas)
    if request.method == "POST":
        if form.is_valid():
            intento = registrar_intento(request.user, form.cleaned_data["semestre"], form.respuestas())
            return redirect("instrumento:resultado", pk=intento.pk)
        faltan = sum(1 for n in form.errors if n.startswith("p_"))
        messages.error(request, f"No se pudo enviar. Te faltan {faltan} pregunta(s) por responder."
                       if faltan else "No se pudo enviar. Revisa el formulario.")

    items = [{"numero": p.orden, "pregunta": p, "campo": form[f"p_{p.pk}"]} for p in preguntas]
    secciones = [items[i:i + POR_SECCION] for i in range(0, len(items), POR_SECCION)]
    return render(request, "instrumento/cuestionario.html", {"form": form, "secciones": secciones})


@rol_requerido(Rol.ESTUDIANTE)
def resultado(request, pk):
    intento = get_object_or_404(Intento.objects.select_related("config"), pk=pk, usuario=request.user)
    return render(request, "instrumento/resultado.html",
                  {"intento": intento, "semaforo": semaforo_intento(intento)})


@rol_requerido(Rol.ESTUDIANTE)
def historial(request):
    return render(request, "instrumento/historial.html", {"intentos": request.user.intentos.all()})
