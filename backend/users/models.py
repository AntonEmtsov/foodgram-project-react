from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram import settings

USER = 'user'
MODERATOR = 'moderator'
ADMINISTRATOR = 'admin'
ROLES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMINISTRATOR, 'Администратор'),
]


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=USER,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.FIRST_NAME_MAX_LENGTH,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH,
        blank=True,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='Единственность подписки',
                fields=['user', 'author'],
            ),
            models.CheckConstraint(
                name='Запрет на Самоподписку',
                check=~models.Q(user=models.F('author'))
            ),
        ]
