import os
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import shutil
from resources.addon import notify, alert, ADDON_ID

ADDON = xbmcaddon.Addon(ADDON_ID)
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))
FONTS_PATH = os.path.join(ADDON_PATH, 'resources', 'fonts')
KODI_MEDIA_PATH = xbmcvfs.translatePath('special://home/media')
KODI_FONTS_PATH = os.path.join(KODI_MEDIA_PATH, 'fonts')

def get_available_fonts():
    """Lấy danh sách các font có sẵn trong thư mục fonts của addon"""
    fonts = []
    if os.path.exists(FONTS_PATH):
        for file in os.listdir(FONTS_PATH):
            if file.lower().endswith('.ttf'):
                fonts.append(file)
    return fonts

def ensure_kodi_fonts_dir():
    """Đảm bảo thư mục fonts trong special://home/media tồn tại"""
    if not os.path.exists(KODI_MEDIA_PATH):
        os.makedirs(KODI_MEDIA_PATH)
    
    if not os.path.exists(KODI_FONTS_PATH):
        os.makedirs(KODI_FONTS_PATH)
        return True
    return os.path.exists(KODI_FONTS_PATH)

def install_font(font_name):
    """Cài đặt font được chọn vào thư mục fonts của Kodi"""
    source_path = os.path.join(FONTS_PATH, font_name)
    dest_path = os.path.join(KODI_FONTS_PATH, font_name)

    try:
        # Kiểm tra và tạo thư mục fonts nếu cần
        if not ensure_kodi_fonts_dir():
            alert("Không thể tạo thư mục fonts trong Kodi")
            return False
            
        # Copy font vào thư mục fonts của Kodi
        shutil.copy2(source_path, dest_path)

        # Cố gắng thiết lập font phụ đề trong Kodi (có thể không hoạt động trên một số phiên bản Kodi)
        font_setting = f"media/fonts/{font_name}"
        xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","method":"Settings.SetSettingValue","params":{{"setting":"subtitles.font","value":"{font_setting}"}},"id":1}}')

        # Thông báo thành công và hướng dẫn thiết lập thủ công
        dialog = xbmcgui.Dialog()
        dialog.ok("Cài đặt font thành công", 
                 f"Đã cài đặt font {font_name} thành công.\n\nKodi sẽ khởi động lại, bạn cần thiết lập thủ công:\n1. Vào [COLOR yellow]Cài đặt (Settings) của Kodi\n2. Chọn Player > Language\n3. Chọn Font phụ đề và tìm đến [/COLOR]{font_name}")

        # Hỏi người dùng có muốn khởi động lại Kodi không
        if dialog.yesno("Khởi động lại Kodi", 
                       "Bạn có muốn khởi động lại Kodi ngay bây giờ không?"):
            xbmc.executebuiltin("RestartApp")
            
        return True
    except Exception as e:
        alert(f"Lỗi khi cài đặt font: {str(e)}")
        return False

def list_subtitle_fonts():
    """Liệt kê các font phụ đề có sẵn trong addon"""
    # Đảm bảo thư mục fonts trong Kodi tồn tại
    ensure_kodi_fonts_dir()
    
    # Lấy danh sách fonts có sẵn
    fonts = get_available_fonts()
    
    if not fonts:
        alert("Không tìm thấy font nào trong thư mục fonts của addon")
        return {"content_type": "", "items": []}
    
    # Tạo danh sách các mục menu
    items = []
    for font in fonts:
        item = {
            "label": font,
            "is_playable": False,
            "path": f"plugin://plugin.video.vietmediaF?action=install_subtitle_font&font={font}",
            "thumbnail": "special://home/addons/plugin.video.vietmediaF/resources/images/settings.png",
            "icon": "special://home/addons/plugin.video.vietmediaF/resources/images/settings.png",
            "label2": "",
            "info": {"plot": f"Cài đặt font phụ đề {font}"},
            "art": {"fanart": ""}
        }
        items.append(item)
    
    return {"content_type": "", "items": items}
