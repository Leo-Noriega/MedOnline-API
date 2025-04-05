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
]
