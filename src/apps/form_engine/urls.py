from django.urls import path
from . import views

urlpatterns = [
    path("list", views.FormListView.as_view()),
    path("create", views.FormCreateView.as_view()),
    path("update/<str:form_id>", views.FormUpdateView.as_view()),
    path("destroy/<str:form_id>", views.FormDestroyView.as_view()),

    path("fields/update-order", views.UpdateFieldIndexView.as_view()),
    path("fields/<str:form_id>", views.FormFieldListView.as_view()),
    path("fields/create/<str:form_id>", views.FieldCreateView.as_view()),
    path("fields/update/<str:field_id>", views.FormFieldUpdateView.as_view()),
    path("fields/destroy/<str:field_id>", views.FieldDestroyView.as_view()),

    path("submissions/create/<str:form_id>", views.FormSubmissionView.as_view()),
    path("submissions", views.FormSubmissionListView.as_view()),
]