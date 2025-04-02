from autoslug import AutoSlugField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch.dispatcher import receiver
from django.utils.timezone import now


@receiver(user_logged_in)
def update_last_login(sender, user, **kwargs):
    user.last_login = now()
    user.save()


# == ROLES predeterminados entonrno de desarrollo ==
@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    roles = ["Admin", "Doctor", "Patient"]
    for role in roles:
        if not Role.objects.filter(name=role).exists():
            Role.objects.create(name=role)
            print(f"=== ROL {role} PARA DESARROLLO CREADO ===")


# == USERS predeterminados entonrno de desarrollo ==
# TODO: Borrar en producción
@receiver(post_migrate)
def create_defaullt_user(sender, **kwargs):
    if not CustomUser.objects.filter(email="admin@mail.com").exists():
        admin_role = Role.objects.get(name="Admin")
        CustomUser.objects.create_superuser(
            email="admin@mail.com",
            password="admin",
            name="Admin",
            surnames="Admin",
            username="admin",
            role=admin_role
        )
        print('=== USUARIO ADMIN PARA DESARROLLO CREADO ===')

    if not CustomUser.objects.filter(email="doctor@mail.com").exists():
        doctor_role = Role.objects.get(name="Doctor")
        CustomUser.objects.create_user(
            email="doctor@mail.com",
            password="doctor",
            name="Doctor",
            surnames="Doctor",
            username="doctor",
            role=doctor_role
        )
        print('=== USUARIO DOCTOR PARA DESARROLLO CREADO ===')

    if not CustomUser.objects.filter(email="user@mail.com").exists():
        user_role = Role.objects.get(name="Patient")
        CustomUser.objects.create_user(
            email="user@mail.com",
            password="user",
            name="User",
            surnames="User",
            username="user",
            role=user_role
        )
        print('=== USUARIO USER PARA DESARROLLO CREADO ===')


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
    photo= models.ImageField(upload_to="user", default="default.png")
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.BooleanField(default=True)
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
    def __str__(self):
        return self.name

    class Meta:
        db_table = "role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
