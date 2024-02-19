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
from web.utils import to_correct
from web.core.application import Application
from web.core.statics import get_all_statics


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

    def _install_apps(self) -> None:
        """
        Installs applications in the
        list of installed applications.
        If the application is not found,
        a ApplicationNotFound exception is raised.
        """
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

    def _install_static(self):
        """
        Iterates through the STATIC_FILE_DIRS
        dictionary from your_application.settings
        and updates the statics files dictionary
        (web.core.settings.Settings.statics).
        """
        sfd_items = self.settings.STATIC_FILE_DIRS.items()
        for app_name, directories in sfd_items:
            for root_url, catalog, media_types in directories:
                self.settings.statics.update(
                    get_all_statics(
                        root_url=to_correct(root_url),
                        root_path=(app_name + to_correct(catalog)),
                        media_types=media_types
                    )
                )

    def set_config(self) -> Settings | NoReturn:
        """
        The function sets the settings
        from 'your_application.settings'
        to the web.core.Settings object and run application.
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
        self._install_static()

        self.settings.check()
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
        """
        Returns the application name.
        """
        return self.path.name

    def __str__(self):
        return str(self.settings)
