from secrets import choice
from typing import Dict, Any

import requests
from base_plugin import BasePlugin
from ui.settings import Text, Divider

from .base_service import BasePlatform
from .track import Track

from elyx import strings # type: ignore

from ..utils.utils import logcat, open_link


class SoundCloud(BasePlatform):
    def __init__(self, value: str):
        super().__init__(value)
        self.value_text = strings.Settings_Auth_Value_SoundCloud_Text

        if not value: return
        self.token: str = value.strip()

        chrome_user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1',
            'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.112 Safari/535.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.27 Safari/532.0',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.38 Safari/532.0',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) Chrome/4.0.221.7 Safari/532.2',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.29 Safari/525.13',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
        ]

        self.headers: Dict[str, str] = {
            'User-Agent': choice(chrome_user_agents),
            'Authorization': f'OAuth {self.token}',
            'Origin': 'https://soundcloud.com',
            'Referer': 'https://soundcloud.com/',
        }
        self.params: Dict[str, str] = {
            'client_id': '1HxML01xkzWgtHfBreaeZfpANMe3ADjb',
            'app_version': '1739181955',
            'app_strings': 'en',
            'limit': '20',
            'offset': '0',
            'linked_partitioning': '1'
        }
        self.api_url: str = 'https://api-v2.soundcloud.com/'
        self.can_download_track = False
        self.pre_auth_settings = True

    def get_track(self) -> Track | None:
        if not self.token:
            self.now_track = Track(active=False)
            return Track(active=False)

        try:
            data = requests.get(
                url=f"{self.api_url}me/play-history/tracks",
                params=self.params,
                headers=self.headers
            )

            if data.status_code != 200:
                logcat(f"[Soundcloud] Status code: {data.status_code}")
                self.now_track = Track(active=False)
                return Track(active=False)

            collection = data.json()['collection']

            if not collection or len(collection) <= 0:
                logcat("[Soundcloud] Collection is empty")
                self.now_track = Track(active=False)
                return Track(active=False)

            track_id: int = collection[0].get('track_id', 0)
            t: Dict[str, Any] = collection[0].get('track', None)

            if not t:
                logcat("[Soundcloud] TrackInfo is None")
                self.now_track = Track(active=False)
                return Track(active=False)

            metadata: Dict[str, Any] | None = t.get('publisher_metadata', None)
            track = Track(
                active=True,
                id=track_id,
                title=t.get('title', 'No title provided'),
                artist=[metadata.get('artist', 'Anonymous artist')] if metadata is not None else 'No artist',
                album=metadata.get('album_title', '') if metadata is not None else '',
                thumb=t.get('artwork_url', ''),
                duration=int(t.get('duration', 0)) // 1000,
                link=t.get('permalink_url', '')
            )

            self.now_track = track
            logcat(f"[Soundcloud] built track: {track.title} — {track.artist}")
            return track

        except Exception as e:
            import traceback
            logcat(f"[Soundcloud] Exception in get_track: {e}\nFull traceback: {traceback.format_exc()}")
            self.now_track = Track(active=False)
            return Track(active=False)

    def create_pre_auth_settings(self, plugin: BasePlugin) -> list[Any]:
        return [
            Text(
                text=strings.Settings_YandexMusic_Auth_Guide,
                icon="msg_info",
                on_click=lambda _: open_link(strings.Guide_Soundcloud_Link)
            ),
            Divider(
                text=strings.SoundCloud_Warning
            )
        ]