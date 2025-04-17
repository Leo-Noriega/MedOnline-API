from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'