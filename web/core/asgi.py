__all__ = [
    'asgi_app'
]

from pathlib import Path

from web import Setup
from web.core import App

path = Path('.').absolute()


def asgi_app(path: Path = path):
    """
    Configures the project and returns asgi.
    """
    setup = Setup(path)
    return App(
        setup.set_config()
    ).asgi()
