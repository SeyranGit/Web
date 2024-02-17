from typing import Union
from os.path import splitext as _splitext


def splitext(path):
    if path.endswith('/'):
        return _splitext(path[:-1])

    return _splitext(path)


def to_sep_corrent(url: str) -> str:
    return url.replace('//', '/')


def merge_url(url_1: str, url_2: str) -> str:
    return to_sep_corrent(f'{url_1}{url_2}')


def to_correct(url: str) -> str:
    if not url.startswith('/'):
        url = f'/{url}'
    if not url.endswith('/'):
        url = f'{url}/'

    return url


def decode(string: Union[bytes, str]) -> str:
    if isinstance(string, bytes):
        return string.decode()

    return string


def encode(string: Union[bytes, str]) -> bytes:
    if isinstance(string, str):
        return string.encode()

    return string


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
    host = (
        f'{app.settings.SERVER_HOST
        if app.settings.SERVER_PORT != '0.0.0.0'
        else 'localhost'}:{app.settings.SERVER_PORT}'
    )
    print(f'Launched {app.settings.APP_NAME} application:')
    print(f'  Running on the http://{host}.')
    print(f'  Installed applications:')
    print('    -\n' if len(app.settings.applications.items()) == 0 else '', end='')

    for app_name, app in app.settings.applications.items():
        print(f'    - {app_name}')
