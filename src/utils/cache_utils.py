import os

from ..constants import TEMP_DIR_NAME, PLATFORMS_COUNT, DEFAULT_VALUE
from .utils import logcat, read, show_error, write, show_success, get_temp_dir


def _get_cache_file_path() -> str | None:
    from elyx import assets # type: ignore
    return os.path.join(assets.dir_path, "cached_values.json")


def initialize_cached_platforms_values() -> list[str | None]:
    try:
        empty_values = [DEFAULT_VALUE for _ in range(PLATFORMS_COUNT)]
        path = _get_cache_file_path()
        if path:
            write(_get_cache_file_path(), empty_values)
            logcat("Cached values initialized in file.")
        else:
            logcat("Could not initialize cache file: path is invalid.")
        return empty_values
    except Exception as e:
        import traceback
        logcat(traceback.format_exc())
        return []


def is_cached_values_exist() -> bool:
    path = _get_cache_file_path()
    if not path:
        return False

    values_list = read(path)

    return isinstance(values_list, list) and len(values_list) == PLATFORMS_COUNT


def is_cached_value_exist(platform: int) -> bool:
    cached_value = get_cached_values()[platform]
    return cached_value is not None and cached_value != DEFAULT_VALUE


def get_cached_values() -> list[str | None]:
    path = _get_cache_file_path()
    if not path:
        return [DEFAULT_VALUE for _ in range(PLATFORMS_COUNT)]

    exist_values = read(path)

    if not isinstance(exist_values, list) or len(exist_values) != PLATFORMS_COUNT:
        logcat("Cached values are missing or corrupted, re-initializing.")
        return initialize_cached_platforms_values()

    return exist_values


def get_cached_value(platform: int) -> str | None:
    return get_cached_values()[platform]


def save_platform_value(platform: int, value: str):
    path = _get_cache_file_path()
    if not path:
        show_error("Cannot save value: cache storage is unavailable.")
        return

    exist_values = get_cached_values()

    if exist_values[platform] == value:
        logcat(f"Value '{value}' at index {platform} is already set.")
        return

    exist_values[platform] = value
    write(path, exist_values)

    if is_cached_value_exist(platform):
        show_success("New service value cached.")
        logcat(f"Saved value '{value}' at index {platform}.")