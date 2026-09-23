from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = (
        (5, '5 - Excellent ★★★★★'),
        (4, '4 - Very Good ★★★★☆'),
        (3, '3 - Good ★★★☆☆'),
        (2, '2 - Fair ★★☆☆☆'),
        (1, '1 - Poor ★☆☆☆☆'),
    )

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select your overall rating for this property."
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Share your authentic experience living or staying in this property (landlord responsiveness, amenities, neighborhood, condition)...'
                }
            )
        }

    def clean_rating(self):
        rating = int(self.cleaned_data.get('rating'))
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating
