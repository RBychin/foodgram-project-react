from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='email',
        unique=True,
        blank=False,
        null=False)
    first_name = models.CharField(
        verbose_name='Имя',
        blank=False,
        null=False
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['id']

    def has_module_perms(self, app_label):
        return self.is_staff
