from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetDoneView,
)
from django.urls import path

from . import views

app_name = "cuentas"
urlpatterns = [
    path("ingresar/", views.Ingresar.as_view(), name="login"),
    path("salir/", LogoutView.as_view(), name="logout"),
    path("registro/", views.registro, name="registro"),
    path(
        "recuperar/",
        views.RecuperarPassword.as_view(),
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
        views.ConfirmarPassword.as_view(),
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

