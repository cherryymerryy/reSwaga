"""



                            ДИСКЛЕЙМЕР

Если при создании своего плагина вы решили использовать готовые кодовые решения
нашего плагина у себя, то не забудьте упомянуть в описании своего плагина
канал @MeeowPlugins в качестве кредитов за помощь в разработке плагина. Спасибо


                  ⣾⡇⣿⣿⡇⣾⣿⣿⣿⣿⣿⣿⣿⣿⣄⢻⣦⡀⠁⢸⡌⠻⣿⣿⣿⡽⣿⣿
                  ⡇⣿⠹⣿⡇⡟⠛⣉⠁⠉⠉⠻⡿⣿⣿⣿⣿⣿⣦⣄⡉⠂⠈⠙⢿⣿⣝⣿
                  ⠤⢿⡄⠹⣧⣷⣸⡇⠄⠄⠲⢰⣌⣾⣿⣿⣿⣿⣿⣿⣶⣤⣤⡀⠄⠈⠻⢮
                  ⠄⢸⣧⠄⢘⢻⣿⡇⢀⣀⠄⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠄⢀
                  ⠄⠈⣿⡆⢸⣿⣿⣿⣬⣭⣴⣿⣿⣿⣿⣿⣿⣿⣯⠝⠛⠛⠙⢿⡿⠃⠄⢸
                  ⠄⠄⢿⣿⡀⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⡾⠁⢠⡇⢀
                  ⠄⠄⢸⣿⡇⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⣫⣻⡟⢀⠄⣿⣷⣾
                  ⠄⠄⢸⣿⡇⠄⠈⠙⠿⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣿⣿⡿⢠⠊⢀⡇⣿⣿
                  ⠒⠤⠄⣿⡇⢀⡲⠄⠄⠈⠙⠻⢿⣿⣿⠿⠿⠟⠛⠋⠁⣰⠇⠄⢸⣿⣿⣿



                            DISCLAIMER

If, when creating your plugin, you decided to use the ready-made code solutions
of our plugin, then do not forget to mention the @MeeowPlugins channel in the description
of your plugin as credits for help in developing your plugin. Thanks



"""

import datetime
import os
import random
import re
import textwrap
import threading
import time
from io import BytesIO
from typing import Optional, Any, Callable, List

import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from android.content import Intent  # type: ignore
from android.graphics import Color  # type: ignore
from android.net import Uri  # type: ignore
from android.view import View, Gravity, ViewGroup, MotionEvent  # type: ignore
from android.widget import LinearLayout, FrameLayout, ScrollView, TextView  # type: ignore
from android_utils import run_on_ui_thread
from base_plugin import (
    BasePlugin,
    HookResult,
    HookStrategy,
    MenuItemData,
    MenuItemType
)
from client_utils import (
    get_last_fragment,
    get_user_config,
    get_send_messages_helper,
    send_message,
    get_messages_controller,
    send_request,
    get_messages_storage,
    get_account_instance
)
from com.exteragram.messenger.plugins import PluginsController  # type: ignore
from com.exteragram.messenger.plugins.ui import PluginSettingsActivity  # type: ignore
from com.exteragram.messenger.utils import AppUtils  # type: ignore
from elyx import strings, assets  # type: ignore
from java import dynamic_proxy  # type: ignore
from java.io import File  # type: ignore
from java.lang import Integer, Math, Class, Boolean, Integer, Float  # type: ignore
from java.lang.reflect import Array, Modifier  # type: ignore
from java.util import ArrayList  # type: ignore
from markdown_utils import parse_markdown
from org.telegram.messenger import ApplicationLoader, R, AndroidUtilities, SendMessagesHelper, MessageObject, \
    MediaController, ChatObject  # type: ignore
from org.telegram.tgnet import TLRPC  # type: ignore
from org.telegram.tgnet.tl import TL_account  # type: ignore
from org.telegram.ui import ChatActivity  # type: ignore
from org.telegram.ui.Components import LayoutHelper  # type: ignore
from org.telegram.ui.Stories.recorder import ButtonWithCounterView  # type: ignore
from ui.alert import AlertDialogBuilder
from ui.settings import Selector, Input, Divider, Header, Switch, Text

from .constants import *
from .keyboard.hooks.adapter_get_icon_hook import AdapterGetIconHook
from .keyboard.hooks.adapter_get_title_hook import AdapterGetTitleHook
from .keyboard.hooks.check_grid_visibility_hook import CheckGridVisibilityHook
from .keyboard.hooks.emoji_view_constructor_hook import EmojiViewConstructorHook
from .keyboard.hooks.set_allow_hook import SetAllowHook
from .keyboard.keyboard_utils import get_java_class, find_constructor_exact, find_method_exact
from .poller import Poller
from .services.base_service import BasePlatform, get_platform, get_download_link, get_songlink
from .services.lastfm import LastFm
from .services.service_type import Platform
from .services.soundcloud import SoundCloud
from .services.spotify import Spotify
from .services.telegram import TgMusic
from .services.track import Track
from .services.vk_music import VkMusic
from .services.yandex_music import YandexMusic
from .utils.cache_utils import is_cached_values_exist, initialize_cached_platforms_values, get_cached_value, \
    save_platform_value, get_cached_values, is_cached_value_exist
from .utils.image_utils import get_cover_accent_color, adjust_color_for_readability, get_font_family
from .utils.stream_utils import get_local_stream_id, set_profile_saved_track, save_stream_account_id, \
    create_minimal_id3_mp3
from .utils.utils import logcat, show_success, show_error, get_temp_dir, show_info, open_plugin_settings, \
    get_platform_logo_path, copy, delete_file_delayed


class ReSwagaPlugin(BasePlugin):
    def __init__(self):
        super().__init__()

        self.platform: BasePlatform | None = None
        self.poller: Optional[Poller] = None
        self.spinner: Optional[AlertDialogBuilder] = None
        self.info: Optional[AlertDialogBuilder] = None
        self.loading: Optional[AlertDialogBuilder] = None
        self.hooks = []

    def on_plugin_load(self):
        try:
            get_temp_dir()

            stream_bio_enabled: bool = self.get_setting("stream_bio_enabled", False)
            stream_account_id: int = get_local_stream_id()

            enable = any([
                stream_bio_enabled,
                self.get_setting("fast_card_render", False)
            ])
            self.set_poller_enabled(enable)

            user_id: int = get_user_config().getClientUserId()
            if stream_account_id == 0 and get_local_stream_id() != user_id:
                self.set_new_stream_account()

            current_platform = self.get_setting("selected_platform", 0)
            if current_platform != int(Platform.NotSelected.value[0]):
                self.update_platform_object(current_platform, True)

            if not self.is_poller_enabled() and self.enabled and not self.platform is None:
                self.poller.start_poller()

            if self.get_setting("default_stream_text", DEFAULT_STREAM_TEXT) == DEFAULT_STREAM_TEXT:
                self.save_default_user_bio()

            if self.get_setting("enable_auth_data_cache", False):
                if not is_cached_values_exist():
                    initialize_cached_platforms_values()
                else:
                    if current_platform != int(Platform.NotSelected.value[0]):
                        cached_value = get_cached_value(current_platform)
                        current_value = self.get_setting("value", "")

                        if cached_value != current_value:
                            save_platform_value(current_platform, current_value)

            if self.get_setting("enable_auth_data_cache", False):
                self.set_menu_items(False)

            self.add_on_send_message_hook()
            self.add_hook('TL_messages_sendMedia')
            self._setup_hooks()

            self.update_stream_place()

            logcat(f"Plugin loaded.")
        except Exception as _:
            import traceback
            logcat(traceback.format_exc())

    def on_plugin_unload(self):
        if self.poller is not None:
            self.set_poller_enabled(False)
            self.poller = None

        self.remove_hook('TL_messages_sendMedia')
        for h in self.hooks:
            self.unhook_method(h)
        self.hooks.clear()

        logcat(f"Plugin unloaded.")

    def create_settings(self):
        platforms = [p.value[1] for p in Platform]
        selected_platform = self.get_setting("selected_platform", 0)
        is_value_valid = self.is_platform_value_valid(selected_platform)

        settings = [
            Header(text=strings.Alert_Donate_Header),
            Text(
                text="TON",
                icon="msg_ton",
                accent=True,
                on_click=lambda view: copy("UQBVxjueXqAEpALX_b0yr-ytXN26LOTpSBn26b9VRHKrmm5F")
            ),
            Text(
                text="Card (Alfa-Bank)",
                icon="msg_payment_card",
                accent=True,
                on_click=lambda view: copy("2200154564046463")
            ),
            Divider(),
            Header(text=strings.Settings_Auth_Header),
            Selector(
                key="selected_platform",
                text=strings.Settings_Auth_Platform,
                icon="msg_tone_on",
                items=platforms,
                default=0,
                on_change=lambda new_value: self.update_platform_object(new_value, False)
            )
        ]

        if selected_platform == int(Platform.NotSelected.value[0]):
            return settings

        if selected_platform != int(Platform.TgMusic.value[0]):
            settings += [
                Input(
                    key="value",
                    text=strings.Settings_Auth_Value_Text if self.platform.value_text is None else self.platform.value_text,
                    on_change=lambda _: self.update_platform_object(self.get_setting("selected_platform", 0), True),
                    icon="msg_pin_code"
                ) if selected_platform != int(Platform.NotSelected.value[0]) and selected_platform != int(Platform.TgMusic.value[0]) else None
            ]

        if self.platform.pre_auth_settings:
            pre_auth_settings = self.platform.create_pre_auth_settings(self)
            if len(pre_auth_settings) > 0:
                settings += [
                    Divider(),
                    Header(text=get_platform(selected_platform).value[1])
                ]
                settings += pre_auth_settings

                if self.platform.additional_settings:
                    additional_settings = self.platform.create_additional_settings(self)
                    if len(additional_settings) > 0:
                        settings += additional_settings

        if not is_value_valid and selected_platform != int(Platform.TgMusic.value[0]):
            return settings

        advanced = self.get_setting('advanced_mode', False)

        settings += [
            Divider(),

            Header(text='Cobalt API'),
            Selector(
                key='cobalt_api_url',
                text=strings.Settings_CobaltApi_Text,
                default=1,
                items=COBALT_API_URLS,
                icon='msg_instant_link'
            ),
            Input(
                key='cobalt_api_url_custom',
                text=strings.Settings_CobaltApi_Custom_Text,
                subtext=strings.Settings_CobaltApi_Subtext,
                default=DEFAULT_COBALT_API_URL,
                icon='msg2_devices'
            ) if self.get_setting('cobalt_api_url', 1) == 0 else None,
            Divider(),

            Header(text=strings.Settings_CardSettings_Header),
            Selector(
                key='card_type',
                text=strings.Settings_CardType_Header,
                default=0,
                icon="msg_background",
                items=[
                    strings.Settings_CardType_1,
                    strings.Settings_CardType_2
                ]
            ),
            Selector(
                key="background",
                text=strings.Settings_BackgroundMode_Text,
                default=1,
                items=[
                    strings.Settings_BackgroundMode_Item_1,
                    strings.Settings_BackgroundMode_Item_2
                ],
                icon="msg_photos"
            ),
            Selector(
                key="font",
                text=strings.Settings_Font_Text,
                default=0,
                items=[
                    strings.Settings_Font_Item1,
                    strings.Settings_Font_Item2,
                    strings.Settings_Font_Item3,
                    "Yandex Music",
                    "Yandex Text",
                ],
                icon="msg_photo_text_regular"
            ),
            Selector(
                key="platform_link",
                text=strings.Settings_PlatformLink_Text,
                default=1,
                items=[
                    strings.Settings_PlatformLink_Item_1,
                    strings.Settings_PlatformLink_Item_2,
                    strings.Settings_PlatformLink_Item_3
                ],
                icon="msg_link2"
            ) if selected_platform != int(Platform.TgMusic.value[0]) else None,
            Switch(
                key="songlink_link_include",
                text=strings.Settings_SongLinkInclude_Text,
                default=True,
                subtext=strings.Settings_SongLinkInclude_Subtext,
                icon="msg_language"
            ),
            Switch(
                key="fast_card_render",
                text=strings.Settings_FastCardRender_Text,
                default=False,
                subtext=strings.Settings_FastCardRender_Subtext,
                on_change=lambda new_value: self.set_fast_card_render_enabled(new_value),
                icon="boosts_solar"
            ),

            Switch(
                key="advanced_mode",
                text=strings.Setting_AdvancedMode_Text,
                default=False,
                subtext=strings.Setting_AdvancedMode_Subtext,
                icon="msg_palette"
            ),
            Text(
                text=strings.Setting_AdvancedMode_Title,
                icon="msg_download_settings",
                create_sub_fragment=self.create_customization_settings
            ) if advanced else None,

            Divider(),

            Header(text=strings.Settings_Stream_Header),
            Switch(
                key="stream_bio_enabled",
                text=strings.Settings_Stream_Text,
                default=False,
                subtext=strings.Settings_Stream_Subtext,
                on_change=lambda new_value: self.set_stream_bio_enabled(new_value),
                icon="msg_online"
            ),
            Text(
                text=strings.Settings_Stream_AccountId,
                on_click=lambda _: self.set_new_stream_account(),
                accent=True,
                icon="msg_mention"
            ) if get_user_config().getClientUserId() != get_local_stream_id() else None,
            Text(
                text=strings.Setting_Stream_Title,
                icon="msg_download_settings",
                create_sub_fragment=self.create_stream_settings
            ),
            Divider(text=strings.Settings_Stream_Alert),

            Header(text=strings.Settings_Cache_Header),
            Switch(
                key="enable_auth_data_cache",
                text=strings.Setting_Cache_Enable_Text,
                icon="menu_clear_cache",
                default=True,
                on_change=lambda new_value: self.update_cache(new_value)
            ),
            Text(
                text=strings.Setting_Cache_DeleteCached,
                icon="msg_delete",
                red=True,
                on_click=lambda _: self.clear_cached_platforms_values()
            ) if self.get_setting("enable_auth_data_cache", False) else None
        ]

        return settings

    def create_customization_settings(self):
        return [
            Input(
                key="background_color",
                text=strings.Settings_BackgroundColor_Text,
                default=DEFAULT_COLOR["background_color"],
                subtext=strings.Settings_BackgroundColor_Subtext,
                icon="menu_feature_custombg",
                on_change=lambda new_value: self.is_hex_valid(new_value, "background_color")
            ) if self.get_setting("background", 1) == 1 else None,
            Input(
                key="title_text_color",
                text=strings.Settings_AccentColor_Text,
                default=DEFAULT_COLOR["title_text_color"],
                subtext=strings.Settings_AccentColor_Subtext,
                icon="msg_photo_text_framed",
                on_change=lambda new_value: self.is_hex_valid(new_value, "title_text_color")
            ),
            Input(
                key="subtext_color",
                text=strings.Settings_SecondaryColor_Text,
                default=DEFAULT_COLOR["subtext_color"],
                subtext=strings.Settings_SecondaryColor_Subtext,
                icon="msg_photo_text_framed2",
                on_change=lambda new_value: self.is_hex_valid(new_value, "subtext_color")
            ),
            Input(
                key="instant_subtext",
                text=strings.Settings_InstantCardSubtext_Text,
                default=DEFAULT_INSTANT_SUBTEXT,
                subtext=strings.Settings_InstantCardSubtext_Subtext,
                icon="menu_feature_intro"
            ),
            Input(
                key="instant_main_text",
                text=strings.Settings_InstantCardMainText_Text,
                default=DEFAULT_INSTANT_MAIN_TEXT,
                subtext=strings.Settings_InstantCardMainText_Subtext,
                icon="menu_feature_cover"
            ),
            Switch(
                key="show_service_logo",
                text=strings.Settings_Vertical_ShowServiceLogo_Text,
                default=True,
                icon="msg_archive_hide" if not self.get_setting("show_service_logo", True) else "msg_message",
            ) if self.get_setting("card_type", 0) else None
        ]

    def create_stream_settings(self):
        stream_places: List[str] = [strings.Setting_TrackStream_Item1]

        if get_user_config().isPremium():
            stream_places.append(strings.Setting_TrackStream_Item2)

        # stream_places.append(strings.Setting_TrackStream_Item3)

        stream_place = self.get_setting("stream_place", 0)
        is_to_profile_stream = stream_place == 2 or (stream_place == 1 and not get_user_config().isPremium())

        return [
            Selector(
                key="stream_place",
                text=strings.Setting_TrackStream_Text,
                default=0,
                items=stream_places,
                icon="menu_premium_location" if self.get_setting("stream_place", 0) else "msg_openprofile"
            ),
            Input(
                key="default_stream_text",
                text=strings.Settings_InStream_Text,
                default=DEFAULT_STREAM_TEXT,
                subtext=strings.Settings_InStream_Subtext,
                icon="msg_photo_text_framed3"
            ) if not is_to_profile_stream else None,
            Input(
                key="track_display_format",
                text=strings.Settings_FormatInStream_Text,
                default=DEFAULT_STREAM_STRING,
                subtext=strings.Settings_FormatInStream_Subtext,
                icon="msg_view_file"
            ) if not is_to_profile_stream else None
        ]

    def set_menu_items(self, remove: bool):
        def on_menu_item_click(new_platform: int):
            self.set_menu_items(True)
            self.set_setting('selected_platform', new_platform)
            self.create_settings()

            platform: Platform = get_platform(new_platform)

            if self.get_setting('selected_platform', int(Platform.NotSelected.value[0])) == new_platform:
                self.update_platform_object(new_platform, False)
                self.set_menu_items(False)

                success_text = strings.MenuItem_Service_Success.format(platform.value[1])

                if self.get_setting('value', DEFAULT_VALUE) in ['', None, DEFAULT_VALUE] and platform != Platform.TgMusic:
                    show_info(
                        message=f'\n{success_text}\n{strings.MenuItem_Service_Success_Subtext}',
                        on_click=lambda: open_plugin_settings(),
                        button_text=strings.Check_Value_NotValid_Button
                    )
                else:
                    show_success(success_text)
            else:
                show_error(strings.MenuItem_Service_Fail.format(pl.value[1]))

        selected_platform = self.get_setting('selected_platform', int(Platform.NotSelected.value[0]))
        platforms = [p for p in Platform if p.value[0] != selected_platform and p.value[0] != int(Platform.NotSelected.value[0])]

        for pl in platforms:
            cleared_item_name: str = str(pl.value[1]).lower().strip().replace(" ", "").replace(".", "")
            item_id: str = f'{cleared_item_name}-{pl.value[0]}'

            if remove:
                self.remove_menu_item(item_id)
            else:
                self.add_menu_item(
                    menu_item_data=MenuItemData(
                        menu_type=MenuItemType.CHAT_ACTION_MENU,
                        item_id=item_id,
                        icon='msg_tone_on',
                        text=strings.MenuItem_Service_Select_Text.format(pl.value[1]),
                        # subtext=strings.MenuItem_Service_Select_Subtext,
                        on_click=lambda _, p=pl: on_menu_item_click(int(p.value[0]))
                    )
                )

    def on_send_message_hook(self, account: int, params: Any):
        has_caption = hasattr(params, 'caption') and isinstance(params.caption, str)
        has_text = hasattr(params, 'message') and isinstance(params.message, str)

        if has_caption or has_text:
            is_modified = False
            current_text = params.caption if has_caption else params.message

            try:
                metadata_flag = f"{__name__}_flag_metadata"
                markdown_flag = f"{__name__}_flag_markdown"

                if metadata_flag in current_text:

                    if self.is_poller_enabled():
                        track = self.platform.now_track
                    else:
                        track = self.platform.get_track()

                    if has_caption:
                        attributes = params.document.attributes
                        for i in range(attributes.size()):
                            attr = attributes.get(i)
                            if isinstance(attr, TLRPC.TL_documentAttributeAudio):
                                attr.title = track.title if track.active else f"[{__name__}] ERROR"
                                attr.performer = ", ".join(track.artist) if track.active else strings.Track_Not_Active
                                attr.duration = track.duration if track.active else 0

                    current_text = current_text.replace(" " + metadata_flag, "")
                    is_modified = True

                if markdown_flag in current_text:
                    try:
                        current_text = current_text.replace(" " + markdown_flag, "")

                        caption = parse_markdown(current_text)
                        current_text = caption.text

                        new_entities = ArrayList()
                        for i in caption.entities:
                            new_entities.add(i.to_tlrpc_object())
                        params.entities = new_entities

                        is_modified = True
                    except Exception as e:
                        import traceback
                        logcat(traceback.format_exc())

                params.searchLinks = False

                if is_modified:
                    if has_caption:
                        params.caption = current_text
                    elif has_text:
                        params.message = current_text

                    return HookResult(HookStrategy.MODIFY, params=params)
                else:
                    return HookResult(strategy=HookStrategy.DEFAULT)

            except Exception as e:
                import traceback
                logcat(traceback.format_exc())
                return HookResult(strategy=HookStrategy.DEFAULT)

        else:
            return HookResult(strategy=HookStrategy.DEFAULT)

    def post_request_hook(self, request_name: str, account: int, response: Any, error: Any) -> HookResult:
        if not self.get_setting('stream_bio_enabled', False):
            logcat('Streamer disabled')
            return HookResult(strategy=HookStrategy.DEFAULT)

        stream_place = self.get_setting('stream_place', 0)
        if stream_place == 2 or (stream_place == 1 and not get_user_config().isPremium()):
            set_profile_saved_track(response)
            return HookResult(strategy=HookStrategy.DEFAULT)

        logcat('Stream place not valid')
        return HookResult(strategy=HookStrategy.DEFAULT)

    def _setup_hooks(self):
        try:
            emoji_view = get_java_class("org.telegram.ui.Components.EmojiView")
            if not emoji_view: return

            base_fragment = get_java_class("org.telegram.ui.ActionBar.BaseFragment")
            resources_provider = get_java_class("org.telegram.ui.ActionBar.Theme$ResourcesProvider")
            chat_full = get_java_class("org.telegram.tgnet.TLRPC$ChatFull")
            context = get_java_class("android.content.Context")
            view_group = get_java_class("android.view.ViewGroup")

            ctor = find_constructor_exact(
                emoji_view,
                base_fragment, # fragment
                Boolean.TYPE, # needAnimatedEmoji
                Boolean.TYPE, # needStickers
                Boolean.TYPE, # needGif
                context, # context
                Boolean.TYPE, # needSearch
                chat_full, # chatFull
                view_group, # parentView
                Boolean.TYPE, # shouldDrawBackground
                resources_provider, # resourcesProvider
                Boolean.TYPE, # frozenAtStart
                Boolean.TYPE # glassDesign
            )

            if ctor is None:
                ctor = find_constructor_exact(
                    emoji_view,
                    base_fragment,  # fragment
                    Boolean.TYPE,  # needAnimatedEmoji
                    Boolean.TYPE,  # needStickers
                    Boolean.TYPE,  # needGif
                    context,  # context
                    Boolean.TYPE,  # needSearch
                    chat_full,  # chatFull
                    view_group,  # parentView
                    Boolean.TYPE,  # shouldDrawBackground
                    resources_provider,  # resourcesProvider
                    Boolean.TYPE  # frozenAtStart
                )

            if ctor is None:
                logcat("Failed to find EmojiView constructor")
                return

            if ctor: self.hooks.append(self.hook_method(ctor, EmojiViewConstructorHook(self)))

            set_allow = find_method_exact(emoji_view, "setAllow", Boolean.TYPE, Boolean.TYPE, Boolean.TYPE)
            if set_allow: self.hooks.append(self.hook_method(set_allow, SetAllowHook(self)))

            check_grid = find_method_exact(emoji_view, "checkGridVisibility", Integer.TYPE, Float.TYPE)
            if check_grid: self.hooks.append(self.hook_method(check_grid, CheckGridVisibilityHook(self)))

            adapter_class = get_java_class("org.telegram.ui.Components.EmojiView$EmojiPagesAdapter")
            if adapter_class:
                get_icon = find_method_exact(adapter_class, "getPageIconDrawable", Integer.TYPE)
                if get_icon: self.hooks.append(self.hook_method(get_icon, AdapterGetIconHook(self)))

                get_title = find_method_exact(adapter_class, "getPageTitle", Integer.TYPE)
                if get_title: self.hooks.append(self.hook_method(get_title, AdapterGetTitleHook(self)))

        except Exception as e:
            import traceback
            logcat(traceback.format_exc())
            logcat(f"Setup error: {e}")

    def set_new_stream_account(self):
        save_stream_account_id(get_user_config().getClientUserId())
        self.save_default_user_bio()
        self.set_setting("stream_bio_enabled", self.get_setting("stream_bio_enabled", False))

    def is_platform_value_valid(self, platform: int) -> bool:
        value = str(self.get_setting("value", ""))
        if platform == int(Platform.YandexMusic.value[0]):
            return not len(value) <= 4 and not value in ["", None, DEFAULT_VALUE]
        elif platform == int(Platform.TgMusic.value[0]):
            return True
        else:
            return not value in ["", None, DEFAULT_VALUE]

    def update_cache(self, new_value: bool):
        initialize_cached_platforms_values()
        if new_value:
            self.set_menu_items(False)
            save_platform_value(
                self.get_setting("selected_platform", int(Platform.NotSelected.value[0])),
                self.get_setting("value", "")
            )
        else:
            self.set_menu_items(True)

    def clear_cached_platforms_values(self):
        initialize_cached_platforms_values()
        cached_values = get_cached_values()
        values = [cl for cl in cached_values if cl == DEFAULT_VALUE]
        if len(values) == PLATFORMS_COUNT:
            save_platform_value(
                self.get_setting("selected_platform", int(Platform.NotSelected.value[0])),
                self.get_setting("value", "")
            )
            show_success(strings.CachedAuthData_Clear_Success)
        else:
            show_error(strings.CachedAuthData_Clear_Error)

    def download_track_with_cobalt(self, url: str, track: Track) -> Optional[str]:
        api_url_index: int = self.get_setting('cobalt_api_url', 1)

        if api_url_index == 0:
            api_url = self.get_setting('cobalt_api_url_custom', DEFAULT_COBALT_API_URL)

            if api_url in ['', None]:
                api_url = DEFAULT_COBALT_API_URL
        else:
            api_url: str = COBALT_API_URLS[api_url_index]

        payload: Dict[str, str] = {
            "url": url,
            "downloadMode": "audio",
            "audioBitrate": "320",
            "audioFormat": "best"
        }
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            try:
                response = requests.post(f"{api_url}/", json=payload, headers=headers, timeout=30)
                response.raise_for_status()
            except Exception as e:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                show_error(strings.Bulletin_InvalidCobaltResponse)
                logcat(f"Cobalt Request Error: {e} | data = {payload}")
                return None

            data = response.json()
            logcat(f"Cobalt Response Data: {data}")

            status = data.get("status")

            if status == "error":
                code = data.get("error", {}).get("code", "Unknown error")
                show_error(strings.Bulletin_CobaltErrorCode.format(code))
                return None

            elif status == "picker":
                items = data.get("picker", [])
                if not items:
                    show_error(strings.Bulletin_NoItemsToDownload)
                    return None
                item = items[0]
                direct_url = item.get("url")
                original_filename = item.get("filename")

            elif status in ["stream", "redirect", "success", "tunnel"]:
                direct_url = data.get("url")
                original_filename = data.get("filename")

            else:
                logcat(f"Cobalt Warning: Received an unhandled status: '{status}'")
                show_error(strings.Bulletin_InvalidCobaltResponse)
                return None

            if not direct_url:
                show_error(strings.Bulletin_InvalidCobaltResponse)
                return None

            temp_dir = get_temp_dir()

            file_extension = original_filename.split('.')[-1] if original_filename and '.' in original_filename else 'mp3'
            filename: str = f"{track.title} (via {__name__}).{file_extension}"
            file_path: str = File(temp_dir, filename).getAbsolutePath()

            logcat(f"Downloading audio in background thread: {filename}")

            try:
                track_resp = requests.get(direct_url, stream=True, timeout=60)
                track_resp.raise_for_status()
            except Exception as e:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat(f"Cobalt Download Error: {e}")
                show_error(strings.Bulletin_InvalidCobaltResponse)
                return None

            with open(file_path, "wb") as f:
                for chunk in track_resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            ext_root = ApplicationLoader.applicationContext.getExternalCacheDir()
            plugin_dir = File(ext_root, TEMP_DIR_NAME)
            ext_path = File(plugin_dir, File(file_path).getName()).getAbsolutePath()

            with open(file_path, 'rb') as fin, open(ext_path, 'wb') as fout:
                fout.write(fin.read())

            return file_path
        except Exception as _:
            import traceback
            logcat(traceback.format_exc())

    def send_card_message(self, param):
        try:
            run_on_ui_thread(lambda: self.show_spinner())
            params = {
                "message": None,
                "peer": param.peer
            }

            if self.is_poller_enabled():
                track = self.platform.now_track
            else:
                track = self.platform.get_track()

            if track is None:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat("z1")
                show_error(strings.Track_Not_Active)
                return

            if not track.active:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat("z2")
                show_error(strings.Track_Not_Active)
                return

            temp_dir = get_temp_dir()
            temp_file_path = None

            card_type: int = self.get_setting('card_type', 0)

            if card_type == 0:
                card = self.create_horizontal_card()
            elif card_type == 1:
                card = self.create_vertical_card()
            else:
                card = None

            answer = card if not (self.get_setting("fast_card_render", False)) else True
            if answer:
                temp_file_path = File(temp_dir, f"now_{__name__}.png").getAbsolutePath()

            if temp_file_path in ["", None]:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat("z3")
                show_error(strings.Track_Not_Active)
                return

            generated_photo = get_send_messages_helper().generatePhotoSizes(temp_file_path, None)

            if generated_photo is None:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat("z4")
                show_error(strings.Track_Not_Active)
                return

            params["photo"] = generated_photo
            params["path"] = temp_file_path
            params["replyToMsg"] = param.replyToMsg
            params["replyToTopMsg"] = param.replyToTopMsg

            if not track.active:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                logcat("z5")
                show_error(strings.Track_Not_Active)
                return

            platform = self.get_setting("selected_platform", 0)

            platform_link: int = self.get_setting("platform_link", 1)
            platform_link_added: bool = False

            songlink: bool = self.get_setting("songlink_link_include", True)
            songlink_added: bool = False

            caption: str = ""

            if (platform_link and platform_link != 0) and platform != int(Platform.TgMusic.value[0]):
                link = track.link if (platform_link == 1 or track is None) else track.album
                caption += strings.Message_CaptionLink_Text.format(get_platform(platform).value[1], link)
                platform_link_added = True

            if songlink and songlink != 0:
                if platform_link_added:
                    caption += strings.Message_CaptionDivider

                songlink_platform = get_songlink(platform)

                if not songlink_platform is '':
                    caption += strings.Message_CaptionSongLink_Text.format(f"https://song.link/{songlink_platform}/{track.id}")
                    songlink_added = True

            if any([platform_link_added, songlink_added]):
                emoji: str = random.choice(["[🎵](5188621441926438751) | ", "[🎶](5188705588925702510) | "])
                caption = emoji + caption

                parsed_caption = parse_markdown(caption)
                params["caption"] = parsed_caption.text
                params["entities"] = set()

                for i in parsed_caption.entities:
                    params["entities"].add(i.to_tlrpc_object())

            run_on_ui_thread(lambda: send_message(params))
            run_on_ui_thread(lambda: self.dismiss_spinner())
        except Exception as _:
            run_on_ui_thread(lambda: self.dismiss_spinner())
            show_error(strings.Track_Not_Active)
            import traceback
            logcat(f'send_card_message: {traceback.format_exc()}')

    def send_audio_message(self, param, silent: bool = False) -> bool:
        if not silent:
            run_on_ui_thread(lambda: self.show_spinner())

        if self.is_poller_enabled():
            track = self.platform.now_track
        else:
            track = self.platform.get_track()

        if not track.active:
            run_on_ui_thread(lambda: self.dismiss_spinner())
            if not silent:
                show_error(strings.Track_Not_Active)
            return False

        if not self.platform.can_download_track:
            run_on_ui_thread(lambda: self.dismiss_spinner())
            if not silent:
                show_error(strings.Check_Platform_DownloadNotAvailable)
            return False

        url = track.download_url
        temp_dir = get_temp_dir()

        try:
            if not url is None:
                ext = os.path.splitext(url)[1] or ".mp3"
                filename = f"{track.title}{ext}"
                file_path = File(temp_dir, filename).getAbsolutePath()
                resp = requests.get(url, stream=True, timeout=60)
                resp.raise_for_status()

                with open(file_path, 'wb') as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)

                ext_root = ApplicationLoader.applicationContext.getExternalCacheDir()
                plugin_dir = File(ext_root, TEMP_DIR_NAME)

                if not plugin_dir.exists() and not plugin_dir.mkdirs():
                    pass

                ext_path = File(plugin_dir, File(file_path).getName()).getAbsolutePath()

                with open(file_path, 'rb') as fin, open(ext_path, 'wb') as fout:
                    fout.write(fin.read())

                delete_file_delayed(file_path)
            else:
                new_url = get_download_link(
                    platform=self.get_setting('selected_platform', int(Platform.NotSelected.value[0])),
                    track_id=track.id
                )

                if new_url in ['', None]:
                    run_on_ui_thread(lambda: self.dismiss_spinner())
                    return False

                file_path = self.download_track_with_cobalt(new_url, track)
                if file_path in ['', None] or not os.path.exists(file_path):
                    run_on_ui_thread(lambda: self.dismiss_spinner())
                    return False

                ext_root = ApplicationLoader.applicationContext.getExternalCacheDir()
                plugin_dir = File(ext_root, TEMP_DIR_NAME)
                ext_path = File(plugin_dir, File(file_path).getName()).getAbsolutePath()

            account = get_account_instance()

            if ext_path.endswith('.opus'):
                mime = 'audio/opus'
            else:
                mime = 'audio/mpeg'

            platform = self.get_setting("selected_platform", 0)

            platform_link: int = self.get_setting("platform_link", 1)
            platform_link_added: bool = False

            songlink: bool = self.get_setting("songlink_link_include", True)
            songlink_added: bool = False

            caption: str = ""

            if (platform_link and platform_link != 0) and platform != int(Platform.TgMusic.value[0]):
                link = track.link if (platform_link == 1 or track is None) else track.album
                caption += strings.Message_CaptionLink_Text.format(get_platform(platform).value[1], link)
                platform_link_added = True

            if songlink and songlink != 0:
                if platform_link_added:
                    caption += strings.Message_CaptionDivider

                caption += strings.Message_CaptionSongLink_Text.format(f"https://song.link/{get_songlink(platform)}/{track.id}")
                songlink_added = True

            if any([platform_link_added, songlink_added]):
                emoji: str = random.choice(["[🎵](5188621441926438751) | ", "[🎶](5188705588925702510) | "])
                caption = emoji + caption

            markdown_need = any([platform_link_added, songlink_added])

            SendMessagesHelper.prepareSendingDocument(
                account,
                ext_path,
                ext_path,
                None,
                f"{caption} {__name__}_flag_metadata{f' {__name__}_flag_markdown' if markdown_need else ''}",
                mime,
                param.peer,
                param.replyToMsg,
                param.replyToTopMsg,
                None, None, None, True, 0, None, None, 0, False
            )

            if not silent:
                run_on_ui_thread(lambda: self.dismiss_spinner())

            delete_file_delayed(ext_path)
            return True
        except Exception as e:
            logcat(str(e))

            if not silent:
                run_on_ui_thread(lambda: self.dismiss_spinner())
                show_error(strings.Track_Not_Active)

            return False

    def send_text_message(self, param):
        run_on_ui_thread(lambda: self.show_spinner())

        if self.is_poller_enabled():
            track = self.platform.now_track
        else:
            track = self.platform.get_track()

        if not track.active:
            run_on_ui_thread(lambda: self.dismiss_spinner())
            show_error(strings.Track_Not_Active)
            return

        platform = self.get_setting("selected_platform", 0)

        platform_link: int = self.get_setting("platform_link", 1)
        platform_link_added: bool = False

        songlink: bool = self.get_setting("songlink_link_include", True)
        songlink_added: bool = False

        text: str = ""
        track_info: str = f"{track.title} - {','.join(track.artist)}\n"

        if (platform_link and platform_link != 0) and platform != int(Platform.TgMusic.value[0]):
            link = track.link if (platform_link == 1 or track is None) else track.album
            text += strings.Message_CaptionLink_Text.format(get_platform(platform).value[1], link)
            platform_link_added = True

        if songlink and songlink != 0:
            if platform_link_added:
                text += strings.Message_CaptionDivider

            text += strings.Message_CaptionSongLink_Text.format(f"https://song.link/{get_songlink(platform)}/{track.id}")
            songlink_added = True

        if any([platform_link_added, songlink_added]):
            emoji: str = random.choice(["[🎵](5188621441926438751) | ", "[🎶](5188705588925702510) | "])
            text = emoji + track_info + text

        markdown_need = any([platform_link_added, songlink_added])
        params = {
            "message": f"{text} {__name__}_flag_metadata{f' {__name__}_flag_markdown' if markdown_need else ''}",
            "peer": param.peer,
            "replyToMsg": param.replyToMsg,
            "replyToTopMsg": param.replyToTopMsg,
        }

        run_on_ui_thread(lambda: send_message(params))
        run_on_ui_thread(lambda: self.dismiss_spinner())

    def update_platform_object(self, new_platform: int, value: bool):
        cache_enabled: bool = self.get_setting("enable_auth_data_cache", False)

        if self.is_poller_enabled():
            self.poller.stop_poller()

        if cache_enabled:
            self.set_menu_items(True)

        if not value:
            if cache_enabled and is_cached_value_exist(new_platform):
                self.set_setting("value", get_cached_value(new_platform))
            else:
                self.set_setting("value", "")

        token = self.get_setting("value", "")
        token_default_values = ["", None, DEFAULT_VALUE]
        new_platform_obj: BasePlatform | None = None

        if cache_enabled and (not new_platform in [int(Platform.NotSelected.value[0]), int(Platform.TgMusic.value[0])]):
            cached_value = get_cached_value(new_platform)
            if token not in token_default_values and token != cached_value:
                save_platform_value(new_platform, token)

        if new_platform == int(Platform.NotSelected.value[0]):
            new_platform_obj = None

        elif new_platform == int(Platform.Spotify.value[0]):
            new_platform_obj = Spotify(token)

        elif new_platform == int(Platform.YandexMusic.value[0]):
            is_custom_api_enabled = self.get_setting("enable_yandex_custom_api", False)
            custom_api = self.get_setting("yandex_custom_api", None)
            custom_api_url: Optional[str] = custom_api if is_custom_api_enabled else None
            new_platform_obj = YandexMusic(token, custom_api_url)

        elif new_platform == int(Platform.SoundCloud.value[0]):
            new_platform_obj = SoundCloud(token)

        elif new_platform == int(Platform.VkMusic.value[0]):
            new_platform_obj = VkMusic(token)

        elif new_platform == int(Platform.TgMusic.value[0]):
            new_platform_obj = TgMusic(token)

        elif new_platform == int(Platform.LastFm.value[0]):
            new_platform_obj = LastFm(token)

        else:
            logcat(f"Unknown platform ({new_platform})")

        self.platform = new_platform_obj

        if self.get_setting("default_stream_text", DEFAULT_STREAM_TEXT) == DEFAULT_STREAM_TEXT:
            self.save_default_user_bio()

        self.set_stream_text(True)

        stream_bio_enabled: bool = self.get_setting('stream_bio_enabled', False)
        fast_card_render: bool = self.get_setting('fast_card_render', False)

        if token not in token_default_values and any([stream_bio_enabled, fast_card_render]):
            self.set_poller_enabled(True)

        if cache_enabled:
            self.set_menu_items(False)

        self.set_setting('value', token, True)

    def is_args_not_valid(self, platform: int) -> bool:
        if platform == int(Platform.NotSelected.value[0]) or self.platform is None:
            show_error(
                message=strings.Check_Platform_NotSelected,
                on_click=lambda: open_plugin_settings(),
                button_text=strings.Check_Platform_NotSelected_Button
            )
            return True

        if self.platform.need_special_platform_args_check and self.platform.special_platform_args_check(self):
            return True

        elif not self.is_platform_value_valid(platform):
            show_error(
                message=strings.Check_Value_NotValid,
                on_click=lambda: open_plugin_settings(),
                button_text=strings.Check_Value_NotValid_Button
            )
            return True

        else:
            return False

    def set_fast_card_render_enabled(self, enable: bool):
        if enable:
            self.poller.start_poller()
        else:
            if not self.get_setting("stream_bio_enabled", False):
                self.poller.stop_poller()

    def save_default_user_bio(self):
        stream_place = self.get_setting("stream_place", 0)
        default_stream_text = self.get_setting("default_stream_text", DEFAULT_STREAM_TEXT)

        client_user_id = get_user_config().getClientUserId()
        if client_user_id is None or client_user_id == 0:
            logcat("Client userId not found")
            return

        user_full = get_messages_controller().getUserFull(client_user_id)
        if user_full is None:
            logcat("User fullInfo not found")
            return

        if stream_place == 0:  # current bio
            if user_full.about and user_full.about != default_stream_text:
                if not str(user_full.about).startswith("🎵 | "):
                    self.set_setting("default_stream_text", user_full.about)

        elif stream_place == 1:  # current address
            if user_full.business_location and user_full.business_location.address and user_full.business_location.address != default_stream_text:
                if not str(user_full.business_location.address).startswith("🎵 | "):
                    self.set_setting("default_stream_text", user_full.business_location.address)

        else:  # Index out of range
            self.set_setting("default_stream_text", DEFAULT_STREAM_TEXT)

    def set_stream_bio_enabled(self, enable: bool):
        if enable:
            self.poller.start_poller()
            self.save_default_user_bio()
            self.set_stream_text(False)
        else:
            self.set_stream_text(True)
            if not self.get_setting("fast_card_render", False):
                self.poller.stop_poller()

    def set_stream_text(self, default: bool):
        if get_local_stream_id() != get_user_config().getClientUserId():
            return

        stream_enable = self.get_setting("stream_bio_enabled", False)
        stream_place = self.get_setting("stream_place", 0)

        if not stream_enable:
            return

        client_user_id = get_user_config().getClientUserId()
        if client_user_id is None or client_user_id == 0:
            logcat("Client userId not found")
            return

        user_full = get_messages_controller().getUserFull(client_user_id)
        if user_full is None:
            logcat("User fullInfo not found")
            return

        current_text: str = ""

        if stream_place == 0:  # current bio
            if user_full.about:
                current_text = user_full.about

        elif stream_place == 1 and get_user_config().isPremium():  # current address
            if user_full.business_location and user_full.business_location.address:
                current_text = user_full.business_location.address

        elif stream_place == 2 or (stream_place == 1 and not get_user_config().isPremium()):
            if not user_full.saved_music is None:
                pass

        else:
            logcat("Index out of range. Can't get current bio text.")

        if self.platform is None or self.platform.now_track is None:
            return

        text_to_set: str

        if default:
            text_to_set = self.get_setting("default_stream_text", DEFAULT_STREAM_TEXT)
        else:
            if self.platform and self.platform.now_track and self.platform.now_track.active:
                text_to_set = self.get_setting("track_display_format", DEFAULT_STREAM_STRING)
                text_to_set = text_to_set.replace("{title}", self.platform.now_track.title)
                text_to_set = text_to_set.replace("{artists}", ", ".join(self.platform.now_track.artist))
            else:
                text_to_set = self.get_setting("default_stream_text", DEFAULT_STREAM_TEXT)

        final_text_to_set = text_to_set
        if stream_place == 0:
            max_len = 140 if get_user_config().isPremium() else 70
            final_text_to_set = text_to_set[:max_len]
        elif stream_place == 1 and get_user_config().isPremium():
            final_text_to_set = text_to_set[:96]

        if final_text_to_set == current_text and (stream_place == 0 or (stream_place == 1 and get_user_config().isPremium())):
            logcat("No need to update bio.")
            return

        if stream_place == 0:  # in bio
            # online update
            request = TL_account.updateProfile()
            request.flags = 4
            request.about = final_text_to_set

            # local update
            user_full.flags = 2
            user_full.about = final_text_to_set

        elif stream_place == 1 and get_user_config().isPremium():  # in business location
            # online update
            request = TL_account.updateBusinessLocation()
            request.flags = 1
            request.address = final_text_to_set

            # local update
            user_full.flags2 = 2
            user_full.business_location = TLRPC.TL_businessLocation()
            user_full.business_location.address = final_text_to_set

        elif stream_place == 2 or (stream_place == 1 and not get_user_config().isPremium()):  # in saved music
            logcat(f'current mem id : {self.platform.memory_id}, new id: {self.platform.now_track.id}')
            if self.platform.memory_id == self.platform.now_track.id:
                return

            self.platform.memory_id = self.platform.now_track.id
            threading.Thread(target=self.download_track_for_stream, daemon=True).start()

            request = None

        else:  # out of range
            logcat("Stream place index out of range.")
            return

        if request:
            try:
                send_request(request, ())
                get_messages_storage().updateUserInfo(user_full, False)
                logcat(f"Updating bio to \"{text_to_set}\"...")
            except Exception as e:
                logcat(f"set_stream_text exception: {e}")

    def download_track_for_stream(self):
        client_user_id = get_user_config().getClientUserId()
        if client_user_id is None or client_user_id == 0:
            return

        if self.platform.can_download_track:
            params = SendMessagesHelper.SendMessageParams()
            params.peer = client_user_id
            result = self.send_audio_message(
                params,
                True
            )

            if result:
                return

        logcat('Failed to download track, creating empty file...')

        track = self.platform.now_track
        temp_dir = get_temp_dir()

        filename: str = f"{track.title} - {','.join(track.artist)}.mp3"
        file_path: str = File(temp_dir, filename).getAbsolutePath()

        create_minimal_id3_mp3(
            file_path,
            track.title,
            ', '.join(track.artist),
            random.randint(30, 240) if track.duration is None else track.duration,
            random.randint(1, 2)
        )

        ext_root = ApplicationLoader.applicationContext.getExternalCacheDir()
        plugin_dir = File(ext_root, TEMP_DIR_NAME)

        if not plugin_dir.exists():
            plugin_dir.mkdirs()

        ext_path = File(plugin_dir, File(file_path).getName()).getAbsolutePath()

        with open(file_path, 'rb') as fin:
            with open(ext_path, 'wb') as fout:
                fout.write(fin.read())

        platform = self.get_setting("selected_platform", 0)

        platform_link: int = self.get_setting("platform_link", 1)
        platform_link_added: bool = False

        songlink: bool = self.get_setting("songlink_link_include", True)
        songlink_added: bool = False

        caption: str = ""

        if (platform_link and platform_link != 0) and platform != int(Platform.TgMusic.value[0]):
            link = track.link if (platform_link == 1 or track is None) else track.album
            caption += strings.Message_CaptionLink_Text.format(get_platform(platform).value[1], link)
            platform_link_added = True

        if songlink and songlink != 0:
            if platform_link_added:
                caption += strings.Message_CaptionDivider

            caption += strings.Message_CaptionSongLink_Text.format(f"https://song.link/{get_songlink(platform)}/{track.id}")
            songlink_added = True

        if any([platform_link_added, songlink_added]):
            emoji: str = random.choice(["[🎵](5188621441926438751) | ", "[🎶](5188705588925702510) | "])
            caption = emoji + caption

        markdown_need = any([platform_link_added, songlink_added])

        SendMessagesHelper.prepareSendingDocument(
            get_account_instance(),
            ext_path,
            ext_path,
            None,
            f"{caption} {__name__}_flag_metadata{f' {__name__}_flag_markdown' if markdown_need else ''}" ,
            "audio/mpeg",
            client_user_id,
            None,
            None,
            None, None, None, True, 0, None, None, 0, False
        )

    def create_horizontal_card(self):
        try:
            track = self.platform.now_track
            temp_dir = get_temp_dir()
            font_family: int = self.get_setting("font", 0)
            logcat(f'{font_family}: {get_font_family(font_family, False)}')
            width, height = 1440, 600

            advanced_mode = self.get_setting("advanced_mode", False)
            if not advanced_mode:
                background_color = DEFAULT_COLOR["background_color"]
                title_text_color = DEFAULT_COLOR["title_text_color"]
                subtext_color = DEFAULT_COLOR["subtext_color"]
            else:
                background_color = self.get_setting("background_color", DEFAULT_COLOR["background_color"])
                title_text_color = self.get_setting("title_text_color", DEFAULT_COLOR["title_text_color"])
                subtext_color = self.get_setting("subtext_color", DEFAULT_COLOR["subtext_color"])

            if not track.active:
                if strings.language == 'ru' and font_family == 1:
                    font_family = 0

                card = Image.new('RGB', (width, height), background_color)
                draw = ImageDraw.Draw(card)

                plugin_font = ImageFont.truetype(get_font_family(font_family, False), 40)
                not_active_font = ImageFont.truetype(get_font_family(font_family, True), 80)

                draw.text(
                    xy=(width // 2, 45),
                    text=__name__,
                    font=plugin_font,
                    fill=title_text_color,
                    align="center",
                    anchor="mm"
                )

                draw.text(
                    xy=(width // 2, height // 2),
                    text="player_not_active_text",
                    font=not_active_font,
                    fill=title_text_color,
                    align="center",
                    anchor="mm"
                )

                filename = f"now_{__name__}.png"
                temp_photo_path = File(temp_dir, filename).getAbsolutePath()
                card.save(temp_photo_path)
                return temp_photo_path

            background_setting = self.get_setting("background", 1)

            try:
                logcat(track.thumb)
                if track.thumb != '' and track.thumb is not None:
                    resp = requests.get(track.thumb, timeout=5)
                    resp.raise_for_status()
                    thumb = BytesIO(resp.content)
                    thumb.seek(0)

                else:
                    logcat('failed to get thumb')
                    with open(assets.img.empty_cover.path_str, 'rb') as f:
                        thumb = BytesIO(f.read())
            except:
                logcat('failed to get thumb')
                with open(assets.img.empty_cover.path_str, 'rb') as f:
                    thumb = BytesIO(f.read())

            logcat(thumb)
            background = Image.open(thumb)
            thumbnail = background.copy()

            if background_setting == 0:
                background = (background
                              .resize((width, width))
                              .crop((0, (width - height) // 2, width, width))
                              .filter(ImageFilter.GaussianBlur(radius=14)))
                background = ImageEnhance.Brightness(background).enhance(0.3)

                card = Image.new('RGB', (width, height), background_color)
                card.paste(background, (0, 0))

            elif not advanced_mode:
                card = Image.new('RGB', (width, height), get_cover_accent_color(background))

            else:
                card = Image.new('RGB', (width, height), background_color)

            thumbnail = thumbnail.resize((450, 450))
            mask = Image.new('L', thumbnail.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, *thumbnail.size), 30, fill=255)
            thumbnail = thumbnail.copy()
            thumbnail.putalpha(mask)
            card.paste(thumbnail, (75, 75), thumbnail)
            draw = ImageDraw.Draw(card)

            if re.findall(r"[А-Яа-яЁё]", track.title) and font_family == 1:
                font_family = 0

            title_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 60)

            x, y = 590, 85
            artists_plus_y = 0
            lines = textwrap.wrap(track.title, width=21)

            if len(lines) > 1:
                lines[1] = lines[1] + "..." if len(lines) > 2 else lines[1]
                artists_plus_y = 70
            else:
                pass

            lines = lines[:2]

            for line in lines:
                draw.text((x, y), line, font=title_font, fill=title_text_color)
                y += 70

            if re.findall(r"[А-Яа-яЁё]", "".join(track.title)) and font_family == 1:
                font_family = 0

            artist_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 40)
            artists = textwrap.wrap(" • ".join(track.artist), width=32)
            if len(artists) > 1:
                if "•" in artists[0][-2:]:
                    artists[0] = artists[0][:artists[0].rfind("•") - 1]
                artists[0] = artists[0]
            artists = artists[0]

            draw.text((590, 170 + artists_plus_y), artists, subtext_color, font=artist_font)
            if not (self.get_setting("fast_card_render", False)) and track.progress:
                progress_bar_empty = Image.new('RGBA', (width - 665, 10), (0, 0, 0, 0))

                progress_draw = ImageDraw.Draw(progress_bar_empty)
                progress_draw.rounded_rectangle(
                    xy=(0, 0, *progress_bar_empty.size),
                    radius=7,
                    fill=subtext_color
                )
                progress_draw.rounded_rectangle(
                    xy=(0, 0, progress_bar_empty.width * (track.progress / track.duration), 10),
                    radius=7,
                    fill=title_text_color
                )
                card.paste(progress_bar_empty, (590, 460), progress_bar_empty)

                timers_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 30)

                draw.text(
                    xy=(590, 490),
                    text=f"{datetime.datetime.fromtimestamp(track.progress).strftime('%M:%S')}",
                    fill=subtext_color,
                    font=timers_font,
                    anchor="la"
                )
                draw.text(
                    xy=(1365, 490),
                    text=f"{datetime.datetime.fromtimestamp(track.duration).strftime('%M:%S')}",
                    fill=subtext_color,
                    font=timers_font,
                    anchor="ra"
                )
            else:
                local_font_family = None

                if advanced_mode:
                    subtext = self.get_setting("instant_subtext", "powered by")
                    maintext = self.get_setting("instant_main_text", __name__)
                else:
                    subtext = "powered by"
                    maintext = __name__

                subtext = subtext[:26] + "..." if len(subtext) > 26 else subtext
                maintext = maintext[:21] + "..." if len(maintext) > 21 else maintext

                ru_flag_subtext = True if re.findall(r"[А-Яа-яЁё]", subtext) else False
                ru_flag_maintext = True if re.findall(r"[А-Яа-яЁё]", maintext) else False

                if ru_flag_subtext and font_family == 1:
                    font_family = 0

                info_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 42)

                if ru_flag_maintext and font_family == 1:
                    font_family = 0

                device_font = ImageFont.truetype(get_font_family(font_family, True).getAbsolutePath(), 52)

                draw.text((590, 415), subtext, subtext_color, font=info_font, anchor="ls")
                draw.text((590, 485), maintext, title_text_color, font=device_font, anchor="ls")

            filename = f"now_{__name__}.png"
            temp_photo_path = File(temp_dir, filename).getAbsolutePath()
            card.save(temp_photo_path)

            return temp_photo_path
        except Exception as _:
            import traceback
            logcat(f'Failed generate card: {traceback.format_exc()}')
            return None

    def create_vertical_card(self):
        track = self.platform.now_track
        temp_dir = get_temp_dir()
        font_family: int = self.get_setting("font", 0)

        cover_as_background = self.get_setting("background", 1)
        show_service_logo = self.get_setting("show_service_logo", True)

        max_title_symbols = 19
        max_subtitle_symbols = 30

        advanced_mode = self.get_setting("advanced_mode", False)
        if not advanced_mode:
            title_text_color = (255, 255, 255)
            subtext_color = None
            background_color = None
        else:
            background_color = self.get_setting("background_color", DEFAULT_COLOR["background_color"])
            title_text_color = self.get_setting("title_text_color", DEFAULT_COLOR["title_text_color"])
            subtext_color = self.get_setting("subtext_color", DEFAULT_COLOR["subtext_color"])

        if re.findall(r"[А-Яа-яЁё]", track.title) and font_family == 1:
            font_family = 0

        title_font = ImageFont.truetype(get_font_family(font_family, True).getAbsolutePath(), 40)
        artist_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 30)
        duration_font = ImageFont.truetype(get_font_family(font_family, False).getAbsolutePath(), 14)

        artists = ", ".join(track.artist)

        try:
            logcat(track.thumb)
            if track.thumb != '' and track.thumb is not None:
                resp = requests.get(track.thumb, timeout=5)
                resp.raise_for_status()
                cover = BytesIO(resp.content)
                cover.seek(0)

            else:
                logcat('failed to get thumb')
                with open(assets.img.empty_cover.path_str, 'rb') as f:
                    cover = BytesIO(f.read())
        except:
            logcat('failed to get thumb')
            with open(assets.img.empty_cover.path_str, 'rb') as f:
                cover = BytesIO(f.read())

        original_cover_img = Image.open(cover)
        center_img = original_cover_img.copy().resize((384, 384), Image.Resampling.LANCZOS)
        background_fill = get_cover_accent_color(center_img)
        second_fill = adjust_color_for_readability(background_fill)

        if cover_as_background == 0:
            card = original_cover_img.resize((600, 660), Image.Resampling.LANCZOS)
            card = card.filter(ImageFilter.GaussianBlur(radius=25))
            overlay = Image.new('RGBA', card.size, (0, 0, 0, 90))
            card = card.convert('RGBA')
            card = Image.alpha_composite(card, overlay)
            card = card.convert('RGB')
        else:
            final_bg_color = background_color if advanced_mode else background_fill
            card = Image.new('RGB', (600, 660), final_bg_color)

        draw = ImageDraw.Draw(card)

        img_alpha = center_img.convert('RGBA')
        mask = Image.new('L', img_alpha.size, 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle((0, 0, *img_alpha.size), 25, fill=255)
        img_alpha.putalpha(mask)

        card.paste(img_alpha, (108, 60), img_alpha)

        if track.duration:
            progress_bar_color = subtext_color if advanced_mode else second_fill

            draw.rounded_rectangle(
                xy=(108, 468, 492, 483),
                radius=25,
                fill=progress_bar_color
            )

            progress = track.progress / track.duration
            draw.rounded_rectangle(
                xy=(112, 472, 112 + max(7, int(376 * progress)), 479),
                radius=25 if progress >= 0.1 else 5,
                fill=(255, 255, 255)
            )

            draw.text(
                xy=(108, 490),
                text=time.strftime("%M:%S", time.gmtime(track.progress)),
                font=duration_font,
                fill=progress_bar_color,
                anchor="la"
            )

            draw.text(
                xy=(492, 490),
                text=time.strftime("%M:%S", time.gmtime(track.duration)),
                font=duration_font,
                fill=progress_bar_color,
                align="center",
                anchor="ra"
            )

        final_title_color = title_text_color if advanced_mode else (255, 255, 255)

        draw.text(
            xy=(15, 550),
            text=track.title if len(track.title) < max_title_symbols else track.title[:max_title_symbols] + '...',
            font=title_font,
            fill=final_title_color,
            align="center",
            anchor="la"
        )

        draw.text(
            xy=(15, 605),
            text=artists if len(artists) < max_subtitle_symbols else artists[:max_subtitle_symbols] + '...',
            font=artist_font,
            fill=subtext_color if advanced_mode else second_fill,
            align="center",
            anchor="la"
        )

        if show_service_logo:
            selected_platform: int = self.get_setting('selected_platform', 0)
            platform_logo_path: str = get_platform_logo_path(get_platform(selected_platform)).getAbsolutePath()
            logo = Image.open(platform_logo_path).convert("RGBA")
            card.paste(logo, (490, 555), logo)

        filename = f"now_{__name__}.png"
        temp_photo_path = File(temp_dir, filename).getAbsolutePath()
        card.save(temp_photo_path)

        return temp_photo_path

    def is_hex_valid(self, new: str, variable_name: str):
        if not re.match("^#[A-Fa-f0-9]{6}$", new):
            run_on_ui_thread(lambda: self.show_info_alert(title=strings.Alert_HEX_Title, message=strings.Alert_HEX_Text))
            self.set_setting(variable_name, DEFAULT_COLOR[variable_name])

    def is_poller_enabled(self) -> bool:
        return self.poller is not None and self.poller.is_looping()

    def set_poller_enabled(self, enable: bool):
        if self.poller is not None:
            if enable: self.poller.start_poller()
            else: self.poller.stop_poller()
        elif self.poller is None and enable:
            self.poller = Poller(self)
            self.poller.start_poller()

    def update_stream_place(self):
        is_premium = get_user_config().isPremium()

        stream_place = self.get_setting('stream_place', 0)
        is_business_stream_np = stream_place == 1 and not is_premium
        is_profile_stream = stream_place == 2

        if is_business_stream_np or is_profile_stream:
            stream_place_to_set = 0

            self.set_setting('stream_place', stream_place_to_set)
            show_info(strings.StreamPlaceUpdated)

    def show_spinner(self):
        fragment = get_last_fragment()
        ctx = fragment.getParentActivity() if fragment else ApplicationLoader.applicationContext
        if ctx is None:
            logcat("Context not found, can't show spinner.")
            return

        self.spinner = AlertDialogBuilder(ctx, AlertDialogBuilder.ALERT_TYPE_SPINNER)
        self.spinner.set_cancelable(False)
        self.spinner.set_canceled_on_touch_outside(False)
        self.spinner.set_on_cancel_listener(None)

        if self.spinner.get_dialog() and self.spinner.get_dialog().isShowing():
            java = self.spinner.get_dialog()
            java.setCancelable(False)
            java.setCanceledOnTouchOutside(False)

        self.spinner.create()
        self.spinner.show()

    def dismiss_spinner(self):
        if self.spinner and self.spinner.get_dialog() and self.spinner.get_dialog().isShowing():
            self.spinner.dismiss()

        self.spinner = None

    def show_info_alert(self,
                        title: str,
                        message: str,
                        positive_text: Optional[str] = None,
                        positive_listener: Optional[Callable] = None,
                        neutral_text: Optional[str] = "Ok",
                        neutral_listener: Optional[Callable] = None):
        if title == "" or message == "":
            logcat("Title or message not found, can't show info alert.")
            return

        fragment = get_last_fragment()
        ctx = fragment.getParentActivity() if fragment else ApplicationLoader.applicationContext
        if ctx is None:
            logcat("Context not found, can't show info alert.")
            return

        self.info = AlertDialogBuilder(ctx, AlertDialogBuilder.ALERT_TYPE_MESSAGE)
        self.info.set_title(title)
        self.info.set_message(message)

        if positive_text:
            if positive_listener:
                self.info.set_positive_button(positive_text, lambda alert, i: positive_listener())
            else:
                self.info.set_positive_button(positive_text, lambda alert, i: self.dismiss_info_alert())

        if neutral_text:
            if neutral_listener:
                self.info.set_neutral_button(neutral_text, lambda alert, i: neutral_listener())
            else:
                self.info.set_neutral_button(neutral_text, lambda alert, i: self.dismiss_info_alert())

        self.info.show()

    def dismiss_info_alert(self):
        if self.info and self.info.get_dialog() and self.info.get_dialog().isShowing():
            self.info.dismiss()

        self.info = None

    def show_loading_alert(self, title: str):
        if title is None:
            logcat("Title is empty, can't show loading.")
            return

        fragment = get_last_fragment()
        ctx = fragment.getParentActivity() if fragment else ApplicationLoader.applicationContext
        if ctx is None:
            logcat("Context not found, can't show loading alert.")
            return

        self.loading = AlertDialogBuilder(ctx, AlertDialogBuilder.ALERT_TYPE_LOADING)
        self.loading.set_title(title)
        self.loading.set_cancelable(False)
        self.loading.set_canceled_on_touch_outside(False)
        self.loading.set_on_cancel_listener(None)
        self.loading.show()

        if self.loading.get_dialog() and self.loading.get_dialog().isShowing():
            java = self.loading.get_dialog()
            java.setCancelable(False)
            java.setCanceledOnTouchOutside(False)

        self.loading.set_progress(0)

    def update_loading_progress(self, progress: int):
        if self.loading is None or not self.loading.get_dialog().isShowing():
            logcat("Can't update loading alert, because he is None or not showing.")
            return

        self.loading.set_progress(progress)

    def dismiss_loading_alert(self):
        if self.loading and self.loading.get_dialog() and self.loading.get_dialog().isShowing():
            self.loading.dismiss()

        self.loading = None


"""



                            ДИСКЛЕЙМЕР

Если при создании своего плагина вы решили использовать готовые кодовые решения
нашего плагина у себя, то не забудьте упомянуть в описании своего плагина
канал @MeeowPlugins в качестве кредитов за помощь в разработке плагина. Спасибо


                  ⣾⡇⣿⣿⡇⣾⣿⣿⣿⣿⣿⣿⣿⣿⣄⢻⣦⡀⠁⢸⡌⠻⣿⣿⣿⡽⣿⣿
                  ⡇⣿⠹⣿⡇⡟⠛⣉⠁⠉⠉⠻⡿⣿⣿⣿⣿⣿⣦⣄⡉⠂⠈⠙⢿⣿⣝⣿
                  ⠤⢿⡄⠹⣧⣷⣸⡇⠄⠄⠲⢰⣌⣾⣿⣿⣿⣿⣿⣿⣶⣤⣤⡀⠄⠈⠻⢮
                  ⠄⢸⣧⠄⢘⢻⣿⡇⢀⣀⠄⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠄⢀
                  ⠄⠈⣿⡆⢸⣿⣿⣿⣬⣭⣴⣿⣿⣿⣿⣿⣿⣿⣯⠝⠛⠛⠙⢿⡿⠃⠄⢸
                  ⠄⠄⢿⣿⡀⣿⣿⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣿⣿⣿⣿⡾⠁⢠⡇⢀
                  ⠄⠄⢸⣿⡇⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⣫⣻⡟⢀⠄⣿⣷⣾
                  ⠄⠄⢸⣿⡇⠄⠈⠙⠿⣿⣿⣿⣮⣿⣿⣿⣿⣿⣿⣿⣿⡿⢠⠊⢀⡇⣿⣿
                  ⠒⠤⠄⣿⡇⢀⡲⠄⠄⠈⠙⠻⢿⣿⣿⠿⠿⠟⠛⠋⠁⣰⠇⠄⢸⣿⣿⣿



                            DISCLAIMER

If, when creating your plugin, you decided to use the ready-made code solutions
of our plugin, then do not forget to mention the @MeeowPlugins channel in the description
of your plugin as credits for help in developing your plugin. Thanks



"""