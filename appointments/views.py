from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from .models import Appointment
from .serializers import AppointmentSerializer
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            return self.queryset.filter(user_id=user_id)
        return self.queryset
    @action(detail=False, methods=['get'], url_path='by-user')
    def get_all_by_user_id(self,request):
        user_id=request.query_params.get('user_id', None)
        if user_id is None:
            return Response({"message": "El id del usuario es requerido."}, status=400)
        appointments= self.queryset.filter(user_id=user_id)
        if not appointments.exists():
            return Response({"message": "No se encontraron citas para este usuario."}, status=200)
        serializer= self.get_serializer(appointments, many=True)
        return Response(serializer.data, status=200)
        
class DoctorAppointmentsView(APIView):
    def get(self, request, doctor_id):
        appointments = Appointment.objects.filter(doctor_id=doctor_id)
        if not appointments.exists():
            return Response({"message": "No se encontraron citas para este doctor."}, status=200)
        
        serializer = AppointmentSerializer(appointments, many=True)
        appointments_data = serializer.data
        for appointment in appointments_data:
            user = appointment.get('user')
            if user:
                appointment['user_full_name'] = f"{user.get('name', '')} {user.get('surnames', '')}"
        return Response(appointments_data, status=200)