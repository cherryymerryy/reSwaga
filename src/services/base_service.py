import re
from typing import Any

import requests
from base_plugin import BasePlugin

from .service_type import Platform
from .track import Track
from ..constants import DEFAULT_VALUE
from ..utils.utils import logcat


class BasePlatform:
    def __init__(self, value: str):
        self.now_track: Track | None = None

        if value not in ['', None, DEFAULT_VALUE]:
            self.value: str = value
        else:
            logcat("Value is none.")

        self.memory_id: Any = 0
        self.value_text: str | None = None
        self.pre_auth_settings: bool | None = None
        self.additional_settings: bool | None = None
        self.can_download_track: bool = True
        self.need_special_platform_args_check: bool = False

    def get_track(self) -> Track | None:
        pass

    def special_platform_args_check(self, plugin: BasePlugin) -> bool:
        pass

    def create_pre_auth_settings(self, plugin: BasePlugin) -> list[Any]:
        pass

    def create_additional_settings(self, plugin: BasePlugin) -> list[Any]:
        pass


def get_platform(platform: int) -> Platform:
    if platform == 0:
        return Platform.NotSelected
    elif platform == 1:
        return Platform.Spotify
    elif platform == 2:
        return Platform.YandexMusic
    elif platform == 3:
        return Platform.SoundCloud
    elif platform == 4:
        return Platform.VkMusic
    elif platform == 5:
        return Platform.TgMusic
    elif platform == 6:
        return Platform.LastFm
    else:
        return Platform.NotSelected


def get_songlink(platform: int) -> str:
    if platform == int(Platform.NotSelected.value[0]):
        return ''
    elif platform == int(Platform.Spotify.value[0]):
        return 's'
    elif platform == int(Platform.YandexMusic.value[0]):
        return 'ya'
    elif platform == int(Platform.SoundCloud.value[0]):
        return 'sc'
    else:
        return ''


def get_download_link(platform: int, track_id: int) -> str | None:
    songlink_codename = get_songlink(platform)
    if songlink_codename == '':
        return None

    songlink = requests.get(f"https://song.link/{songlink_codename}/{track_id}")
    if songlink.status_code == 200:
        youtube_link = re.findall(r"(https://(www\.)?youtube.com/.+?=.+?\")", songlink.text)
        soundcloud_link = re.findall(r"(https://(www\.)?soundcloud\.com/.+?\")", songlink.text)
        if soundcloud_link or youtube_link:
            return soundcloud_link[0][0][:-1] if soundcloud_link else youtube_link[0][0][:-1]
        else:
            return None
    else:
        return None