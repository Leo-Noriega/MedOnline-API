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
import secrets
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

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

def recovery_password_view(request):
    return render(request, 'users/recovery_password.html')

def reset_password_view(request, token):
    user = CustomUser.objects.filter(token=token).first()
    if not user:
        return render(request, 'users/invalid_token.html')
    
    return render(request, 'users/reset_password.html', {'token': token})

@csrf_exempt
def send_reset_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user:
            token = secrets.token_urlsafe(20)
            user.token = token
            user.save()

            reset_link = f"http://localhost:8000/users/reset-password/{token}"

            send_mail(
                subject="Recuperación de contraseña",
                message=f"Hola, usa este enlace para restablecer tu contraseña: {reset_link}",  
                from_email="no-reply@medonline.com",
                recipient_list=[email],
                fail_silently=False,
                html_message=f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>MedOnline - Recuperación de Contraseña</title>
                </head>
                <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #7F807F; -webkit-font-smoothing: antialiased; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
                    <table align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="max-width: 600px; margin: 20px auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td align="center" bgcolor="#2E5077" style="padding: 20px; text-align: center; height: 40px;">
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 30px 30px 20px 30px;">
                                <h1 style="color: #2E5077; font-size: 24px; font-weight: 700; margin-top: 0; margin-bottom: 20px; line-height: 32px;">Recuperación de Contraseña</h1>
                                                
                                <p style="margin-top: 20px; margin-bottom: 15px; line-height: 24px; font-size: 16px;">Hola</p>
                                <p style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px;">Has solicitado restablecer tu contraseña. Para continuar, haz clic en el siguiente botón:</p>
                                
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center" style="padding: 25px 0;">
                                            <table border="0" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td align="center" bgcolor="#2E5077" style="border-radius: 4px;">
                                                        <a href="{reset_link}" target="_blank" style="display: inline-block; padding: 12px 30px; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: 500;">Restablecer Contraseña</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin-top: 0; margin-bottom: 15px; line-height: 24px; font-size: 16px;">O copia y pega este enlace en tu navegador:</p>
                                <p style="margin-top: 0; margin-bottom: 30px; line-height: 24px; font-size: 16px; word-break: break-all;"><a href="{reset_link}" style="color: #4DA1A9; text-decoration: none;">{reset_link}</a></p>
                                
                                <p style="margin-top: 0; margin-bottom: 15px; line-height: 24px; font-size: 16px;">Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" bgcolor="#F9F9F9" style="padding: 20px; text-align: center; color: #7F807F; font-size: 14px;">
                                <p style="margin: 5px 0;">Atentamente, El equipo de MedOnline</p>
                                <p style="margin: 5px 0;">&copy; 2025 MedOnline. Todos los derechos reservados.</p>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            )
            return JsonResponse({"message": "Correo de recuperación enviado."}, status=200)
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)


@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        token = request.POST.get("token")
        new_password = request.POST.get("password")
        user = CustomUser.objects.filter(token=token).first()

        if user:
            user.password = make_password(new_password) 
            user.token = None  
            user.save()

            send_mail(
                subject="Recuperación de contraseña",
                message=f"Tu contraseña fue cambiada con exito!", 
                from_email="no-reply@medonline.com",
                recipient_list=[user.email],
                fail_silently=False,
                html_message=f"""
                <!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>MedOnline - Contraseña Actualizada</title>
                </head>
                <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #7F807F; -webkit-font-smoothing: antialiased; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
                    <table align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="max-width: 600px; margin: 20px auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td align="center" bgcolor="#2E5077" style="padding: 20px; text-align: center; height: 40px;">
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 30px 30px 20px 30px;">
                                <h1 style="color: #2E5077; font-size: 24px; font-weight: 700; margin-top: 0; margin-bottom: 20px; line-height: 32px;">¡Tu contraseña fue cambiada con éxito!</h1>
                                                
                                <p style="margin-top: 20px; margin-bottom: 15px; line-height: 24px; font-size: 16px;">Hola</p>
                                <p style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px;">Tu contraseña ha sido actualizada correctamente. Ya puedes iniciar sesión con tu nueva contraseña.</p>
                                
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td align="center" style="padding: 25px 0;">
                                            <table border="0" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td align="center" bgcolor="#2E5077" style="border-radius: 4px;">
                                                        <a href="http://localhost:8000/users/login/" target="_blank" style="display: inline-block; padding: 12px 30px; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: 500;">Iniciar Sesión</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <p style="margin-top: 0; margin-bottom: 15px; line-height: 24px; font-size: 16px; color: #565C5F;">Si no realizaste este cambio, tu cuenta podría estar en peligro. Por favor, contacta inmediatamente con <a href="mailto:medonlineapi@gmail.com" style="color: #4DA1A9; text-decoration: none;">medonlineapi@gmail.com</a>.</p>
                            </td>
                        </tr>

                        <tr>
                            <td align="center" bgcolor="#F9F9F9" style="padding: 20px; text-align: center; color: #7F807F; font-size: 14px;">
                                <p style="margin: 5px 0;">Atentamente, El equipo de MedOnline</p>
                                <p style="margin: 5px 0;">&copy; 2025 MedOnline. Todos los derechos reservados.</p>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """
            )

            return JsonResponse({"message": "Contraseña restablecida exitosamente."})
        return JsonResponse({"error": "Token inválido"}, status=400)
