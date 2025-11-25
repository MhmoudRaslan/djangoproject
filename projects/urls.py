from django.contrib import admin
from django.urls import path
from projects import views as project_views
from . import views  # لو عندك views للتسجيل/تسجيل الدخول هنا

urlpatterns = [

    # Project URLs
    path('', project_views.ProjectListView.as_view(), name='project_list'),
    path('projects/mine/', project_views.my_projects, name='my_projects'),
    path('projects/create/', project_views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', project_views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', project_views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', project_views.ProjectDeleteView.as_view(), name='project_delete'),
]
