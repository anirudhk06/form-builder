from bson import ObjectId
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from core.utils.password_generation import generate_password
from core.db.mongo import forms_collection
from rest_framework import serializers

USER = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirm_password"] = serializers.CharField(
            required=False, allow_null=True, allow_blank=True
        )

    password = serializers.CharField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = USER
        fields = ["username", "email", "first_name", "last_name", "phone", "password"]

    def validate(self, attrs):
        self.fields.pop("confirm_password", None)
        confirm_password = attrs.pop("confirm_password", None)
        password = attrs.get("password")
        
        user = USER(**attrs)
        if password is None:
            attrs["password"] = generate_password()
        else:
            if password == confirm_password:
                try:
                    validate_password(password, user)
                except ValidationError as e:
                    error = serializers.as_serializer_error(e)
                    raise serializers.ValidationError(
                        {"password": error.get("errors", [])}
                    )
                return attrs
            else:
                raise serializers.ValidationError(
                    {"confirm_password": "Password not matching."}
                )

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = USER(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "display_name",
            "first_name",
            "last_name",
            "avatar",
            "cover_image",
            "user_timezone"
        ]


class AssignFormsSerializer(serializers.Serializer):
    form_ids = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True
    )

    def validate_form_ids(self, value):
        invalid = []

        for form_id in value:
            try:
                exists = forms_collection().count_documents(
                    {"_id": ObjectId(form_id)},
                    limit=1
                )
                if not exists:
                    invalid.append(form_id)
            except Exception:
                invalid.append(form_id)

        if invalid:
            raise serializers.ValidationError(
                f"These form IDs do not exist: {invalid}"
            )
        return value