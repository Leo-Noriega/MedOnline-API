from django import forms

from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Role
from doctors.models import Doctor, Specialty, DoctorSpecialty, Address
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import timedelta

INPUT_CLASS = 'form-control'


class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.TextInput(attrs={'class': INPUT_CLASS})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS})
    )

class BaseRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ['name', 'surnames', 'email', 'phone', 'username', 'password']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden')
            
        return cleaned_data

class PatientRegistrationForm(BaseRegistrationForm):
    photo = forms.ImageField(required=False)
    
    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ['photo']

class DoctorRegistrationForm(BaseRegistrationForm):
    # Campos adicionales para doctores
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=True,
        empty_label="Selecciona tu especialidad"
    )
    
    license_number = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{7,8}$|^AESSA-[0-9]{7}$|^AE-[0-9]{7}$',
                message='Debe ser un número de cédula válido (7-8 dígitos o con prefijos AESSA/AE).'
            )
        ]
    )
    
    consultation_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True
    )
    
    consultation_time = forms.CharField(
        required=True,
        help_text="Formato: HH:MM:SS",
        validators=[
            RegexValidator(
                regex=r'^([0-9]{2}):([0-5][0-9]):([0-5][0-9])$',
                message='El tiempo de consulta debe tener formato HH:MM:SS'
            )
        ]
    )
    
    photo = forms.ImageField(required=False)

    class Meta(BaseRegistrationForm.Meta):
        fields = BaseRegistrationForm.Meta.fields + ['photo']
    
    def clean_consultation_time(self):
        time_str = self.cleaned_data.get('consultation_time')
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise ValidationError("El tiempo de consulta debe tener formato HH:MM:SS")