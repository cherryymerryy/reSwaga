import threading
from typing import Any

from base_plugin import BasePlugin
from client_utils import get_last_fragment
from hook_utils import find_class, get_private_field

from ..utils.utils import open_plugin_settings, open_tg_link, logcat

from elyx import strings # type: ignore

from org.telegram.ui import ChatActivity  # type: ignore
from org.telegram.messenger import AndroidUtilities, SendMessagesHelper, ChatObject  # type: ignore
from org.telegram.ui.Components import LayoutHelper  # type: ignore
from org.telegram.ui.Stories.recorder import ButtonWithCounterView  # type: ignore

from android.view import View, Gravity, MotionEvent  # type: ignore
from android.widget import LinearLayout, ScrollView  # type: ignore

from java import dynamic_proxy  # type: ignore
from java.lang import Class  # type: ignore


RESWAGA_TAB_INDEX = 3
VIEW_TAG = "RESWAGA_CUSTOM_TAB_VIEW_TAG"


def get_java_class(name):
    try:
        return Class.forName(name)
    except:
        return None


def find_constructor_exact(clazz, *params):
    try:
        ctor = clazz.getDeclaredConstructor(*params)
        ctor.setAccessible(True)
        return ctor
    except:
        import traceback
        logcat(traceback.format_exc())
        return None


def find_method_exact(clazz, name, *params):
    try:
        m = clazz.getDeclaredMethod(name, *params)
        m.setAccessible(True)
        return m
    except:
        import traceback
        logcat(traceback.format_exc())
        return None


def create_button(context, text: str, subtext: str = "", enabled: bool = True, listener: View.OnClickListener = None, tonal: bool = True) -> ButtonWithCounterView | None:
    if text == "":
        return None

    button = ButtonWithCounterView(context, tonal, None)
    button.setText(text, False)

    if subtext != "" and len(subtext) > 0:
        button.setSubText(subtext, False)

    button.setEnabled(enabled)
    if button.isEnabled() and not listener is None:
        button.setOnClickListener(listener)

    return button


def create_custom_view(context, plugin: BasePlugin):
    class SendCardButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            fragment2 = get_last_fragment()
            if not isinstance(fragment2, ChatActivity): return
            params = SendMessagesHelper.SendMessageParams()
            params.peer = fragment2.getDialogId()
            params.replyToMsg = fragment2.getReplyMessage()
            params.replyToTopMsg = fragment2.getThreadMessage()
            threading.Thread(target=plugin.send_card_message, args=(params,), daemon=True).start()

    class SendAudioButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            fragment2 = get_last_fragment()
            if not isinstance(fragment2, ChatActivity): return
            params = SendMessagesHelper.SendMessageParams()
            params.peer = fragment2.getDialogId()
            params.replyToMsg = fragment2.getReplyMessage()
            params.replyToTopMsg = fragment2.getThreadMessage()
            threading.Thread(target=plugin.send_audio_message, args=(params,), daemon=True).start()

    class SendTextButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            fragment2 = get_last_fragment()
            if not isinstance(fragment2, ChatActivity): return
            params = SendMessagesHelper.SendMessageParams()
            params.peer = fragment2.getDialogId()
            params.replyToMsg = fragment2.getReplyMessage()
            params.replyToTopMsg = fragment2.getThreadMessage()
            threading.Thread(target=plugin.send_text_message, args=(params,), daemon=True).start()

    class SettingsButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            open_plugin_settings()

    class ChannelButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            open_tg_link("meeowPlugins")

    class DonateButtonListener(dynamic_proxy(View.OnClickListener)):
        def onClick(self, view):
            open_tg_link("meeowPlugins/93")

    class ScrollTouchListener(dynamic_proxy(View.OnTouchListener)):
        def onTouch(self, v, event):
            v.onTouchEvent(event)

            action = event.getAction()

            if action == MotionEvent.ACTION_DOWN:
                self.last_y = event.getY()
                v.getParent().requestDisallowInterceptTouchEvent(True)

            elif action == MotionEvent.ACTION_MOVE:
                current_y = event.getY()
                delta_y = current_y - self.last_y


                if delta_y > 0 and not v.canScrollVertically(-1):
                    v.getParent().requestDisallowInterceptTouchEvent(False)

                elif delta_y < 0 and not v.canScrollVertically(1):
                    v.getParent().requestDisallowInterceptTouchEvent(False)

                else:
                    v.getParent().requestDisallowInterceptTouchEvent(True)

            elif action == MotionEvent.ACTION_UP or action == MotionEvent.ACTION_CANCEL:
                v.getParent().requestDisallowInterceptTouchEvent(False)

            return True

    layout_helper = find_class("org.telegram.ui.Components.LayoutHelper")
    try:
        ScrollView = find_class("androidx.core.widget.NestedScrollView")
    except:
        ScrollView = find_class("android.widget.ScrollView")

    fragment = get_last_fragment()
    can_send_photo = True
    can_send_audio = True
    can_send_text = True

    if isinstance(fragment, ChatActivity):
        current_chat = fragment.currentChat
        if current_chat is not None:
            if not ChatObject.hasAdminRights(current_chat):
                can_send_photo = ChatObject.canSendPhoto(current_chat)
                can_send_audio = ChatObject.canSendMusic(current_chat)
                can_send_text = ChatObject.canSendMessages(current_chat)

    if not plugin.platform.can_download_track:
        can_send_audio = False

    scroll_view = ScrollView(context)
    scroll_view.setFillViewport(True)
    scroll_view.setVerticalScrollBarEnabled(False)
    scroll_view.setNestedScrollingEnabled(True)
    scroll_view.setOnTouchListener(ScrollTouchListener())

    vertical_container = LinearLayout(context)
    vertical_container.setOrientation(LinearLayout.VERTICAL)
    vertical_container.setPadding(
        AndroidUtilities.dp(4),
        AndroidUtilities.dp(4),
        AndroidUtilities.dp(4),
        AndroidUtilities.dp(4)
    )

    scroll_view.addView(
        vertical_container,
        layout_helper.createScroll(-1, -2, Gravity.TOP)
    )

    buttons_data: list[tuple[str, str, bool, Any, bool]] = [
        (strings.Action_SendCard_Title, strings.Action_SendCard_Subtext, can_send_photo, SendCardButtonListener(), True),
        (strings.Action_SendAudio_Title, strings.Action_SendAudio_Subtext, can_send_audio, SendAudioButtonListener(), True),
        (strings.Action_SendText_Title, strings.Action_SendText_Subtext, can_send_text, SendTextButtonListener(), True),
        (strings.Action_Settings_Title, strings.Action_Settings_Subtext, True, SettingsButtonListener(), False),
        (strings.Alert_Donate_Header, "<3", True, DonateButtonListener(), False),
        ("@MeeowPlugins", "<3", True, ChannelButtonListener(), False),
        ("z", "v", True, ChannelButtonListener(), False)
    ]

    columns = 1
    row_layout = None

    btn_width = (AndroidUtilities.displaySize.x - AndroidUtilities.dp(24)) // columns
    btn_height = AndroidUtilities.dp(52)
    btn_margin = AndroidUtilities.dp(4)

    for i, (title, subtext, enabled, listener, tonal) in enumerate(buttons_data):
        if i % columns == 0:
            row_layout = LinearLayout(context)
            row_layout.setOrientation(LinearLayout.HORIZONTAL)
            vertical_container.addView(
                row_layout,
                layout_helper.createLinear(-1, -2)
            )

        btn = create_button(context, title, subtext, enabled, listener, tonal)

        lp = LinearLayout.LayoutParams(btn_width, btn_height)
        lp.setMargins(btn_margin, btn_margin, btn_margin, btn_margin)
        btn.setLayoutParams(lp)

        row_layout.addView(btn)

    lp_main = LinearLayout.LayoutParams(
        LinearLayout.LayoutParams.MATCH_PARENT,
        AndroidUtilities.dp(300)
    )

    scroll_view.setTag(VIEW_TAG)
    scroll_view.setVisibility(View.GONE)
    scroll_view.setLayoutParams(lp_main)

    scroll_view.setClickable(True)
    scroll_view.setFocusable(True)

    return scroll_view


def force_update_ui(emoji_view):
    try:
        type_tabs = get_private_field(emoji_view, "typeTabs")
        pager = get_private_field(emoji_view, "pager")

        if pager and pager.getAdapter():
            pager.getAdapter().notifyDataSetChanged()

        if type_tabs and pager:
            methods = type_tabs.getClass().getMethods()
            for m in methods:
                if m.getName() == "setViewPager" and len(m.getParameterTypes()) == 1:
                    m.invoke(type_tabs, pager)
                    logcat("UI Updated")
                    break
    except Exception as e:
        logcat(f"UI update failed: {e}")