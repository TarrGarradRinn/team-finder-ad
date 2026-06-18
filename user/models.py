import random
from io import BytesIO

from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    AVATAR_COLORS = [
        (255, 107, 107),
        (78, 205, 196),
        (69, 183, 209),
        (150, 206, 180),
        (255, 234, 167),
        (221, 160, 221),
        (255, 138, 92),
        (162, 155, 254),
        (253, 121, 168),
        (0, 206, 201),
        (253, 203, 110),
        (108, 92, 231),
        (0, 184, 148),
        (225, 112, 85),
        (9, 132, 227),
    ]

    email = models.EmailField(
        unique=True,
        verbose_name="Почта"
    )
    name = models.CharField(
        max_length=124,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=124,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Аватар')
    phone = models.CharField(
        max_length=12,
        verbose_name='Телефон')
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на GitHub')
    about = models.TextField(
        max_length=256,
        blank=True,
        verbose_name='О себе')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        color = random.choice(self.AVATAR_COLORS)
        size = (200, 200)
        image = Image.new('RGB', size, color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text = self.name[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        processed_email = self.email.replace('@', '_at_').replace('.', '_dot_')
        return ContentFile(
            buffer.getvalue(),
            name=f'avatar_{processed_email}.png'
        )
