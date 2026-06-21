import random
import uuid
from io import BytesIO

from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from .constants import (
    AVATAR_COLORS,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    MAX_LENGTH_ABOUT,
    MAX_LENGTH_NAME,
    MAX_LENGTH_PHONE,
    MAX_LENGTH_SURNAME,
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

    email = models.EmailField(
        unique=True,
        verbose_name="Почта"
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name="Имя",
    )
    surname = models.CharField(
        max_length=MAX_LENGTH_SURNAME,
        verbose_name="Фамилия",
    )
    avatar = models.ImageField(
        blank=True,
        upload_to='avatars/',
        verbose_name='Аватар')
    phone = models.CharField(
        blank=True,
        max_length=MAX_LENGTH_PHONE,
        verbose_name='Телефон')
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на GitHub')
    about = models.TextField(
        max_length=MAX_LENGTH_ABOUT,
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
            super().save(*args, **kwargs)
            avatar_file = self.generate_avatar()
            self.avatar.save(avatar_file.name, avatar_file, save=True)
        else:
            super().save(*args, **kwargs)

    def generate_avatar(self):
        color = random.choice(AVATAR_COLORS)
        size = AVATAR_SIZE
        image = Image.new('RGB', size, color)
        draw = ImageDraw.Draw(image)

        text = self.name[0].upper()

        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf", size=120)
        except OSError:
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", size=120)
            except OSError:
                font = ImageFont.load_default(size=120)

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2 - bbox[0]
        y = (size[1] - text_height) // 2 - bbox[1]
        draw.text((x, y), text, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        avatar_name = f'avatar_{uuid.uuid5(uuid.NAMESPACE_DNS, self.email).hex}.png'
        return ContentFile(buffer.getvalue(), name=avatar_name)
