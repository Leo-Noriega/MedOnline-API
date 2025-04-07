from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from users.models import CustomUser, Role
from doctors.models import Doctor, DoctorSpecialty, Address,Specialty
from appointments.models import Appointment,Status
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
import json
from schedule.models import Availability, DailySchedule
@login_required
def home(request):
    return render(request, 'home_Admin.html', status=200)

@login_required
def manage_patients(request):
    if not request.user.is_authenticated or request.user.role.name != 'Admin':
        return redirect('login')
    user_id = request.GET.get('user_id')
    return render(request, 'patientView.html')

@login_required
def manage_doctors(request):
    user_id = request.GET.get('user_id')
    print(f"User ID: {user_id}")
    return render(request, 'doctorView.html')

@login_required
def admin_account(request):
    if not request.user.is_authenticated and request.user.role and request.user.role.name != 'Admin':
        return redirect('admin_home')
    return render(request, 'adminAccount.html',{
        'user_id': request.user.id,
    })

@require_http_methods(["GET"])
def get_all_users(request):
    try:
        admin_role = Role.objects.get(name='Admin')
        users = CustomUser.objects.filter(is_active=True).exclude(role=admin_role)
        
        data = [{
            'id': user.id,
            'name': user.name,
            'surnames': user.surnames,
            'email': user.email,
            'phone': user.phone,
            'status': user.status,
            'username': user.username,
            'photo': user.photo.url if user.photo else None,
            'role': user.role.name if user.role else None
        } for user in users]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def cerrar_sesion(request):
    logout(request)
    return redirect('/')


@require_http_methods(["GET"])
def get_admin(request, user_id):
    try:
        admin = CustomUser.objects.get(id=user_id, role__name='Admin')
        data = {
            'admin': {
                'id': admin.id,
                'name': admin.name,
                'surnames': admin.surnames,
                'email': admin.email,
                'phone': admin.phone,
                'username': admin.username,
                'photo': admin.photo.url if admin.photo else None,
            }
        }
        return JsonResponse(data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Administrador no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
def update_admin(request, user_id):
    try:
        admin = CustomUser.objects.get(id=user_id, role__name='Admin')
        data = json.loads(request.body)

       
        admin.name = data.get('name', admin.name)
        admin.surnames = data.get('surnames', admin.surnames)
        admin.email = data.get('email', admin.email)
        admin.phone = data.get('phone', admin.phone)
        admin.username = data.get('username', admin.username)

        
        if 'password' in data:
            admin.password = make_password(data['password'])

       
        if 'photo' in request.FILES:
            admin.photo = request.FILES['photo']

        admin.save()

        return JsonResponse({
            'message': 'Información actualizada exitosamente',
            'admin': {
                'name': admin.name,
                'surnames': admin.surnames,
                'email': admin.email,
                'phone': admin.phone,
                'username': admin.username,
                'photo': admin.photo.url if admin.photo else None
            }
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Administrador no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_patient(request, user_id):
    try:
        print(f"Buscando paciente con ID: {user_id}")
        patient = CustomUser.objects.get(id=user_id, role__name='Patient')
        appointments = Appointment.objects.filter(user_id=user_id).select_related(
            'doctor__user', 'address').order_by('-appointment_date')
        print(f"Citas encontradas: {appointments.count()}")
        data = {
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'surnames': patient.surnames,
                'email': patient.email,
                'phone': patient.phone,
                'username': patient.username,
                'photo': patient.photo.url if patient.photo else None,
                'status': patient.status,
                'role': patient.role.name,
                'join_date': patient.join_date.strftime("%Y-%m-%d")
            },
            'appointments': [{
                'id': appointment.id,
                'date': appointment.appointment_date.strftime("%Y-%m-%d %H:%M"),
                'doctor': f"{appointment.doctor.user.name} {appointment.doctor.user.surnames}",
                'clinic': appointment.address.clinic_name,
                'status': appointment.get_status_display(),
                'note': appointment.note,
                'patient_name': appointment.patient_name,
                'patient_surnames': appointment.patient_surnames
            } for appointment in appointments]
        }
        return JsonResponse(data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
def update_appointment_status(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in [s.value for s in Status]:
          return JsonResponse({'error': 'Estado no válido'}, status=400)
        
        appointment.status = new_status
        appointment.save()
        
        return JsonResponse({
            'message': 'Estado actualizado exitosamente',
            'status': appointment.get_status_display()
        })
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Cita no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
def update_patient(request, user_id):
    try:
        patient = CustomUser.objects.get(id=user_id, role__name='Patient')
        data = json.loads(request.body)

        
        patient.name = data.get('name', patient.name)
        patient.surnames = data.get('surnames', patient.surnames)
        patient.email = data.get('email', patient.email)
        patient.phone = data.get('phone', patient.phone)
        patient.username = data.get('username', patient.username)
        if 'status' in data:
            patient.status = data['status']

        
        if 'photo' in request.FILES:
            patient.photo = request.FILES['photo']

        patient.save()

        return JsonResponse({
            'message': 'Información actualizada exitosamente',
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'surnames': patient.surnames,
                'email': patient.email,
                'phone': patient.phone,
                'username': patient.username,
                'photo': patient.photo.url if patient.photo else None,
                'status': patient.status,
                'role': patient.role.name
            }
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_doctor(request, user_id):
    try:
        
        doctor_user = CustomUser.objects.select_related('role').get(id=user_id, role__name='Doctor')
        
        
        doctor = Doctor.objects.filter(user=doctor_user).first()
        
        
        if not doctor:
            doctor = Doctor.objects.create(
                user=doctor_user,
                years_experience=0,
                consultation_fee=0.00
            )
            print(f"Perfil de doctor creado automáticamente para: {doctor_user.email}")

        
        specialties = DoctorSpecialty.objects.filter(doctor=doctor).select_related('specialty')
        addresses = Address.objects.filter(doctor=doctor)
        availabilities = Availability.objects.filter(doctor=doctor)
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')

        
        response_data = {
            'status': 'success',
            'message': 'Datos encontrados exitosamente',
            'data': {
                'doctor': {
                    'id': doctor_user.id,
                    'name': doctor_user.name,
                    'surnames': doctor_user.surnames,
                    'email': doctor_user.email,
                    'phone': doctor_user.phone,
                    'username': doctor_user.username,
                    'photo': doctor_user.photo.url if doctor_user.photo else None,
                    'status': doctor_user.status,
                    'years_experience': doctor.years_experience,
                    'consultation_fee': float(doctor.consultation_fee)
                },
                'specialties': [{
                    'id': spec.specialty.id,  
                    'doctor_specialty_id': spec.id,  
                    'name': spec.specialty.name,
                    'license_number': spec.license_number,
                    'doctor_id': doctor.id
                } for spec in specialties],
                'addresses': [{
                    'id': addr.id,
                    'clinic_name': addr.clinic_name,
                    'street': addr.street,
                    'city': addr.city,
                    'state': addr.state,
                    'postal_code': addr.postal_code
                } for addr in addresses],
                'schedules': [{
                    'weekday': availability.get_weekday_display(),
                    'weekday_value': availability.weekday,
                    'consultation_time': str(availability.consultation_time),
                    'times': [{
                        'start_time': schedule.start_time.strftime("%H:%M"),
                        'end_time': schedule.end_time.strftime("%H:%M")
                    } for schedule in DailySchedule.objects.filter(availability=availability)]
                } for availability in availabilities],
                'appointments': [{
                    'id': appointment.id,
                    'date': appointment.appointment_date.strftime("%Y-%m-%d %H:%M"),
                    'patient_name': f"{appointment.patient_name} {appointment.patient_surnames}",
                    'clinic': appointment.address.clinic_name,
                    'status': appointment.get_status_display()
                } for appointment in appointments]
            }
        }
        
        return JsonResponse(response_data)
        
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Doctor no encontrado',
            'data': None
        }, status=404)
    except Exception as e:
        print(f"Error en get_doctor: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'data': None
        }, status=500)

@require_http_methods(["PUT"])
def update_doctor(request, user_id):
    try:
        doctor_user = CustomUser.objects.get(id=user_id, role__name='Doctor')
        doctor = Doctor.objects.get(user=doctor_user)
        data = json.loads(request.body)

        
        doctor_user.name = data.get('name', doctor_user.name)
        doctor_user.surnames = data.get('surnames', doctor_user.surnames)
        doctor_user.email = data.get('email', doctor_user.email)
        doctor_user.phone = data.get('phone', doctor_user.phone)
        doctor_user.username = data.get('username', doctor_user.username)
        doctor_user.status = data.get('status', doctor_user.status)

        
        doctor.years_experience = data.get('years_experience', doctor.years_experience)
        doctor.consultation_fee = data.get('consultation_fee', doctor.consultation_fee)

        doctor_user.save()
        doctor.save()

        return JsonResponse({
            'message': 'Información actualizada exitosamente',
            'doctor': {
                'id': doctor_user.id,
                'name': doctor_user.name,
                'surnames': doctor_user.surnames,
                'email': doctor_user.email,
                'phone': doctor_user.phone,
                'username': doctor_user.username,
                'status': doctor_user.status,
                'years_experience': doctor.years_experience,
                'consultation_fee': float(doctor.consultation_fee)
            }
        })
    except (CustomUser.DoesNotExist, Doctor.DoesNotExist):
        return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
def update_specialty(request, doctor_id, doctor_specialty_id):
    try:
        data = json.loads(request.body)
        print(f"Recibiendo actualización para doctor_id: {doctor_id}, doctor_specialty_id: {doctor_specialty_id}")
        print(f"Datos recibidos: {data}")

        
        doctor_specialty = DoctorSpecialty.objects.select_related('specialty', 'doctor').get(
            id=doctor_specialty_id,
            doctor_id=doctor_id
        )
        
        
        if not data.get('name') or not data.get('license_number'):
            return JsonResponse({
                'status': 'error',
                'message': 'Todos los campos son requeridos'
            }, status=400)

        
        doctor_specialty.license_number = data['license_number']
        
        
        specialty = doctor_specialty.specialty
        specialty.name = data['name']
        specialty.save()
        
        doctor_specialty.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Especialidad actualizada exitosamente',
            'data': {
                'id': specialty.id,
                'doctor_specialty_id': doctor_specialty.id,
                'name': specialty.name,
                'license_number': doctor_specialty.license_number,
                'doctor_id': doctor_id
            }
        })
        
    except DoctorSpecialty.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Especialidad no encontrada'
        }, status=404)
    except Exception as e:
        print(f"Error en update_specialty: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["PUT"])
def update_address(request, address_id):
    try:
        data = json.loads(request.body)
        address = Address.objects.get(id=address_id)
        
        address.clinic_name = data.get('clinic_name', address.clinic_name)
        address.street = data.get('street', address.street)
        address.city = data.get('city', address.city)
        address.state = data.get('state', address.state)
        address.postal_code = data.get('postal_code', address.postal_code)
        
        address.save()
        
        return JsonResponse({
            'message': 'Consultorio actualizado exitosamente',
            'address': {
                'id': address.id,
                'clinic_name': address.clinic_name,
                'street': address.street,
                'city': address.city,
                'state': address.state,
                'postal_code': address.postal_code
            }
        })
    except Address.DoesNotExist:
        return JsonResponse({'error': 'Consultorio no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["PUT"])
def update_schedule(request, doctor_id):
    try:
        data = json.loads(request.body)
        
        availability = Availability.objects.get(
            doctor_id=doctor_id,
            weekday=data['weekday']
        )
        
        
        availability.consultation_time = data.get('consultation_time', availability.consultation_time)
        availability.save()
        
        
        if 'times' in data:
            
            DailySchedule.objects.filter(availability=availability).delete()
            
            
            for time in data['times']:
                DailySchedule.objects.create(
                    availability=availability,
                    start_time=time['start_time'],
                    end_time=time['end_time']
                )
        
        return JsonResponse({
            'message': 'Horario actualizado exitosamente'
        })
    except Availability.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



 