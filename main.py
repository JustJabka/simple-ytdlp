from enum import Enum
from typing import TypedDict, Final, Any

import yt_dlp

TITLE_FALLBACK: Final[str] = 'Unknown Title'
DURATION_FALLBACK: Final[str] = 'Unknown Duration'

SHARED_OPTIONS: Final[dict[Any, Any]] = {
    'quiet': True,
    'no_warnings': True,
    'outtmpl': '%(title)s.%(ext)s',
}


def main() -> None:
    while True:
        # Get URL
        url: str = input('Enter URL: ').strip()
        if not validate_url(url): continue

        # Get Content Format
        content_format: ContentFormat = get_content_format()

        # Download Content
        download_with_options(url, content_format)


def get_info(url: str) -> dict:
    options = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            ydl.sanitize_info(info)
            return ydl.sanitize_info(info)
    except Exception:
        pass

    return {}


def parse_info(info: dict) -> ParsedVideoInfo:
    title = info.get('title', TITLE_FALLBACK)
    duration = info.get('duration_string', DURATION_FALLBACK)

    return ParsedVideoInfo(title=title, duration=duration)


def get_content_format() -> ContentFormat:
    options_list = '\n'.join(f'{f.value} - {f.name.replace('_', ' ').lower().capitalize()}' for f in ContentFormat)

    prompt = f'Enter content format (1-{len(ContentFormat)}):\n{options_list}\n> '
    user_input = int(input(prompt).strip())

    return ContentFormat(user_input)

def is_empty_info(info: ParsedVideoInfo) -> bool:
    title = info.get('title')
    duration = info.get('duration')

    return (title is TITLE_FALLBACK) and (duration is DURATION_FALLBACK)

def validate_url(url: str) -> bool:
    print('Searching...')

    if not url:
        return False

    info = parse_info(get_info(url))

    if is_empty_info(info):
        return False

    print(f'Found - {info.get('title')} ({info.get('duration')})\n')
    return True


def download_with_options(url: str, content_format: ContentFormat):
    options = SHARED_OPTIONS.copy()
    options.update(content_format.options)

    print('Downloading...')

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
            print('Download complete!\n')
    except Exception:
        pass


class ParsedVideoInfo(TypedDict):
    title: str
    duration: str


class ContentFormat(Enum):
    VIDEO_AND_AUDIO = 1
    VIDEO = 2
    AUDIO = 3
    THUMBNAIL = 4

    @property
    def options(self) -> dict:
        mapping = {
            ContentFormat.VIDEO_AND_AUDIO: {
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            },
            ContentFormat.VIDEO: {
                'format': 'bestvideo',
                'merge_output_format': 'mp4',
            },
            ContentFormat.AUDIO: {
                'format': 'bestaudio',
                'writethumbnail': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'EmbedThumbnail',
                    },
                    {
                        'key': 'FFmpegMetadata',
                    },
                ]
            },
            ContentFormat.THUMBNAIL: {
                'skip_download': True,
                'writethumbnail': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegThumbnailsConvertor',
                        'format': 'png',
                        'when': 'before_dl',
                    }
                ]
            },
        }

        return mapping[self]


if __name__ == '__main__':
    main()
