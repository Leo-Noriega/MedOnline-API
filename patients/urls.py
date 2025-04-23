from django.urls import path, include
from .views import *

urlpatterns = [
    path('mis-citas/', my_appointments, name='mis-citas-paciente'),
    path('mi-cuenta/', my_account_user, name='mi-account-user'),
    path('inicio/', user_home, name='user_home'),
    path('reservar_cita/<int:doctor_id>/<path:selected_date>/<int:specialty_id>/', confirm_appointment, name='confirm_appointment'),
]