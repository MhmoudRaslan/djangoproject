from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("mine/", views.my_projects, name="my_projects"),
    path("create/", views.ProjectCreateView.as_view(), name="project_create"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("<int:pk>/donate/", views.donate_project, name="project_donate"),
    path("<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project_edit"),
    path("<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project_delete"),
]
