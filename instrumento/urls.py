from django.urls import path

from . import views

app_name = "instrumento"
urlpatterns = [
    path("", views.cuestionario, name="cuestionario"),
    path("resultado/<int:pk>/", views.resultado, name="resultado"),
    path("historial/", views.historial, name="historial"),
]
