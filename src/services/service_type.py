from enum import Enum
from elyx import strings # type: ignore

class Platform(Enum):
    NotSelected = (0, strings.Settings_Auth_Value_NotSelected_Text)
    Spotify = (1, 'Spotify')
    YandexMusic = (2, strings.Platform_YandexMusic)
    SoundCloud = (3, 'SoundCloud')
    VkMusic = (4, strings.Platform_VkMusic)
    TgMusic = (5, 'Telegram')
    LastFm = (6, 'Last.FM')
