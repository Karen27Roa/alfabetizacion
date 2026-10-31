from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .models import Perfil, Rol


class BootstrapValidationMixin:
    """Añade la clase 'is-invalid' a los widgets de campos con errores de validación."""

    def full_clean(self):
        super().full_clean()
        self._marcar_campos_invalidos()

    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            self._marcar_campos_invalidos()
        return valid

    def _marcar_campos_invalidos(self):
        if not getattr(self, "is_bound", False) or not self.errors:
            return
        for name, field in self.fields.items():
            if name in self.errors:
                self._aplicar_is_invalid(field)
        if "__all__" in self.errors:
            for field in self.fields.values():
                self._aplicar_is_invalid(field)

    def _aplicar_is_invalid(self, field):
        clases = field.widget.attrs.get("class", "").split()
        if "is-invalid" not in clases:
            clases.append("is-invalid")
        field.widget.attrs["class"] = " ".join(clases)


class RecuperarPasswordForm(BootstrapValidationMixin, PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Correo electrónico"
        self.fields["email"].error_messages = {
            "required": "Por favor, ingresa tu correo electrónico.",
            "invalid": "Por favor, ingresa un correo electrónico válido.",
        }
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"
            f.widget.attrs["placeholder"] = "tu.correo@ejemplo.com"


class NuevaPasswordForm(BootstrapValidationMixin, SetPasswordForm):
    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden. Por favor, asegúrate de escribirlas idénticas.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password1"].error_messages = {
            "required": "Por favor, ingresa tu nueva contraseña.",
        }
        self.fields["new_password2"].label = "Confirma la nueva contraseña"
        self.fields["new_password2"].error_messages = {
            "required": "Por favor, confirma tu nueva contraseña.",
        }
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"


class LoginForm(BootstrapValidationMixin, AuthenticationForm):
    error_messages = {
        "invalid_login": "Usuario o contraseña incorrectos. Por favor, verifica tus datos.",
        "inactive": "Esta cuenta ha sido desactivada.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["username"].error_messages = {
            "required": "Por favor, ingresa tu nombre de usuario.",
        }
        self.fields["password"].label = "Contraseña"
        self.fields["password"].error_messages = {
            "required": "Por favor, ingresa tu contraseña.",
        }
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"


class RegistroForm(BootstrapValidationMixin, UserCreationForm):
    first_name = forms.CharField(
        label="Nombres",
        max_length=60,
        error_messages={
            "required": "Por favor, ingresa tus nombres.",
            "max_length": "Los nombres no pueden superar los 60 caracteres.",
        },
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=60,
        error_messages={
            "required": "Por favor, ingresa tus apellidos.",
            "max_length": "Los apellidos no pueden superar los 60 caracteres.",
        },
    )
    email = forms.EmailField(
        label="Correo institucional",
        error_messages={
            "required": "Por favor, ingresa tu correo institucional.",
            "invalid": "Por favor, ingresa una dirección de correo válida.",
        },
    )
    codigo_estudiante = forms.CharField(
        label="Código de estudiante (opcional)",
        max_length=20,
        required=False,
        error_messages={
            "max_length": "El código no puede superar los 20 caracteres.",
        },
    )

    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden. Por favor, asegúrate de escribirlas idénticas.",
    }

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {"username": "Usuario"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].error_messages = {
            "required": "Por favor, elige un nombre de usuario.",
            "unique": "Este nombre de usuario ya está registrado. Por favor, elige otro.",
            "invalid": "Ingresa un usuario válido (letras, números y @/./+/-/_).",
        }
        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].error_messages = {
            "required": "Por favor, crea una contraseña.",
        }
        self.fields["password2"].label = "Repite la contraseña"
        self.fields["password2"].error_messages = {
            "required": "Por favor, repite la contraseña para confirmarla.",
        }
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()
        dominios = settings.DOMINIOS_PERMITIDOS
        if dominios and email.split("@")[-1] not in dominios:
            raise forms.ValidationError("Usa tu correo institucional (" + ", ".join("@" + d for d in dominios) + ").")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo electrónico.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            # Solo se auto-registran estudiantes; docentes y admins los crea el administrador.
            Perfil.objects.create(usuario=usuario, rol=Rol.ESTUDIANTE,
                                  codigo_estudiante=self.cleaned_data["codigo_estudiante"])
        return usuario

