from django.contrib import admin
from django.urls import include, path

from cuentas.views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("cuentas/", include("cuentas.urls")),
    path("cuestionario/", include("instrumento.urls")),
    path("panel/", include("reportes.urls")),
]
