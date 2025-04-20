from rest_framework import serializers
from .models import Appointment
from doctors.models import Address, Doctor

class AppointmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.name', read_only=True)
    doctor_surnames = serializers.CharField(source='doctor.user.surnames', read_only=True)
    doctor_photo = serializers.SerializerMethodField()
    consultation_fee = serializers.DecimalField(source='doctor.consultation_fee', max_digits=10, decimal_places=2, read_only=True)
    address_details = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'

    def get_doctor_photo(self, obj):
        if obj.doctor and obj.doctor.user.photo:
            return obj.doctor.user.photo.url
        return None

    def get_address_details(self, obj):
        try:
            address = Address.objects.get(id=obj.address.id)  
            return {
                "clinic_name": address.clinic_name,
                "street": address.street,
                "city": address.city,
                "state": address.state,
                "postal_code": address.postal_code
            }
        except Address.DoesNotExist:
            return "No especificado"

