from django import forms
from healthxpfront.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'birth_date', 'height', 'weight']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'min': '0'})
        }
