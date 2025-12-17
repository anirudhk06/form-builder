from django.db import IntegrityError, transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


USER = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirm_password"] = serializers.CharField()

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
                raise serializers.ValidationError({
                    "password": error.get("errors", [])
                })
            return attrs
        else:
            raise serializers.ValidationError({"confirm_password": "Password not matching."})
    
    def create(self, validated_data):
        try:
            validated_data["is_staff"] = True
            user = self.perform_create(validated_data)
        except IntegrityError:
            raise ValueError("Cannot create user")
        return user

    def perform_create(self, validated_data):
        with transaction.atomic():
            user = USER.objects.create_user(**validated_data)        
        return user