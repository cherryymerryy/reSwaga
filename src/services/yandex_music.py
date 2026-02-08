import requests
from base_plugin import BasePlugin
from ui.settings import Switch, Input, Text

from ..utils.utils import logcat, open_link
from ..constants import DEFAULT_API_URL
from .base_service import BasePlatform
from .service_type import Platform
from .track import Track

from elyx import strings # type: ignore


class YandexMusic(BasePlatform):
    def __init__(self, value: str, api_url: str | None = None):
        super().__init__(value)
        self.token = value.strip()
        self.value_text = strings.Settings_Auth_Value_YandexMusic_Text
        self.pre_auth_settings = True
        self.additional_settings = True
        self.need_special_platform_args_check = True
        self.api_url: str = api_url if api_url else "https://track.mipoh.ru"
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "ya-token": self.token
        }

    def get_track(self) -> Track | None:
        if not self.token:
            self.now_track = Track(active=False)
            return Track(active=False)

        try:
            r = requests.get(f"{self.api_url}/get_current_track_beta", headers=self.headers, timeout=10, verify=False)
            logcat(f"[YandexMusic] get_current_track status={r.status_code}")
            data = r.json()

            if r.status_code != 200 or 'track' not in data:
                logcat("[YandexMusic] no 'track' key or bad status")
                self.now_track = Track(active=False)
                return Track(active=False)

            t = data['track']

            raw_artist = t.get('artist', '')
            if isinstance(raw_artist, str):
                artists = [x.strip() for x in raw_artist.split(',') if x.strip()]
            elif isinstance(raw_artist, list):
                artists = raw_artist
            else:
                artists = []

            track = Track(
                active=True,
                id=t.get('track_id'),
                title=t.get('title'),
                artist=artists,
                album=t.get('album'),
                thumb=t.get('img'),
                duration=int(t.get('duration', 0)),
                progress=int(data.get('progress_ms', 0)) // 1000,
                link=f"https://music.yandex.ru/track/{t.get('track_id')}",
                download_url=t.get('download_link')
            )
            self.now_track = track
            logcat(f"[YandexMusic] built track: {track.title} — {track.artist}")
            return track
        except Exception as e:
            logcat(f"[YandexMusic] get_current_track exception: {e}")
            self.now_track = Track(active=False)
            return Track(active=False)

    def special_platform_args_check(self, plugin):
        if plugin.get_setting('enable_yandex_custom_api_url', False):
            yandex_custom_api: str | None = plugin.get_setting('yandex_custom_api', None)
            if yandex_custom_api in ["", None]:
                return True
            elif not yandex_custom_api.startswith('https://') and not yandex_custom_api.startswith('http://'):
                return True
            elif len(yandex_custom_api) <= 7:
                return True
            else:
                return True
        else:
            return False

    def create_pre_auth_settings(self, plugin):
        return [
            Text(
                text=strings.Settings_YandexMusic_Auth_Guide,
                icon="msg_info",
                on_click=lambda _: plugin.show_info_alert(
                    title=strings.Settings_YandexMusic_Auth_Guide,
                    message=strings.Settings_YandexMusic_LoginGuide,
                    positive_text="Ok",
                    neutral_text="Guide",
                    neutral_listener=lambda: open_link("https://yandex-music.readthedocs.io/en/main/token.html")
                )
            )
        ]

    def create_additional_settings(self, plugin: BasePlugin):
        custom_api_url = plugin.get_setting("enable_yandex_custom_api_url", False)
        return [
            Switch(
                key="enable_yandex_custom_api_url",
                text=strings.Settings_YandexMusic_CustomApi_Enable_Text,
                subtext=strings.Settings_YandexMusic_CustomApi_Enable_Subtext,
                icon="msg_language",
                default=False,
                on_change=lambda _: plugin.update_platform_object(
                    plugin.get_setting("selected_platform", int(Platform.NotSelected.value[0])),
                    True
                )
            ),
            Input(
                key="yandex_custom_api",
                text=strings.Settings_YandexMusic_CustomApi_Input_Text,
                icon="msg_instant_link",
                default=DEFAULT_API_URL,
                on_change=lambda _: plugin.update_platform_object(
                    plugin.get_setting("selected_platform", int(Platform.NotSelected.value[0])),
                    True
                )
            ) if custom_api_url else None,
            Text(
                text="Custom API Guide",
                icon="msg_info",
                on_click=lambda _: open_link("https://github.com/MIPOHBOPOHIH/megacurrenttrack-go")
            ) if custom_api_url else None
        ]