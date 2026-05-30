from django import forms
from .models import Penimbangan


class PenimbanganForm(forms.ModelForm):
    class Meta:
        model = Penimbangan
        fields = '__all__'