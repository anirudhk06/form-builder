from django.contrib.auth import get_user_model
from rest_framework import generics
from .serializers import UserCreateSerializer, UserListSerializer
from .permissions import IsStaffUser

USER = get_user_model()
class UserListCreateView(generics.ListCreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [IsStaffUser]

    def get_queryset(self):
        return USER.objects.filter(
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserListSerializer
        return super().get_serializer_class()
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
