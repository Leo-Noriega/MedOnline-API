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
    path('mi-cuenta/',my_account, name='mi-cuenta'),
    path('opiniones/', opinions,name='opiniones'),
    path('mis-consultorios/', medicalOffice, name='mis-consultorios'),
    path('details/<int:user_id>/', user_doctor_details, name='user_doctor_details'),
    path('editar-doctor/<int:user_id>/',edit_user_doctor,name='editar_doctor'),
    path('asociar-especialidad/',associate_specialty,name='asociar'),
    path('<int:doctor_id>/reviews/', get_doctor_reviews,name='reviews_doctor'),
    path('mi-agenda/',agenda,name='agenda'),
    path('api/address/<int:doctor_id>/', get_doctor_addresses,name='doctor_addresses'),
]
