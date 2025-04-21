from django.db import models
from django.conf import settings
from doctors.models import Doctor, Address
import logging
from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_user")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='addresses')
    patient_name = models.CharField(max_length=60, blank=False, null=False, default="Unknown Patient")
    patient_surnames = models.CharField(max_length=80, blank=False, null=False, default="Unknown Surnames")
    birthdate = models.DateField(null=True, blank=True)
    gender = models.IntegerField(choices=Gender.choices, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=False, null=False, default="",validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',message="El número de teléfono debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos.")])
    note = models.TextField(blank=False, default="No notes provided")
    appointment_date = models.DateTimeField(null=False, blank=False)
    status = models.IntegerField(choices=Status.choices, default=Status.PENDING, blank=False, null=False)
    
    def __str__(self):
        return f"Patient {self.patient_name} {self.patient_surnames} - Doctor {self.doctor.name} - Date {self.appointment_date}"
    
    def get_status_display(self):
        return self.get_status_display()
    
    def save(self, *args, **kwargs):
        # Verificar si el estado ha cambiado
        if self.pk:  # Si ya existe en la base de datos
            previous = Appointment.objects.get(pk=self.pk)
            if previous.status != self.status:
                from reviews.models import Review 
                print(f"El estado ha cambiado: {previous.status} -> {self.status}")  # Depuración
                logger.info(f"El estado ha cambiado: {previous.status} -> {self.status}")
                Review.handle_appointment_status_change(self)

        super().save(*args, **kwargs)  # Guardar normalmente en la base de datos
    class Meta:
        db_table = 'appointment'