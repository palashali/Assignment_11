from django import forms
from .models import RentalRequest


class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Introduce yourself, specify intended move-in date, number of occupants, and any questions you have for the property owner...'
                }
            )
        }
