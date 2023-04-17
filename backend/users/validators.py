import re

from rest_framework import serializers


def validate_username(value):
    USERNAME_ME = 'Нельзя использовать "me" в качестве username'
    USERNAME_EMPTY = 'Поле "username" не должно быть пустым'
    if value == 'me' or '':
        invalid_username = USERNAME_ME if (
            value == 'me') else USERNAME_EMPTY
        raise serializers.ValidationError(detail=[invalid_username])
    result = re.findall(r'[^\w.@+-]', value)
    if result:
        raise serializers.ValidationError(
            f'Некорректные символы в username:'
            f' `{"`, `".join(set(result))}`.'
        )
    return value
