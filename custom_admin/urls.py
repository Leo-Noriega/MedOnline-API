from django.urls import path,include
from .views import *

urlpatterns = [
    path('inicio/', home, name='admin_home'),
    path('gestion-pacientes/', manage_patients, name='manage_patients'),
    path('gestion-especialistas/', manage_doctors, name='manage_doctors'),
    path('mi-cuenta/', admin_account, name='admin_account'),
    path('users/', get_all_users, name='get_all_users'),
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
    path('get-admin/<int:user_id>/', get_admin, name='get_admin'),
    path('update-admin/<int:user_id>/', update_admin, name='update_admin'),
    path('patients/<int:user_id>/', get_patient, name='get_patient'),
    path('patients/update/<int:user_id>/', update_patient, name='update_patient'),
    path('appointments/<int:appointment_id>/status/', update_appointment_status, name='update_appointment_status'),
    path('doctors/<int:user_id>/', get_doctor, name='get_doctor'),
    path('doctors/update/<int:user_id>/', update_doctor, name='update_doctor'),
    path('doctors/<int:doctor_id>/specialties/<int:specialty_id>/', update_specialty, name='update_specialty'),
    path('doctors/addresses/<int:address_id>/', update_address, name='update_address'),
    path('doctors/<int:doctor_id>/schedules/', update_schedule, name='update_schedule'),
]
