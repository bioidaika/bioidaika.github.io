


import os
import re
import json
import time
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import urllib.parse
from datetime import datetime

from resources.lib.constants import *

def log(message, level=xbmc.LOGINFO):
    """
    Ghi log vào Kodi log file
    
    Args:
        message: Nội dung cần ghi log
        level: Mức độ log (xbmc.LOGDEBUG, xbmc.LOGINFO, xbmc.LOGWARNING, xbmc.LOGERROR, xbmc.LOGFATAL)
    """
    if isinstance(message, bytes):
        message = message.decode('utf-8')
    
    if isinstance(message, str):
        message = f"[{ADDON_ID}] {message}"
        xbmc.log(message, level)

def notify(message, title=None, time=5000, icon=ADDON_ICON, sound=True):
    """
    Hiển thị thông báo trên màn hình
    
    Args:
        message: Nội dung thông báo
        title: Tiêu đề thông báo (mặc định là tên addon)
        time: Thời gian hiển thị (ms)
        icon: Đường dẫn đến icon
        sound: Có phát âm thanh khi hiển thị thông báo hay không
    """
    if title is None:
        title = f'[COLOR darkgoldenrod]{ADDON_NAME}[/COLOR]'
    
    xbmc.executebuiltin(f'Notification("{title}", "{message}", "{time}", "{icon}")')

def alert(message, title=None):
    """
    Hiển thị hộp thoại thông báo
    
    Args:
        message: Nội dung thông báo
        title: Tiêu đề thông báo (mặc định là tên addon + phiên bản)
    """
    if title is None:
        title = f"{ADDON_NAME} {ADDON_VERSION}"
    
    dialog = xbmcgui.Dialog()
    dialog.ok(title, message)

def extract_fshare_code(url):
    """
    Trích xuất mã code từ URL Fshare
    
    Args:
        url: URL Fshare (dạng https://www.fshare.vn/file/ABCXYZ123 hoặc https://www.fshare.vn/folder/ABCXYZ123)
        
    Returns:
        Mã code Fshare hoặc None nếu không tìm thấy
    """
    if not url:
        return None
    
    
    pattern = r'fshare\.vn\/(file|folder)\/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(2)
    
    return None

def load_from_cache(cache_key, max_age_seconds=3600):
    """
    Tải dữ liệu từ cache
    
    Args:
        cache_key: Khóa cache
        max_age_seconds: Thời gian tối đa (giây) mà cache còn hợp lệ
        
    Returns:
        Dữ liệu từ cache hoặc None nếu không tìm thấy hoặc cache đã hết hạn
    """
    
    cache_file = os.path.join(CACHE_PATH, f"{cache_key}.json")
    
    
    if not os.path.exists(cache_file):
        return None
    
    
    file_age = time.time() - os.path.getmtime(cache_file)
    if file_age > max_age_seconds:
        
        return None
    
    try:
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Lỗi khi đọc cache: {str(e)}", xbmc.LOGERROR)
        return None

def save_to_cache(cache_key, data):
    """
    Lưu dữ liệu vào cache
    
    Args:
        cache_key: Khóa cache
        data: Dữ liệu cần lưu (phải có thể chuyển đổi thành JSON)
        
    Returns:
        Boolean: True nếu lưu thành công, False nếu có lỗi
    """
    
    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    
    
    cache_file = os.path.join(CACHE_PATH, f"{cache_key}.json")
    
    try:
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log(f"Lỗi khi lưu cache: {str(e)}", xbmc.LOGERROR)
        return False

def clear_specific_cache(cache_key):
    """
    Xóa một file cache cụ thể
    
    Args:
        cache_key: Khóa cache cần xóa
        
    Returns:
        Boolean: True nếu xóa thành công hoặc file không tồn tại, False nếu có lỗi
    """
    cache_file = os.path.join(CACHE_PATH, f"{cache_key}.json")
    
    if not os.path.exists(cache_file):
        return True
    
    try:
        os.remove(cache_file)
        return True
    except Exception as e:
        log(f"Lỗi khi xóa cache: {str(e)}", xbmc.LOGERROR)
        return False

def save_history_item(item):
    """
    Lưu một mục vào lịch sử xem
    
    Args:
        item: Dictionary chứa thông tin về mục cần lưu
        
    Returns:
        Boolean: True nếu lưu thành công, False nếu có lỗi
    """
    
    history_file = os.path.join(PROFILE_PATH, 'history.json')
    
    
    history = load_history()
    if history is None:
        history = []
    
    
    if 'timestamp' not in item:
        item['timestamp'] = int(time.time())
    
    
    for i, existing_item in enumerate(history):
        if existing_item.get('url') == item.get('url'):
            
            history.pop(i)
            break
    
    
    history.insert(0, item)
    
    
    max_history_items = 100
    if len(history) > max_history_items:
        history = history[:max_history_items]
    
    try:
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log(f"Lỗi khi lưu lịch sử: {str(e)}", xbmc.LOGERROR)
        return False

def load_history():
    """
    Tải danh sách lịch sử xem
    
    Returns:
        List: Danh sách các mục trong lịch sử hoặc [] nếu không có lịch sử
    """
    
    history_file = os.path.join(PROFILE_PATH, 'history.json')
    
    if not os.path.exists(history_file):
        return []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Lỗi khi đọc lịch sử: {str(e)}", xbmc.LOGERROR)
        return []

def delete_history_item(url):
    """
    Xóa một mục khỏi lịch sử xem
    
    Args:
        url: URL của mục cần xóa
        
    Returns:
        Boolean: True nếu xóa thành công, False nếu có lỗi
    """
    
    history_file = os.path.join(PROFILE_PATH, 'history.json')
    
    
    history = load_history()
    if not history:
        return True
    
    
    for i, item in enumerate(history):
        if item.get('url') == url:
            history.pop(i)
            break
    
    try:
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log(f"Lỗi khi xóa mục khỏi lịch sử: {str(e)}", xbmc.LOGERROR)
        return False

def clear_history():
    """
    Xóa toàn bộ lịch sử xem
    
    Returns:
        Boolean: True nếu xóa thành công, False nếu có lỗi
    """
    
    history_file = os.path.join(PROFILE_PATH, 'history.json')
    
    if not os.path.exists(history_file):
        return True
    
    try:
        
        os.remove(history_file)
        return True
    except Exception as e:
        log(f"Lỗi khi xóa lịch sử: {str(e)}", xbmc.LOGERROR)
        return False

def format_size(size_bytes):
    """
    Định dạng kích thước file từ byte sang đơn vị dễ đọc
    
    Args:
        size_bytes: Kích thước file tính bằng byte
        
    Returns:
        String: Kích thước file đã được định dạng
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def get_direct_link_from_cache(url):
    """
    Lấy link trực tiếp từ cache
    
    Args:
        url: URL Fshare
        
    Returns:
        String: Link trực tiếp hoặc None nếu không tìm thấy trong cache
    """
    
    file_code = extract_fshare_code(url)
    if not file_code:
        return None
    
    
    cache_key = f"direct_link_{file_code}"
    
    
    max_age_seconds = 4 * 3600
    
    
    cache_data = load_from_cache(cache_key, max_age_seconds)
    
    if cache_data and 'direct_url' in cache_data:
        return cache_data['direct_url']
    
    return None

def save_direct_link_cache(url, direct_url):
    """
    Lưu link trực tiếp vào cache
    
    Args:
        url: URL Fshare
        direct_url: Link trực tiếp
        
    Returns:
        Boolean: True nếu lưu thành công, False nếu có lỗi
    """
    
    file_code = extract_fshare_code(url)
    if not file_code:
        return False
    
    
    cache_key = f"direct_link_{file_code}"
    
    
    cache_data = {
        'url': url,
        'direct_url': direct_url,
        'timestamp': int(time.time())
    }
    
    
    return save_to_cache(cache_key, cache_data)
