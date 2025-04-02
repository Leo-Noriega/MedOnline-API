from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'api', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('review/<str:token>/', ReviewDoctorView.as_view(), name='review_doctor'),
]