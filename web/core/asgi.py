from pathlib import Path

from web import Setup
from web.core import App

path = Path('.').absolute()


def asgi_app(path: Path = path):
    setup = Setup(path)
    return App(
        setup.set_config()
    ).asgi()
