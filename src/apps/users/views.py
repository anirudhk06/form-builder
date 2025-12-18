from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, views
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserListSerializer, AssignFormsSerializer
from .permissions import IsStaffUser
from .filters import UserFilter
from core.utils.pagination import CustomLimitPagination
from apps.form_engine.models import FormMaster

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


class AssignFormsView(views.APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, user_id=None, *args, **kwargs):
        try:
            user = USER.objects.get(id=user_id, created_by=request.user)
        except USER.DoesNotExist:
            return Response({
                "detail": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "detail": "Something went wrong"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        serializer = AssignFormsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        incoming_form_ids = set(serializer.validated_data["form_ids"])

        existing_form_ids = set(
            FormMaster.objects.filter(user=user)
            .values_list("form_id", flat=True)
        )

        to_add = incoming_form_ids - existing_form_ids
        to_remove = existing_form_ids - incoming_form_ids

        with transaction.atomic():
            if to_remove:
                FormMaster.objects.filter(
                    user=user,
                    form_id__in=to_remove
                ).delete()

            if to_add:
                FormMaster.objects.bulk_create(
                    [
                        FormMaster(user=user, form_id=form_id)
                        for form_id in to_add
                    ]
                )

        return Response(
            {
                "message": "Forms assigned successfully",
                "added": list(to_add),
                "removed": list(to_remove),
                "total": len(incoming_form_ids),
            },
            status=status.HTTP_201_CREATED,
        )

