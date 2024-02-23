from abc import abstractmethod
from typing import (
    TypedDict,
    Unpack,
    Coroutine
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
    @abstractmethod
    async def view(
            self,
            request: HttpRequest,
            **kwargs: Unpack[DynamicPath]
    ) -> HttpResponse:
        raise NotImplementedError(
            'view method is not defined.'
        )

    def as_view(self):
        try:
            if not isinstance(self.view, Coroutine):
                raise TypeError(
                    "The 'view' method must "
                    "be of coroutine type."
                )

            return self.view

        except AttributeError as exc:
            raise ViewNotFoundError(self) from exc
