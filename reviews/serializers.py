from rest_framework import serializers
from django.utils.timezone import now
from .models import Review
from appointments.models import Appointment

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "user", "doctor", "rating", "comment", "review_date"]
        read_only_fields = ["id", "review_date", "user"]

    def validate(self, data):
        user = self.context["request"].user
        doctor = data.get("doctor")

        # Obtener todas las citas pasadas del usuario con ese doctor
        past_appointments = Appointment.objects.filter(
            user=user, doctor=doctor, appointment_date__lt=now()
        ).order_by("-appointment_date")

        print("=== CITAS PASADAS ORDENADAS ===")
        for appointment in past_appointments:
            print(f"ID: {appointment.id}, Fecha: {appointment.appointment_date}")

        if not past_appointments.exists():
            raise serializers.ValidationError("Solo puedes hacer una reseña después de haber tenido una cita con el doctor.")

        # Obtener la última cita pasada
        last_appointment = past_appointments.first()

        print(f"Última cita encontrada: {last_appointment.appointment_date}")

        # Contar cuántas reseñas ha dejado el usuario para este doctor
        total_reviews = Review.objects.filter(user=user, doctor=doctor).count()

        # Contar cuántas citas pasadas ha tenido el usuario con este doctor
        total_past_appointments = past_appointments.count()

        print(f"Total de citas pasadas: {total_past_appointments}")
        print(f"Total de reseñas hechas: {total_reviews}")

        # El usuario solo puede hacer una reseña por cada cita pasada
        if total_reviews >= total_past_appointments:
            raise serializers.ValidationError("Ya has dejado una reseña por todas tus citas con este doctor.")

        return data
