from django.shortcuts import render, redirect
from users.models import CustomUser
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.conf import settings
from doctors.models import Doctor, Specialty, Address
from datetime import datetime
from django.contrib import messages

@login_required
def my_appointments(request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Patient']:
        return redirect('login')
    else:
        return render(request, 'myAppointments.html', {'user_id': user_id}, status=200)
    
@login_required
def my_account_user (request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Patient']:
       return redirect('login')
    else:
        return render(request, 'myAccountUser.html', {'user_id': user_id}, status=200)
    
def get_all_specialities():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors_specialty")
        rows = cursor.fetchall()
    return rows

@login_required
def user_home(request):
    print("Usuario:", request.user)
    print("Sesión:", request.user.is_authenticated)
    print("info_sesion:", dict(request.session)) 
    user_id = request.session.get('_auth_user_id')
    nombre = request.user.name
    apellidos = request.user.surnames

    if request.user.role.name not in ['Patient']:
        return redirect('login')
    else:
        specialities = get_all_specialities()
        mexican_states = [
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua",
            "Ciudad de México", "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo",
            "Jalisco", "Estado de México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
            "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco",
            "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
        ]
        return render(request, 'userHome.html',
                      {'nombre': nombre,
                       'apellidos':apellidos,
                       'specialities' : specialities,
                       'mexican_states': mexican_states},
                      status=200)
        
@login_required
def confirm_appointment(request, doctor_id, selected_date, specialty_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        specialty = Specialty.objects.get(id=specialty_id)
        addresses = Address.objects.filter(doctor=doctor).all()
        dt = datetime.strptime(selected_date, "%Y-%m-%dT%H:%M:%S")
        if settings.USE_TZ:
            from django.utils import timezone
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor no encontrado.")
        return redirect('user_home')
    context = {
        'doctor': doctor,
        'specialty': specialty,
        'addresses': addresses,
        'selected_date': dt,
        'user': request.user,
    }
    return render(request, 'appointmentForm.html', context)