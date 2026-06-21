from django.db import models
from django.conf import settings
from .constants import (
    MAX_LENGTH_SKILL_NAME,
    MAX_LENGTH_PROJECT_NAME,
    MAX_LENGTH_STATUS,
    STATUS_OPEN,
    STATUS_CLOSED,
    STATUS_DEFAULT,
    STATUS_CHOICES
)


class Skill(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_SKILL_NAME,
        unique=True,
        verbose_name="Название навыка"
    )

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Project(models.Model):

    name = models.CharField(
        max_length=MAX_LENGTH_PROJECT_NAME,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='owned_projects',
        on_delete=models.CASCADE,
        verbose_name="Владелец"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    github_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на GitHub"
    )
    status = models.CharField(
        max_length=MAX_LENGTH_STATUS,
        choices=STATUS_CHOICES,
        default=STATUS_DEFAULT,
        verbose_name="Статус"
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True,
        verbose_name='Участники'
    )
    skills = models.ManyToManyField(
        Skill,
        related_name='projects',
        blank=True,
        verbose_name='Навыки, необходимые проекту'
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name
