from django import forms
from django.contrib.auth.models import User
from main.models import Place, Reservation, UserProfile
from django.core.exceptions import ValidationError
import re

class PlaceForm(forms.ModelForm):
    image_url = forms.CharField(
        required=True,  # Ahora es obligatorio
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Image URL or Path'
    )

    class Meta:
        model = Place
        fields = ['name', 'latitude', 'longitude', 'open_time', 'close_time',
                  'open_days', 'description', 'image_url', 'sport_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'open_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'open_days': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Monday-Friday'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'sport_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Football, Basketball'}),
        }

    def clean_image_url(self):
        url = self.cleaned_data.get('image_url')
        if not url:
            raise ValidationError('Este campo es obligatorio.')
        # Validamos que sea URL absoluta o ruta /static/
        if not (re.match(r'^https?://', url) or url.startswith('/static/')):
            raise ValidationError('Debe ser una URL valida que comience con http:// o https://, o una ruta que empiece con /static/')
        return url



class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['user', 'place', 'date', 'start_time', 'end_time', 'confirmed']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'confirmed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'biometric_enabled']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'biometric_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AdminSettingsForm(forms.Form):
    max_bookings_per_week = forms.IntegerField(
        min_value=1, 
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    time_slot_duration = forms.ChoiceField(
        choices=[(30, '30 minutes'), (60, '1 hour'), (90, '1.5 hours'), (120, '2 hours')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notifications_enabled = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    support_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    support_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )