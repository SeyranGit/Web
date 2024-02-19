__all__ = [
    'get_all_statics',
    'load_static',
    'get_static',
    'Static',
    'sp'
]

from typing import (
    Generator,
    NoReturn,
    Union
)
from pathlib import Path

from web.http import (
    HttpResponse,
    HTTP_STATUS_200
)
from web.utils import (
    to_correct,
    splitext
)
from web.core.exceptions import StaticNotFound

mime_types = {
    '.aac': 'audio/aac',
    '.abw': 'application/x-abiword',
    '.arc': 'application/x-freearc',
    '.avi': 'video/x-msvideo',
    '.azw': 'application/vnd.amazon.ebook',
    '.bin': 'application/octet-stream',
    '.bmp': 'image/bmp',
    '.bz': 'application/x-bzip',
    '.bz2': 'application/x-bzip2',
    '.csh': 'application/x-csh',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.eot': 'application/vnd.ms-fontobject',
    '.epub': 'application/epub+zip',
    '.gz': 'application/gzip',
    '.gif': 'image/gif',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.ico': 'image/vnd.microsoft.icon',
    '.ics': 'text/calendar',
    '.jar': 'application/java-archive',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.jsonld': 'application/ld+json',
    '.mid': 'audio/midi',
    '.midi': 'audio/x-midi',
    '.mjs': 'text/javascript',
    '.mp3': 'audio/mpeg',
    '.mpeg': 'video/mpeg',
    '.mpkg': 'application/vnd.apple.installer+xml',
    '.odp': 'application/vnd.oasis.opendocument.presentation',
    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
    '.odt': 'application/vnd.oasis.opendocument.text',
    '.oga': 'audio/ogg',
    '.ogv': 'video/ogg',
    '.ogx': 'application/ogg',
    '.opus': 'audio/opus',
    '.otf': 'font/otf',
    '.png': 'image/png',
    '.pdf': 'application/pdf',
    '.php': 'application/php',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.rar': 'application/vnd.rar',
    '.rtf': 'application/rtf',
    '.sh': 'application/x-sh',
    '.svg': 'image/svg+xml',
    '.swf': 'application/x-shockwave-flash',
    '.tar': 'application/x-tar',
    '.tif': 'image/tiff',
    '.ts': 'video/mp2t',
    '.ttf': 'font/ttf',
    '.txt': 'text/plain',
    '.vsd': 'application/vnd.visio',
    '.wav': 'audio/wav',
    '.weba': 'audio/webm',
    '.webm': 'video/webm',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.xhtml': 'application/xhtml+xml',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xml': 'application/xml',
    '.xul': 'application/vnd.mozilla.xul+xml',
    '.zip': 'application/zip',
    '.3gp': 'video/3gpp',
    '.3g2': 'video/3gpp2',
    '.7z': 'application/x-7z-compressed',
    '.sfnt': 'font/sfnt',
    '.aces': 'image/aces',
    '.apng': 'image/apng',
    '.avci': 'image/avci',
    '.avcs': 'image/avcs',
    '.avif': 'image/avif',
    '.cgm': 'image/cgm',
    '.dpx': 'image/dpx',
    '.emf': 'image/emf',
    '.example': 'image/example',
    '.fits': 'image/fits',
    '.g3fax': 'image/g3fax',
    '.heic': 'image/heic',
    '.heic-sequence': 'image/heic-sequence',
    '.heif': 'image/heif',
    '.heif -sequence': 'image/heif-sequence',
    '.hej2k': 'image/hej2k',
    '.hsj2': 'image/hsj2',
    '.j2c': 'image/j2c',
    '.jls': 'image/jls',
    '.jp2': 'image/jp2',
    '.jph': 'image/jph',
    '.jphc': 'image/jphc',
    '.jpm': 'image/jpm',
    '.jpx': 'image/jpx',
    '.jxr': 'image/jxr',
    '.jxs': 'image/jxs',
    '.jxsc': 'image/jxsc',
    '.jxsi': 'image/jxsi',
    '.jxss': 'image/jxss',
    '.ktx': 'image/ktx',
    '.ktx2': 'image/ktx2',
    '.naplps': 'image/naplps',
    '.pwg-raster': 'image/pwg-raster',
    '.t38': 'image/t38',
    '.tiff': 'image/tiff',
    '.tiff-fx': 'image/tiff-fx'
}

UPaths = list[
    tuple[
        str,
        Generator[Path, None, None]
    ]
]

_fn_type = type(lambda: None)
get_app = None


class Static:
    __slots__ = (
        'url',
        'path',
        'content_type'
    )

    url: str
    path: str
    content_type: Union[str, None]

    def __init__(
            self,
            url: str,
            path: str,
            content_type: Union[str, None]
    ) -> None:
        self.url = url
        self.path = path
        self.content_type = content_type

    async def get_http_response(self) -> HttpResponse:
        """
        Returns HttpResponse static file.
        """
        return (
            HttpResponse(
                status=HTTP_STATUS_200,
                body=await load_static(self.path),
                headers={
                    'Content-Type': self.content_type or ''
                }
            )
        )


def auto_definition(path: str):
    return mime_types.get(splitext(path))


async def load_static(path):
    return open(path, 'rb').read()


def get_all_statics(
        root_url: str,
        root_path: str,
        media_types: dict
) -> dict[str, Static]:
    """
    Iterates through a given directory,
    matching each file with a URL address
    and adds statics to the dictionary,
    which it returns upon completion.
    """
    statics = {}
    upaths: UPaths = [
        (
            root_url,
            Path(root_path).iterdir()
        )
    ]
    for url, paths in upaths:
        for path in paths:
            if path.is_file():
                _url = to_correct(url + path.name)
                _path = str(path.absolute())

                statics[_url] = Static(
                    _url,
                    _path,
                    media_types.get(
                        splitext(_path)[-1]
                    ) or auto_definition(_path)
                )

            elif path.is_dir():
                upaths.append((
                    to_correct(url + path.name),
                    path.iterdir()
                ))

    return statics


def sp(
        root_url: str,
        root_path: str,
        media_types: Union[dict, None] = None
) -> tuple[str, str, dict]:
    return (
        root_url,
        root_path,
        media_types or mime_types
    )


async def get_static(url: str) -> Union[bytes, NoReturn]:
    """
    If there is a static file,
    returns its contents read in byte mode,
    otherwise raises a StaticNotFound exception.
    """
    global get_app

    if not get_app:
        from web.core import get_app

    if isinstance(get_app, _fn_type):
        app = get_app()
        static: Static = (
            app
            .settings
            .statics
            .get(to_correct(url))
        )
        if not static:
            raise StaticNotFound()

        return await load_static(static.path)

    raise TypeError(
        f'get_app must be of type '
        f'{_fn_type} and not {type(get_app)}'
    )
