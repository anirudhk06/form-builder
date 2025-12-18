def validate_field_value(field, value) -> None:
    field_type = field["type"]
    required = field.get("required", False)

    if value is None:
        if required:
            raise ValueError("This field is required")
        return

    if field_type == "text":
        if not isinstance(value, str):
            raise ValueError("Must be a string")

    elif field_type == "number":
        if not isinstance(value, (int, float)):
            raise ValueError("Must be a number")

    elif field_type == "date":
        if not isinstance(value, str):
            raise ValueError("Must be a date string")

    elif field_type == "checkbox":
        if not isinstance(value, bool):
            raise ValueError("Must be true or false")

    elif field_type == "file":
        if not isinstance(value, str):
            raise ValueError("Invalid file reference")

    else:
        raise ValueError("Unsupported field type")
