# base http file.
from typing import (
    Generator,
    Union,
    Any
)
from urllib.parse import unquote
from collections import UserDict

HTTP_STATUS_100 = (100, 'Continue')
HTTP_STATUS_101 = (101, 'Switching Protocols')
HTTP_STATUS_102 = (102, 'Processing')
HTTP_STATUS_103 = (103, 'Early Hints')
HTTP_STATUS_200 = (200, 'OK')
HTTP_STATUS_201 = (201, 'Created')
HTTP_STATUS_202 = (202, 'Accepted')
HTTP_STATUS_203 = (203, 'Non-Authoritative Information')
HTTP_STATUS_204 = (204, 'No Content')
HTTP_STATUS_205 = (205, 'Reset Content')
HTTP_STATUS_206 = (206, 'Partial Content')
HTTP_STATUS_207 = (207, 'Multi-Status')
HTTP_STATUS_208 = (208, 'Already Reported')
HTTP_STATUS_226 = (226, 'IM Used')
HTTP_STATUS_300 = (300, 'Multiple Choices')
HTTP_STATUS_301 = (301, 'Moved Permanently')
HTTP_STATUS_302 = (302, 'Found')
HTTP_STATUS_303 = (303, 'See Other')
HTTP_STATUS_304 = (304, 'Not Modified')
HTTP_STATUS_307 = (307, 'Temporary Redirect')
HTTP_STATUS_308 = (308, 'Permanent Redirect')
HTTP_STATUS_400 = (400, 'Bad Request')
HTTP_STATUS_401 = (401, 'Unauthorized')
HTTP_STATUS_402 = (402, 'Payment Required')
HTTP_STATUS_403 = (403, 'Forbidden')
HTTP_STATUS_404 = (404, 'Not Found')
HTTP_STATUS_405 = (405, 'Method Not Allowed')
HTTP_STATUS_406 = (406, 'Not Acceptable')
HTTP_STATUS_407 = (407, 'Proxy Authentication Required')
HTTP_STATUS_408 = (408, 'Request Timeout')
HTTP_STATUS_409 = (409, 'Conflict')
HTTP_STATUS_410 = (410, 'Gone')
HTTP_STATUS_411 = (411, 'Length Required')
HTTP_STATUS_412 = (412, 'Precondition Failed')
HTTP_STATUS_413 = (413, 'Content Too Large')
HTTP_STATUS_414 = (414, 'URI Too Long')
HTTP_STATUS_415 = (415, 'Unsupported Media Type')
HTTP_STATUS_416 = (416, 'Range Not Satisfiable')
HTTP_STATUS_417 = (417, 'Expectation Failed')
HTTP_STATUS_418 = (418, "I'm a teapot")
HTTP_STATUS_421 = (421, 'Misdirected Request')
HTTP_STATUS_422 = (422, 'Unprocessable Content')
HTTP_STATUS_423 = (423, 'Locked')
HTTP_STATUS_424 = (424, 'Failed Dependency')
HTTP_STATUS_425 = (425, 'Too Early')
HTTP_STATUS_426 = (426, 'Upgrade Required')
HTTP_STATUS_428 = (428, 'Precondition Required')
HTTP_STATUS_429 = (429, 'Too Many Requests')
HTTP_STATUS_431 = (431, 'Request Header Fields Too Large')
HTTP_STATUS_451 = (451, 'Unavailable For Legal Reasons')
HTTP_STATUS_500 = (500, 'Internal Server Error')
HTTP_STATUS_501 = (501, 'Not Implemented')
HTTP_STATUS_502 = (502, 'Bad Gateway')
HTTP_STATUS_503 = (503, 'Service Unavailable')
HTTP_STATUS_504 = (504, 'Gateway Timeout')
HTTP_STATUS_505 = (505, 'HTTP Version Not Supported')
HTTP_STATUS_506 = (506, 'Variant Also Negotiates')
HTTP_STATUS_507 = (507, 'Insufficient Storage')
HTTP_STATUS_508 = (508, 'Loop Detected')
HTTP_STATUS_510 = (510, 'Not Extended')
HTTP_STATUS_511 = (511, 'Network Authentication Required')

HttpStatusType = tuple[int, str]
KvType = Union[bytes, str]


class WebDict(UserDict):
    def __setitem__(
            self,
            key: KvType,
            value: KvType
    ) -> None:
        types = [bytes, str]
        if (type(key) in types
                and type(value) in types):

            super().__setitem__(
                unquote(key).lower(),
                (unquote(key), unquote(value))
            )

        else:
            raise TypeError(
                'key and value type can '
                'only be bytes and str.'
            )

    def get(self, key, default=None):
        return super().get(key.lower(), default)
    
    def __getitem__(self, item: Any) -> KvType:
        return super().__getitem__(item)[1]

    def __iter__(self) -> Generator[
        tuple[KvType, KvType],
        None, None
    ]:
        items = self.data.items()
        for key, value in items:
            yield value


class BaseHttp:
    __slots__ = ()

    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_TRACE = 'TRACE'
    METHOD_CONNECT = 'CONNECT'
    METHOD_DELETE = 'DELETE'
    METHOD_HEAD = 'HEAD'
    METHOD_OPTIONS = 'OPTIONS'
    METHOD_PATCH = 'PATCH'

    encoding = 'UTF-8'
    ln = '\r\n'.encode(encoding)
