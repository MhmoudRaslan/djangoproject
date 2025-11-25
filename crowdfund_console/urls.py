from django.contrib import admin
from django.urls import path, include
from projects import views as project_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # User auth views
    path('register/', project_views.register, name='register'),
    path('activate/<uidb64>/<token>/', project_views.activate, name='activate'),
    path('login/', project_views.login_view, name='login'),
    path('logout/', project_views.logout_view, name='logout'),

    # Project URLs
    path('', project_views.ProjectListView.as_view(), name='project_list'),
    path('projects/mine/', project_views.my_projects, name='my_projects'),
    path('projects/create/', project_views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', project_views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', project_views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', project_views.ProjectDeleteView.as_view(), name='project_delete'),
]
