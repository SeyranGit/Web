__all__ = [
    'Application',
    'View'
]

from typing import (
    Callable,
    Sequence,
    Coroutine
)
from web.http import HttpResponse

View = Callable[
    ...,
    Coroutine[None, None, HttpResponse]
]


class Application:
    def __init__(
            self,
            name: str,
            urlpatterns: Sequence[tuple[str, View]]
    ) -> None:
        self.name = name
        self.urlpatterns = urlpatterns

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def __iter__(self):
        for url, view in self.urlpatterns:
            yield url, view
