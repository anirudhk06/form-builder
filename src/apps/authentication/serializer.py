from django.db import IntegrityError, transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


USER = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirm_password"] = serializers.CharField(
            style={"input_type": "password"}, write_only=True
        )

    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = USER
        fields = ("id", "username", "email", "password")
    
    def validate(self, attrs):
        self.fields.pop("confirm_password", None)
        confirm_password = attrs.pop("confirm_password", None)
        password = attrs.get("password")

        user = USER(**attrs)
        if password == confirm_password:
            try:
                validate_password(password, user)
            except ValidationError as e:
                error = serializers.as_serializer_error(e)
                raise serializers.ValidationError(error)
            return attrs
        else:
            raise serializers.ValidationError("Password not matching.")
    
    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise ValueError("Cannot create user")
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = USER.objects.create_user(**validated_data)
        return user