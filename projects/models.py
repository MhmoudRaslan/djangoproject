from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

############################################
# CUSTOM USER MODEL (Email Login)
############################################
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    mobile_phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(\+201|01)[0-5][0-9]{8}$",
                message="Enter a valid Egyptian mobile number (e.g., 010xxxxxxxx)",
            )
        ],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


############################################
# PROJECT MODEL
############################################
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    details = models.TextField()
    target_amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10_000_000),
        ]
    )
    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before or equal to end date.")

        if self.end_date < timezone.now().date():
            raise ValidationError("End date cannot be in the past.")

    def __str__(self):
        return self.title
