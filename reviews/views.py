from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    renderer_classes = [JSONRenderer]
    http_method_names = ['get', 'post', 'put', 'delete']
