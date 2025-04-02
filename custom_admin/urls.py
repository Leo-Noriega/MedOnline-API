from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet, home

router = DefaultRouter()
router.register(r'users', AdminUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('home/', home, name='home'),
]