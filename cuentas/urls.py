from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from . import views
from .forms import NuevaPasswordForm, RecuperarPasswordForm

app_name = "cuentas"
urlpatterns = [
    path("ingresar/", views.Ingresar.as_view(), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path(
        "recuperar/",
        PasswordResetView.as_view(
            template_name="cuentas/password_reset.html",
            email_template_name="cuentas/password_reset_email.html",
            subject_template_name="cuentas/password_reset_subject.txt",
            success_url=reverse_lazy("cuentas:password_reset_done"),
            form_class=RecuperarPasswordForm,
        ),
        name="password_reset",
    ),
    path(
        "recuperar/enviado/",
        PasswordResetDoneView.as_view(
            template_name="cuentas/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="cuentas/password_reset_confirm.html",
            success_url=reverse_lazy("cuentas:password_reset_complete"),
            form_class=NuevaPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar/completado/",
        PasswordResetCompleteView.as_view(
            template_name="cuentas/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]

