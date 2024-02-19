__all__ = [
    'HttpResponse'
]

from typing import Iterable

from web.http import (
    BaseHttp,
    HttpStatusType,
    WebDict
)
from web.utils import (
    concat,
    ascii_quote
)


def enc(t: tuple[str, str]) -> tuple[bytes, bytes]:
    return t[0].encode(), t[1].encode()


class HttpResponse(BaseHttp):
    __slots__ = (
        'status',
        'headers',
        'body',
        'http_version',
        'status_code'
    )

    http_version: str
    status_code: int
    status: str
    headers: WebDict
    body: bytes

    def __init__(
            self,
            status: HttpStatusType,
            headers: dict | None = None,
            body: bytes = b''
    ) -> None:
        if not isinstance(body, bytes):
            raise TypeError(
                f"'body' must be of type "
                f"bytes not {type(body)}"
            )

        self.http_version = 'HTTP/1.1'
        self.status_code = int(status[0])
        self.status = str(status[1])
        self.body = body
        self.headers = WebDict(headers)

    def _collect(
            self,
            _list: Iterable[tuple[str, str]],
    ) -> bytes:
        between = ': '
        return (
            result
            if isinstance(
                result := concat(
                    result.encode()
                    for key, value in _list
                    if isinstance(
                        result := concat((
                            ascii_quote(key),
                            between,
                            ascii_quote(value),
                            self.ln.decode()
                        )), str
                    )
                ), bytes)

            else result.encode()
        )

    def as_http(self) -> bytes:
        return (
            result
            if isinstance(
                result := concat(
                    (
                        (
                            f'{self.http_version} '
                            f'{self.status_code} '
                            f'{self.status}'
                            .encode()
                        ),
                        self.ln,
                        self._collect(self.headers),
                        self.ln,
                        self.body
                    )
                ), bytes
            )
            else result.encode()
        )
