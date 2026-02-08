from dataclasses import dataclass
from typing import Any

@dataclass
class Track:
    active: bool
    id: Any = None
    title: str = None
    artist: list = None
    album: str = None
    thumb: str = None
    duration: int = None
    progress: int = None
    link: str = None
    device: str = None
    download_url: str = None