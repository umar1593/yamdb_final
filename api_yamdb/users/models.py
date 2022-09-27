from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )

    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(
        blank=True,
    )
    role = models.TextField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.TextField()

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN
