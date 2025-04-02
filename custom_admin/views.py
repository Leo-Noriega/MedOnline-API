from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework.permissions import IsAdminUser

class AdminUserViewSet(viewsets.ModelViewSet):
      queryset  = CustomUser.objects.all()
      serializer_class = CustomUserSerializer
      permission_classes = [IsAdminUser]

      def list(self, request):
           users = self.get_queryset()
           serializer = self.get_serializer(users, many=True)
           return Response(serializer.data)
      
      def get_one (self,requesrt,pk =None):
           try:
                user = self.get_queryset().get(pk=pk)
                serializer = self.get_serializer(user)
                return Response(serializer.data)
           except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
      def update(self, request, pk=None):
           try:
                user = self.get_queryset().get(pk=pk)
                serializer = self.get_serializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
           except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
           
      def destroy(self, request, pk=None):
           try:
                user = self.get_queryset().get(pk=pk)
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
           except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)     
           
def home(request):
   return render(request,'home_Admin.html', status=200)
# Create your views here.

