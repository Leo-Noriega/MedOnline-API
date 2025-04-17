from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from rest_framework import serializers


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'surnames', 'phone', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}  # El campo no es obligatorio.
        }

    def update(self, instance, validated_data):
        # Si se proporciona la contraseña, actualízala.
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        # Actualiza los demás campos normalmente.
        return super().update(instance, validated_data)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token