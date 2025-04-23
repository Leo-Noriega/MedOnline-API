from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_duration, parse_time
from .models import Availability, DailySchedule
from doctors.models import Doctor
from appointments.models import Appointment, Status
import json
from django.utils import timezone
from rest_framework import viewsets, permissions
from .serializers import AvailabilitySerializer
from rest_framework.renderers import JSONRenderer


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated]


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


from datetime import datetime, time, timedelta

def generate_time_slots(start, end, duration_minutes, weekday):
    slots = []
    
    start_time = time.fromisoformat(start)
    end_time = time.fromisoformat(end)
    
    current = datetime.combine(datetime.min, start_time).time()
    end_dt = datetime.combine(datetime.min, end_time).time()
    
    while True:
        slot_end = (datetime.combine(datetime.min, current) + timedelta(minutes=duration_minutes)).time()
        if slot_end > end_dt:
            break
            
        slots.append(current.strftime('%H:%M'))
        current = (datetime.combine(datetime.min, current) + timedelta(minutes=duration_minutes)).time()
    
    return slots

def get_doctor_schedule(request, doctor_id):
    try:
        availabilities = Availability.objects.filter(doctor_id=doctor_id).select_related('doctor')
        if not availabilities.exists():
            return JsonResponse({'error': 'No se encontraron horarios para este doctor.'}, status=404)

        doctor = Doctor.objects.get(id=doctor_id)
        consultation_duration = int(doctor.consultation_time.total_seconds() / 60)
        today_weekday = datetime.now().isoweekday()
        current_time = datetime.now().time().strftime('%H:%M')
        current_date = datetime.now().date()

        booked_appointments = Appointment.objects.filter(
            doctor_id=doctor_id,
        )
        
        booked_slots = {}
        for appointment in booked_appointments:
            local_appt_datetime = timezone.localtime(appointment.appointment_date)
            appt_date = local_appt_datetime.date()
            appt_time = local_appt_datetime.time()
    
            date_str = appt_date.strftime('%Y-%m-%d')
            time_str = appt_time.strftime('%H:%M')
    
            if date_str not in booked_slots:
                booked_slots[date_str] = {}
    
            booked_slots[date_str][time_str] = appointment.status

        schedule_data = []
        for availability in availabilities:
            daily_schedules = DailySchedule.objects.filter(availability=availability)
            for daily_schedule in daily_schedules:
                if availability.weekday >= today_weekday:
                    slots = generate_time_slots(
                        str(daily_schedule.start_time),
                        str(daily_schedule.end_time),
                        consultation_duration,
                        availability.weekday
                    )
                    
                    days_ahead = (availability.weekday - today_weekday) % 7
                    slot_date = current_date + timedelta(days=days_ahead)
                    date_str = slot_date.strftime('%Y-%m-%d')
                    
                    all_slots_info = []
                    for slot in slots:
                        slot_info = {
                            'time': slot,
                            'status': None  
                        }
                        
                        if date_str in booked_slots and slot in booked_slots[date_str]:
                            status = booked_slots[date_str][slot]
                            if status == Status.CANCELLED:
                                pass
                            else:
                                slot_info['status'] = status
                        
                        all_slots_info.append(slot_info)
                    
                    schedule_data.append({
                        'weekday': availability.weekday,
                        'weekday_label': availability.get_weekday_display(),
                        'start_time': str(daily_schedule.start_time),
                        'end_time': str(daily_schedule.end_time),
                        'slots': all_slots_info,
                        'is_today': availability.weekday == today_weekday,
                        'date': date_str
                    })

        return JsonResponse({
            'doctor': {
                'id': doctor.id,
                'consultation_time': consultation_duration,
            },
            'current_date': current_date.strftime('%Y-%m-%d'),
            'current_time': current_time,
            'current_weekday': today_weekday,
            'schedule': sorted(schedule_data, key=lambda x: x['weekday'])
        }, status=200)

    except Exception as e:
        print(f"Error al obtener el horario: {e}")
        return JsonResponse({'error': str(e)}, status=500)