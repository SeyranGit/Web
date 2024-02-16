__all__ = [
    'exc_uvicorn_response',
    'uvicorn_response',
    'uvc_exc'
]

from typing import (
    Sequence,
    Callable,
    Coroutine,
    Any
)
from uvicorn.lifespan.on import LifespanSendMessage

UvicornSendMethod = Callable[
    [LifespanSendMessage],
    Coroutine[Any, Any, None]
]


def exc_uvicorn_response(
        traceback: str,
        status_code: int
) -> tuple[dict, dict]:
    return (
        {
            'type': 'http.response.start',
            'status': status_code,
            'headers': [
                ('content-type', 'text/plain')
            ],
        },
        {
            'type': 'http.response.body',
            'body': traceback.encode(),
        }
    )


async def uvicorn_response(
        responses: Sequence[dict],
        send: UvicornSendMethod
) -> None:
    for response in responses:
        await send(response)


async def uvc_exc(
        traceback: str,
        status_code: int,
        send: UvicornSendMethod
) -> None:
    await uvicorn_response(
        exc_uvicorn_response(
            traceback,
            status_code
        ), send
    )
