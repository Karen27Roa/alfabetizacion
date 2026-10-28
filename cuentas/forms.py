from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Perfil, Rol


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario"
        self.fields["password"].label = "Contraseña"
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"
        self.error_messages["invalid_login"] = "Usuario o contraseña incorrectos."


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", max_length=60)
    last_name = forms.CharField(label="Apellidos", max_length=60)
    email = forms.EmailField(label="Correo institucional")
    codigo_estudiante = forms.CharField(label="Código de estudiante (opcional)", max_length=20, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {"username": "Usuario"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Repite la contraseña"
        for f in self.fields.values():
            f.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        dominios = settings.DOMINIOS_PERMITIDOS
        if dominios and email.split("@")[-1] not in dominios:
            raise forms.ValidationError("Usa tu correo institucional (" + ", ".join("@" + d for d in dominios) + ").")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese correo.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            # Solo se auto-registran estudiantes; docentes y admins los crea el administrador.
            Perfil.objects.create(usuario=usuario, rol=Rol.ESTUDIANTE,
                                  codigo_estudiante=self.cleaned_data["codigo_estudiante"])
        return usuario
