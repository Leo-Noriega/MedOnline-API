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
    address = instance.address
    appointment_date = instance.appointment_date.strftime("%Y-%m-%d %H:%M:%S")
    doctor_email = doctor.user.email
    user_email = user.email

    message_doc_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>MedOnline - Nueva cita</title></head>
    <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #2e5077;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <tr><td bgcolor="#2E5077" style="height: 40px;"></td></tr>
            <tr>
                <td style="padding: 30px;">
                    <h2 style="color: #2E5077;">Nueva cita agendada</h2>
                    <p>Estimado/a Dr. {doctor.user.name} {doctor.user.surnames},</p>
                    <p>El usuario {user.name} {user.surnames} ha agendado una cita contigo.</p>"""

    if instance.patient_name and instance.patient_surnames:
        message_doc_html += f"""
                    <p><strong>Tu paciente:</strong> {instance.patient_name} {instance.patient_surnames}</p>"""

    message_doc_html += f"""
                    <p><strong>Dirección de la cita:</strong> {address}</p>
                    <p><strong>Fecha y hora:</strong> {appointment_date}</p>
                    <p>Por favor, ingresa a tu panel para más detalles.</p>
                    <p style="margin-top: 40px;">Atentamente,<br>Equipo de MedOnline</p>
                </td>
            </tr>
            <tr><td align="center" bgcolor="#F9F9F9" style="padding: 20px; font-size: 14px; color: #7F807F;">
                <p>© 2025 MedOnline. Todos los derechos reservados.</p>
            </td></tr>
        </table>
    </body>
    </html>
    """

    send_mail(
        subject="Nueva cita agendada",
        message="Nueva cita",  
        from_email='noreply@medonline.com',
        recipient_list=[doctor_email],
        fail_silently=False,
        html_message=message_doc_html
    )

    message_user_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>MedOnline - Confirmación de cita</title></head>
    <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #2e5077;">
        <table align="center" width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <tr><td bgcolor="#2E5077" style="height: 40px;"></td></tr>
            <tr>
                <td style="padding: 30px;">
                    <h2 style="color: #2E5077;">Tu cita ha sido confirmada</h2>
                    <p>Hola {user.name} {user.surnames},</p>
                    <p>Tu cita con el Dr. {doctor.user.name} {doctor.user.surnames} ha sido confirmada.</p>
                    <p><strong>Fecha y hora:</strong> {appointment_date}</p>
                    <p><strong>Dirección de la cita:</strong> {address}</p>
                    <p>Te recomendamos estar al pendiente de cualquier cambio.</p>
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin: 30px 0;">
                        <tr><td align="center">
                            <table border="0" cellpadding="0" cellspacing="0">
                                <tr><td align="center" bgcolor="#2E5077" style="border-radius: 4px;">
                                    <a href="http://localhost:8000/users/login/" target="_blank" style="display: inline-block; padding: 12px 30px; font-size: 16px; color: #ffffff; text-decoration: none; font-weight: 500;">Ver detalles</a>
                                </td></tr>
                            </table>
                        </td></tr>
                    </table>
                    <p>Si necesitas modificar tu cita, contáctanos.</p>
                    <p style="margin-top: 40px;">Gracias por confiar en nosotros,<br>Equipo de MedOnline</p>
                </td>
            </tr>
            <tr><td align="center" bgcolor="#F9F9F9" style="padding: 20px; font-size: 14px; color: #7F807F;">
                <p>© 2025 MedOnline. Todos los derechos reservados.</p>
            </td></tr>
        </table>
    </body>
    </html>
    """

    send_mail(
        subject="Confirmación de cita",
        message="Tu cita ha sido confirmada",  # plain fallback
        from_email='noreply@medonline.com',
        recipient_list=[user_email],
        fail_silently=False,
        html_message=message_user_html
    )
