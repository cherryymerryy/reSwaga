from typing import Any

import requests
from base_plugin import BasePlugin
from ui.settings import Text

from .base_service import BasePlatform
from .track import Track
from ..utils.utils import open_link, logcat

from elyx import strings # type: ignore


class Spotify(BasePlatform):
    def __init__(self, value: str):
        super().__init__(value)
        self.value_text = strings.Settings_Auth_Value_Spotify_Text
        username = value.strip() if value else ""
        if '/' in username:
            username = username.split('/')[-1]
        self.username = username
        self.headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        self.now_track = Track(active=False)
        self.pre_auth_settings = True
        self.can_download_track = False

    def get_track(self) -> Track | None:
        data = requests.get(f"https://api.stats.fm/api/v1/users/{self.username}/streams/current", headers=self.headers)

        if data.status_code == 204 or data.status_code != 200:
            self.now_track = Track(active=False)
            return Track(active=False)
        else:
            data = data.json()['item']
            if data:
                track_id = data['track']['externalIds']['spotify']
                track_id = track_id[0] if track_id else 0
                album = self.get_album_link(data['track']['id'])
                track = Track(
                    active=True,
                    id=track_id,
                    title=data['track']['name'],
                    artist=[artist['name'] for artist in data['track']['artists']],
                    album=album,
                    thumb=data['track']['albums'][0]['image'],
                    duration=data['track']['durationMs'] // 1000,
                    progress=data['progressMs'] // 1000,
                    link=f"https://open.spotify.com/track/{track_id}",
                    device=data['deviceName']
                )
            else:
                self.now_track = Track(active=False)
                track = Track(active=False)

            self.now_track = track
            return track

    def get_album_link(self, internal_track_id) -> str | None:
        data = requests.get(f"https://api.stats.fm/api/v1/tracks/{internal_track_id}/albums", headers=self.headers)
        if data.status_code != 200:
            return None
        else:
            data = data.json()['items']
            if data:
                try:
                    if data[0]['externalIds']['spotify'][0]:
                        album_id = data[0]['externalIds']['spotify'][0]
                        return f"https://open.spotify.com/album/{album_id}"

                    elif data[0]['externalIds']['appleMusic'][0]:
                        album_id = data[0]['externalIds']['appleMusic'][0]
                        return f"https://open.spotify.com/album/{album_id}"

                    else:
                        album_id = data[0]['externalIds']['id']
                        return f"https://open.spotify.com/album/{album_id}"
                except Exception as e:
                    logcat("[Spotify] get_album_link: " + str(e))
                    return None
            else:
                return None

    def create_pre_auth_settings(self, plugin: BasePlugin) -> list[Any]:
        return [
            Text(
                text=strings.Settings_YandexMusic_Auth_Guide,
                icon="msg_info",
                on_click=lambda _: open_link(strings.Guide_Spotify_Link)
            )
        ]