__all__ = [
    'exc_uvicorn_response',
    'uvicorn_response',
    'uvc_exc'
]

from typing import (
    Sequence,
    Callable,
    Coroutine,
    Union,
    Any
)
from uvicorn.lifespan.on import LifespanSendMessage

UvicornSendMethod = Callable[
    [Union[LifespanSendMessage, dict]],
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
        send: Union[UvicornSendMethod, None]
) -> None:
    if send is not None:
        return (
            await uvicorn_response(
                exc_uvicorn_response(
                    traceback,
                    status_code
                ), send
            )
        )

    raise TypeError(
        f'The send argument must be '
        f'of type {UvicornSendMethod}'
    )
