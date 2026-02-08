from typing import Any

from android_utils import run_on_ui_thread
from base_plugin import MethodHook
from hook_utils import get_private_field

from ..keyboard_utils import RESWAGA_TAB_INDEX, force_update_ui
from ...utils.utils import logcat


class SetAllowHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param) -> Any:
        emoji_view = param.thisObject
        all_tabs = get_private_field(emoji_view, "allTabs")
        current_tabs = get_private_field(emoji_view, "currentTabs")
        if not all_tabs or not current_tabs: return

        my_tab = None
        for i in range(all_tabs.size()):
            t = all_tabs.get(i)
            if get_private_field(t, "type") == RESWAGA_TAB_INDEX:
                my_tab = t
                break

        if my_tab and not current_tabs.contains(my_tab):
            current_tabs.add(my_tab)
            run_on_ui_thread(lambda: force_update_ui(emoji_view))