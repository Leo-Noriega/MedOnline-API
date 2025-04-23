from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from django.utils.timezone import now
from appointments.models import Appointment
from cryptography.fernet import Fernet
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

fernet = Fernet(settings.FERNET_KEY)

def decrypt_id(encrypted_id):
    try:
        decrypted_bytes = fernet.decrypt(encrypted_id.encode())
        return int(decrypted_bytes.decode())
    except Exception as e:
        raise  

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_queryset(self):
        queryset = Review.objects.all()
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset

    def perform_create(self, serializer):
        # Asignar el usuario autenticado a la reseña
        serializer.save(user=self.request.user)
      
@method_decorator(ensure_csrf_cookie, name='dispatch')
class ReviewDoctorView(View):   
    def get(self, request, token):
        try:
            appointment_id = decrypt_id(token)  
            appointment = get_object_or_404(Appointment, id=appointment_id)
            doctor = appointment.doctor
            review_exists = Review.objects.filter(appointment=appointment).exists()
            
            context = {
                "appointment": appointment,
                "review_token": token,
                "doctor_name": f"{doctor.user.name} {doctor.user.surnames}",
                "doctor_photo": doctor.user.photo if doctor.user.photo else None,
                "review_exists": review_exists,
            }
            
            
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse(
                {"error": "El enlace no es válido."},
                status=400,
            )
        return render(request, "review_doctor.html", context)
        
    def post(self, request, token):
        print(f"Origin: {request.headers.get('Origin')}")
        try:
            appointment_id = decrypt_id(token)  # 🔹 Descifra el ID de la cita
            appointment = get_object_or_404(Appointment, id=appointment_id)
        except Exception:
            messages.error(request, "El enlace no es válido.")
            return redirect("/")
        
        import json
        try: 
            data = json.loads(request.body)
            rating = data.get("rating")
            comment = data.get("comment")
        except json.JsonDecodeError:
            return JsonResponse(
                {"error": "Error al procesar la solicitud."},
                status=400,
            )

        if not rating:
            return JsonResponse(
                {"error": "El campo de calificación es obligatorio."},
                status=400,
            )

        review, created = Review.objects.get_or_create(
            appointment=appointment,
            doctor=appointment.doctor,
            user=appointment.user,
            defaults={"rating": rating, "comment": comment, "review_date": now()},
        ) 

        if not created:
            return JsonResponse(
                {"error": "Ya has dejado una reseña para esta cita."},
                status=400,
            )
            

        review.rating = rating
        review.comment = comment
        review.review_date = now()
        review.save()

        return JsonResponse(
            {"message": "Gracias por tu reseña"},
            status=200,
        )
        
        
        
