from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """User model for the project."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Email address',
        help_text='Enter your email address',
    )
    username = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Username contains forbidden characters'
            )
        ],
        verbose_name='Username',
        help_text='Enter your username',
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        verbose_name='Name',
        help_text='Enter your name',
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        verbose_name='Surname',
        help_text='Enter your surname',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.username} -> {self.email}'


class Subscription(models.Model):
    """Model for user subscriptions."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Subscriptions',
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Followers',
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} subscribed to {self.author}'
