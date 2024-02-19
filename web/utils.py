__all__ = [
    'ascii_quote',
    'concat',
    'splitext',
    'to_sep_correct',
    'merge_url',
    'to_correct',
    'lunch_trace',
    'request_trace',
    'encode',
    'decode'
]

from typing import (
    Union,
    TypeVar,
    Iterable,
)
from os.path import splitext as _splitext
from urllib.parse import quote


def ascii_quote(
        string: Union[str, bytes]
) -> Union[str, bytes]:
    return (
        quote(string)
        if not string.isascii() else string
    )


def concat(
        _list: Iterable[Union[bytes, str]]
) -> Union[bytes, str]:
    content = None
    for item in _list:
        if content is None:
            content = type(item)()

        if type(content) is not type(item):
            raise TypeError(
                'concat accepts an iterable object '
                'that returns values of only one type.'
            )

        content += item

    return content or b''


def splitext(path):
    if path.endswith('/'):
        return _splitext(path[:-1])

    return _splitext(path)


def to_sep_correct(url: str) -> str:
    return url.replace('//', '/')


def merge_url(url_1: str, url_2: str) -> str:
    return to_sep_correct(f'{url_1}{url_2}')


def to_correct(url: str) -> str:
    if not url.startswith('/'):
        url = f'/{url}'
    if not url.endswith('/'):
        url = f'{url}/'

    return url


T = TypeVar('T')


def decode[T](
        obj: T,
        encoding: str = 'UTF-8'
) -> Union[T, str]:
    if isinstance(obj, bytes):
        return obj.decode(encoding)

    return obj


def encode[T](
        obj: T,
        encoding: str = 'UTF-8'
) -> Union[T, bytes]:
    if isinstance(obj, str):
        return obj.encode(encoding)

    return obj


def request_trace(request, app) -> None:
    if (app.settings.TRACING
            and app.server_type != 'uvicorn'):
        print(
            f'\033[34m{request.client[0]} '
            f'\033[36m-> '
            f'\033[32m'
            f'"{request.method} '
            f'{request.path} '
            f'{request.http_version}" '
        )


def lunch_trace(app):
    _host = app.settings.SERVER_HOST
    _port = app.settings.SERVER_PORT

    host = f'{_host if _port != '0.0.0.0' else 'localhost'}:{_port}'

    print(f'Launched {app.settings.APP_NAME} application:')
    print(f'  Running on the http://{host}.')
    print(f'  Installed applications:')
    print('    -\n' if len(app.settings.applications.items()) == 0 else '', end='')

    for app_name, app in app.settings.applications.items():
        print(f'    - {app_name}')
