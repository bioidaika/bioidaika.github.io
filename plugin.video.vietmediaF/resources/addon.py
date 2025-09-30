import xbmcaddon
import xbmcgui
import xbmc
import xbmcvfs
import requests
import os
import time
import json
import hashlib
from .history_utils import search_history
import datetime

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_PROFILE = ADDON.getAddonInfo("profile")
VERSION = ADDON.getAddonInfo("version")
ADDON_PATH = ADDON.getAddonInfo("path")
LOG = os.path.join(xbmcvfs.translatePath('special://logpath/'))
PROFILE = os.path.join(xbmcvfs.translatePath('special://profile/'))
CURRENT_PATH = ADDON.getAddonInfo("path")
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)
USER_PIN_CODE = ADDON.getSetting('user_pin_code')
USER_VIP_CODE = ADDON.getSetting('user_vip_code')
CACHE_PATH = xbmcvfs.translatePath("special://temp")
_icon = ADDON.getAddonInfo('icon')
_fanart = ADDON.getAddonInfo('fanart')
USER = ADDON.getSetting('user_id')
LOCK_PIN = ADDON.getSetting('lock_pin')
VIEWMODE = ADDON.getSetting('view_mode')
VIEWXXX = ADDON.getSetting('view_xxx')
DOWNLOAD_PATH = ADDON.getSetting("download_path")
DOWNLOAD_SUB = ADDON.getSetting("download_sub")
DIALOG = xbmcgui.Dialog()
# Sử dụng DialogProgressBG để hiển thị tiến trình ở góc màn hình
vDialog = xbmcgui.DialogProgressBG()
HOME = xbmcvfs.translatePath('special://home/')
USERDATA = os.path.join(xbmcvfs.translatePath('special://home/'), 'userdata')
ADDONDATA = os.path.join(USERDATA, 'addon_data', ADDON_ID)
CHECK = ADDON.getSetting("check")
play_icon = xbmcvfs.translatePath('special://home/addons/'+ADDON_ID+'/icon_play.png')
fourshare_icon = xbmcvfs.translatePath('special://home/addons/'+ADDON_ID+'/4s.png')
FSHARE_ICON = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'images', 'fshareicon.png'))
DELETE_INTERVAL = 10
addon_url = "plugin://{}/".format(ADDON_ID)

icon = xbmcvfs.translatePath('special://home/addons/'+ADDON_ID+'/icon.png')
headers = {'User-Agent': 'kodivietmediaf-K58W6U'}

def notify(message='', header=None, time=5000, image=icon):
    if header is None:
        header = '[COLOR darkgoldenrod]'+ADDON_NAME+'[/COLOR]'
    xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' % (header, message, time, image))

def alert(message, title=None):
    if not title:
        title = ADDON_NAME + " " + VERSION
    dialog = xbmcgui.Dialog()
    ok = dialog.ok(title, message)

def logError(message):
    xbmc.log(message, xbmc.LOGERROR)
def log(message, level=xbmc.LOGINFO):
    xbmc.log(message, level)
def logDebug(message):
    xbmc.log(message, xbmc.LOGDEBUG)
def TextBoxes(heading, announce):
    class TextBox():
        WINDOW = 10147
        CONTROL_LABEL = 1
        CONTROL_TEXTBOX = 5

        def __init__(self, *args, **kwargs):
            xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, ))
            self.win = xbmcgui.Window(self.WINDOW)
            xbmc.sleep(500)
            self.setControls()
            self.win.setProperty('resolution', '1920x1080')


        def setControls(self):
            self.win.getControl(self.CONTROL_LABEL).setLabel(heading)
            try:
                f = open(announce)
                text = f.read()
            except:
                text = announce
            self.win.getControl(self.CONTROL_TEXTBOX).setText(str(text))
            return

    TextBox()
    while xbmc.getCondVisibility('Window.IsVisible(10147)'):
        time.sleep(.5)


def debug(text):
    text = str(text)
    filename = os.path.join(PROFILE_PATH, 'debug.dat')
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            f.write(text)
    else:
        with open(filename, "w") as f:
            f.write(text)

def fetch_data(url, headers=None):

    if headers is None:
        headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36 VietMedia/1.0',
                'Referers': 'http://www.google.com',
                'X-Version': VERSION,
                'X-User-VIP': USER_VIP_CODE
                }
    try:
        response = requests.get(url, headers=headers)

        return json.loads(response.content.decode('utf-8'))
    except:
        pass

def getadv():
    try:
        response = requests.get('https://fshare.vip/adv/adv.json', timeout=3)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == 1:
            return data.get("item_adv", {})
        else:
            return {}
    except requests.exceptions.Timeout:

        return {}

    except Exception as e:

        return {}

def save_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_from_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return None

def get_file_name(url):
    unique_string = datetime.datetime.now().strftime("%Y-%m-%d") + url
    return hashlib.md5(unique_string.encode()).hexdigest() + ".json"

def check_history():
    """Kiểm tra xem file lịch sử có tồn tại và có dữ liệu không"""
    return search_history.check_history()

def save_search_history(query):
    """Lưu một query mới vào lịch sử"""
    search_history.save_history(query)

def get_search_history():
    """Lấy lịch sử tìm kiếm từ file"""
    return search_history.get_history()

def delete_search_history():
    """Xóa toàn bộ lịch sử"""
    search_history.delete_history()

def get_password(encrypted_password):
    """
    Lấy mật khẩu đã giải mã từ chuỗi mã hóa
    """
    if not encrypted_password:
        return ""

    # Kiểm tra xem chuỗi có được mã hóa không
    try:
        import base64
        base64.b64decode(encrypted_password)
        # Nếu giải mã base64 thành công, có thể là chuỗi đã mã hóa
        from resources.password_crypto import PasswordDecryption
        decryptor = PasswordDecryption()
        return decryptor.decrypt(encrypted_password)
    except:
        # Nếu không phải chuỗi mã hóa, trả về nguyên gốc
        return encrypted_password

def get_fshare_password():
    password = ADDON.getSetting('fshare_password')
    return password
