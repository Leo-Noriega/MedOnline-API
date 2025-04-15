from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth import logout, login
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

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
        if self.request.method in ['POST', 'DELETE']:
            return [IsAuthenticated()]
        return []

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = "users/login.html"
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        if user.role.name == 'Doctor':
            return redirect('inicio')
        elif user.role.name== 'Patient':
            return redirect('account_patient')
        elif user.role.name == 'Admin':
            return redirect('/')
        else:
            return redirect('/') 

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

class UserUpdateView(APIView):
    def put(self, request, user_id):
        user = User.objects.get(id=user_id)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)  # Permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)