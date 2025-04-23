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
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator, FileExtensionValidator


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
    name = models.CharField(max_length=60, blank=False, null=False, validators=[
            MinLengthValidator(2, "El nombre debe tener al menos 2 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message="El nombre solo puede contener letras y espacios"
            )
        ])
    surnames = models.CharField(max_length=80, blank=False, null=False, validators=[
            MinLengthValidator(2, "Los apellidos deben tener al menos 2 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$',
                message="Los apellidos solo pueden contener letras y espacios"
            )
        ])
    email = models.EmailField(unique=True, blank=False, null=False, validators=[
            EmailValidator(message="Ingrese un correo electrónico válido")
        ],
        error_messages={
            'unique': 'Ya existe un usuario con este correo electrónico'
        })
    token = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=False, null=False, default="", validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="El número de teléfono debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos."
            )
        ])
    username = models.CharField(max_length=45, blank=False, null=False, unique=True, validators=[
            MinLengthValidator(3, "El nombre de usuario debe tener al menos 3 caracteres"),
            RegexValidator(
                regex=r'^[a-zA-Z][a-zA-Z0-9_-]*$',
                message="El nombre de usuario debe comenzar con una letra y solo puede contener letras, números, guiones y guiones bajos"
            )
        ],
        error_messages={
            'unique': 'Este nombre de usuario ya está en uso'
        })
    photo= models.ImageField(upload_to="user", default="default.png", blank=False, null=False, validators=[
        FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
            message="Solo se permiten archivos de imagen en formato JPG, JPEG, PNG o GIF"
        ),
    ])
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.BooleanField(default=True, blank=False, null=False)
    join_date = models.DateTimeField(default=now, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    is_staff = models.BooleanField(default=False, blank=False, null=False)

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
    name = models.CharField(max_length=45, blank=False, null=False, unique=True, validators=[
            MinLengthValidator(2, "El nombre del rol debe tener al menos 2 caracteres")
        ])
    def __str__(self):
        return self.name

    class Meta:
        db_table = "role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
