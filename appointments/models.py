from django.db import models
from django.conf import settings

class Status(models.IntegerChoices):
    PENDING = 1, 'Pending'
    CONFIRMED = 2, 'Confirmed'
    CANCELLED = 3, 'Cancelled'
    COMPLETED = 4, 'Completed'

class Gender(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'
    OTHER = 3, 'Other'


class Appointment(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient")
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='appoitnments')
    address = models.ForeignKey('Address', on_delete=models.CASCADE, related_name='addresses')
    patient_name = models.CharField(max_length=60, blank=False, null=False)
    patient_surnames = models.CharField(max_length=80, blank=False, null=False)
    birthdate = models.DateField(null=False, blank=False)
    gender = models.IntegerField(choices=Gender.choices, blank=False, null=False)
    phone = models.CharField(max_length=16, blank=False, null=False)
    note = models.TextField(blank=True, null=True)
    appointment_date = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(choices=Status.choices, default=Status.PENDING, blank=False, null=False)
    
    def __str__(self):
        return f"Patient {self.user.name} {self.user.surnames} - {self.user.username}"
