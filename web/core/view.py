from abc import abstractmethod
from typing import (
    TypedDict,
    Unpack,
    Coroutine,
    Callable
)
from web.http import (
    HttpRequest,
    HttpResponse
)
from web.core.exceptions import ViewNotFoundError


class DynamicPath(TypedDict):
    var_name: str
    path: str


class View:
    __slots__ = ()
    _view = None
    __attrs = (
        '__module__',
        '__dict__',
        '__weakref__',
        'as_view'
    )

    # @abstractmethod
    # async def view(
    #         self,
    #         request: HttpRequest,
    #         **kwargs: Unpack[DynamicPath]
    # ) -> HttpResponse:
    #     raise NotImplementedError(
    #         'view method is not defined.'
    #     )

<<<<<<< HEAD
    def as_view(self):
        self_attrs = set(dir(self))
=======
    def as_view(self) -> Callable[..., Coroutine[None, None, HttpResponse]]:
        try:
            return self.view
>>>>>>> 99d3f0cf72f2898cd00e7dd4bef7a03de3001f53

        user_defined_attrs = (
                self_attrs - set(dir(object)) -
                set()
        )
        print(user_defined_attrs)

        user_defined_methods = [
            attr for attr in user_defined_attrs
            if isinstance(getattr(self, attr), Callable)
        ]
        if user_defined_methods:
            return getattr(self, user_defined_methods[0])

        raise ViewNotFoundError(self)
