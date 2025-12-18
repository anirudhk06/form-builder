from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserListSerializer
from .permissions import IsStaffUser
from .filters import UserFilter
from core.utils.pagination import CustomLimitPagination

USER = get_user_model()
class UserListCreateView(generics.ListCreateAPIView):
    serializer_class = UserCreateSerializer
    pagination_class = CustomLimitPagination
    permission_classes = [IsStaffUser]
    search_fields = [
        "email"
    ]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        return USER.objects.filter(
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserListSerializer
        return super().get_serializer_class()
    
    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        users = self.get_serializer(page, many=True).data
        return Response({**self.paginator.get_pagination_details(), "users": users})
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "User created successfully"
        }, status=status.HTTP_201_CREATED)
