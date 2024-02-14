class HttpParser(BaseHttp):
    __slots__ = (
        'GET',
        'POST',
        'addr',
        'cookies',
        'method',
        'path',
        'headers',
        'content',
        'unprocessed_http',
        'http_version',
        'original_path'
    )

    def __init__(self) -> None:
        self.GET = {}
        self.POST = {}

        self.method = None
        self.path = None
        self.original_path = None
        self.headers = WebDict()
        self.cookies = WebDict()
        self.content = None
        self.unprocessed_http = None
        self.http_version = None

    def __getitem__(self, attribute):
        return getattr(self, attribute)

    def __getattribute__(self, attribute):
        original = super().__getattribute__(attribute)
        if original and attribute in [
            'method',
            'path',
            'original_path',
            'http_version'
        ]:
            return (
                super()
                .__getattribute__(attribute)
                .decode(self.encoding)
            )

        return original

    def set_http(self, http: bytes):
        if not http:
            raise EmptyHttp

        def corrent_path(path: bytes):
            # доделать
            return path.replace(b'%20', b' ')

        self.unprocessed_http = http
        (
            (
                self.method,
                path,
                self.http_version
            ),
            headers,
            self.content
        ) = self._parse(http)
        (
            self.path,
            self.original_path,
            self.GET
        ) = self._path(corrent_path(path))

        if self.method == self.METHOD_POST:
            self.POST = self._form_parse(self.content)

        for header, value in headers:
            if header.decode(self.encoding) == 'Cookie':
                self.set_cookies(
                    value.decode(self.encoding))
            else:
                self.headers[header.decode(self.encoding)] = value

        return self

    def set_cookies(self, cookies):
        for cookie in (cookies
                .replace(' ', '')
                .split(';')
        ):
            name, value = cookie.split('=')
            self.cookies[name] = value

    @classmethod
    def _path(cls, path: bytes) -> list[bytes, bytes]:
        def abs(path: bytes) -> bytes:
            return path if path.endswith(b'/') else path + b'/'

        _: list[bytes] = path.split('?'.encode(cls.encoding))
        if len(_) == 2:
            path, payload = _
            return (
                path,  # abs
                path,
                cls._form_parse(payload)
            )
        if len(_) == 1:
            return _[0], _[0], {}

    @classmethod
    def _form_parse(cls, payload: bytes) -> dict[str, str]:
        return {
            payload[0].decode(cls.encoding):
                payload[1].decode(cls.encoding)

            for _payload in payload.split(
                '&'.encode(cls.encoding)
            ) if len(payload := _payload.split(
                '='.encode(cls.encoding))) == 2 and payload[0]
        }

    @classmethod
    def _parse(cls, http: bytes) -> HTTP:
        _, content = http.split(cls._ln * 2)
        first_line, *_ = _.split(cls._ln)
        return (
            first_line.split(),
            (
                (
                    header[0],
                    header[1]
                )
                for _header in _
                if (header := _header.split(': '.encode(cls.encoding)))
            ),
            content
        )