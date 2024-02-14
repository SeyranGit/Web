from typing import Sequence


def exc_uvicorn_response(
        traceback: str
) -> tuple[dict, dict]:
    return (
        {
            'type': 'http.response.start',
            'status': 404,
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
        send
) -> None:
    for response in responses:
        await send(response)


async def uvc_exc(traceback, send):
    return (
        await uvicorn_response(
            exc_uvicorn_response(
                traceback
            ), send
        )
    )
