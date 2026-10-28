from django import forms

ESCALA = [("1", "Nunca"), ("2", "Casi nunca"), ("3", "A veces"), ("4", "Casi siempre"), ("5", "Siempre")]
SEMESTRES = [("", "Selecciona tu semestre…")] + [(str(i), "Semestre " + str(i)) for i in range(0, 11)]


class CuestionarioForm(forms.Form):
    semestre = forms.TypedChoiceField(
        label="Semestre que cursas", choices=SEMESTRES, coerce=int, empty_value=None,
        error_messages={"required": "Elige el semestre que cursas."},
        widget=forms.Select(attrs={"class": "form-select"}))

    def __init__(self, *args, preguntas, **kwargs):
        super().__init__(*args, **kwargs)
        self.preguntas = preguntas
        for p in preguntas:
            self.fields[f"p_{p.pk}"] = forms.ChoiceField(
                label=p.texto, choices=ESCALA, widget=forms.RadioSelect,
                error_messages={"required": "Falta responder esta pregunta."})

    def respuestas(self) -> dict[int, int]:
        return {p.pk: int(self.cleaned_data[f"p_{p.pk}"]) for p in self.preguntas}
