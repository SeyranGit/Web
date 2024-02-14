from typing import Union


def decode(string: Union[bytes, str]) -> str:
    if isinstance(string, bytes):
        return string.decode()

    return string


def encode(string: Union[bytes, str]) -> bytes:
    if isinstance(string, str):
        return string.encode()

    return string


def request_trace(request) -> None:
    print(
        f'\033[34m{request.addr} '
        f'\033[36m-> '
        f'\033[32m'
        f'"{request.method} '
        f'{request.original_path} '
        f'{request.http_version}" '
    )


def lunch_trace(app):
    host = (
        f'{app.settings.SERVER_HOST
        if app.settings.SERVER_PORT != '0.0.0.0'
        else 'localhost'}:{app.settings.SERVER_PORT}'
    )
    print(
        f'Launched {app.settings.APP_NAME} application:\n'
        f'  Running on the http://{host}.\n'
        f'  Installed applications:'
    )
    for app_name, app in app.settings.applications.items():
        print(f'    - {app_name}\n')
