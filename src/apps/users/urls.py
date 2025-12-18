from django.urls import path
from . import views


urlpatterns = [
    path("create", views.UserListCreateView.as_view()),
    path("list", views.UserListCreateView.as_view()),
    path("form/assign/<uuid:user_id>", views.AssignFormsView.as_view()),
]