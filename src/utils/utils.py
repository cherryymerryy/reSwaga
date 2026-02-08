import json
import os
import threading
import time
from typing import Any, Callable

import requests
from android.content import Intent  # type: ignore
from android.graphics import Color  # type: ignore
from android.net import Uri  # type: ignore
from android.view import View, Gravity, ViewGroup, MotionEvent  # type: ignore
from android.widget import LinearLayout, FrameLayout, ScrollView, TextView  # type: ignore
from android_utils import log, run_on_ui_thread
from client_utils import (
    get_last_fragment,
    get_messages_controller
)
from com.exteragram.messenger.plugins import PluginsController  # type: ignore
from com.exteragram.messenger.plugins.ui import PluginSettingsActivity  # type: ignore
from com.exteragram.messenger.utils import AppUtils  # type: ignore
from java import dynamic_proxy  # type: ignore
from java.io import File  # type: ignore
from java.lang import Integer, Math, Class, Boolean, Integer, Float  # type: ignore
from java.lang.reflect import Array, Modifier  # type: ignore
from java.util import ArrayList, Locale  # type: ignore
from org.telegram.messenger import ApplicationLoader, R, AndroidUtilities, SendMessagesHelper, MessageObject, MediaController, ChatObject  # type: ignore
from org.telegram.tgnet import TLRPC  # type: ignore
from org.telegram.tgnet.tl import TL_account  # type: ignore
from org.telegram.ui import ChatActivity  # type: ignore
from org.telegram.ui.Components import LayoutHelper  # type: ignore
from org.telegram.ui.Stories.recorder import ButtonWithCounterView  # type: ignore
from ui.bulletin import BulletinHelper
from ..constants import RESOURCE_DIR_NAME
from ..services.service_type import Platform
from elyx import metainfo, assets # type: ignore

def logcat(message: Any): log(f"[{metainfo['id']}] {message}")


def to_json(obj: Any): return AppUtils.getGson().toJson(obj)


def show_error(message: str, on_click: Callable | None = None, button_text: str = ""):
    if on_click is None:
        BulletinHelper.show_error(f"[{metainfo['name']}] {message}")
    elif on_click is not None and button_text != "":
        BulletinHelper.show_with_button(f"[{metainfo['name']}] {message}", R.raw.error, button_text, lambda: on_click())
    else:
        BulletinHelper.show_error(f"[{metainfo['name']}] {message}")


def show_info(message: str, on_click: Callable | None = None, button_text: str = ""):
    if on_click is None:
        BulletinHelper.show_info(f"[{metainfo['name']}] {message}")
    elif on_click is not None and button_text != "":
        BulletinHelper.show_with_button(f"[{metainfo['name']}] {message}", R.raw.info, button_text, lambda: on_click())
    else:
        BulletinHelper.show_error(f"[{metainfo['name']}] {message}")


def show_success(message: str, on_click: Callable | None = None, button_text: str = ""):
    if on_click is None:
        BulletinHelper.show_success(f"[{metainfo['name']}] {message}")
    elif on_click is not None and button_text != "":
        BulletinHelper.show_with_button(f"[{metainfo['name']}] {message}", R.raw.success, button_text, lambda: on_click())
    else:
        BulletinHelper.show_success(f"[{metainfo['name']}] {message}")


def get_temp_dir() -> File | None:
    try:
        base_dir = ApplicationLoader.getFilesDirFixed()
        if not base_dir:
            return None
        temp_dir = File(base_dir.getAbsolutePath(), f"plugins/{RESOURCE_DIR_NAME}")
        if not temp_dir.exists() and not temp_dir.mkdirs():
            return None
        return temp_dir
    except Exception as e:
        logcat(f"Error getting/creating temp directory: {e}")
        return None


def download_file(url: str, file_path: str):
    if url is None or url == "":
        logcat("No URL provided to download.")
        return

    if file_path is None or file_path == "":
        logcat("No file_path provided to download.")
        return

    name = url.split("/").pop()

    try:
        logcat(f"Downloading {name}...")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        content = response.content

        if content:
            with open(file_path, "wb") as f:
                f.write(content)
            logcat(f"Successfully downloaded {name}.")
        else:
            logcat(f"Downloaded empty file for {name}.")

    except requests.exceptions.HTTPError as e:
        show_error(f"Failed to download {name}. Server returned error: {e}")
        logcat(f"Failed to download {name}. Server returned error: {e}")
    except requests.exceptions.RequestException as e:
        show_error(f"Failed to download {name} due to a network error: {e}")
        logcat(f"Failed to download {name} due to a network error: {e}")
    except IOError as e:
        show_error(f"Failed to save {name}. Permission or disk error: {e}")
        logcat(f"Failed to save {name}. Permission or disk error: {e}")
    except Exception as e:
        show_error(f"An unexpected error occurred while downloading {name}: {e}")
        logcat(f"An unexpected error occurred while downloading {name}: {e}")


def open_plugin_settings():
    try:
        java_plugin = PluginsController.getInstance().plugins.get(metainfo['id'])
        if java_plugin:
            run_on_ui_thread(lambda: get_last_fragment().presentFragment(PluginSettingsActivity(java_plugin)))
    except Exception as e:
        logcat(f"Error opening plugin settings: {e}")


def open_link(url: str):
    fragment = get_last_fragment()
    ctx = fragment.getContext() if fragment else ApplicationLoader.applicationContext
    intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
    run_on_ui_thread(lambda: ctx.startActivity(intent))


def open_tg_link(path: str):
    try:
        fragment = get_last_fragment()
        ctx = fragment.getContext() if fragment else ApplicationLoader.applicationContext
        if "/" in path:
            domain, post = path.split("/", 1)
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(f"tg://resolve?domain={domain}&post={post}"))
            run_on_ui_thread(lambda: ctx.startActivity(intent))
        else:
            mc = get_messages_controller()
            run_on_ui_thread(lambda: mc.openByUserName(path, fragment, 1))
    except Exception as e:
        log(f"[{metainfo['id']}] Failed to open tg link: {e}")


def get_platform_logo_path(platform: Platform) -> Any | None:
    if platform == Platform.NotSelected:
        return None
    elif platform == Platform.LastFm:
        return assets.img.lastfm.java_file
    elif platform == Platform.Spotify:
        return assets.img.spotify.java_file
    elif platform == Platform.TgMusic:
        return assets.img.tgmusic.java_file
    elif platform == Platform.VkMusic:
        return assets.img.vkmusic.java_file
    elif platform == Platform.SoundCloud:
        return assets.img.soundcloud.java_file
    elif platform == Platform.YandexMusic:
        return assets.img.yandexmusic.java_file
    else:
        return None


def read(path: str) -> Any | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as file:
            file_content = file.read()
        return json.loads(file_content.decode("utf-8", errors="replace"))
    except Exception:
        import traceback
        logcat(f"Failed to load data from {path}: {traceback.format_exc()}")
        return None


def write(path: str, content: Any):
    try:
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        save_data = json.dumps(content, indent=4).encode("utf-8", errors="replace")
        with open(path, "wb") as file:
            file.write(save_data)
    except PermissionError as e:
        logcat(f"Have no permissions to edit {path}: {e}")
    except Exception as e:
        logcat(f"Failed to write data to {path}: {e}")


def copy(to_copy: str) -> bool:
    return AndroidUtilities.addToClipboard(to_copy)


def delete_file_delayed(path: str, delay: int = 60):
    def action():
        try:
            time.sleep(delay)
            if os.path.exists(path):
                os.remove(path)
                logcat(f"Deleted temp file: {path}")
        except Exception as e:
            logcat(f"Delayed delete error: {e}")

    threading.Thread(target=action, daemon=True).start()