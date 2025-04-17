from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Address(models.Model):
    clinic_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)  
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    doctor = models.ForeignKey(
        'Doctor', 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )

    def __str__(self):
        return f"{self.clinic_name} - {self.city}, {self.state}"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Precio de consulta" )
    consultation_time = models.DurationField(blank=False, null=False, help_text="Duration de consulta debe tener este formato HH:MM:SS format")

    
    def __str__(self):
        return f"Dr. {self.user.name}"
    
    def clean(self):
        if self.consultation_fee is not None and self.consultation_fee < 0:
            raise ValidationError("The consultation fee cannot be negative.")
        
        if self.consultation_time is not None and self.consultation_time.total_seconds() < 0:
            raise ValidationError("The consultation time cannot be negative.")

class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=15, unique=True)  

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['doctor', 'specialty'], name='unique_doctor_specialty')
        ]

    def __str__(self):
        return f"{self.doctor.user.name} - {self.specialty.name} - {self.license_number}"
