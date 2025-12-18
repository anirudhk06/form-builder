from bson import ObjectId
from django.utils import timezone
from rest_framework import status, generics, views
from rest_framework.response import Response
from pymongo import ReturnDocument, UpdateOne

from .serializer import DynamicFormSerializer, FormFieldSerializer, UpdateFieldOrderSerializer
from core.db.mongo import forms_collection, field_collection
from core.utils.pagination import MongoPageNumberPagination


class FormCreateView(views.APIView):
    def post(self, request, *args, **kwargs):
        auth_user = request.user

        serializer = DynamicFormSerializer(
            data=request.data,
            context={
                "auth_user": auth_user,
            },
        )
        serializer.is_valid(raise_exception=True)
        form = serializer.save()
        return Response(
            {"message": "Form created successfully", "form_id": form.get("form_id")},
            status=status.HTTP_201_CREATED,
        )


class FormUpdateView(views.APIView):
    def patch(self, request, form_id=None, *args, **kwargs):
        form = forms_collection().find_one({"_id": ObjectId(form_id)})

        if not form:
            return Response(
                {"detail": "Form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = DynamicFormSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        update_data = serializer.validated_data

        updated_form = forms_collection().find_one_and_update(
            {"_id": ObjectId(form_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        updated_form["id"] = str(updated_form.pop("_id"))

        return Response(
            {
                "message": "Form updated successfully",
                "form": updated_form,
            }
        )


class FormDestroyView(views.APIView):
    def delete(self, request, form_id=None, *args, **kwargs):
        auth_user = request.user

        form = forms_collection().find_one(
            {"_id": ObjectId(form_id), "created_by": str(auth_user.pk)}
        )

        if not form:
            return Response(
                {"detail": "Form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        field_collection().delete_many({"form_id": ObjectId(form_id)})

        forms_collection().delete_one({"_id": ObjectId(form_id)})

        return Response(
            {
                "message": "Form deleted successfully",
            },
            status=status.HTTP_200_OK,
        )


class FormListView(views.APIView):
    def get(self, request, *args, **kwargs):
        paginator = MongoPageNumberPagination(request)

        auth_user = request.user

        query = {"created_by": str(auth_user.pk)}

        results, count, total_page = paginator.paginate(
            collection=forms_collection(),
            query=query,
            sort=("created_at", -1),
        )

        for doc in results:
            doc["id"] = str(doc.pop("_id"))

        return Response(paginator.get_paginated_response(results, count, total_page))


# Fields
class FieldCreateView(views.APIView):
    def post(self, request, form_id=None, *args, **kwargs):
        auth_user = request.user

        form = forms_collection().find_one(
            {"_id": ObjectId(form_id), "created_by": str(auth_user.pk)}
        )

        if not form:
            return Response(
                {"detail": "Form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = FormFieldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_datetime = timezone.now()
        validated_data: dict = serializer.validated_data

        last_field = field_collection().find_one(
            {"form_id": ObjectId(form_id)},
            sort=[("order", -1)],
            projection={"order": 1}
        )

        next_order = (last_field.get("order", 0) + 1) if last_field else 1

        result = field_collection().insert_one(
            {
                **validated_data,
                "form_id": ObjectId(form_id),
                "created_by": str(auth_user.pk),
                "created_at": current_datetime,
                "updated_at": current_datetime,
                "order": next_order
            }
        )

        field = field_collection().find_one({"_id": result.inserted_id})
        field["id"] = str(field.pop("_id"))
        field["form_id"] = str(field.pop("form_id"))

        return Response(
            {"message": "Field created successfully", "field": field},
            status=status.HTTP_201_CREATED,
        )


class FormFieldListView(views.APIView):
    def get(self, request, form_id=None, *args, **kwargs):
        paginator = MongoPageNumberPagination(request)
        query = {"form_id": ObjectId(form_id)}

        results, count, total_page = paginator.paginate(
            collection=field_collection(),
            query=query,
            sort=("created_at", -1),
        )

        for doc in results:
            doc["id"] = str(doc.pop("_id"))
            doc["form_id"] = str(doc.pop("form_id")) if doc.get("form_id") else None

        return Response(paginator.get_paginated_response(results, count, total_page))


class FormFieldUpdateView(views.APIView):
    def patch(self, request, field_id=None, *args, **kwargs):
        field = field_collection().find_one({"_id": ObjectId(field_id)})

        if not field:
            return Response(
                {"detail": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = FormFieldSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        update_data = serializer.validated_data

        updated_field = field_collection().find_one_and_update(
            {"_id": ObjectId(field_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )

        updated_field["id"] = str(updated_field.pop("_id"))
        updated_field["form_id"] = str(updated_field.get("form_id"))

        return Response(
            {
                "message": "Field updated successfully",
                "field": updated_field,
            }
        )


class FieldDestroyView(views.APIView):
    def delete(self, request, field_id=None, *args, **kwargs):
        auth_user = request.user

        field = field_collection().find_one(
            {"_id": ObjectId(field_id), "created_by": str(auth_user.pk)}
        )

        if not field:
            return Response(
                {"detail": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )

        field_collection().delete_one({"_id": ObjectId(field_id)})

        return Response(
            {
                "message": "Field deleted successfully",
            },
            status=status.HTTP_200_OK,
        )


class UpdateFieldIndexView(views.APIView):
    def post(self, request, *args, **kwargs):
        auth_user = request.user

        serializer = UpdateFieldOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        fields = serializer.validated_data["fields"]
        current_datetime = timezone.now()

        operations = []

        for item in fields:
            operations.append(
                UpdateOne(
                    {
                        "_id": ObjectId(item["id"]),
                        "created_by": str(auth_user.pk),
                    },
                    {
                        "$set": {
                            "order": item["order"],
                            "updated_at": current_datetime,
                        }
                    }
                )
            )

        if operations:
            result = field_collection().bulk_write(operations)

            return Response(
                {
                    "message": "Field order updated successfully",
                    "modified": result.modified_count,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "No updates performed"},
            status=status.HTTP_400_BAD_REQUEST,
        )
