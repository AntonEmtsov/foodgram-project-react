from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram import settings

from .validators import username_validate

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
        validators=[username_validate],
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
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH,
    )

    @property
    def is_admin(self):
        return self.role == ADMINISTRATOR or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'


class Subscribe(models.Model):
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
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='Единственность подписки',
            ),
            models.CheckConstraint(
                name='Запрет на Самоподписку',
                check=~models.Q(user=models.F('author'))
            ),
        )

    def __str__(self):
        return (f'Пользователь: {self.user.username},'
                f' автор: {self.author.username}')
