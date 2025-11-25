from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
import datetime
from django.utils import timezone

from .models import User, Project, Donation
from .forms import RegistrationForm, ProjectForm, DonationForm
from crowdfund_console.tokens import account_activation_token


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  
            user.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect("project_list")
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect("register")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        if not email or not password:
            messages.error(request, "Please provide email and password.")
            return render(request, "login.html")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")

        if not user.is_active:
            messages.error(request, "Account not activated. Check your email.")
            return render(request, "login.html")

        if not user.check_password(password):
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html")

    
        backend = settings.AUTHENTICATION_BACKENDS[0]
        user.backend = backend
        login(request, user)
        return redirect("project_list")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("project_list")


@login_required(login_url='login')
def my_projects(request):
    projects = Project.objects.filter(creator=request.user)
    return render(request, "projects/my_projects.html", {"projects": projects})


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True).order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        date_str = self.request.GET.get("date", "").strip()

        if q:
            qs = qs.filter(title__icontains=q)

        if date_str:
            try:
                # expects YYYY-MM-DD
                d = datetime.date.fromisoformat(date_str)
                qs = qs.filter(start_date__lte=d, end_date__gte=d)
            except ValueError:
                # invalid date — return empty queryset or ignore filter
                qs = qs.none()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["date"] = self.request.GET.get("date", "")
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["donation_form"] = DonationForm()
        ctx["donations"] = self.object.donations.all()[:10]
        ctx["total_donated"] = self.object.total_donated()
        return ctx


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("project_list")
    login_url = "login"

    def form_valid(self, form):
        # set the owner field (not the `creator` property)
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    login_url = "login"

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.creator

    def get_success_url(self):
        return reverse_lazy("project_detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("project_list")
    login_url = "login"

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.creator


def donate_project(request, pk):
    project = get_object_or_404(Project, pk=pk, is_active=True)

    if request.user.is_authenticated and request.user == project.owner:
        messages.error(request, "You cannot donate to your own project.")
        return redirect("project_detail", pk=project.pk)

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.project = project
            if request.user.is_authenticated:
                donation.donor = request.user
                if not donation.donor_email:
                    donation.donor_email = request.user.email
                if not donation.donor_name:
                    donation.donor_name = f"{request.user.first_name} {request.user.last_name}".strip()
            donation.save()
            messages.success(request, f"Thank you for donating {donation.amount} EGP!")
            return redirect("project_detail", pk=project.pk)
        else:
            messages.error(request, "Please correct the donation form errors.")
            return render(request, "projects/project_detail.html", {
                "project": project,
                "donation_form": form,
                "donations": project.donations.all()[:10],
                "total_donated": project.total_donated(),
            })
    return redirect("project_detail", pk=project.pk)