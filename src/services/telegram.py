from typing import Dict

import requests

from .base_service import BasePlatform
from .track import Track

from org.telegram.messenger import MediaController  # type: ignore


class TgMusic(BasePlatform):
    def __init__(self, value):
        super().__init__(value)

    def get_track(self):
        now_playing = MediaController.getInstance().getPlayingMessageObject()
        if now_playing is None or MediaController.getInstance().isMessagePaused():
            self.now_track = Track(active=False)
            return Track(active=False)

        self.can_download_track = now_playing.isMusic()
        owner_id: int | None = now_playing.messageOwner.id
        title: str | None = now_playing.getMusicTitle()
        author: str | None = now_playing.getMusicAuthor()
        thumbnail: str = elyx.assets.empty_cover
        album: str = ""
        link: str = ""

        if now_playing.isMusic() and (not now_playing.isVoice() or not now_playing.isRoundVideo()):
            # pizdec govnishe
            artwork = now_playing.getArtworkUrl(False)
            req = requests.get(str(artwork).replace('athumb', 'https')).json()
            results: list[Dict[str, str]] | None = req.get('results', None)

            if results and not results[0] is None:
                owner_id = results[0].get('trackId', now_playing.messageOwner.id)
                album = results[0].get('collectionViewUrl', None)
                link = results[0].get('trackViewUrl', None)
                artwork_url = results[0].get('artworkUrl30', None)
                thumbnail = str(artwork_url).replace('30x30bb', '600x600bb') \
                    if not artwork_url is None \
                    else elyx.assets.empty_cover

        duration = now_playing.getDuration()
        progress = now_playing.audioProgressSec

        track = Track(
            active=True,
            id=owner_id,
            title=title,
            artist=[author],
            album=album,
            thumb=thumbnail,
            duration=duration,
            progress=progress,
            link=link
        )
        self.now_track = track
        return track