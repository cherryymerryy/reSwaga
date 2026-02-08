# FROM 'VkNowPlay' PLUGIN
from typing import Dict, Any

import requests
from base_plugin import BasePlugin
from ui.settings import Text, Divider

from .base_service import BasePlatform
from .track import Track
from ..utils.utils import logcat, open_link

from elyx import strings, assets


class VkMusic(BasePlatform):
    def __init__(self, value: str):
        super().__init__(value)
        self.value_text = strings.Settings_Auth_Value_YandexMusic_Text
        self.token: str = value.strip()
        self.pre_auth_settings = True
        self.additional_settings = True
        self.can_download_track = False
        self.need_special_platform_args_check = True

    def get_track(self) -> Track | None:
        params: Dict[str, Any] = {
            'fields': 'status',
            'v': 5.199,
            'access_token': self.token
        }

        try:
            response = requests.get('https://api.vk.ru/method/users.get', params=params)
            data = response.json()

            if data.get('response', None) is None:
                logcat('Response not found')
                return Track(active=False)

            response = data['response'][0]

            if response.get('status_audio', None) is None:
                logcat('Audio status not found')
                return Track(active=False)

            t = response.get('status_audio', None)
            if t is None:
                logcat('Audio status not found2')
                return Track(active=False)

            main_artists: list = t.get('main_artists', None)
            if main_artists is None:
                artists_names: list[str] = [t.get('artist', 'Artist w/out name')]
            else:
                artists: list = [ma for ma in main_artists]
                artists_names: list[str] = [a.get('name', 'Artist w/out name') for a in artists]

            thumbnail = assets.empty_cover
            link: str = f"https://vk.ru/audio{t.get('owner_id', 0)}_{t.get('id', 0)}"
            album = t.get('album', None)

            if not album is None:
                album_link: str = f"https://vk.ru/music/album/{album.get('owner_id', 0)}_{album.get('id', 0)}_{album.get('access_key', None)}"
                thumb = album.get('thumb', None)
                if not thumb is None:
                    thumbnail = thumb.get('photo_1200', None)
            else:
                album_link: str = link

            track = Track(
                active=True,
                id=t.get('id', 0),
                title=t.get('title', 'No title provided'),
                artist=artists_names,
                album=album_link,
                thumb=thumbnail,
                link=link
            )

            self.now_track = track
            return track

        except Exception as e:
            import traceback
            logcat(f"Exception occurred while getting VK status: {e}\nFull traceback: {traceback.format_exc()}")
            self.now_track = Track(active=False)
            return Track(active=False)

    def create_pre_auth_settings(self, plugin: BasePlugin):
        return [
            Text(
                text=strings.Settings_YandexMusic_Auth_Guide,
                icon="msg_info",
                on_click=lambda _: open_link('https://telegra.ph/reSwaga-Gajd-po-avtorizacii-v-VK-09-21')
            )
        ]

    def create_additional_settings(self, plugin: BasePlugin):
        return [
            Divider(
                text=strings.VkMusic_Warning
            )
        ]