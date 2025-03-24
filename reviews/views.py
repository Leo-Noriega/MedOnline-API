from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_queryset(self):
        # El usuario solo puede ver sus propias reseñas
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Asignar el usuario autenticado a la reseña
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Agregar información de depuración
        print(f"Datos recibidos en create: {request.data}")
        return super().create(request, *args, **kwargs)
        
