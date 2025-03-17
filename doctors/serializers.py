from rest_framework import serializers
from .models import *

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        
class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'
        
class DoctorSpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSpecialty
        fields = '__all__'
        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'