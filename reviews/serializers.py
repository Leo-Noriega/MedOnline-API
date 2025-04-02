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

        print(f"Datos recibidos en el serializer: {data}")
        print(f"Usuario autenticado: {user.id}")
        print(f"Doctor ID: {doctor.id if doctor else 'None'}")
        print(f"Appointment ID: {appointment.id if appointment else 'None'}")

        if not appointment:
            raise serializers.ValidationError("Debes proporcionar una cita válida.")

        if appointment.user.id != user.id:
            raise serializers.ValidationError("Esta cita no te pertenece.")

        if appointment.doctor.id != doctor.id:
            raise serializers.ValidationError("Esta cita no corresponde a este doctor.")

        appointment_date_local = timezone.localtime(appointment.appointment_date)
        now_local = timezone.localtime(timezone.now())

        print(f"Fecha actual en zona horaria local: {now_local}")
        print(f"Fecha de la cita en zona horaria local: {appointment_date_local}")

        if appointment_date_local >= now_local:
            raise serializers.ValidationError("Solo puedes hacer una reseña después de que la cita haya pasado.")

        if Review.objects.filter(appointment=appointment).exists():
            existing_review = Review.objects.get(appointment=appointment)
            print(f"Ya existe una reseña para esta cita: Usuario {existing_review.user.id}")
            raise serializers.ValidationError("Ya has dejado una reseña para esta cita.")

        return data

