from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer
from django.shortcuts import render, get_object_or_404

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

class DoctorAppointmentsView(APIView):
    def get(self, request, doctor_id):
        appointments = Appointment.objects.filter(doctor_id=doctor_id)
        if not appointments.exists():
            return Response({"message": "No se encontraron citas para este doctor."}, status=404)
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=200)
