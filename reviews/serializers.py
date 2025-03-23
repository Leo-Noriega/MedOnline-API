from rest_framework import serializers
from django.utils.timezone import now
from .models import Review
from appointments.models import Appointment
from django.utils import timezone


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["id", "user", "doctor", "rating", "comment", "review_date", "appointment"]
        read_only_fields = ["id", "review_date", "user"]

    def validate(self, data):
        user = self.context["request"].user
        doctor = data.get("doctor")
        appointment = data.get("appointment")

        # Verificar logs para depuración
        print(f"Datos recibidos en el serializer: {data}")
        print(f"Usuario autenticado: {user.id}")
        print(f"Doctor ID: {doctor.id if doctor else 'None'}")
        print(f"Appointment ID: {appointment.id if appointment else 'None'}")

        # Validar que se proporcionó una cita
        if not appointment:
            raise serializers.ValidationError("Debes proporcionar una cita válida.")

        # Validar que la cita pertenece al usuario
        if appointment.user.id != user.id:
            raise serializers.ValidationError("Esta cita no te pertenece.")

        # Validar que la cita corresponde al doctor
        if appointment.doctor.id != doctor.id:
            raise serializers.ValidationError("Esta cita no corresponde a este doctor.")

        # Convertir las fechas a la zona horaria local antes de comparar
        appointment_date_local = timezone.localtime(appointment.appointment_date)
        now_local = timezone.localtime(timezone.now())

        print(f"Fecha actual en zona horaria local: {now_local}")
        print(f"Fecha de la cita en zona horaria local: {appointment_date_local}")

        # Validar que la cita ya pasó
        if appointment_date_local >= now_local:
            raise serializers.ValidationError("Solo puedes hacer una reseña después de que la cita haya pasado.")

        # Validar que no existe ya una reseña para esta cita
        if Review.objects.filter(appointment=appointment).exists():
            existing_review = Review.objects.get(appointment=appointment)
            print(f"Ya existe una reseña para esta cita: Usuario {existing_review.user.id}")
            raise serializers.ValidationError("Ya has dejado una reseña para esta cita.")

        return data

