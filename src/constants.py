from typing import Dict
from elyx import metainfo # type: ignore

TEMP_DIR_NAME: str = 'swaga_temp'
RESOURCE_DIR_NAME: str = "../resources"
RESOURCES: list[str] = [
    "Onest_Regular.ttf",
    "Onest_Bold.ttf",
    "Onest.ttf",
    "NotoSansJP_Regular.ttf",
    "NotoSansJP_Bold.ttf",
    "Circular_Regular.ttf",
    "Circular_Bold.ttf",
    "YSMusic_Bold.ttf",
    "YSMusic_Regular.ttf",
    "YSText_Bold.ttf",
    "YSText_Regular.ttf",
]

PLATFORMS_COUNT: int = 7

DEFAULT_LASTFM_API_URL: str = "19e0b83fb81f7043c02e4f070848a57a"
DEFAULT_COBALT_API_URL: str = 'https://cobalt.255x.ru'
DEFAULT_API_URL: str = "https://your.api.url"
DEFAULT_STREAM_STRING: str = "🎵 | {title} — {artists}"
DEFAULT_VALUE: str = "platform value"
DEFAULT_STREAM_TEXT: str = "🤙"
DEFAULT_INSTANT_SUBTEXT: str = "Powered by"
DEFAULT_INSTANT_MAIN_TEXT: str = metainfo['name']


FONTS: Dict[int, str] = {
    0: "Onest",
    1: "Circular",
    2: "NotoSansJP",
    3: "YSMusic",
    4: "YSText"
}
DEFAULT_COLOR: Dict[str, str] = {
    "background_color": "#000000",
    "title_text_color": "#FFFFFF",
    "subtext_color": "#A0A0A0"
}
COBALT_API_URLS = [
    'Custom',
    DEFAULT_COBALT_API_URL,
    "https://co.eepy.today",
    "https://co.otomir23.me",
]