import os
import re
import sys
import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
import urllib.request
import json
import requests
import zipfile
from resources.addon import notify, PROFILE_PATH, LOCK_PIN, alert, ADDON_ID
from resources.lib.constants import CACHE_PATH

ADDON_PATH = 'special://home/addons/plugin.video.vietmediaF'
# Sử dụng ảnh từ thư mục mới resources/images/tienich/
download_icon = ADDON_PATH + '/resources/images/tienich/my_downloads_.png'
clearcache_icon = ADDON_PATH + '/resources/images/tienich/clear_cache_.png'
backup_icon = ADDON_PATH + '/resources/images/tienich/backup_data__.png'
restore_icon = ADDON_PATH + '/resources/images/tienich/restore_data_.png'
forbidden_icon = ADDON_PATH + '/resources/images/tienich/restricted_.png'
log_icon = ADDON_PATH + '/resources/images/tienich/log.png'
onoff_icon = ADDON_PATH + '/resources/images/tienich/exit_.png'
settings_icon = ADDON_PATH + '/resources/images/tienich/advance_settings__.png'
fonts_icon = ADDON_PATH + '/resources/images/tienich/subtitle_fonts_.png'
install_skin_icon = ADDON_PATH + '/resources/images/tienich/install_skin_.png'


def add_menu_item(handle, label, path, is_playable=False, thumbnail='', plot=''):
    """Thêm một mục vào menu"""
    import xbmcgui
    import xbmcplugin

    list_item = xbmcgui.ListItem(label=label)
    list_item.setInfo('video', {'title': label, 'plot': plot})

    if thumbnail:
        list_item.setArt({'thumb': thumbnail, 'icon': thumbnail})

    list_item.setProperty('IsPlayable', 'true' if is_playable else 'false')

    xbmcplugin.addDirectoryItem(
        handle=handle,
        url=path,
        listitem=list_item,
        isFolder=not is_playable
    )

def get_tienich_menu_items():
    """
    Tạo danh sách các mục menu tiện ích
    """
    menu_items = [
        {
            "label": "Thiết lập nâng cao",
            "path": "plugin://plugin.video.vietmediaF?action=advanced_settings_menu",
            "is_playable": False,
            "thumbnail": settings_icon,
            "icon": settings_icon,
            "plot": "Thiết lập nâng cao cho Kodi"
        },
        {
            "label": "Thay đổi Skin Menu",
            "path": "plugin://plugin.video.vietmediaF?action=install_arctic_zephyr",
            "is_playable": False,
            "thumbnail": install_skin_icon,
            "icon": install_skin_icon,
            "plot": "Cài đặt skin Arctic Zephyr Mod và giải nén các file cấu hình"
        },
        {
            "label": "Thêm source repo vmf",
            "path": "plugin://plugin.video.vietmediaF?action=install_vmf_source",
            "is_playable": False,
            "thumbnail": install_skin_icon,
            "icon": install_skin_icon,
            "plot": "Thêm source repo VMF vào sources.xml"
        },
        {
            "label": "Cài fonts phụ đề",
            "path": "plugin://plugin.video.vietmediaF?action=subtitle_fonts",
            "is_playable": False,
            "thumbnail": fonts_icon,
            "icon": fonts_icon,
            "plot": "Cài đặt fonts phụ đề cho Kodi"
        },
        {
            "label": "Thư mục tải xuống",
            "path": "plugin://plugin.video.vietmediaF?action=__showdownload__",
            "is_playable": False,
            "thumbnail": download_icon,
            "icon": download_icon,
            "plot": "Hiển thị thư mục tải xuống"
        },
        {
            "label": "Xóa Cache",
            "path": "plugin://plugin.video.vietmediaF?action=clearCache",
            "is_playable": False,
            "thumbnail": clearcache_icon,
            "icon": clearcache_icon,
            "plot": "Xóa tất cả cache tạo ra bởi addon"
        },
        {
            "label": "Backup dữ liệu Addon",
            "path": "plugin://plugin.video.vietmediaF?action=__backup__",
            "is_playable": False,
            "thumbnail": backup_icon,
            "icon": backup_icon,
            "plot": "Lưu trữ dữ liệu cá nhân addon lên Fshare Drive"
        },
        {
            "label": "Phục hồi dữ liệu Addon",
            "path": "plugin://plugin.video.vietmediaF?action=__restore__",
            "is_playable": False,
            "thumbnail": restore_icon,
            "icon": restore_icon,
            "plot": "Phục hồi dữ liệu cá nhân lưu trên Fshare"
        },
        {
            "label": "Vùng cấm",
            "path": "plugin://plugin.video.vietmediaF?action=__forbiddenZone__",
            "is_playable": False,
            "thumbnail": forbidden_icon,
            "icon": forbidden_icon,
            "plot": "Các mục người dùng khóa"
        },

        {
            "label": "Thoát KODI",
            "path": "plugin://plugin.video.vietmediaF?action=__exitKodi__",
            "is_playable": False,
            "thumbnail": onoff_icon,
            "icon": onoff_icon,
            "plot": "Thoát KODI"
        }
    ]

    return menu_items


def display_tienich_menu():
    """
    Hiển thị menu tiện ích
    """

    menu_items = get_tienich_menu_items()


    for item in menu_items:

        list_item = xbmcgui.ListItem(label=item["label"])
        list_item.setArt({"icon": item["icon"], "thumb": item["thumbnail"]})


        info_tag = list_item.getVideoInfoTag()
        info_tag.setPlot(item["plot"])


        xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url=item["path"],
            listitem=list_item,
            isFolder=not item["is_playable"]
        )


    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

    return {"content_type": "", "items": []}


def get_tienich_data():
    """
    Lấy dữ liệu menu tiện ích
    """

    menu_items = get_tienich_menu_items()


    items = []
    for item in menu_items:

        formatted_item = {
            "label": item["label"],
            "is_playable": item["is_playable"],
            "path": item["path"],
            "thumbnail": item["thumbnail"],
            "icon": item["icon"],
            "label2": "",
            "info": {"plot": item["plot"]},
            "art": {"fanart": ""}
        }

        items.append(formatted_item)

    return {"content_type": "", "items": items}


def viewlog():
    """
    Hiển thị các lỗi ERROR trong file kodi.log
    """

    log_file = xbmcvfs.translatePath('special://logpath/kodi.log')

    error_logs = []

    try:

        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:

            for line in f:

                if ' ERROR: ' in line or 'ERROR:' in line:
                    error_logs.append(line.strip())


        if error_logs:

            if len(error_logs) > 1000:
                content = "\n".join(error_logs[-1000:]) + "\n\n[...] Hiển thị 1000 lỗi gần nhất trong tổng số " + str(len(error_logs)) + " lỗi."
            else:
                content = "\n".join(error_logs)


            dialog = xbmcgui.Dialog()
            dialog.textviewer("Kodi Log - ERROR", content)
        else:

            dialog = xbmcgui.Dialog()
            dialog.ok("Kodi Log", "Không có lỗi nào trong kodi.log")

    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi đọc log: {e}", level=xbmc.LOGERROR)
        dialog = xbmcgui.Dialog()
        dialog.ok("Lỗi", f"Không thể đọc kodi.log: {e}")


def add_lock_dir(item_path):
    item_path = re.sub('&d=__.*__','',item_path)
    filename = os.path.join(PROFILE_PATH, 'lock_dir.dat' )
    with open(filename,"a+") as f:
        f.write(item_path + "\n")
    notify('Đã khoá thành công')

def remove_lock_dir(item_path):
    filename = os.path.join(PROFILE_PATH, 'lock_dir.dat')
    if not os.path.exists(filename):
        return
    dialog = xbmcgui.Dialog()
    result = dialog.input('Nhập mã khoá', type=xbmcgui.INPUT_NUMERIC, option=xbmcgui.ALPHANUM_HIDE_INPUT | xbmcgui.INPUT_NUMERIC)

    if len(result) == 0 or result != LOCK_PIN:
        alert('Sai mật mã, vui lòng nhập lại')
        return
    item_path = re.sub('&d=__.*__', '', item_path)

    with open(filename, "r") as f:
        lines = f.readlines()
    with open(filename, "w") as f:
        for line in lines:
            if line != item_path + "\n":
                f.write(line)
    notify('Đã mở khoá thành công')

def check_lock_tmp(item_path):
    filename = os.path.join(PROFILE_PATH, 'lock_temp.dat')
    if not os.path.exists(filename):
        return False
    with open(filename, "r") as f:
        lines = f.readlines()
    return (item_path + "\n") in lines

def check_lock(item_path):
    filename = os.path.join(PROFILE_PATH, 'lock_dir.dat')
    if not os.path.exists(filename):
        return False
    with open(filename, "r") as f:
        lines = f.readlines()
    return (item_path + "\n") in lines

def writesub(text):
    filename = os.path.join(PROFILE_PATH, 'phude.srt' )
    if not os.path.exists(filename):
        with open(filename,"w+") as f:
            f.write("")
    else:
        with open(filename, "wb") as f:
            f.write(text.encode("UTF-8"))

def qrlink(url):
    match = re.search(r"url=([^&]+)", url)
    if match:
        url = match.group(1)

        image_url = f"https://api.qrserver.com/v1/create-qr-code/?color=000000&bgcolor=FFFFFF&data={url}&qzone=1&margin=1&size=400x400&ecc=L"
        import urllib.request
        userdata_path = xbmcvfs.translatePath('special://userdata')
        filename = 'qr_code.png'
        image_path = os.path.join(userdata_path, filename)

        urllib.request.urlretrieve(image_url, image_path)
        xbmc.executebuiltin('ShowPicture(%s)'%(image_path))
        notify("Dùng Fshare mobile và VLC Player để play trên điện thoại")
    else:
        alert("No link to display")
        exit()


def save_fshare_metadata(link, img, description):
    """
    Lưu metadata của các liên kết Fshare để sử dụng sau này

    Args:
        link (str): Liên kết Fshare
        img (str): Đường dẫn ảnh thumbnail
        description (str): Mô tả nội dung
    """
    try:

        cache_dir = xbmcvfs.translatePath('special://temp/fshare_cache')

        try:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
        except Exception as e:

            cache_dir = xbmcvfs.translatePath('special://temp')
            alert(f"Không thể tạo thư mục cache: {str(e)}. Sử dụng thư mục temp.")


        filename = link.split('/')[-1]

        filename = re.sub(r'[\r\n\t\\/:*?"<>|]', '', filename)

        if len(filename) > 50:
            filename = filename[:50]
        cache_path = os.path.join(cache_dir, f"{filename}.json")


        metadata = {
            "link": link,
            "image": img,
            "description": description
        }


        try:

            json_data = json.dumps(metadata, ensure_ascii=False)

            file_handle = xbmcvfs.File(cache_path, 'w')
            file_handle.write(json_data)
            file_handle.close()
        except Exception as e:
            alert(f"Lỗi khi ghi file metadata: {str(e)}")

    except Exception as e:
        alert(f"Lỗi khi lưu metadata Fshare: {str(e)}")


def get_cached_metadata(url):
    """
    Đọc metadata của các liên kết Fshare đã lưu trước đó

    Args:
        url (str): Liên kết Fshare cần đọc metadata

    Returns:
        dict: Metadata của liên kết Fshare hoặc None nếu không tìm thấy
    """
    try:

        filename = url.split('/')[-1]


        filename = re.sub(r'[\r\n\t\\/:*?"<>|]', '', filename)

        if len(filename) > 50:
            filename = filename[:50]


        cache_dirs = [
            xbmcvfs.translatePath('special://temp/fshare_cache'),
            xbmcvfs.translatePath('special://temp/cache/fshare'),
            xbmcvfs.translatePath('special://temp')
        ]

        for cache_dir in cache_dirs:
            cache_path = os.path.join(cache_dir, f"{filename}.json")


            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "r", encoding='utf-8') as f:
                        metadata = json.load(f)
                        return metadata
                except Exception:
                    pass


            try:
                if xbmcvfs.exists(cache_path):
                    file_handle = xbmcvfs.File(cache_path, 'r')
                    content = file_handle.read()
                    file_handle.close()
                    if content:
                        metadata = json.loads(content)
                        return metadata
            except Exception:
                pass

    except Exception as e:
        alert(f"Lỗi khi đọc metadata Fshare: {str(e)}")

    return None

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
        xbmc.log(f"[VietmediaF] Lỗi khi xóa cache: {str(e)}", xbmc.LOGERROR)
        return False
