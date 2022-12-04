import re

from django.core.exceptions import ValidationError


def username_validate(value):
    if value == 'me':
        raise ValidationError(
            f'Нельзя использовать username: {value} '
        )
    if re.findall(r'[^\w@.+-]+', value):
        value_re = re.sub(r'[\w@.+-]+', '', value, flags=re.UNICODE)
        value_re_single_sample = set(value_re)
        raise ValidationError(
            (
                f'Некорректное имя Пользователя: {value}! '
                f'Недопустимые символы: {value_re_single_sample} !! '
                'Имя пользователя может содержать только:'
                'Буквы, цифры, и символы: @/./+/-/_'
            )
        )
    return value
