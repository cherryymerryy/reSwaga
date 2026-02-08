import requests

from ..constants import DEFAULT_LASTFM_API_URL
from .base_service import BasePlatform
from .track import Track


class LastFm(BasePlatform):
    def __init__(self, value, api_key: str = DEFAULT_LASTFM_API_URL):
        super().__init__(value)
        self.value_text = elyx.strings.Settings_Auth_Value_Spotify_Text
        self.api_key: str = api_key
        self.value = value.strip()
        self.pre_auth_settings = False
        self.additional_settings = False
        self.can_download_track = False
        self.need_special_platform_args_check = False

    def get_track(self) -> Track | None:
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {
            'method': 'user.getrecenttracks',
            'user': self.value,
            'api_key': self.api_key,
            'format': 'json',
            'limit': 1
        }

        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            tracks = data.get('recenttracks', {}).get('track', [])
            if tracks and isinstance(tracks, list) and len(tracks) > 0:
                track = tracks[0]
                title = track.get('name', '')
                artist = track.get('artist', {}).get('#text', '') if isinstance(track.get('artist'), dict) else str(track.get('artist', ''))
                album = track.get('album', {}).get('#text', '') if isinstance(track.get('album'), dict) else str(track.get('album', ''))
                images = track.get('image', [])
                image_url = elyx.assets.empty_cover
                if images:
                    size_priority = ['mega', 'extralarge', 'large']
                    size_map = {img.get('size'): img.get('#text', '') for img in images if img.get('#text')}
                    for s in size_priority:
                        if size_map.get(s):
                            image_url = size_map[s]
                            break
                    if not image_url:
                        for img in reversed(images):
                            if img.get('#text'):
                                image_url = img.get('#text', '')
                                break

                track = Track(
                    active=True,
                    id=str(title).replace(' ', '_').lower(),
                    title=title,
                    artist=[artist],
                    album=album,
                    thumb=image_url,
                    progress=0,
                    duration=0,
                    link=track.get('url', '')
                )
                self.now_track = track
                return track
            else:
                track = Track(active=False)
                self.now_track = track
                return track
        else:
            track = Track(active=False)
            self.now_track = track
            return track