import os
import time
import json
import xbmcvfs
import datetime as dt
import hashlib
import requests
import re
import urllib.parse
import xbmcaddon
import shutil
from .addon import notify, logError, alert
from . import gsheet, fshare
import xbmcgui
import xbmc


ADDON = xbmcaddon.Addon()


HOME_DIR = xbmcvfs.translatePath('special://home/')
TEMP_DIR = xbmcvfs.translatePath('special://temp/')
USERDATA_DIR = xbmcvfs.translatePath('special://userdata/')
DATABASE_DIR = xbmcvfs.translatePath('special://database/')
THUMBNAILS_DIR = xbmcvfs.translatePath('special://thumbnails/')


PACKAGES_DIR = os.path.join(HOME_DIR, 'addons', 'packages')
ARCHIVE_CACHE_DIR = os.path.join(TEMP_DIR, 'archive_cache')


ADDON_TITLE = "VietmediaF Cache Cleaner"

CACHE_TIMEOUT = 600

from resources.lib.constants import CACHE_PATH

def clean_old_json_files():
    """Xóa các file cache JSON cũ hơn 60 phút trong thư mục cache của addon"""
    deleted_count = 0
    current_time = dt.datetime.now()


    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
        return


    try:
        files = os.listdir(CACHE_PATH)
        #logError(f"Tìm thấy {len(files)} files trong {CACHE_PATH}")

        for file_name in files:
            if file_name.endswith('.json'):
                file_path = os.path.join(CACHE_PATH, file_name)
                try:

                    creation_time = dt.datetime.fromtimestamp(os.path.getctime(file_path))


                    if (current_time - creation_time) > dt.timedelta(minutes=60):
                        #logError(f"Đang xóa file cũ: {file_path}")
                        os.remove(file_path)
                        deleted_count += 1
                        #logError(f"Đã xóa thành công: {file_path}")
                except Exception as e:
                    logError(f"Lỗi khi xử lý file {file_path}: {str(e)}")
    except Exception as e:
        logError(f"Lỗi khi đọc thư mục cache: {str(e)}")

    notify(f"Đã xóa {deleted_count} file cache cũ")

def check_cache(cache_key, max_age_minutes=60):
    """Kiểm tra xem cache có tồn tại và còn hạn không

    Args:
        cache_key: Khóa cache hoặc đường dẫn đến file cache
        max_age_minutes: Thời gian tối đa (phút) mà cache còn hợp lệ

    Returns:
        Boolean: True nếu cache còn hợp lệ, False nếu không
    """
    try:

        if os.path.isabs(cache_key):
            cache_path = cache_key
        else:

            cache_path = os.path.join(CACHE_PATH, f"{cache_key}.json")

        if not os.path.exists(cache_path):
            logError(f"Cache không tồn tại: {cache_path}")
            return False


        creation_time = dt.datetime.fromtimestamp(os.path.getctime(cache_path))
        current_time = dt.datetime.now()


        is_valid = (current_time - creation_time) <= dt.timedelta(minutes=max_age_minutes)
        if not is_valid:
            try:
                os.remove(cache_path)
                #logError(f"Xóa cache hết hạn: {cache_path}")
            except Exception as e:
                logError(f"Lỗi khi xóa cache hết hạn: {str(e)}")
        return is_valid
    except Exception as e:
        logError(f"Lỗi kiểm tra cache: {str(e)}")
        return False

def get_cache(cache_key):
    """Lấy dữ liệu từ cache

    Args:
        cache_key: Khóa cache hoặc đường dẫn đến file cache

    Returns:
        Dữ liệu từ cache hoặc None nếu không tìm thấy hoặc có lỗi
    """
    try:

        if os.path.isabs(cache_key):
            cache_path = cache_key
        else:

            cache_path = os.path.join(CACHE_PATH, f"{cache_key}.json")

        if not os.path.exists(cache_path):
            return None

        with open(cache_path, 'r', encoding='utf-8') as cache_file:
            return json.load(cache_file)
    except Exception as e:
        logError(f"Lỗi đọc cache: {str(e)}")
        return None

def set_cache(cache_key, data):
    """Lưu dữ liệu vào cache

    Args:
        cache_key: Khóa cache hoặc đường dẫn đến file cache
        data: Dữ liệu cần lưu (phải có thể chuyển đổi thành JSON)

    Returns:
        Boolean: True nếu lưu thành công, False nếu có lỗi
    """
    try:

        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)


        if os.path.isabs(cache_key):
            cache_path = cache_key
        else:

            cache_path = os.path.join(CACHE_PATH, f"{cache_key}.json")


        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        with open(cache_path, 'w', encoding='utf-8') as cache_file:
            json.dump(data, cache_file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logError(f"Lỗi lưu cache: {str(e)}")
        return False

def cache_data(url):
    """Cache dữ liệu từ URL và trả về dữ liệu đã cache

    Args:
        url: URL cần lấy dữ liệu và cache

    Returns:
        Dữ liệu từ cache hoặc từ URL nếu cache không tồn tại hoặc hết hạn
    """

    # Chỉ tạo cache_key chung cho các URL không phải FShare folder
    if 'fshare' not in url or 'folder' not in url:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        
        if check_cache(cache_key):
            data = get_cache(cache_key)
            if data:
                return data
            #logError("Cache không có dữ liệu")


    if "docs.google.com" in url:
        regex = r"url=(.+)"
        match = re.search(regex, url)
        if match:
            link = match.group(1)
            data = gsheet.getdata(link)
            if data:
                set_cache(cache_key, data)
            return data

    if 'fshare' in url and 'folder' in url:
        url = urllib.parse.unquote_plus(url)
        #logError("Xử lý folder Fshare: " + url)
        if 'api' in url:
            try:
                url_match = re.search(r"url=(.+)", url)
                play_match = re.search(r"play(.+)&", url)
                if url_match and play_match:
                    link = url_match.group(1) + play_match.group(1)
                else:
                    logError("Không thể parse API URL")
                    return None
            except Exception as e:
                logError(f"Lỗi parse API URL: {str(e)}")
                return None
        else:
            try:
                # Kiểm tra nếu URL đã là FShare URL trực tiếp
                if url.startswith('https://www.fshare.vn/folder/'):
                    link = url
                else:
                    # Tìm URL trong parameter
                    regex = r"url=(.+)"
                    match = re.search(regex, url)
                    if not match:
                        logError("Không tìm thấy URL trong: " + url)
                        return None
                    link = match.group(1)


                page_match = re.search(r"page=(\d+)", url)
                if page_match:
                    page = page_match.group(1)

                    if '?' in link:
                        link += '&'
                    else:
                        link += '?'
                    link += "page=" + page

            except Exception as e:
                logError(f"Lỗi parse URL: {str(e)}")
                return None



        # Extract folder code from URL for safe cache key
        folder_code = link.split('/')[-1] if '/' in link else link
        folder_cache_key = f"fshare_folder_{folder_code}"
        
        # Check cache first
        if check_cache(folder_cache_key, 30):
            cache_data = get_cache(folder_cache_key)
            if cache_data:
                return cache_data

        data = fshare.fsharegetFolder(link)
        if data:
            set_cache(folder_cache_key, data)
            return data
        else:
            logError("fsharegetFolder trả về None")

    return None

def clear_addon_cache():
    """Xóa các file cache trong thư mục cache của addon"""

    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
        notify("Không có cache addon để xóa")
        return

    deleted_count = 0

    try:

        files = os.listdir(CACHE_PATH)
        #logError(f"Tìm thấy {len(files)} files trong {CACHE_PATH}")

        for file_name in files:
            file_path = os.path.join(CACHE_PATH, file_name)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    #logError(f"Đã xóa thành công: {file_path}")
                except Exception as e:
                    logError(f"Lỗi khi xóa file {file_path}: {str(e)}")
            elif os.path.isdir(file_path):
                try:
                    import shutil
                    shutil.rmtree(file_path)
                    deleted_count += 1
                    #logError(f"Đã xóa thư mục thành công: {file_path}")
                except Exception as e:
                    logError(f"Lỗi khi xóa thư mục {file_path}: {str(e)}")
    except Exception as e:
        logError(f"Lỗi khi xóa cache addon: {str(e)}")

    notify(f"Đã xóa {deleted_count} file cache addon")
    return deleted_count

def clear_cache_links():
    """Xóa các file cache link do addon tạo ra"""

    if not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
        return 0

    deleted_count = 0

    try:

        files = os.listdir(CACHE_PATH)

        for file_name in files:

            if file_name.startswith("fshare_") or file_name.endswith(".json"):
                file_path = os.path.join(CACHE_PATH, file_name)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        logError(f"Đã xóa cache link: {file_path}")
                    except Exception as e:
                        logError(f"Lỗi khi xóa cache link {file_path}: {str(e)}")
    except Exception as e:
        logError(f"Lỗi khi xóa cache link: {str(e)}")

    if deleted_count > 0:
        logError(f"Đã xóa {deleted_count} file cache link")

    return deleted_count

def clear_system_cache():
    """Xóa cache toàn bộ hệ thống Kodi dựa trên mã được cung cấp"""
    dialog = xbmcgui.Dialog()
    deleted_items = 0


    # Sử dụng DialogProgressBG để hiển thị tiến trình ở góc màn hình
    progress = xbmcgui.DialogProgressBG()
    progress.create("VietmediaF", "Xóa cache hệ thống...")

    try:

        progress.update(0, "VietmediaF", "Xóa các gói cài đặt...")
        if xbmcvfs.exists(PACKAGES_DIR):
            try:
                dirs, files = xbmcvfs.listdir(PACKAGES_DIR)
                for file in files:
                    xbmcvfs.delete(os.path.join(PACKAGES_DIR, file))
                    deleted_items += 1
                for dir in dirs:
                    shutil.rmtree(os.path.join(PACKAGES_DIR, dir), ignore_errors=True)
                    deleted_items += 1
                logError(f"{ADDON_TITLE}: Đã xóa thư mục Packages.")
            except Exception as e:
                logError(f"{ADDON_TITLE}: Lỗi khi xóa Packages: {str(e)}")


        progress.update(20, "VietmediaF", "Xóa cache hình ảnh...")

        xbmc.executebuiltin("ClearMemCache")
        xbmc.executebuiltin("ClearImageCache")


        texture_db = os.path.join(DATABASE_DIR, 'Textures21.db')
        if xbmcvfs.exists(texture_db):
            try:

                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Textures.Cleanup","id":1}')
                deleted_items += 1
                logError(f"{ADDON_TITLE}: Đã dọn dẹp database Textures.")
            except Exception as e:
                logError(f"{ADDON_TITLE}: Lỗi khi dọn dẹp database Textures: {str(e)}")


        progress.update(40, "VietmediaF", "Xóa cache các addon phụ trợ...")
        try:
            if xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)'):
                xbmc.executebuiltin('RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)')
                deleted_items += 1
                logError(f"{ADDON_TITLE}: Đã xóa cache ResolveURL.")
            if xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
                xbmc.executebuiltin('RunPlugin(plugin://script.module.urlresolver/?mode=reset_cache)')
                deleted_items += 1
                logError(f"{ADDON_TITLE}: Đã xóa cache URLResolver.")
        except Exception as e:
            logError(f"{ADDON_TITLE}: Lỗi khi xóa Function Cache: {str(e)}")


        progress.update(60, "VietmediaF", "Xóa cache lưu trữ...")
        if xbmcvfs.exists(ARCHIVE_CACHE_DIR):
            try:
                dirs, files = xbmcvfs.listdir(ARCHIVE_CACHE_DIR)
                for file in files:
                    xbmcvfs.delete(os.path.join(ARCHIVE_CACHE_DIR, file))
                    deleted_items += 1
                for dir in dirs:
                    shutil.rmtree(os.path.join(ARCHIVE_CACHE_DIR, dir), ignore_errors=True)
                    deleted_items += 1
                logError(f"{ADDON_TITLE}: Đã xóa thư mục Archive Cache.")
            except Exception as e:
                logError(f"{ADDON_TITLE}: Lỗi khi xóa Archive Cache: {str(e)}")


        progress.update(80, "VietmediaF", "Xóa các cache khác...")

        xbmc.executebuiltin("ClearDbCache")

        xbmc.executebuiltin("ClearMusicCache")
        xbmc.executebuiltin("ClearAddonCache")
        xbmc.executebuiltin("ClearWatchedCache")

        xbmc.executebuiltin("CleanLibrary(video)")
        xbmc.executebuiltin("CleanLibrary(music)")


        if xbmcvfs.exists(TEMP_DIR):
            try:
                dirs, files = xbmcvfs.listdir(TEMP_DIR)
                for file in files:
                    xbmcvfs.delete(os.path.join(TEMP_DIR, file))
                    deleted_items += 1

            except Exception as e:
                logError(f"{ADDON_TITLE}: Lỗi khi xóa Temp: {str(e)}")

        progress.update(100, "VietmediaF", "Hoàn tất!")
        xbmc.sleep(1000)
        progress.close()


        if deleted_items > 0:
            notify(f"Đã xóa thành công {deleted_items} mục cache hệ thống!")
            logError(f"{ADDON_TITLE}: Đã xóa {deleted_items} mục cache.")
        else:
            notify("Không tìm thấy cache nào để xóa!")
            logError(f"{ADDON_TITLE}: Không có cache nào được xóa.")


        xbmc.executebuiltin('Container.Refresh()')
        return True
    except Exception as e:
        progress.close()
        logError(f"Lỗi khi xóa cache hệ thống: {str(e)}")
        alert(f"Lỗi khi xóa cache hệ thống: {str(e)}")
        return False

def should_clear_cache_on_startup():
    """Kiểm tra xem có nên xóa cache khi khởi động không"""

    if not ADDON.getSettingBool("clear_cache_on_startup"):
        return False


    last_clear_date = ADDON.getSetting("last_cache_clear_date")
    today = dt.datetime.now().strftime("%Y-%m-%d")

    if last_clear_date == today:

        return False


    ADDON.setSetting("last_cache_clear_date", today)
    return True

def should_clear_cache_links_daily():
    """Kiểm tra xem có nên xóa cache link hàng ngày không"""



    last_clear_links_date = ADDON.getSetting("last_cache_links_clear_date")
    today = dt.datetime.now().strftime("%Y-%m-%d")

    if last_clear_links_date == today:

        return False


    ADDON.setSetting("last_cache_links_clear_date", today)
    return True

def clear_all_addon_cache():
    """Xóa tất cả cache tạo ra bởi addon, bao gồm cả cache link"""

    deleted_links = clear_cache_links()


    deleted_addon = clear_addon_cache()


    total_deleted = deleted_links + deleted_addon

    return total_deleted

def clear_cache_manual():
    """Hàm xóa cache khi người dùng chọn từ menu"""

    # Sử dụng DialogProgressBG để hiển thị tiến trình ở góc màn hình
    progress = xbmcgui.DialogProgressBG()
    progress.create("VietmediaF", "Đang xóa cache...")

    try:

        progress.update(0, "VietmediaF", "Xóa cache link...")
        deleted_links = clear_cache_links()

        progress.update(50, "VietmediaF", "Xóa cache addon...")
        deleted_addon = clear_addon_cache()

        total_deleted = deleted_links + deleted_addon
        progress.update(100, "VietmediaF", "Hoàn tất!")


        xbmc.sleep(1000)
        progress.close()

        notify(f"Xóa thành công {total_deleted} file cache addon")


        xbmc.executebuiltin('Container.Refresh()')
    except Exception as e:
        progress.close()
        logError(f"Lỗi khi xóa cache: {str(e)}")
        alert(f"Lỗi khi xóa cache: {str(e)}")

def clear_cache():
    """Hàm chính để xóa cache, tự động xóa cache link hàng ngày"""

    today = dt.datetime.now().strftime("%Y-%m-%d")
    last_auto_clear_date = ADDON.getSetting("last_auto_clear_date")


    if last_auto_clear_date != today:

        deleted = clear_cache_links()
        if deleted > 0:
            logError(f"Tự động xóa {deleted} file cache link hàng ngày")


        ADDON.setSetting("last_auto_clear_date", today)
    else:
        logError("Hàm xóa cache đã chạy trong ngày, bỏ qua xóa cache tự động")


    if should_clear_cache_on_startup():

        clear_all_addon_cache()
        return



