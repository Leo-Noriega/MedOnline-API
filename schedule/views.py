from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_duration, parse_time
from .models import Availability, DailySchedule
from doctors.models import Doctor
import json
from rest_framework import viewsets, permissions
from .serializers import AvailabilitySerializer
from rest_framework.renderers import JSONRenderer


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes=[permissions.IsAuthenticated]

@csrf_exempt
def save_doctor_availability(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 
            if not isinstance(data, list):
                return JsonResponse({'error': 'Se esperaba una lista de horarios.'}, status=400)

            for schedule in data:
                doctor_id = schedule.get('doctor_id')
                weekday = schedule.get('weekday')
                start_time = schedule.get('start_time')
                end_time = schedule.get('end_time')

                # Validar que todos los campos requeridos estén presentes
                if not all([doctor_id, weekday, start_time, end_time]):
                    return JsonResponse({'error': 'Todos los campos son obligatorios.'}, status=400)

                # Obtener el doctor
                doctor = get_object_or_404(Doctor, id=doctor_id)

                # Crear o actualizar la disponibilidad
                availability, created = Availability.objects.get_or_create(
                    doctor=doctor,
                    weekday=weekday
                )

                # Crear o actualizar el horario diario
                daily_schedule, created = DailySchedule.objects.get_or_create(
                    availability=availability,
                    defaults={
                        'start_time': parse_time(start_time),
                        'end_time': parse_time(end_time)
                    }
                )
                if not created:
                    daily_schedule.start_time = parse_time(start_time)
                    daily_schedule.end_time = parse_time(end_time)
                    daily_schedule.save()

            return JsonResponse({'message': 'Disponibilidad guardada exitosamente.'}, status=200)

        except Exception as e:
            print(f"Error al guardar la disponibilidad: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

def get_doctor_schedule(request, doctor_id):
    try:
        availabilities = Availability.objects.filter(doctor_id=doctor_id).select_related('doctor')

        if not availabilities.exists():
            return JsonResponse({'error': 'No se encontraron horarios para este doctor.'}, status=404)

        schedule_data = []
        for availability in availabilities:
            daily_schedules = DailySchedule.objects.filter(availability=availability)
            for daily_schedule in daily_schedules:
                schedule_data.append({
                    'id':availability.id,
                    'weekday': availability.weekday,
                    'weekday_label': availability.get_weekday_display(),
                    'start_time': str(daily_schedule.start_time),
                    'end_time': str(daily_schedule.end_time),
                })

        return JsonResponse({'doctor_id': doctor_id, 'schedule': schedule_data}, status=200)

    except Exception as e:
        print(f"Error al obtener el horario: {e}")
        return JsonResponse({'error': str(e)}, status=500)