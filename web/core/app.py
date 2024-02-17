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
    Coroutine,
    NoReturn,
    Union,
    Any
)
from web.http import (
    HttpRequest,
    HttpResponse,
    HTTP_STATUS_404,
    HTTP_STATUS_301,
    HTTP_STATUS_500,
    HttpStatusType
)
from web.core.exceptions import (
    ApplicationNotInit,
    InvalidReturnType,
    ServerTypeError
)
from web.core.uvc import (
    uvicorn_response,
    uvc_exc
)
from web.core.application import (
    Application,
    View
)
from web.utils import (
    lunch_trace,
    to_correct,
    merge_url,
    request_trace
)
from web.core.statics import Static
from web.core.urlmatch import pattern_matching
from web.server import run_server
from web.core import Settings

UvicornSendMethod = Callable[
    [Union[LifespanSendMessage, dict]],
    Coroutine[Any, Any, None]
]
UvicornReceiveMethod = Callable[
    [],
    Coroutine[Any, Any, LifespanReceiveMessage]
]


def get_app():
    """
    After the application is initialized,
    returns an instance of the App class.
    Raises an exception "ApplicationNotInit"
    before initialization.
    """
    if isinstance(App.instance, App):
        return App.instance

    raise ApplicationNotInit(
        'Application is not initialized.')


def stop_aloop():
    asyncio.get_running_loop().stop()


async def get_exception_response(
        app: 'App',
        status: HttpStatusType,
        _traceback: str
) -> Union[bytes, None, NoReturn]:
    match app.server_type:
        case 'std':
            return (
                HttpResponse(
                    status=status,
                    body=_traceback.encode()
                ).as_http()
            )

        case 'uvicorn':
            await uvc_exc(
                _traceback, status[0], app.send)
        case _:
            stop_aloop()
            raise ServerTypeError(app.server_type)

    return None


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
        except Exception:
            _traceback = traceback.format_exc()
            app = get_app()
            if app.settings.DEBUG:
                sys.stderr.write(_traceback)
                return (
                    await get_exception_response(
                        app, HTTP_STATUS_404, _traceback
                    )
                )

            if app.settings.STOP_ON_EXCEPTION:
                stop_aloop()
                raise
            else:
                return (
                    await get_exception_response(
                        app,
                        HTTP_STATUS_500,
                        HTTP_STATUS_500[1]
                    )
                )

    return _coro


class Asgi:
    def __init__(self, app: 'App') -> None:
        app.server_type = 'uvicorn'
        self.app = app

    @staticmethod
    async def get_body(receive: UvicornReceiveMethod) -> bytes:
        """
        Read and returns all body.
        """
        body = b''

        while True:
            message: LifespanReceiveMessage = await receive()
            chunk = message.get('body', b'')
            if isinstance(chunk, bytes):
                body += chunk

            if not message.get('more_body', False):
                break

        return body

    @staticmethod
    def uvicorn_response(response: HttpResponse) -> Sequence[dict]:
        """
        Generates a http response from
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
        router and returning a http response.
        """
        view, response = await (
            self.app.routing(
                HttpRequest(
                    scope,
                    await self.get_body(receive)
                )
            )
        )
        if not check_response(response):
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
        server to process a http request.
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
    instance = None

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
        Initializes the application.
        """
        App.instance = self

    def run(self):
        """
        Displays tracing information about
        the application on the screen if the
        user specified the value TRACING=True
        in the configuration file and starts
        the server built into the framework.
        """
        lunch_trace(self)
        return run_server(self, _run)

    def asgi(self) -> Asgi:
        return Asgi(self)

    @staticmethod
    def redirection(
            request: HttpRequest
    ) -> Union[HttpResponse, None]:
        """
        Returns a http redirect response
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

        return None

    def get_static(
            self,
            request: HttpRequest
    ) -> Union[HttpResponse, None]:
        static: Union[Static, None] = (
            self.settings.statics.get(
                to_correct(request.path)
            )
        )
        if static:
            return static.get_http_response()

        return None

    @staticmethod
    async def traversal_by_urlpatterns(
            root_url: str,
            app: Application,
            request: HttpRequest
    ) -> tuple[Union[View, None], HttpResponse]:
        """
        Walk through the urlpatterns specified by
        the user in the urls file of the application
        created by him and, if the url address matches
        the pattern, launches the user-created view,
        passing it the HttpRequest object and returns
        HttpResponse and the presentation itself to the caller.
        """
        for url, view in app:
            url, variables = matching(
                merge_url(root_url, to_correct(url)),
                request.path
            )
            if variables or request.path == url:
                response = await view(request, **variables)
                return (
                    view,
                    not_found() if not check_response(response) else response
                )

        return None, not_found()

    async def routing(
            self,
            request: HttpRequest
    ) -> tuple[Union[View, None], HttpResponse]:
        """
        Iterates through ROOT_URLPATTERNS
        and runs the method "App.traversal_by_urlpatterns"
        to check if the url matches.
        """
        request_trace(request, self)
        if static := self.get_static(request):
            return None, static

        if redirection := self.redirection(request):
            return None, redirection

        for root_url, app_name in self.settings.ROOT_URLPATTERNS:
            app: Union[Application, None] = (
                self
                .settings
                .applications
                .get(app_name)
            )
            if app:
                view, response = (
                    await self.traversal_by_urlpatterns(
                        to_correct(root_url),
                        app, request
                    )
                )
                if view:
                    return view, response

        return None, not_found()


def matching(
        url: str,
        path: str
) -> tuple[str, dict]:
    return (
        url,
        pattern_matching(path, url, '/') or {}
    )


def check_response(response) -> bool:
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


@exc_handler
async def _run(
        app: App,
        request: bytes,
        client: tuple
) -> bytes:
    """
    A function passed to the server as an entry point.
    It is responsible for starting routing
    and returning a http response to the server.

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
