from django.utils import timezone
from rest_framework import serializers
from pprint import pprint

from core.db.mongo import forms_collection, field_collection

class FormFieldSerializer(serializers.Serializer):
    FIELD_TYPE_CHOICES = (
        ("text", "Text"),
        ("email", "Email"),
        ("number", "Number"),
        ("date", "Date"),
        ("file", "File"),
        ("checkbox", "Checkbox (Boolean)"),
        ("multi_checkbox", "Checkbox (Multiple)"),
    )

    field_id = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=100)
    label = serializers.CharField(max_length=255)

    type = serializers.ChoiceField(choices=FIELD_TYPE_CHOICES)

    required = serializers.BooleanField(default=False)
    allow_null = serializers.BooleanField(default=True)
    allow_blank = serializers.BooleanField(default=True)
    is_active = serializers.BooleanField(default=True)

    placeholder = serializers.CharField(required=False, allow_blank=True)
    help_text = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False, min_value=0)

    min_length = serializers.IntegerField(required=False, min_value=0)
    max_length = serializers.IntegerField(required=False, min_value=1)

    min_length = serializers.IntegerField(required=False, min_value=0)
    max_length = serializers.IntegerField(required=False, min_value=1)

    allowed_extensions = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    max_size_mb = serializers.IntegerField(required=False, min_value=1)

    options = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate(self, attrs):
        field_type = attrs.get("type")

        if field_type == "file":
            if not attrs.get("allowed_extensions"):
                raise serializers.ValidationError(
                    {"allowed_extensions": "This field is required for file type."}
                )
            if not attrs.get("max_size_mb"):
                raise serializers.ValidationError(
                    {"max_size_mb": "This field is required for file type."}
                )


        return super().validate(attrs)
    

class DynamicFormSerializer(serializers.Serializer):
    name = serializers.CharField()
    submit = serializers.CharField(default="Submit")
    expired_at = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField(
        default=True,
        required=False
    )

    fields = FormFieldSerializer(many=True, required=False)


    def create(self, validated_data: dict) -> dict:
        auth_user = self.context.get("auth_user")
        current_datetime = timezone.now()
        fields = validated_data.pop("fields", [])

        
        form = forms_collection().insert_one({
            **validated_data,
            "created_by": str(auth_user.pk),
            "created_at": current_datetime,
            "updated_at": current_datetime,
        })

        for idx, field in enumerate(fields):
            field_collection().insert_one({
                **field,
                "form_id": form.inserted_id,
                "created_by": str(auth_user.pk),
                "created_at": current_datetime,
                "updated_at": current_datetime,
                "order": idx
            })

        return {
            "form_id": str(form.inserted_id)
        }


class FieldOrderSerializer(serializers.Serializer):
    id = serializers.CharField()
    order = serializers.IntegerField(min_value=1)


class UpdateFieldOrderSerializer(serializers.Serializer):
    fields = FieldOrderSerializer(many=True)

    def validate_fields(self, value):
        orders = [item["order"] for item in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError(
                "Duplicate order values are not allowed."
            )
        return value
    

class FormSubmissionSerializer(serializers.Serializer):
    values = serializers.DictField(
        child=serializers.JSONField()
    )