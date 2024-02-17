__all__ = [
    'HttpRequest',
    'get_cookies',
    'get_headers'
]

from typing import (
    Iterable,
    Generator,
    AnyStr,
    Self,
    NoReturn,
    Union
)
from web.http.exceptions import (
    EmptyHttp,
    HttpSyntaxError
)
from web.http.base import (
    BaseHttp,
    WebDict
)

ParsedHttp = tuple[
    list[str],
    Generator[tuple[bytes, bytes], None, None],
    bytes
]


class HttpRequest(BaseHttp):
    __slots__ = (
        'method',
        'path',
        'headers',
        'http_version',
        'client',
        'scheme',
        'query_string',
        'raw_path',
        'root_path',
        'body',
        'payload',
        'cookies',
        'raw_http'
    )

    raw_http: bytes
    payload: dict
    body: bytes
    http_version: Union[str, None]
    client: Union[tuple, None]
    scheme: str
    method: str
    root_path: str
    path: str
    raw_path: bytes
    query_string: str
    headers: WebDict
    cookies: WebDict

    def __init__(
            self,
            scope: dict | None = None,
            body: bytes = b''
    ) -> None:
        if not isinstance(body, bytes):
            raise TypeError(
                f"'body' must be of type "
                f"bytes not {type(body)}"
            )

        if not isinstance(scope, dict):
            scope = {}

        self.payload = {}
        self.body = body
        self.http_version = scope.get('http_version')
        self.client = scope.get('client')
        self.scheme = scope.get('scheme', 'http')
        self.method = scope.get('method', '')
        self.root_path = scope.get('root_path', '')
        self.path = scope.get('path', '')
        self.raw_path = scope.get('raw_path', b'')
        self.query_string = scope.get('query_string', '')

        self.headers = get_headers(scope.get('headers', []))
        self.cookies = get_cookies(self.headers.get('cookie', ''))

        self.set_payload()

    def set_payload(self) -> None:
        if self.query_string:
            self.payload.update(
                self.parse_query_string()
            )

    @staticmethod
    def check_http(http):
        if not http:
            raise EmptyHttp()
        if not isinstance(http, bytes):
            raise TypeError()

        return http

    def set_http(self, http: bytes) -> Self:
        (
            (
                self.method,
                self.path,
                http_version
            ),
            _headers,
            self.body
        ) = self.parse(http)

        self.raw_http = http
        self.http_version = http_version.split('/')[1]
        self.headers = get_headers(_headers)
        self.cookies = get_cookies(
            self.headers.get('cookie', '')
        )
        if '?' in self.path:
            index = self.path.index('?')
            self.query_string = self.path[index + 1:]
            self.path = self.path[:index]

            self.set_payload()

        return self

    @staticmethod
    def get_headers(
            headers: list[bytes]
    ) -> Generator[tuple[bytes, bytes], None, None]:
        """
        A generator that processes a list
        of http headers and at each iteration produces
        a tuple from the header name and its value.
        """
        for header in headers:
            processed_header: list[bytes] = (
                header
                .replace(b': ', b':')
                .split(b':')
            )
            if processed_header:
                yield processed_header[0], processed_header[1]

    @classmethod
    def parse(cls, raw_http: bytes) -> ParsedHttp | NoReturn:
        """
        Parses an http request sent as
        argument and returns a tuple containing
        HTTP request in processed form.
        """
        http: list[bytes] = raw_http.split(cls.ln * 2)
        if len(http) != 2:
            raise HttpSyntaxError()

        content: bytes = http[1]
        headers: list[bytes] = (
            http[0]
            .replace(cls.ln, b'\n')
            .split(b'\n')
        )
        first_line: list[str] = headers.pop(0).decode().split()

        return first_line, cls.get_headers(headers), content

    def parse_query_string(self) -> dict:
        """
        The function parses the query string
        and returns the processed dictionary.
        """
        return {
            payload[0]: payload[1]
            for _payload in (
                self
                .query_string
                .split('&') if isinstance(self.query_string, str) else []
            ) if len(payload := _payload.split('=')) == 2
        }

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__} '
            f'{self.method}>'
        )


def get_headers(
        headers: Iterable[
            tuple[AnyStr, AnyStr]
        ]
) -> WebDict:
    """
    Converts the "headers" argument
    to the WebDict class.
    """
    return WebDict({
        key: value
        for key, value in headers
    })


def get_cookies(cookies: str) -> WebDict:
    """
    Parses cookies and converts
    them to WebDict class.
    """
    w_dict = WebDict()
    _cookies: list[str] = (
        cookies
        .replace(' ', '')
        .split(';')
    )
    for cookie in _cookies:
        if cookie and cookie.count('=') == 1:
            key, value = cookie.split('=')
            w_dict[key] = value

    return w_dict
