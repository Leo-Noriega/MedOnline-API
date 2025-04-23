import json
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
import secrets
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .forms import CustomLoginForm, PatientRegistrationForm, DoctorRegistrationForm
from .models import Role, CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from doctors.models import Doctor, Specialty, DoctorSpecialty, Address
from django.db import connection


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


def get_redirect_url(user):
    role = user.role.name if user.role else None

    if role == 'Admin':
        return reverse('admin_home')
    elif role == 'Doctor':
        return reverse('inicio')
    elif role == 'Patient':
         return reverse('user_home')
    else:
        return reverse('login')
    
@login_required
def user_home(request):
    print("Usuario:", request.user)
    print("Sesión:", request.user.is_authenticated)
    print("info_sesion:", dict(request.session)) 
    user_id = request.session.get('_auth_user_id')
    nombre = request.user.name
    apellidos = request.user.surnames

    if request.user.role.name not in ['Patient']:
        return redirect('login')
    else:
        specialities = get_all_specialities()
        mexican_states = [
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua",
            "Ciudad de México", "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo",
            "Jalisco", "Estado de México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
            "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco",
            "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
        ]
        return render(request, 'users/userHome.html',
                      {'nombre': nombre,
                       'apellidos':apellidos,
                       'specialities' : specialities,
                       'mexican_states': mexican_states},
                      status=200)


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
            role = user.role.name if user.role else None
            redirect_url = get_redirect_url(user)

            return JsonResponse({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'redirect_url': redirect_url,
                'role': role,
            })

        return JsonResponse({'error': 'Credenciales incorrectas'}, status=401)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


def cerrar_sesion(request):
    logout(request)
    return redirect('/')


def register(request):
    """Vista para la página inicial de registro donde se elige el tipo de usuario"""
    return render(request, 'users/register.html', status=200)

def register_patient(request):
    """Vista para el registro de pacientes"""
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                
                try:
                    role = Role.objects.get(name='Patient')
                    user.role = role
                    user.save()
                    
                    # Enviar correo de confirmación
                    send_mail(
                        subject="Bienvenido a MedOnline - Registro Exitoso",
                        message=f"Tu cuenta ha sido creada exitosamente!", 
                        from_email="no-reply@medonline.com",
                        recipient_list=[user.email],
                        fail_silently=False,
                        html_message=f"""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>MedOnline - Registro Exitoso</title>
                        </head>
                        <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #7F807F; -webkit-font-smoothing: antialiased; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
                            <table align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="max-width: 600px; margin: 20px auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                                <tr>
                                    <td align="center" bgcolor="#2E5077" style="padding: 20px; text-align: center; height: 40px;">
                                    </td>
                                </tr>
                                
                                <tr>
                                    <td style="padding: 30px 30px 20px 30px;">
                                        <h1 style="color: #2E5077; font-size: 24px; font-weight: 700; margin-top: 0; margin-bottom: 20px; line-height: 32px;">¡Bienvenido/a a MedOnline!</h1>
                                                        
                                        <p style="margin-top: 20px; margin-bottom: 15px; line-height: 24px; font-size: 16px;">Hola {user.name},</p>
                                        <p style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px;">Gracias por registrarte en MedOnline. Tu cuenta ha sido creada exitosamente y ya puedes disfrutar de todos nuestros servicios.</p>
                                        
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
                                        
                                        <p style="margin-top: 0; margin-bottom: 15px; line-height: 24px; font-size: 16px; color: #565C5F;">Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos a <a href="mailto:medonlineapi@gmail.com" style="color: #4DA1A9; text-decoration: none;">medonlineapi@gmail.com</a>.</p>
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
                    
                    # Verificar si se solicita respuesta JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'message': 'Registro exitoso. Redirigiendo...'})
                    else:
                        messages.success(request, "Registro exitoso. Ahora puedes iniciar sesión.")
                        return redirect('login')
                    
                except Role.DoesNotExist:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'error': "El rol de Paciente no existe en el sistema."}, status=400)
                    else:
                        messages.error(request, "El rol de Paciente no existe en el sistema.")
                    
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({'error': "Por favor corrija los errores en el formulario.", 'field_errors': errors}, status=400)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    
    return render(request, 'users/register_patient.html')

@method_decorator(csrf_exempt, name='dispatch')
class RegisterDoctorView(View):
    """Vista para el registro de especialistas (doctores)"""
    template_name = 'users/register_doctor.html'
    
    def get(self, request):
        specialties = Specialty.objects.all()
        context = {'specialties': specialties}
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = DoctorRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Crear usuario
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    
                    role = Role.objects.get(name='Doctor')
                    user.role = role
                    user.save()
                    
                    # Crear doctor
                    doctor = Doctor.objects.create(
                        user=user,
                        consultation_fee=form.cleaned_data['consultation_fee'],
                        consultation_time=form.cleaned_data['consultation_time']
                    )
                    
                    # Crear especialidad del doctor
                    specialty = form.cleaned_data['specialty']
                    DoctorSpecialty.objects.create(
                        doctor=doctor,
                        specialty=specialty,
                        license_number=form.cleaned_data['license_number']
                    )
                    
                    # Enviar correo de confirmación
                    send_mail(
                        subject="Bienvenido a MedOnline - Registro de Especialista Exitoso",
                        message=f"Tu cuenta de especialista ha sido creada exitosamente!", 
                        from_email="no-reply@medonline.com",
                        recipient_list=[user.email],
                        fail_silently=False,
                        html_message=f"""
                        <!DOCTYPE html>
                        <html lang="es">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>MedOnline - Registro de Especialista Exitoso</title>
                        </head>
                        <body style="font-family: 'DM Sans', Arial, sans-serif; background-color: #f5f5f5; margin: 0; padding: 0; color: #7F807F; -webkit-font-smoothing: antialiased; -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%;">
                            <table align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="max-width: 600px; margin: 20px auto; background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                                <tr>
                                    <td align="center" bgcolor="#2E5077" style="padding: 20px; text-align: center; height: 40px;">
                                    </td>
                                </tr>
                                
                                <tr>
                                    <td style="padding: 30px 30px 20px 30px;">
                                        <h1 style="color: #2E5077; font-size: 24px; font-weight: 700; margin-top: 0; margin-bottom: 20px; line-height: 32px;">¡Bienvenido/a a MedOnline!</h1>
                                                        
                                        <p style="margin-top: 20px; margin-bottom: 15px; line-height: 24px; font-size: 16px;">Hola Dr./Dra. {user.surnames},</p>
                                        <p style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px;">Gracias por registrarte como especialista en MedOnline. Tu cuenta ha sido creada exitosamente y ya puedes comenzar a ofrecer tus servicios profesionales a través de nuestra plataforma.</p>
                                        
                                        <p style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px;">Información de tu registro:</p>
                                        <ul style="margin-top: 0; margin-bottom: 20px; line-height: 24px; font-size: 16px; color: #565C5F;">
                                            <li>Especialidad: {specialty.name}</li>
                                            <li>Tarifa de consulta: ${doctor.consultation_fee}</li>
                                            <li>Tiempo de consulta: {str(doctor.consultation_time).split(':')[0]}h:{str(doctor.consultation_time).split(':')[1]}m</li>
                                        </ul>
                                        
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
                                        
                                        <p style="margin-top: 0; margin-bottom: 15px; line-height: 24px; font-size: 16px; color: #565C5F;">Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos a <a href="mailto:medonlineapi@gmail.com" style="color: #4DA1A9; text-decoration: none;">medonlineapi@gmail.com</a>.</p>
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
                    
                    return redirect('login')
                    
            except Role.DoesNotExist:
                messages.error(request, "El rol de Doctor no existe en el sistema.")
            except Exception as e:
                messages.error(request, f"Error durante el registro: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        specialties = Specialty.objects.all()
        context = {'specialties': specialties, 'form_data': request.POST}
        return render(request, self.template_name, context)

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

def get_all_specialities():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM doctors_specialty")
        rows = cursor.fetchall()
    return rows

def get_doctors_by_specialty_and_state(specialty_id, state):

    query = """
    SELECT u.name, u.surnames, doctor.id, u.photo, sp.name AS specialty, da.clinic_name, da.street, da.city, da.state, da.postal_code
    FROM doctors_doctor doctor
    JOIN user u ON doctor.user_id = u.id
    JOIN doctors_doctorspecialty ds ON doctor.id = ds.doctor_id
    JOIN doctors_specialty sp ON ds.specialty_id = sp.id
    JOIN doctors_address da ON doctor.id = da.doctor_id
    WHERE ds.specialty_id = %s AND da.state = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [specialty_id, state])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

def appointment(request):
    """Vista para la página de citas médicas"""
    doctor_id = request.GET.get('doctor_id')  # Obtén el ID del doctor desde la URL
    user_id = request.session.get('_auth_user_id')
    nombre = request.user.name
    apellidos = request.user.surnames

    if request.user.role.name not in ['Patient']:
        return redirect('login')
    else:
        return render(request, 'users/appointmentForm.html', {
            'nombre': nombre,
            'apellidos': apellidos,
            'doctorId': doctor_id
        }, status=200)

def search_doctors(request):
    specialty_id = request.GET.get('specialty_id')
    state = request.GET.get('state')
    if not specialty_id or not state:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    doctors = get_doctors_by_specialty_and_state(specialty_id, state)
    return JsonResponse({'doctors': doctors}, safe=False)


class DoctorSearchAPIView(APIView):
    def get(self, request):
        specialty_id = request.query_params.get('specialty_id')
        state = request.query_params.get('state')

        if not specialty_id or not state:
            return Response({'error': 'Missing parameters: specialty_id and state are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctors = get_doctors_by_specialty_and_state(specialty_id, state)
            return Response({'doctors': doctors}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserUpdateView(APIView):
    def put(self, request, user_id):
        user = User.objects.get(id=user_id)
        serializer = CustomUserSerializer(user, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)