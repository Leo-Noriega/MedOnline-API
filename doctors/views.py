from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
import json
from .models import *
from .serializers import *
from users.models import CustomUser
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doctor, Address, DoctorSpecialty
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from reviews.models import Review

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
    
class SpecialtyViewSet(viewsets.ModelViewSet):
    queryset = Specialty.objects.all()
    serializer_class = SpecialtySerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
    
class DoctorSpecialtyViewSet(viewsets.ModelViewSet):
    queryset = DoctorSpecialty.objects.all()
    serializer_class = DoctorSpecialtySerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']

def get_doctor_reviews(request, doctor_id):
    try:
        doctor = Doctor.objects.get(id=doctor_id)
        reviews = Review.objects.filter(doctor=doctor)
        reviews_data = [
            {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "review_date": review.review_date,
                "user": {
                    "id": review.user.id,
                    "name": review.user.name,
                    "surnames": review.user.surnames,
                    "photo": review.user.photo.url if review.user.photo else None,
                }
            }
            for review in reviews
        ]
        return JsonResponse(reviews_data, safe=False, status=200)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error inesperado: {str(e)}'}, status=500)
    
@login_required
def user_doctor_details(request,user_id):
    try:
        doctor=Doctor.objects.get(user_id=user_id)
        addresses=Address.objects.filter(doctor=doctor)
        addresses_data=[
            {
                "id":address.id,
                "clinic_name": address.clinic_name,
                "street": address.street,
                "city": address.city,
                "state": address.state,
                "postal_code": address.postal_code,
                "doctor":address.doctor_id,
            }
             for address in addresses
        ]

        specialties=DoctorSpecialty.objects.filter(doctor=doctor)
        specialties_data=[
            {
                "specialty": specialty.specialty.name,
                "license_number": specialty.license_number,
            }
            for specialty in specialties
        ]
        photo_url = doctor.user.photo.url if doctor.user.photo else None

        data={
             "doctor": {
                "id":doctor.id,
                "name": doctor.user.name,
                "surnames": doctor.user.surnames,
                "phone": doctor.user.phone,
                "photo": photo_url,
                "email": doctor.user.email,
                "years_experience": doctor.years_experience,
                "consultation_fee": doctor.consultation_fee,
            },
            "addresses": addresses_data,
            "specialties": specialties_data,
        }
        return JsonResponse(data,safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({"error":"Datos no encontrados para este usuario"}, status=404)

@login_required
@require_http_methods(["PUT"])
def edit_user_doctor(request, user_id):
    try:
        user=CustomUser.objects.get(id=user_id)
        doctor= Doctor.objects.get(user=user)
        print ("cuerpo de la solicitud", request.body)
        data= json.loads(request.body)
        print("Datos recibidos:",data)
        user.name = data.get('name', user.name)if 'name' in data else user.name
        user.surnames = data.get('surnames', user.surnames) if 'surnames' in data else user.surnames
        user.email = data.get('email', user.email)if 'email' in data else user.email
        user.phone=data.get('phone', user.phone)if 'phone' in data else user.phone

        if 'photo' in request.FILES:
            user.photo= request.FILES['photo']

        if 'password' in data:
            user.password= make_password(data['password'])
        user.save()
        print("Datos antes de guardar:", user.__dict__)
        user.save()
        print("Datos después de guardar:", user.__dict__)
        doctor.consultation_fee = data.get('consultation_fee', doctor.consultation_fee)  # Actualiza solo si el dato existe
        doctor.years_experience = data.get('years_experience', doctor.years_experience) if 'years_experience' in data else doctor.years_experience
        doctor.save()

        print("Datos del doctor antes de guardar:", doctor.__dict__)
        doctor.save()
        print("Datos del doctor después de guardar:", doctor.__dict__)

      

        return JsonResponse({
            "message": "Información actualizada exitosamente",
            "user": {
                "name": user.name,
                "surnames": user.surnames,
                "email": user.email,
                "phone": user.phone,
                "photo": user.photo.url if user.photo else None
            },
            "doctor": {
                "years_experience": doctor.years_experience,
                "consultation_fee": doctor.consultation_fee
            }
        })
 
    except Exception as e:
        print(f"Error al guardar el usuario: {str(e)}")
        return JsonResponse({"error": "No se pudo guardar el usuario"}, status=500)
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({"error": "Médico no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

@login_required
@require_http_methods(['POST'])
def associate_specialty(request):
    try:
        data=json.loads(request.body)
        doctor_id=data.get('doctor_id')
        specialty_name=data.get('specialty_name')
        license_number=data.get('license_number')
        if not all([doctor_id, specialty_name,license_number]):
            return JsonResponse({'error':"Faltan datos obligatorios"}, status=400)
        specialty_name= specialty_name.strip().upper()
        try:
            specialty=Specialty.objects.get(name=specialty_name)
        except Specialty.DoesNotExist:
            specialty= Specialty.objects.create(name=specialty_name)

        try:
            doctor=Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return JsonResponse({"Error":"Doctor no encontrado"}, status=404)

        doctor_specialty, created = DoctorSpecialty.objects.get_or_create(
            doctor=doctor,
            specialty=specialty,
            defaults={"license_number": license_number}
        )
        message = "Especialidad asociada exitosamente" if created else "Especialidad actualizada exitosamente"
        return JsonResponse({
            "message": message,
            "doctor_specialty": {
                "doctor": doctor.user.name,
                "specialty": specialty.name,
                "license_number": doctor_specialty.license_number,
            }
        })
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)


@login_required
def home(request):
    print("Usuario:", request.user)
    print("Sesión:", request.user.is_authenticated)
    print("info_sesion:", dict(request.session)) 
    user_id = request.session.get('_auth_user_id')
    nombre = request.user.name
    apellidos = request.user.surnames

    if request.user.role.name not in ['Doctor', 'Administrador']:
        return redirect('login')
    else:
        return render(request, 'home.html',  {'nombre': nombre, 'apellidos':apellidos},status=200)
  
@login_required
def my_account(request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Doctor', 'Administrador']:
        return redirect('login')
    else:
        return render(request,'myAccount.html',{'user_id':user_id}, status=200)
    
@login_required
def opinions(request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Doctor', 'Administrador']:
        return redirect('login')
    else:
        return render(request,'opinions.html',{'user_id':user_id}, status=200)

def medicalOffice(request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Doctor', 'Administrador']:
        return redirect('login')
    else:
        return render(request,'medicalOffice.html',{'user_id':user_id} ,status=200)
