from typing import Any

from base_plugin import MethodHook
from hook_utils import get_private_field

from ..keyboard_utils import VIEW_TAG, RESWAGA_TAB_INDEX

from android.view import View # type: ignore


class CheckGridVisibilityHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param) -> Any:
        emoji_view = param.thisObject
        position = param.args[0]
        my_view = emoji_view.findViewWithTag(VIEW_TAG)
        stickers = get_private_field(emoji_view, "stickersTabContainer")
        search = get_private_field(emoji_view, "emojiSearchField")

        if position == RESWAGA_TAB_INDEX:
            if my_view: my_view.setVisibility(View.VISIBLE)
            if stickers: stickers.setVisibility(View.GONE)
            if search: search.setVisibility(View.GONE)
        else:
            if my_view: my_view.setVisibility(View.GONE)