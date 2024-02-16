__all__ = [
    'get_static',
    'load_static'
]

from web.core.exceptions import StaticNotFound
from web.utils import to_correct

get_app = None


def load_static(path):
    return open(path, 'rb').read()


def get_static(url: str) -> bytes:
    """
    If there is a static file,
    returns its contents read in byte mode,
    otherwise raises a StaticNotFound exception.
    """
    global get_app

    if not get_app:
        from web.core import get_app

    app = get_app()
    path = app.settings.statics.get(to_correct(url))
    if not path:
        raise StaticNotFound()

    return load_static(path)
