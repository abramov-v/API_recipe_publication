from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
        blank=False,
        verbose_name='Адрес электронной почты',
        help_text='Введите Ваш адрес электронной почты',
    )
    username = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        unique=True,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит запрещенные символы'
            )
        ],
        verbose_name='Имя пользователя',
        help_text='Введите ваше Имя пользователя',
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        blank=False,
        verbose_name='Имя',
        help_text='Введите ваше Имя',
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_USER_FIELDS,
        blank=False,
        verbose_name='Фамилия',
        help_text='Введите ваше Фамилию',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.username} -> {self.email}'


class Subscription(models.Model):
    """Модель подписки пользователей."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписки',
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчики',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
