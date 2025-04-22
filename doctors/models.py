from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class Specialty(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'doctors_specialty'


class Address(models.Model):
    clinic_name = models.CharField(max_length=150, blank=False, null=False)
    street = models.CharField(max_length=150, blank=False, null=False)  
    city = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    postal_code = models.CharField(max_length=5, blank=False, null=False)
    doctor = models.ForeignKey(
        'Doctor', 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )

    def __str__(self):
        return f"{self.clinic_name} - {self.city}, {self.state}"

    class Meta:
        db_table = 'doctors_address'


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Precio de consulta" )
    consultation_time = models.DurationField(blank=True, null=True, help_text="Duration de consulta debe tener este formato HH:MM:SS format")

    def __str__(self):
        return f"Dr. {self.user.name}"
    
    def clean(self):
        if self.consultation_fee is not None and self.consultation_fee < 0:
            raise ValidationError("The consultation fee cannot be negative.")
        
        if self.consultation_time is not None and self.consultation_time.total_seconds() < 0:
            raise ValidationError("The consultation time cannot be negative.")

    class Meta:
        db_table = 'doctors_doctor'
    

class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=15, unique=True, null=False, blank=False)  

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['doctor', 'specialty'], name='unique_doctor_specialty')
        ]

    def __str__(self):
        return f"{self.doctor.user.name} - {self.specialty.name} - {self.license_number}"
    
    class Meta:
        db_table = 'doctors_doctorspecialty'


@receiver(post_migrate)
def create_default_specialties(sender, **kwargs):
    specialties = [
        "CARDIOLOGÍA",
        "DERMATOLOGÍA",
        "ENDOCRINOLOGÍA",
        "GASTROENTEROLOGÍA",
        "HEMATOLOGÍA",
        "NEUROLOGÍA",
        "ONCOLOGÍA",
        "PEDIATRÍA",
        "PSIQUIATRÍA",
        "REUMATOLOGÍA",
        "MÉDICO GENERAL"
    ]
    for specialty in specialties:
        if not Specialty.objects.filter(name=specialty).exists():
            Specialty.objects.create(name=specialty)
            print(f"=== Especialidad '{specialty}' creada exitosamente ===")