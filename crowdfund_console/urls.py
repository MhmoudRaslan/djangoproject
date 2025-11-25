from django.contrib import admin
from django.urls import path, include
from projects import views as project_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", project_views.ProjectListView.as_view(), name="project_list"),
    path("register/", project_views.register, name="register"),
    path("login/", project_views.login_view, name="login"),
    path("logout/", project_views.logout_view, name="logout"),
    path("projects/", include("projects.urls")),  # <-- this includes all projects/* paths
]
