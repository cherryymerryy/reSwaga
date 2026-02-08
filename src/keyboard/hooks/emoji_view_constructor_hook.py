from typing import Any

from android_utils import run_on_ui_thread
from base_plugin import MethodHook, BasePlugin
from hook_utils import get_private_field, set_private_field

from ..keyboard_utils import create_custom_view, get_java_class, RESWAGA_TAB_INDEX, force_update_ui
from ...utils.utils import logcat



class EmojiViewConstructorHook(MethodHook):
    def __init__(self, plugin: BasePlugin):
        super().__init__()
        self.plugin = plugin

    def after_hooked_method(self, param) -> Any:
        from java.util import ArrayList  # type: ignore

        emoji_view = param.thisObject
        context = param.args[4]

        all_tabs = get_private_field(emoji_view, "allTabs")
        py_all_tabs = list(ArrayList(all_tabs).toArray())
        if len(py_all_tabs) <= 1:
            logcat("py_all_tabs is empty")
            return

        try:
            my_view = create_custom_view(context, self.plugin)

            tab_class = get_java_class("org.telegram.ui.Components.EmojiView$Tab")
            tab_ctor = tab_class.getDeclaredConstructors()[0]
            tab_ctor.setAccessible(True)
            new_tab = tab_ctor.newInstance(emoji_view)

            set_private_field(new_tab, "type", RESWAGA_TAB_INDEX)
            set_private_field(new_tab, "view", my_view)

            current_tabs = get_private_field(emoji_view, "currentTabs")
            if all_tabs is not None: all_tabs.add(new_tab)
            if current_tabs is not None: current_tabs.add(new_tab)

            run_on_ui_thread(lambda: force_update_ui(emoji_view))

        except Exception as e:
            logcat(f"Ctor error: {e}")