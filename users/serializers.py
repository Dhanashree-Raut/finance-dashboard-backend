from rest_framework import serializers
from .models import User

# users/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom fields
        token['role'] = user.role
        token['username'] = user.username
        
        # 🔥 Smart name logic
        first = user.first_name.strip() if user.first_name else ''
        last = user.last_name.strip() if user.last_name else ''

        if first and last:
            name = f"{first.capitalize()} {last.capitalize()}"
        elif first:
            name = first.capitalize()
        elif last:
            name = last.capitalize()
        else:
            name = user.username.capitalize()

        token['name'] = name

        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance