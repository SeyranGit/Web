__all__ = [
    'matching',
    'get_app',
    'not_found',
    'App'
]

import sys
import traceback
import asyncio

from uvicorn.lifespan.on import (
    LifespanSendMessage,
    LifespanReceiveMessage
)
from typing import (
    Callable,
    Sequence,
    Awaitable,
    Coroutine,
    Any,
    Union
)
from web.http import (
    HttpRequest,
    HttpResponse,
    HTTP_STATUS_404,
    HTTP_STATUS_200,
    HTTP_STATUS_301
)
from web.core.excaptions import (
    ApplicationNotInit,
    InvalidReturnType
)
from web.core.uvc import (
    uvicorn_response,
    uvc_exc
)
from web.core.application import (
    Application,
    View
)
from web.core import Settings
from web.core.urlmatch import pattern_matching
from web.server import run_server
from web.utils import lunch_trace

UvicornSendMethod = Callable[
    [LifespanSendMessage],
    Coroutine[Any, Any, None]
]
UvicornReceiveMethod = Callable[
    [],
    Coroutine[Any, Any, LifespanReceiveMessage]
]


def exc_handler(coro):
    """
    A decorator that allows you to handle
    exceptions raised inside the view and
    transmits trace information to the client,
    provided that DEBUG=True.
    """

    async def _coro(*args, **kwargs):
        try:
            return (
                await coro(*args, **kwargs)
            )
        except Exception as exc:
            _traceback = traceback.format_exc()
            app = get_app()
            if app.settings.DEBUG:
                sys.stderr.write(_traceback)
                match app.server_type:
                    case 'std':
                        return HttpResponse(
                            status=HTTP_STATUS_404,
                            body=_traceback.encode()
                        ).as_http()

                    case 'uvicorn':
                        return await uvc_exc(
                            _traceback, app.send)

            asyncio.get_running_loop().stop()
            raise

    return _coro


class Asgi:
    def __init__(self, app: 'App') -> None:
        app.server_type = 'uvicorn'
        self.app = app

    async def body(self, receive: UvicornReceiveMethod) -> bytes:
        body = b''

        while True:
            message: LifespanReceiveMessage = await receive()
            chunk = message.get('body', b'')
            if isinstance(chunk, bytes):
                body += chunk

            if not message.get('more_body', False):
                break

        return body

    def uvicorn_response(self, response: HttpResponse) -> Sequence[dict]:
        """
        Generates an http response from
        an HttpResponse object that is
        understandable to the uvicorn server.
        """
        return [
            {
                'type': 'http.response.start',
                'status': response.status_code,
                'headers': iter(response.headers),
            },
            {
                'type': 'http.response.body',
                'body': response.body,
            }
        ]

    @exc_handler
    async def handle(
            self,
            scope: dict,
            receive: UvicornReceiveMethod,
            send: UvicornSendMethod
    ) -> None:
        """
        Method responsible for processing
        the http request, starting the
        router and returning an http response.
        """
        view, response = await (
            self.app.routing(
                HttpRequest(
                    scope,
                    await self.body(receive)
                )
            )
        )
        if not chack_response(response):
            response = not_found()

        await uvicorn_response(self.uvicorn_response(response), send)

    async def __call__(
            self,
            scope: dict,
            receive: UvicornReceiveMethod,
            send: UvicornSendMethod
    ) -> None:
        """
        Method called by the uvicorn
        server to process an http request.
        """
        if scope['type'] == 'http':
            self.app.send = send
            return (
                await self.handle(
                    scope, receive, send)
            )

        raise ValueError(
            "Web can only handle ASGI/HTTP "
            "connections, not %s." % scope["type"]
        )


class App:
    send: Union[UvicornSendMethod, None]
    settings: Settings
    server_type: str

    def __init__(self, settings: Settings) -> None:
        self.send = None
        self.settings = settings
        self.server_type = 'std'

        self.init()

    def init(self):
        """

        """
        global get_app

        def get_app():
            return self

    def run(self):
        """
        Displays tracing information about
        the application on the screen if the
        user specified the value TRACING=True
        in the configuration file and starts
        the server built into the framework.
        """
        if self.settings.TRACING:
            lunch_trace(self)

        return run_server(self, _run)

    def asgi(self) -> Asgi:
        return Asgi(self)

    def redirection(
            self,
            request: HttpRequest
    ) -> Union[HttpResponse, None]:
        """
        Returns an http redirect response
        if it is determined that the url
        address does not end with a "/" character.
        """
        if not request.path.endswith('/'):
            return (
                HttpResponse(
                    status=HTTP_STATUS_301,
                    headers={
                        'Location': f'{request.path}/',
                        'Connection': 'close'
                    }
                )
            )

    async def traversal_by_urlpatterns(
            self,
            root_url: str,
            app: Application,
            request: HttpRequest
    ) -> tuple[View | None, HttpResponse]:
        """
        Walk through the urlpatterns specified by
        the user in the urls file of the application
        created by him and, if the url address matches
        the pattern, launches the user-created view,
        passing it the HttpRequest object and returns
        HttpResponse and the presentation itself to the caller.
        """
        for url, view in app:
            url, vars = matching(
                merge_url(root_url, url),
                request.path
            )
            if vars or request.path == url:
                response = await view(request, **vars)
                return (
                    view,
                    not_found() if not chack_response(response) else response
                )

        return None, not_found()

    async def routing(
            self,
            request: HttpRequest
    ) -> tuple[View | None, HttpResponse]:
        """
        Iterates through ROOT_URLPATTERNS
        and runs the method "App.traversal_by_urlpatterns"
        to check if the url matches.
        """
        if redirection := self.redirection(request):
            return None, redirection

        # load_static(request)
        for root_url, app_name in self.settings.ROOT_URLPATTERNS:
            app: Application = (
                self
                .settings
                .applications
                .get(app_name)
            )
            return await self.traversal_by_urlpatterns(root_url, app, request)

        return None, not_found()


def matching(
        url: str,
        path: str
) -> tuple[str, dict]:
    return (
        url,
        pattern_matching(path, url, '/') or {}
    )


def merge_url(
        url_1: str,
        url_2: str
) -> str:
    return f'/{url_1}{url_2}'


def chack_response(response) -> bool:
    """
    if response is an instance of
    HttpResponse -> True otherwise -> False.
    """
    if not isinstance(response, HttpResponse):
        return False

    return True


def not_found() -> HttpResponse:
    """
    Returns HttpResponse not found.
    """
    return (
        HttpResponse(
            status=HTTP_STATUS_404,
            body=HTTP_STATUS_404[1].encode(),
            headers={
                'Content-Type': 'text/plain',
            }
        )
    )


def get_app():
    """
    After the application is initialized,
    returns an instance of the App class.
    Raises an exception "ApplicationNotInit"
    before initialization.
    """
    raise ApplicationNotInit(
        'Application is not initialized.')


@exc_handler
async def _run(
        app: App,
        request: bytes,
        client: tuple
) -> bytes:
    """
    A function passed to the server as an entry point.
    It is responsible for starting routing
    and returning an http response to the server.

    Note:
        Used when the server built
        into the framework is launched.
    """
    view, response = await app.routing(
        HttpRequest({
            'client': client
        }).set_http(request)
    )
    if isinstance(response, HttpResponse):
        return response.as_http()
    else:
        raise InvalidReturnType(
            str(HttpResponse), view.__name__)
