from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer
from django.shortcuts import render

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
