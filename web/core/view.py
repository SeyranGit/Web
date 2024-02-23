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

    def as_view(self) -> Callable[
        ...,
        Coroutine[None, None, HttpResponse]
    ]:
        return self.view
