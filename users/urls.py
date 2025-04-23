from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

router = DefaultRouter()
router.register(r'api', UserViewSets)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', CustomLoginViewAPI.as_view(), name='login'),
    path('logout/', cerrar_sesion, name='cerrar_sesion'),
    path("send-reset-email/", send_reset_email, name="send_reset_email"),
    path("reset-password/", reset_password, name="reset_password"),
    path('recovery-password/', recovery_password_view, name='recovery_password_view'),
    path('reset-password/<str:token>/', reset_password_view, name='reset_password_view'),
    path('register/', register, name='register'),
    path('register/patient/', register_patient, name='register_patient'),
    path('register/doctor/', RegisterDoctorView.as_view(), name='register_doctor'),
    path('search-doctors/', DoctorSearchAPIView.as_view(), name='search-doctors'),
]
