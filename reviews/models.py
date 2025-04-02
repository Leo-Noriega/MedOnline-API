from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import MinValueValidator, MaxValueValidator
from doctors.models import Doctor
from appointments.models import Appointment, Status
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)
fernet = Fernet(settings.FERNET_KEY)

def generate_encrypted_id(appointment_id):
    return fernet.encrypt(str(appointment_id).encode()).decode()


class Review(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="appointment_reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_review")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    
    def __str__(self):
        return f"Review from {self.user.name} {self.user.surnames} - {self.user.username}"
    

    def send_review_email(self):
        encrypted_id = generate_encrypted_id(self.appointment.id)
        review_link = reverse("review_doctor", kwargs={"token": encrypted_id})
        full_link = f"{settings.BASE_URL}{review_link}"

        subject = "Califica tu cita con el doctor"
        message = render_to_string("review_email.html", {
            "review_link": full_link,
            "doctor_name": f"{self.doctor.name} {self.doctor.surnames}",
            "user_name": f"{self.user.name} {self.user.surnames}",
            "appointment_date": self.appointment.appointment_date, 
        })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email], html_message=message)
        
    @staticmethod
    def handle_appointment_status_change(appointment):
        logger.info(f"Cambiando estado de la cita: {appointment.id} - Estado: {appointment.status}")
        subject = ''
        template = ''
        context = {
            "appointment": appointment,
            "doctor_name": appointment.doctor.user.name + " " + appointment.doctor.user.surnames ,
            "user_name": appointment.user.name + " " + appointment.user.surnames or appointment.user.get_full_name(),
            "appointment_date": appointment.appointment_date,
        }
        
        if appointment.status == Status.CONFIRMED:
            subject = "Tu cita ha sido confirmada"
            template = "appointment_confirmed.html"
        elif appointment.status == Status.CANCELLED:
            subject = "Tu cita ha sido cancelada"
            template = "appointment_cancelled.html"
        elif appointment.status == Status.COMPLETED:
            encrypted_id = generate_encrypted_id(appointment.id)
            review_link = f"{settings.BASE_URL}{reverse('review_doctor', kwargs={'token': str(encrypted_id)})}"
            context["review_link"] = review_link

            subject = "Califica tu cita con el doctor"
            template = "review_email.html"

        
        if subject and template:
            message = render_to_string(template, context)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [appointment.user.email], html_message=message)
            
            
            