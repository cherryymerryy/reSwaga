from typing import Optional
import requests

from reswag import BasePlatform, Track, logcat

class Spotify(BasePlatform):
    def __init__(self, value: str):
        super().__init__(value)
        self.username = value.strip()

    def get_track(self) -> Optional[Track]:
        data = requests.get(f"https://api.stats.fm/api/v1/users/{self.username}/streams/current", headers=self.headers)
        if data.status_code == 204:
            return Track(active=False)
        elif data.status_code != 200:
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
                track = Track(active=False)

            return track

    def get_album_link(self, internal_track_id) -> Optional[str]:
        data = requests.get(f"https://api.stats.fm/api/v1/tracks/{internal_track_id}/albums", headers=self.headers)
        if data.status_code != 200:
            return None
        else:
            data = data.json()['items']
            if data:
                try:
                    album_id = data[0]['externalIds']['spotify'][0]
                    return f"https://open.spotify.com/album/{album_id}"
                except:
                    return None
            else:
                return None