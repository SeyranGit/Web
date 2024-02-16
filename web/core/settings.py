__all__ = [
    'Settings'
]

from web.core.application import Application
from web.core.exceptions import ApplicationNotFound


class Settings:
    """
    Class intended only for
    storing installed settings.
    """
    __slots__ = (
        'DEBUG',
        'TRACING',
        'SERVER_HOST',
        'SERVER_PORT',
        'INSTALL_APPS',
        'STATIC_FILE_DIRS',
        'ROOT_URLPATTERNS',
        'STOP_ON_EXCEPTION',
        'APP_NAME',
        'statics',
        'applications'
    )

    def __init__(self):
        self.DEBUG = True
        self.TRACING = True
        self.SERVER_HOST = 'localhost'
        self.SERVER_PORT = 8000
        self.INSTALL_APPS = []
        self.STATIC_FILE_DIRS = {}
        self.ROOT_URLPATTERNS = []
        self.STOP_ON_EXCEPTION = True
        self.APP_NAME = None

        self.statics = {}
        self.applications = {}

    def install_app(self, app: Application) -> None:
        self.applications[app.name] = app

    def check(self):
        for url, app_name in self.ROOT_URLPATTERNS:
            if app_name not in self.INSTALL_APPS:
                raise ApplicationNotFound(app_name)

    def __str__(self):
        return (
            f'Settings for {self.APP_NAME} {{\n'
            f'   DEBUG={self.DEBUG}\n'
            f'   TRACING={self.TRACING}\n'
            f'   SERVER_HOST={self.SERVER_HOST}\n'
            f'   SERVER_PORT={self.SERVER_PORT}\n'
            f'   INSTALL_APPS={self.INSTALL_APPS}\n'
            f'   STATIC_FILE_DIRS={self.STATIC_FILE_DIRS}\n}}\n'
        )
