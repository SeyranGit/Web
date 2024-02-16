__all__ = [
    'ModuleMissingError',
    'ApplicationNotFound',
    'ApplicationNotInit',
    'InvalidReturnType',
    'StaticNotFound',
    'ServerTypeError'
]


class ModuleMissingError(Exception):
    """
    An exception that should be
    thrown if the required module
    is not present.
    """

    def __init__(
            self,
            module: str,
            attr: str
    ) -> None:
        self.module = module
        self.attr = attr

    def __str__(self) -> str:
        return f"Module '{self.module}' must contain module '{self.attr}'."


class ApplicationNotFound(Exception):
    def __init__(self, app_name):
        super().__init__(
            f'Application {app_name} not found!'
        )


class ApplicationNotInit(Exception):
    def __init__(self, trace):
        super().__init__(trace)


class InvalidReturnType(Exception):
    def __init__(self, return_type, view_name):
        super().__init__(
            f'Return type of the view '
            f"'{view_name}' must be {return_type}."
        )


class StaticNotFound(Exception):
    def __init__(self):
        super().__init__('Static file not found.')


class ServerTypeError(Exception):
    def __init__(self, server_type):
        super().__init__(
            f"wrong server type {server_type}. "
            f"Only available 'uvicorn' and 'std'."
        )
