__all__ = [
    'Setup'
]

import os

from pathlib import Path
from importlib import import_module
from typing import NoReturn

from web.core.exceptions import (
    ModuleMissingError,
    ApplicationNotFound
)
from web.core import (
    App,
    Settings
)
from web.core.application import Application


class Setup:
    __slots__ = (
        'path',
        'app_module',
        'settings',
        '__is_conf'
    )

    def __init__(
            self,
            path: Path = Path('.')
    ) -> None:
        self.path = path.absolute()
        self.settings = Settings()
        self.__is_conf = False

        os.chdir(str(self.path))
        self.app_module = (
            import_module(
                self.get_app_name()
            )
        )

    def _install_apps(self):
        apps = [
            path.name
            for path in self.path.iterdir()
        ]
        for app in self.settings.INSTALL_APPS:
            if app not in apps:
                raise ApplicationNotFound(app)

            module = import_module(app)
            self.settings.install_app(
                Application(
                    name=app,
                    urlpatterns=module.urls.urlpatterns
                )
            )

    def set_config(self) -> Settings | NoReturn:
        """
        The function sets the settings
        from 'your_application.settings'
        to the Settings object and run application.
        """
        module_type = type(self.app_module)
        try:
            __settings = getattr(
                self.app_module,
                'settings'
            )
            __settings.APP_NAME = self.get_app_name()
            if isinstance(__settings, module_type):
                for setting in self.settings.__slots__:
                    try:
                        setattr(
                            self.settings,
                            setting,
                            getattr(__settings, setting)
                        )
                    except AttributeError:
                        pass
            else:
                raise TypeError(
                    f"'{self.get_app_name()}.settings' "
                    f"must be a module."
                )

        except AttributeError as exc:
            if (isinstance(exc.obj, module_type)
                    and exc.obj.__name__ == self.get_app_name()):
                raise ModuleMissingError(
                    exc.obj.__name__,
                    exc.name
                ) from exc

            raise

        self._install_apps()
        self.__is_conf = True

        return self.settings

    def run(self):
        """
        Launching the application.
        """
        if not self.__is_conf:
            self.set_config()

        return App(self.settings).run()

    def get_app_name(self) -> str:
        return self.path.name

    def __str__(self):
        return str(self.settings)
