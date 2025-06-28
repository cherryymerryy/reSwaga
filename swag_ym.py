from typing import Optional
import requests
import reSwaga

class YandexMusic(reSwaga.BasePlatform):
    def __init__(self, value: str):
        super().__init__(value)
        self.api_url: str = "https://track.mipoh.ru/"
        self.token = value.strip()
        self.headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "ya-token": self.token}

    def get_track(self) -> Optional[reSwaga.Track]:
        if not self.token:
            return reSwaga.Track(active=False)
        try:
            r = requests.get(f"{self.api_url}/get_current_track_beta", headers=self.headers, timeout=10, verify=False)
            reSwaga.logcat(f"[YandexMusic] get_current_track status={r.status_code}, body={r.text[:200]}")
            data = r.json()
            reSwaga.logcat(f"[YandexMusic] get_current_track data keys={list(data.keys())}")
            if r.status_code != 200 or 'track' not in data:
                reSwaga.logcat("[YandexMusic] no 'track' key or bad status")
                return reSwaga.Track(active=False)
            t = data['track']
            reSwaga.logcat(f"[YandexMusic] raw track: {t}")
            tid = t.get('track_id')
            raw_artist = t.get('artist', '')
            if isinstance(raw_artist, str):
                artists = [x.strip() for x in raw_artist.split(',') if x.strip()]
            elif isinstance(raw_artist, list):
                artists = raw_artist
            else:
                artists = []
            album = t.get('album')
            thumb = t.get('img')
            duration = int(t.get('duration', 0))
            progress_ms_raw = data.get('progress_ms', 0)
            try:
                progress_ms = int(progress_ms_raw)
            except:
                progress_ms = 0
            progress = progress_ms // 1000
            track = reSwaga.Track(
                active=True,
                track_id=tid,
                title=t.get('title'),
                artist=artists,
                album=album,
                thumb=thumb,
                duration=duration,
                progress=progress,
                link=f"https://music.yandex.ru/track/{tid}",
                download_url=t.get('download_link')
            )
            reSwaga.logcat(f"[YandexMusic] built track: {track.title} — {track.artist}, album={track.album}, duration={track.duration}, progress={track.progress}")
            return track
        except Exception as e:
            reSwaga.logcat(f"[YandexMusic] get_current_track exception: {e}")
            return reSwaga.Track(active=False)
