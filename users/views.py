from django.contrib.auth.views import LoginView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.renderers import JSONRenderer

from .forms import CustomLoginForm
from .serializers import *
from .models import *


class UserViewSets(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            return [IsAuthenticated()]
        return []

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = "users/login.html"

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer