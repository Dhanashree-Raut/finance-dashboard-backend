from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from .permissions import IsSuperAdmin

# users/views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset           = User.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [IsSuperAdmin]   # entire viewset — superadmin only

    @action(detail=True, methods=['patch'])
    def set_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get('role')
        valid_roles = [r.value for r in User.Role]
        if role not in valid_roles:
            return Response(
                {'error': f'Invalid role. Choose from: {valid_roles}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.role = role
        user.save()
        return Response({'status': 'role updated', 'role': role})

    @action(detail=True, methods=['patch'])
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'is_active': user.is_active})