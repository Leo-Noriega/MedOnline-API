from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.db import models
from django.utils.timezone import now
from autoslug import AutoSlugField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=60, blank=True)
    surnames = models.CharField(max_length=80, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=16, blank=True)
    username = models.CharField(max_length=45, blank=True)
    photo = models.ImageField(upload_to="user", default="default.png")
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(
        "UserStatus", on_delete=models.SET_NULL, null=True, blank=True
    )

    join_date = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surnames", "username"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(models.Model):
    name = models.CharField(max_length=45, blank=True)
    slug = AutoSlugField(populate_from="name")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class UserStatus(models.Model):
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "user_status"
