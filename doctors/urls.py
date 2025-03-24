from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'specialty', SpecialtyViewSet, basename='specialization')
router.register(r'doctor-specialty', DoctorSpecialtyViewSet, basename='doctor_specialization')
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('', include(router.urls)),
    path('inicio/',home,name='inicio'),
]
