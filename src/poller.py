import threading

from base_plugin import BasePlugin
from client_utils import get_user_config

from .utils.stream_utils import get_local_stream_id
from .utils.utils import logcat


class Poller:
    def __init__(self, plugin: BasePlugin):
        self.plugin = plugin
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock: threading.Lock = threading.Lock()

    def _loop(self):
        logcat("Poller thread started.")
        while not self._stop_event.is_set():
            stream_bio_enabled = self.plugin.get_setting("stream_bio_enabled", False)
            fast_card_render = self.plugin.get_setting("fast_card_render", False)

            if not any([stream_bio_enabled, fast_card_render]):
                logcat("All polling features disabled. Stopping thread.")
                break

            stream_place = self.plugin.get_setting("stream_place", 0)
            if stream_bio_enabled and stream_place == 0:
                sleep_time = 10
            elif stream_bio_enabled and (stream_place == 1 and get_user_config().isPremium()):
                sleep_time = 5
            else:
                sleep_time = 20

            try:
                platform = self.plugin.platform
                if platform is None:
                    logcat("Platform is None. Waiting...")
                    if self._stop_event.wait(5):
                        break
                    continue

                platform.get_track()

                if stream_bio_enabled:
                    user_id = get_user_config().getClientUserId()
                    selected_user_id = get_local_stream_id()

                    if user_id != 0 and selected_user_id != 0 and user_id == selected_user_id:
                        self.plugin.set_stream_text(False)

                if fast_card_render:
                    if platform.now_track and platform.now_track.active:
                        if platform.memory_id != platform.now_track.id:
                            logcat(f"Track changed ({platform.memory_id} -> {platform.now_track.id}). Rendering card...")
                            platform.memory_id = platform.now_track.id
                            card_type = self.plugin.get_setting('card_type', 0)
                            if card_type == 0:
                                self.plugin.create_horizontal_card()
                            else:
                                self.plugin.create_vertical_card()

            except Exception as e:
                import traceback
                logcat(f"Poller iteration error: {e}")
                logcat(traceback.format_exc())

            if self._stop_event.wait(sleep_time):
                logcat("Stop signal received during sleep.")
                break

        logcat("Poller thread finished.")

    def start_poller(self):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logcat("Poller is already running.")
                return

            logcat("Starting poller...")
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop_poller(self):
        with self._lock:
            if self._thread is None:
                return

            logcat("Stopping poller...")
            self._stop_event.set()
            self._thread.join(timeout=2.0)
            self._thread = None

            if self.plugin.get_setting("stream_bio_enabled", False):
                threading.Thread(target=lambda: self.plugin.set_stream_text(True), daemon=True).start()

    def is_looping(self) -> bool:
        return self._thread is not None
