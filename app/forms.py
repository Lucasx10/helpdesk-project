from django import forms
from .models import Comentarios

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentarios
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }
