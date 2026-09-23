from decimal import Decimal
from django import forms
from .models import Property


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'title',
            'description',
            'property_type',
            'location',
            'rent',
            'bedrooms',
            'bathrooms',
            'image',
            'is_available',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Luxury 2BHK Apartment with Balcony'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the property amenities, furnishings, proximity to transit, etc.'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Gulshan 2, Dhaka or Manhattan, NY'}),
            'rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly rent amount', 'step': '0.01', 'min': '0'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_rent(self):
        rent = self.cleaned_data.get('rent')
        if rent is not None and rent <= 0:
            raise forms.ValidationError("Monthly rent must be greater than zero.")
        return rent

    def clean_bathrooms(self):
        bathrooms = self.cleaned_data.get('bathrooms')
        if bathrooms is not None and bathrooms < 1:
            raise forms.ValidationError("Property must have at least 1 bathroom.")
        return bathrooms


class PropertyFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by title, location or keywords...'})
    )
    property_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Property Types')] + list(Property.PROPERTY_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_rent = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price', 'min': '0'})
    )
    max_rent = forms.DecimalField(
        required=False,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price', 'min': '0'})
    )
    bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Beds', 'min': '0'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('rent', 'Price: Low to High'),
            ('-rent', 'Price: High to Low'),
            ('title', 'Alphabetical (A-Z)')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
