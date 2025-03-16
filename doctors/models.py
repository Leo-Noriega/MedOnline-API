from django.db import models
from django.conf import settings

class Speciality(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Address(models.Model):
    clinic_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)  
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='addresses') 
    def __str__(self):
        return f"{self.name_clinic} - {self.city}, {self.state}"


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctor")
    years_experience = models.PositiveSmallIntegerField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.BooleanField(default=True)  
    def __str__(self):
        return f"Dr. {self.user.name} {self.user.usernames}"


class DoctorSpeciality(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=8, unique=True)  

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['doctor', 'speciality'], name='unique_doctor_speciality')
        ]

    def __str__(self):
        return f"{self.doctor.name} - {self.speciality.name} - {self.license_number}"
