from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer
from .filters import TransactionFilter
from users.permissions import IsAdminOrAbove, IsViewerOrAbove

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    filterset_class  = TransactionFilter
    search_fields    = ['category', 'notes']
    ordering_fields  = ['date', 'amount']

    def get_queryset(self):
        return Transaction.objects.filter(is_deleted=False)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsViewerOrAbove()]       # all roles can read
        return [IsAdminOrAbove()]            # admin + superadmin can write

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)