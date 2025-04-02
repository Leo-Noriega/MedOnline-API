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

fernet = Fernet(settings.FERNET_KEY)

def decrypt_id(encrypted_id):
        return int(fernet.decrypt(encrypted_id.encode()).decode())

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_queryset(self):
        # El usuario solo puede ver sus propias reseñas
        user = self.request.user
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            return Review.objects.filter(user=user, doctor_id=doctor_id)
        return Review.objects.filter(user=user)

    def perform_create(self, serializer):
        # Asignar el usuario autenticado a la reseña
        serializer.save(user=self.request.user)
        
class ReviewDoctorView(View):   
    def get(self, request, token):
        try:
            appointment_id = decrypt_id(token)  
            appointment = get_object_or_404(Appointment, id=appointment_id)
        except Exception:
            messages.error(request, "El enlace no es válido.")
            return redirect("/")
        
        return render(request, "review_doctor.html", {"appointment": appointment, "review_token": token})
    
    def post(self, request, token):
        try:
            appointment_id = decrypt_id(token)  # 🔹 Descifra el ID de la cita
            appointment = get_object_or_404(Appointment, id=appointment_id)
        except Exception:
            messages.error(request, "El enlace no es válido.")
            return redirect("/")
        
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating:
            messages.error(request, "Debes seleccionar una calificación.")
            return redirect(request.path)

        review, created = Review.objects.get_or_create(
            appointment=appointment,
            user=appointment.user,
            doctor=appointment.doctor,
            defaults={"rating": rating, "comment": comment, "review_date": now()},
        ) 

        if not created:
            messages.error(request, "Ya has calificado esta cita.")
            return redirect("/")

        review.rating = rating
        review.comment = comment
        review.review_date = now()
        review.save()

        messages.success(request, "Gracias por tu reseña.")
        return redirect("/")
        
        
        
