from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Crear un enrutador y registrar el ViewSet
router = DefaultRouter()
router.register(r'availability', AvailabilityViewSet, basename='availability')

urlpatterns = [
    path('save_availability/', save_doctor_availability, name='save_availability'),
    path('get_schedule/<int:doctor_id>/', get_doctor_schedule, name='get_schedule'),
    path('', include(router.urls)),  # Incluir las rutas generadas por el enrutador
]