__all__ = [
    'HttpResponse'
]

from web.http import (
    BaseHttp,
    HttpStatusType,
    WebDict
)


def enc(obj: str, encoding: str = 'UTF-8') -> bytes:
    return obj.encode(encoding)


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

    def as_http(self) -> bytes:
        data = {
            b'http_version': enc(self.http_version),
            b'status_code': enc(str(self.status_code)),
            b'status': enc(self.status),
            b'content': self.body,
            b'ln': self.ln
        }
        http = (b'%(http_version)s '
                b'%(status_code)s '
                b'%(status)s%(ln)s') % data

        for key, value in self.headers:
            http += b'%(key)s: %(value)s%(ln)s' % {
                b'key': enc(key),
                b'value': enc(value),
                b'ln': self.ln
            }
        else:
            http += b'%(ln)s%(content)s' % data

        return http
