from typing import Any

from base_plugin import MethodHook

from ..keyboard_utils import RESWAGA_TAB_INDEX
from ...utils.utils import logcat


class AdapterGetIconHook(MethodHook):
    def __init__(self, plugin):
        self.plugin = plugin

    def after_hooked_method(self, param) -> Any:
        position = param.args[0]
        if position == RESWAGA_TAB_INDEX:
            param.setResult(None)