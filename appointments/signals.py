from django.db import models
from appointments.models import Appointment
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

@receiver(post_save, sender=Appointment)
def send_appointment_confirmation(sender, instance, created, **kwargs):
    if not created:
        return
    
    doctor = instance.doctor
    user = instance.user
    appointment_date = instance.appointment_date.strftime("%Y-%m-%d %H:%M:%S")
    doctor_email = doctor.user.email
    user_email = user.email
    
    if instance.patient_name and instance.patient_surnames:
        subject_doc = "Nueva cita agendada"
        patient_name = f"{instance.patient_name} {instance.patient_surnames}"
        message_doc = (
            f"Hola {doctor.user.name} {doctor.user.surnames},\n\n"
            f"{user.name} {user.surnames} ha agendado una cita para\n"
            f"{patient_name}"
            f"Fecha y hora: {appointment_date}\n\n"
            "Saludos,\n"
            "El equipo de la clínica."
        )
    else:
        subject_doc = "Nueva cita agendada"
        message_doc = (
            f"Hola {doctor.user.name} {doctor.user.surnames},\n\n"
            f"{user.name} {user.surnames} ha agendado una cita contigo\n"
            f"Fecha y hora: {appointment_date}\n\n"
            "Saludos,\n"
            "El equipo de la clínica."
        )
        
    send_mail(
        subject_doc,
        message_doc,
        'noreply@medonline.com',
        [doctor_email],
        fail_silently=False,
    )
    
    subject_user = "Confirmación de cita"
    message_user = (
        f"Hola {user.name} {user.surnames},\n\n"
        f"Tu cita con {doctor.user.name} {doctor.user.surnames} ha sido correctamente agendada \n"
        f"{appointment_date}\n\n"
        "Mantente pendiente de cualquier cambio.\n\n"
        "Si necesitas realizar algún cambio, no dudes en contactarnos.\n\n"
        "Saludos,\n"
        "El equipo de la clínica."
    )
    
    send_mail(
        subject_user,
        message_user,
        'noreply@medonline.com',
        [user_email],
        fail_silently=False,
    )   