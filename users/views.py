import json

from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .forms import CustomLoginForm
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer


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


from django.shortcuts import redirect


def get_redirect_url(user):
    role = user.role.name if user.role else None

    # if role == 'Admin':
    #     return reverse('landing')
    if role == 'Doctor':
        return reverse('inicio')
    # elif role == 'Patient':
    #     return reverse('inicio')
    else:
        return reverse('login')


@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginViewAPI(FormView):
    template_name = "users/login.html"
    form_class = CustomLoginForm

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            email = body.get('email')
            password = body.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato incorrecto'}, status=400)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            redirect_url = get_redirect_url(user)

            return JsonResponse({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'redirect_url': redirect_url
            })

        return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def cerrar_sesion(request):
    logout(request)
    return redirect('/')


def register(request):
    return render(request, 'users/register.html', status=200)
