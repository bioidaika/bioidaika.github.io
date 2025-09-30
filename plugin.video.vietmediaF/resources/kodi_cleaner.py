

"""
Công cụ xóa bộ nhớ cache và reset Kodi về mặc định
"""


KEEP_ADDONS = ['plugin.video.vietmediaf']

import os
import sys
import shutil
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import sqlite3
import json
import re
import math
from datetime import datetime, timedelta


def log(msg, level=xbmc.LOGINFO):
    """
    Ghi log vào Kodi log
    """
    xbmc.log("[KODI CLEANER] " + msg, level)

def get_size(path, total=0):
    """
    Lấy kích thước của thư mục
    """
    try:
        if os.path.isfile(path):
            return os.path.getsize(path) + total
        else:
            for root, dirs, files in os.walk(path):
                for f in files:
                    total += os.path.getsize(os.path.join(root, f))
    except Exception as e:
        log(f"Lỗi khi tính kích thước: {str(e)}", xbmc.LOGERROR)
        pass
    return total

def convert_size(size):
    """
    Chuyển đổi kích thước từ byte sang đơn vị dễ đọc
    """
    if size == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return f"{s} {size_name[i]}"

def remove_folder(path):
    """
    Xóa thư mục và tất cả nội dung bên trong
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            return True
        except Exception as e:
            log(f"Lỗi khi xóa thư mục {path}: {str(e)}", xbmc.LOGERROR)
            return False
    return False

def remove_file(path):
    """
    Xóa file
    """
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception as e:
            log(f"Lỗi khi xóa file {path}: {str(e)}", xbmc.LOGERROR)
            return False
    return False

def get_kodi_paths():
    """
    Lấy các đường dẫn quan trọng của Kodi
    """
    paths = {}

    
    paths['HOME'] = xbmcvfs.translatePath('special://home/')
    paths['TEMP'] = xbmcvfs.translatePath('special://temp/')
    paths['USERDATA'] = xbmcvfs.translatePath('special://userdata/')
    paths['DATABASE'] = xbmcvfs.translatePath('special://database/')
    paths['THUMBNAILS'] = xbmcvfs.translatePath('special://thumbnails/')
    paths['ADDONS'] = os.path.join(paths['HOME'], 'addons')
    paths['ADDON_DATA'] = os.path.join(paths['USERDATA'], 'addon_data')
    paths['PACKAGES'] = os.path.join(paths['ADDONS'], 'packages')

    return paths

def get_latest_db(database_type):
    """
    Lấy file database mới nhất của một loại cụ thể
    """
    paths = get_kodi_paths()
    database_path = paths['DATABASE']
    files = os.listdir(database_path)

    db_pattern = database_type + '*.db'
    db_files = [f for f in files if re.match(db_pattern, f, re.IGNORECASE)]

    if not db_files:
        return None

    
    db_files.sort(key=lambda x: int(re.search(r'\d+', x).group(0) if re.search(r'\d+', x) else 0), reverse=True)

    return db_files[0]

def clear_cache():
    """
    Xóa bộ nhớ cache của Kodi
    """
    paths = get_kodi_paths()

    
    cache_dirs = [
        os.path.join(paths['HOME'], 'cache'),
        os.path.join(paths['TEMP']),
    ]

    
    for root, dirs, files in os.walk(paths['ADDON_DATA']):
        
        addon_id = os.path.basename(root)
        if addon_id in KEEP_ADDONS:
            log(f"Bỏ qua cache của addon {addon_id} (được bảo vệ)")
            continue

        for d in dirs:
            if 'cache' in d.lower() and d.lower() not in ['meta_cache']:
                cache_dirs.append(os.path.join(root, d))

    
    deleted_size = 0
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            
            skip = False
            for addon in KEEP_ADDONS:
                if addon in cache_dir:
                    log(f"Bỏ qua cache: {cache_dir} (thuộc addon được bảo vệ)")
                    skip = True
                    break

            if skip:
                continue

            size = get_size(cache_dir)
            deleted_size += size
            remove_folder(cache_dir)
            log(f"Đã xóa cache: {cache_dir}")

    
    if xbmc.getCondVisibility('System.HasAddon(script.module.resolveurl)'):
        xbmc.executebuiltin('RunPlugin(plugin://script.module.resolveurl/?mode=reset_cache)')
    if xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
        xbmc.executebuiltin('RunPlugin(plugin://script.module.urlresolver/?mode=reset_cache)')

    return deleted_size

def clear_thumbnails():
    """
    Xóa thumbnails của Kodi
    """
    paths = get_kodi_paths()

    
    thumb_dirs = [
        paths['THUMBNAILS'],
    ]

    
    thumb_dirs.append(os.path.join(paths['ADDON_DATA'], 'script.module.metadatautils', 'animatedgifs'))
    thumb_dirs.append(os.path.join(paths['ADDON_DATA'], 'script.extendedinfo', 'images'))

    
    textures_db = get_latest_db('Textures')
    if textures_db:
        textures_db_path = os.path.join(paths['DATABASE'], textures_db)
        remove_file(textures_db_path)
        log(f"Đã xóa database textures: {textures_db_path}")

    
    deleted_size = 0
    for thumb_dir in thumb_dirs:
        if os.path.exists(thumb_dir):
            
            skip = False
            for addon in KEEP_ADDONS:
                if addon in thumb_dir:
                    log(f"Bỏ qua thumbnails: {thumb_dir} (thuộc addon được bảo vệ)")
                    skip = True
                    break

            if skip:
                continue

            size = get_size(thumb_dir)
            deleted_size += size
            remove_folder(thumb_dir)
            log(f"Đã xóa thumbnails: {thumb_dir}")

    return deleted_size

def clear_packages():
    """
    Xóa các gói cài đặt đã tải về
    """
    paths = get_kodi_paths()
    packages_dir = paths['PACKAGES']

    deleted_size = 0
    if os.path.exists(packages_dir):
        size = get_size(packages_dir)
        deleted_size += size

        
        for root, dirs, files in os.walk(packages_dir):
            for f in files:
                file_path = os.path.join(root, f)
                remove_file(file_path)
                log(f"Đã xóa package: {file_path}")

    return deleted_size

def wipe_kodi():
    """
    Reset Kodi về mặc định
    """
    paths = get_kodi_paths()

    
    exclude_dirs = ['addons', 'userdata', 'packages', 'Database', 'Thumbnails']

    
    keep_files = []

    
    dialog = xbmcgui.Dialog()
    dialog.ok("Thông báo", f"Addon {', '.join(KEEP_ADDONS)} sẽ được giữ lại trong quá trình reset.")
    keep_sources = dialog.yesno("Xóa Kodi", "Bạn có muốn giữ lại nguồn phương tiện (sources.xml) không?")
    keep_favs = dialog.yesno("Xóa Kodi", "Bạn có muốn giữ lại mục yêu thích (favourites.xml) không?")
    keep_profiles = dialog.yesno("Xóa Kodi", "Bạn có muốn giữ lại hồ sơ người dùng (profiles.xml) không?")

    if keep_sources:
        keep_files.append('sources.xml')
    if keep_favs:
        keep_files.append('favourites.xml')
    if keep_profiles:
        keep_files.append('profiles.xml')

    
    for root, dirs, files in os.walk(paths['HOME'], topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for name in files:
            file_path = os.path.join(root, name)

            
            if os.path.basename(root) == 'userdata' and name in keep_files:
                log(f"Giữ lại file: {file_path}")
                continue

            remove_file(file_path)
            log(f"Đã xóa file: {file_path}")

    
    for root, dirs, files in os.walk(paths['HOME'], topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for name in dirs:
            dir_path = os.path.join(root, name)
            if not os.listdir(dir_path):  
                os.rmdir(dir_path)
                log(f"Đã xóa thư mục trống: {dir_path}")

    
    for db_file in os.listdir(paths['DATABASE']):
        if db_file.endswith('.db') and not db_file.startswith('Addons'):
            db_path = os.path.join(paths['DATABASE'], db_file)
            remove_file(db_path)
            log(f"Đã xóa database: {db_path}")

    
    for addon_id in KEEP_ADDONS:
        addon_path = os.path.join(paths['ADDONS'], addon_id)
        addon_data_path = os.path.join(paths['ADDON_DATA'], addon_id)

        if os.path.exists(addon_path):
            log(f"Giữ lại addon: {addon_path}")

        if os.path.exists(addon_data_path):
            log(f"Giữ lại dữ liệu addon: {addon_data_path}")

    
    clear_thumbnails()

    
    clear_cache()

    
    clear_packages()

    log("Đã reset Kodi về mặc định")

    
    dialog = xbmcgui.Dialog()
    if dialog.yesno("Reset Kodi", "Để thay đổi có hiệu lực cần thoát hẳn KODI.\nBạn có muốn thoát Kodi ngay bây giờ không?"):
        xbmc.executebuiltin('Quit')

def show_menu():
    """
    Hiển thị menu và xử lý lựa chọn của người dùng
    """
    dialog = xbmcgui.Dialog()
    dialog.ok("Thông báo", f"Addon {', '.join(KEEP_ADDONS)} sẽ được giữ lại trong quá trình dọn dẹp.")
    choice = dialog.select("Kodi Cleaner", [
        "1. Xóa bộ nhớ cache",
        "2. Xóa thumbnails",
        "3. Xóa packages",
        "4. Reset Kodi về mặc định",
        "5. Thoát"
    ])

    if choice == 0:  
        size = clear_cache()
        dialog.ok("Kodi Cleaner", f"Đã xóa bộ nhớ cache của Kodi.\nAddon {', '.join(KEEP_ADDONS)} được giữ lại.")
    elif choice == 1:  
        size = clear_thumbnails()
        dialog.ok("Kodi Cleaner", f"Đã xóa thumbnails của Kodi.\nAddon {', '.join(KEEP_ADDONS)} được giữ lại.")
    elif choice == 2:  
        size = clear_packages()
        dialog.ok("Kodi Cleaner", f"Đã xóa packages của Kodi.")
    elif choice == 3:  
        if dialog.yesno("Kodi Cleaner", f"Bạn có chắc chắn muốn reset Kodi về mặc định không?\nTất cả cài đặt và dữ liệu sẽ bị xóa.\nAddon {', '.join(KEEP_ADDONS)} sẽ được giữ lại."):
            wipe_kodi()
    elif choice == 4:  
        return
