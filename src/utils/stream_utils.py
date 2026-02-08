import os

from android_utils import run_on_ui_thread
from client_utils import get_user_config, send_request, get_messages_controller

from ..constants import TEMP_DIR_NAME
from .utils import get_temp_dir, logcat, read, show_error, write, show_success

from elyx import strings # type: ignore

from java.lang import Integer, Math # type: ignore
from java.util import ArrayList # type: ignore

from org.telegram.tgnet import TLRPC  # type: ignore

def _get_stream_info_file_path() -> str | None:
    temp_dir_obj = get_temp_dir()
    if not temp_dir_obj:
        logcat("Could not get base temp directory for cache.")
        return None

    swaga_dir_path = os.path.join(temp_dir_obj.getAbsolutePath(), TEMP_DIR_NAME)
    return os.path.join(swaga_dir_path, "stream_info.json")


def is_stream_value_exist() -> bool:
    path = _get_stream_info_file_path()
    if not path:
        return False

    value = read(path)

    return isinstance(value, int)


def save_stream_account_id(new_user_id: int):
    path = _get_stream_info_file_path()
    if path is None:
        show_error(strings.Settings_Stream_AccountId_Failed_Save)
        return

    write(path, new_user_id)
    show_success(strings.Settings_Stream_AccountId_Saved)


def get_local_stream_id() -> int:
    path = _get_stream_info_file_path()
    if path is None:
        show_error("Failed to load data")
        return 0

    value = read(path)

    return value if isinstance(value, int) else 0


def set_profile_saved_track(resp):
    def process(response, error):
        delete_last_message(get_user_config().getClientUserId())
        if error or response is None:
            logcat(f'Failed to set profile saved track: {error.code} - {error.text}')

    update = resp.updates.get(1)
    if update is None:
        logcat('update not valid')
        return

    message = update.message
    if message is None:
        logcat('msg not valid')
        return

    media = message.media
    if media is None:
        logcat('media not valid')
        return

    document = media.document
    if document is None:
        logcat('doc not valid')
        return

    file_id = document.id
    access_hash = document.access_hash
    file_reference = document.file_reference

    if file_id is None:
        logcat('update not valid')
        return

    if access_hash is None:
        logcat('update not valid')
        return

    if file_reference is None:
        logcat('update not valid')
        return

    if message.from_id.user_id is None or message.from_id.user_id != get_user_config().getClientUserId():
        logcat('wrong id')
        return

    req = TLRPC.TL_account_saveMusic()

    req.unsave = False
    req.id = TLRPC.TL_inputDocument()
    req.id.id = file_id
    req.id.access_hash = access_hash
    req.id.file_reference = file_reference

    if req.id.file_reference is None:
        logcat('file ref not valid')
        req.id.file_reference = b''

    send_request(req, process)


def delete_last_message(chat_id):
    def process_result(response, error):
        if error or not response:
            logcat(f'{error.code} | {error.text}')
            return

        if not hasattr(response, 'messages'):
            logcat(f'Response is not \'messages_Messages\' and \'TL_messages_messagesSlice\', received {response}')
            return

        msgs = list(ArrayList(response.messages).toArray())
        if not msgs or msgs[0] is None:
            logcat("Empty list")
            return

        ids = ArrayList()
        ids.add(Integer(Math.toIntExact(msgs[0].id)))

        def delete_msg():
            get_messages_controller().deleteMessages(
                ids,
                None,
                None,
                chat_id,
                0,
                True,
                0
            )

        run_on_ui_thread(lambda: delete_msg())

    req = TLRPC.TL_messages_getHistory()
    req.peer = get_messages_controller().getInputPeer(chat_id)
    req.offset_id = 0
    req.limit = 1

    send_request(req, process_result)


def _to_syncsafe(size: int) -> bytes:
    return bytes([
        (size >> 21) & 0x7F,
        (size >> 14) & 0x7F,
        (size >> 7)  & 0x7F,
        (size)       & 0x7F,
    ])


def _frame_bytes(frame_id: str, text: str) -> bytes:
    try:
        body_text = text.encode('latin-1')
        encoding_byte = b'\x00'
    except UnicodeEncodeError:
        body_text = text.encode('utf-16')
        encoding_byte = b'\x01'
    body = encoding_byte + body_text
    size_bytes = len(body).to_bytes(4, 'big')
    header = frame_id.encode('ascii') + size_bytes + b'\x00\x00'
    return header + body


def create_minimal_id3_mp3(
        path: str,
        title: str,
        artist: str,
        duration_seconds: int | None = None,
        target_size_mb: float = 0):
    frames = bytearray()
    frames += _frame_bytes('TIT2', title)
    frames += _frame_bytes('TPE1', artist)

    if duration_seconds is not None:
        ms = str(int(duration_seconds * 1000))
        frames += _frame_bytes('TLEN', ms)

    tag_size = len(frames)
    header = b'ID3' + bytes([3, 0]) + b'\x00' + _to_syncsafe(tag_size)

    with open(path, 'wb') as f:
        f.write(header)
        f.write(frames)
        fake_frame = bytes([0xFF, 0xFB, 0x90, 0x64]) + (b'\x00' * 418)

        if target_size_mb > 0:
            target_bytes = int(target_size_mb * 1024 * 1024)
            while f.tell() < target_bytes:
                f.write(fake_frame)
        else:
            f.write(fake_frame)

    st = os.stat(path)
    return path, st.st_size