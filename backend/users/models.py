from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram import settings

from .validators import username_validate


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        validators=[username_validate],
        verbose_name='Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscribe(models.Model):
    following = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=["author", "following"],
                                    name="user_following"),
            models.CheckConstraint(
                check=~models.Q(author=models.F('following')),
                name='not_self_following_author'
            )
        ]

    def __str__(self):
        return f'{self.following} подписан на {self.author}'
