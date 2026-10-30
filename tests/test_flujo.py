"""Pruebas de la interfaz: registro, cuestionario, resultado, permisos y dashboard."""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from configuracion.models import ConfigRiesgo
from cuentas.models import Perfil, Rol
from instrumento.models import Intento, Pregunta


@pytest.fixture
def estudiante(client, db):
    u = User.objects.create_user("ana", password="Clave-segura-123", first_name="Ana", last_name="Pérez")
    Perfil.objects.create(usuario=u, rol=Rol.ESTUDIANTE)
    client.force_login(u)
    return u


@pytest.fixture
def docente(db):
    u = User.objects.create_user("profe", password="Clave-segura-123")
    Perfil.objects.create(usuario=u, rol=Rol.DOCENTE)
    return u


def datos(valor, semestre="3"):
    d = {f"p_{p.pk}": str(valor) for p in Pregunta.objects.all()}
    d["semestre"] = semestre
    return d


def test_instrumento_cargado(db):
    assert Pregunta.objects.count() == 18


def test_registro_crea_estudiante(client, db):
    r = client.post(reverse("cuentas:registro"), {
        "username": "luis", "first_name": "Luis", "last_name": "Gómez", "email": "luis@uni.edu.co",
        "password1": "Clave-segura-123", "password2": "Clave-segura-123"})
    assert r.status_code == 302
    assert User.objects.get(username="luis").perfil.rol == Rol.ESTUDIANTE


def test_envio_completo_clasifica_y_muestra_resultado(client, estudiante):
    r = client.post(reverse("instrumento:cuestionario"), datos(5))
    intento = Intento.objects.get()
    assert r.status_code == 302 and intento.puntaje_total == 90 and intento.nivel == "alto"
    assert intento.respuestas.count() == 18
    pagina = client.get(reverse("instrumento:resultado", args=[intento.pk]))
    assert b"90" in pagina.content and b"Riesgo alto" in pagina.content


def test_envio_incompleto_no_guarda_y_avisa(client, estudiante):
    d = datos(3)
    d.pop(next(k for k in d if k.startswith("p_")))
    r = client.post(reverse("instrumento:cuestionario"), d)
    assert r.status_code == 200 and not Intento.objects.exists()
    assert "Falta responder esta pregunta" in r.content.decode()


def test_semestre_obligatorio(client, estudiante):
    r = client.post(reverse("instrumento:cuestionario"), datos(3, semestre=""))
    assert r.status_code == 200 and not Intento.objects.exists()


def test_repetir_no_sobrescribe(client, estudiante):
    client.post(reverse("instrumento:cuestionario"), datos(1))
    client.post(reverse("instrumento:cuestionario"), datos(5))
    assert Intento.objects.count() == 2


def test_estudiante_no_ve_resultado_ajeno(client, estudiante, docente):
    client.post(reverse("instrumento:cuestionario"), datos(3))
    ajeno = Intento.objects.get()
    otro = User.objects.create_user("otro", password="x")
    client.force_login(otro)
    assert client.get(reverse("instrumento:resultado", args=[ajeno.pk])).status_code == 404


def test_estudiante_no_entra_al_dashboard(client, estudiante):
    assert client.get(reverse("reportes:dashboard")).status_code == 403
    assert client.get(reverse("reportes:excel")).status_code == 403


def test_anonimo_va_al_login(client, db):
    r = client.get(reverse("instrumento:cuestionario"))
    assert r.status_code == 302 and "/cuentas/ingresar/" in r["Location"]


def test_dashboard_filtra_y_exporta(client, estudiante, docente):
    client.post(reverse("instrumento:cuestionario"), datos(5, "2"))
    client.post(reverse("instrumento:cuestionario"), datos(1, "4"))
    client.force_login(docente)
    r = client.get(reverse("reportes:dashboard"), {"semestre": "2"})
    assert r.status_code == 200 and r.context["total_intentos"] == 1
    assert r.context["distribucion"]["alto"] == 1
    parcial = client.get(reverse("reportes:dashboard"), HTTP_HX_REQUEST="true")
    assert b"<html" not in parcial.content          # HTMX recibe solo el panel
    x = client.get(reverse("reportes:excel"), {"semestre": "2"})
    assert x.status_code == 200 and x["Content-Disposition"].endswith('.xlsx"')


def test_filtro_invalido_se_ignora(client, docente):
    client.force_login(docente)
    assert client.get(reverse("reportes:dashboard"), {"semestre": "abc"}).status_code == 200


def test_cambio_de_rangos_no_altera_intentos_previos(client, estudiante):
    client.post(reverse("instrumento:cuestionario"), datos(3))        # 54 → medio con rangos por defecto
    viejo = Intento.objects.get()
    ConfigRiesgo.objects.create(bajo_max=50, medio_max=60)              # nueva versión activa
    client.post(reverse("instrumento:cuestionario"), datos(3))
    nuevo = Intento.objects.exclude(pk=viejo.pk).get()
    viejo.refresh_from_db()
    assert viejo.nivel == "medio" and viejo.config.version == 1
    assert nuevo.nivel == "medio" and nuevo.config.version == 2


def test_toggle_password_presente_en_login_y_registro(client, db):
    r_login = client.get(reverse("cuentas:login"))
    assert r_login.status_code == 200
    contenido_login = r_login.content.decode()
    assert 'class="input-group"' in contenido_login
    assert 'btn-toggle-password' in contenido_login
    assert 'icono-ojo-abierto' in contenido_login
    assert 'icono-ojo-tachado' in contenido_login

    r_reg = client.get(reverse("cuentas:registro"))
    assert r_reg.status_code == 200
    contenido_reg = r_reg.content.decode()
    assert 'class="input-group"' in contenido_reg
    # Debe tener botones para password1 y password2
    assert contenido_reg.count('btn-toggle-password" type="button"') == 2
    assert 'icono-ojo-abierto' in contenido_reg
    assert 'icono-ojo-tachado' in contenido_reg


def test_enlace_olvido_contrasena_en_login(client, db):
    r = client.get(reverse("cuentas:login"))
    assert r.status_code == 200
    contenido = r.content.decode()
    assert "¿Olvidaste tu contraseña?" in contenido
    assert reverse("cuentas:password_reset") in contenido


def test_flujo_recuperar_contrasena(client, db):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    u = User.objects.create_user("carlos", email="carlos@uni.edu.co", password="Vieja-Clave-123")
    
    # 1. Página para pedir el correo
    r_form = client.get(reverse("cuentas:password_reset"))
    assert r_form.status_code == 200
    assert 'name="email"' in r_form.content.decode()

    # 2. Envío del correo y redirección a confirmación
    r_post = client.post(reverse("cuentas:password_reset"), {"email": "carlos@uni.edu.co"})
    assert r_post.status_code == 302
    assert r_post.url == reverse("cuentas:password_reset_done")
    r_done = client.get(reverse("cuentas:password_reset_done"))
    assert r_done.status_code == 200
    assert "Revisa tu correo" in r_done.content.decode()

    # 3. Vista de confirmación con token válido
    uid = urlsafe_base64_encode(force_bytes(u.pk))
    token = default_token_generator.make_token(u)
    r_confirm = client.get(reverse("cuentas:password_reset_confirm", kwargs={"uidb64": uid, "token": token}), follow=True)
    assert r_confirm.status_code == 200
    assert "Crea tu nueva contraseña" in r_confirm.content.decode()
    assert "btn-toggle-password" in r_confirm.content.decode()

    # 4. Establecer la nueva contraseña
    post_url = r_confirm.redirect_chain[0][0]
    r_change = client.post(post_url, {
        "new_password1": "Nueva-Segura-456",
        "new_password2": "Nueva-Segura-456",
    }, follow=True)
    assert r_change.status_code == 200
    assert "Contraseña restablecida" in r_change.content.decode()

    # 5. Comprobar que la contraseña se actualizó en la base de datos y permite iniciar sesión
    u.refresh_from_db()
    assert u.check_password("Nueva-Segura-456")
    login_ok = client.login(username="carlos", password="Nueva-Segura-456")
    assert login_ok

    # 6. Enlace con token inválido o expirado
    r_invalido = client.get(reverse("cuentas:password_reset_confirm", kwargs={"uidb64": uid, "token": "token-invalido"}), follow=True)
    assert "Enlace no válido" in r_invalido.content.decode()


