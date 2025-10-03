#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import urlquick
import getlink, loadlistitem
import xbmcplugin
from six.moves import urllib_parse
from config import VIETMEDIA_HOST
from resources.addon import *
from resources import fshare, vmf, search, download, tvcine, tvhd, hdvn, iptv, speedfs, resetfs, cache_utils, gsheet, advanced_settings_menu, quick_account, skin_installer, thuviencine, source_installer, tmdb_search
from resources.utils import *
from resources.fshare import mobileScan
from resources.history_utils import search_history, fshare_history, hdvn_history, tvcine_history, watched_history
from resources.cache_manager import check_and_clear_cache
HANDLE = int(sys.argv[1])

# Định nghĩa biến disclaimer với chuỗi Unicode
disclaimer = """Addon VIETMEDIAF cung cấp nội dung từ nhiều nguồn khác nhau trên Internet.
Tuy nhiên, tác giả không chịu trách nhiệm về tính hợp pháp hoặc bản quyền của nội dung được cung cấp bởi addon này.
Người dùng phải tự chịu trách nhiệm khi sử dụng nội dung từ addon và đảm bảo rằng việc sử dụng nội dung đó tuân thủ các quy định bản quyền và luật pháp áp dụng."""

def check_history():
    return search_history.check_history()

def get_search_history():
    return search_history.get_history()

def save_search_history(query):
    search_history.save_history(query)

def delete_search_history():
    search_history.delete_history()


def check_fshare_history():
    return fshare_history.check_history()

def get_fshare_history():
    return fshare_history.get_history()

def save_fshare_history(query):
    fshare_history.save_history(query)

def delete_fshare_history():
    fshare_history.delete_history()

def check_hdvn_history():
    return hdvn_history.check_history()

def get_hdvn_history():
    return hdvn_history.get_history()

def save_hdvn_history(query):
    hdvn_history.save_history(query)

def delete_hdvn_history():
    hdvn_history.delete_history()


def check_tvcine_history():
    return tvcine_history.check_history()

def get_tvcine_history():
    return tvcine_history.get_history()

def save_tvcine_history(query):
    tvcine_history.save_history(query)

def delete_tvcine_history():
    tvcine_history.delete_history()


def check_watched_history():
    return watched_history.check_history()

def get_watched_history():
    return watched_history.get_history()

def save_watched_history(name, link, size):
    entry = f"{name},{link},{size}"
    watched_history.save_history(entry)

def delete_watched_history():
    watched_history.delete_history()


disclaimer_ = "[COLOR yellow]Addon VietmediaF[/COLOR]: là addon cho chương trình KODI, mã nguồn mở, dùng để thu thập các link của các tệp được chia sẻ trên Internet. Addon VietmediaF không tổ chức sản xuất, lưu trữ bất kì nội dung nào mà addon hiển thị trong chương trình của nó. Để dùng được người sử dụng cần có tài khoản vip của Fshare hoặc 4share.\n[COLOR yellow]Fshare, 4share[/COLOR]: là các dịch vụ cung cấp khả năng lưu trữ dữ liệu trực tuyến và có thể chia sẻ dữ liệu cho người khác.\n\n[B]Các nguồn nội dung addon sử dụng:[/B]\n[COLOR yellow]Cộng đồng chia sẻ[/COLOR]: là các nội dung do những người sử dụng dịch vụ cung cấp bởi Fshare, 4share chia sẻ trực tuyến cho mọi người.\n[COLOR yellow]thuviencine.com[/COLOR], [COLOR yellow]thuvienhd.xyz[/COLOR], [COLOR yellow]hdvietnam.xyz[/COLOR]...\nTrong quá trình sử dụng, các vấn đề liên quan đến các file chia sẻ, xin vui lòng liên hệ người chia sẻ hoặc các chủ sở hữu website trên."


# Hiển thị thông báo miễn trừ trách nhiệm nếu người dùng chưa đồng ý
if not ADDON.getSettingBool('disclaimer_agreed'):
    TextBoxes ("Information",disclaimer_)
    dialog = xbmcgui.Dialog()
    agree = dialog.yesno(ADDON_NAME, disclaimer, yeslabel='ĐỒNG Ý', nolabel='THOÁT')
    if agree:
        ADDON.setSettingBool('disclaimer_agreed', True)
    else:
        dialog.ok(ADDON_NAME, 'Bạn đang thoát khỏi Addon...')
        sys.exit()

# Hiển thị thông báo về các tính năng mới trong phiên bản 11.36
if not ADDON.getSettingBool('v11_36_update_seen'):
    new_features = """
Các tính năng mới cập nhật trong phiên bản 11.36:
[COLOR yellow]Account Profile[/COLOR]:
- Nhập nhanh tài khoản bằng mã QR và Account Code.
[COLOR yellow]Tiện ích[/COLOR]:
- Tắt ipv6.
- Thiết lập cache phù hợp với thiết bị.
- Thiết lập lựa chọn player ngoài.
- Nâng cấp dữ liệu phim từ thuviencine và thuvienhd.
- Thêm font phụ đề cho Kodi.
- Tương thích với skin.
[COLOR yellow]Thêm addon OpenWizard[/COLOR]:
- Cài đặt OpenWizard từ repository VietmediaF Official.
- Tích hợp bản build 11.36 đi kèm skin cực đẹp.
- Các tính năng bảo trì, backup dữ liệu KODI.
[COLOR yellow]Enjoy Kodi![/COLOR]
    """
    TextBoxes("Tính năng mới cập nhật v11.36", new_features)
    ADDON.setSettingBool('v11_36_update_seen', True)

def urlencode(url):
    return urllib.parse.quote_plus(url)

def fetch_data_default(url, headers=None):
    if '?action=menu' in url:
        data = getMenu()
        OnOffHistoryWatching = ADDON.getSettingBool("OnOffHistoryWatching")
        if not OnOffHistoryWatching:
            for item in data['items']:
                if 'Lịch sử xem phim' in item['label']:
                    data['items'].remove(item)
                    break
        return data
    elif 'FshareMenu' in url:
        return getFshareMenu()
    elif 'FshareHost' in url:
        return FshareHost()
    elif 'getTienich' in url:
        return getTienich()
    elif 'getAccFshare' in url:
        return getAccFshare()
    else:

        return fetch_data(url, headers)

def getTinyCC(url):
    import requests
    from requests.structures import CaseInsensitiveDict
    shorten_host = ADDON.getSetting('shorten_host')
    headers = CaseInsensitiveDict()
    headers["authority"] = shorten_host
    headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
    if "gg.gg" in url:
        url = url.replace("https","http")
    resp = requests.get(url, headers=headers)
    return(resp.status_code,resp.url)
def fshare_top_follow():
    return fshare.fshare_top_follow()

def fshare_favourite(url):
    return fshare.fshare_favourite(url)
def add_remove_favourite(url,status):
    fshare.add_remove_favourite(url,status)
def process_url_input(url_input):
    import requests
    url_input = url_input.replace("&", "[]")
    url_input = url_input.replace("+", "[]")
    links = url_input.split('[]')
    if len(links) == 2:
        url_input = links[0]
        subs = links[1]
    else:
        subs = ''

    if 'fshare' in url_input:
        if 'token' in url_input:
            match = re.search(r"(\?.+?\d+)", url_input)
            _token = match.group(1)
            url_input = url_input.replace(_token, '')
        name, file_type, file_size = fshare.get_fshare_file_info(url_input)

        thumbnail = 'fshare.png'
        if 'folder' in url_input:
            regex = r"folder\/(.+)"
        else:
            regex = r"file\/(.+)"
        match = re.search(regex, url_input)
        f_id = match.group(1)

        if "folder" in url_input:
            file = 'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/' + f_id
            playable = False
            if len(name) == 0:
                name = 'Folder to play'
        else:
            file = 'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/' + f_id + '[]' + subs
            playable = True
            if len(name) == 0:
                name = 'File to play'

    elif 'drive.google.com' in url_input:
        file = 'plugin://plugin.video.vietmediaF?action=play&url=' + url_input
        playable = True

    elif "docs.google.com" in url_input:
        r = requests.get(url_input)
        regex = r"title\" content=\"(.*?)\""
        d = re.search(regex, r.text)
        if d:
            name = d.group(1)
            if "|" in name:
                t = name.split("|")
                name = t[0]
                thumbnail = t[1]
            else:
                thumbnail = "https://i.imgur.com/ib5f09u.png"
        else:
            name = "Chia sẻ Google Sheet"
        file = 'plugin://plugin.video.vietmediaF?action=play&url=' + url_input
        playable = False
        file_size = ''

    elif '4share.vn' in url_input:
        if '/f/' in url_input:
            name, file_size = getlink.get_4file_information(url_input)
            file_size = file_size + " Gb - "
            thumbnail = '4s.png'
            playable = True
            file = 'plugin://plugin.video.vietmediaF?action=play&url=' + url_input
        if '/d/' in url_input:

            r = requests.get(url_input)
            regex = r"<h1 style='font-size: 22px'>(.+?)</h1>"
            match = re.search(regex, r.text)
            name = match.group(1)
            file_size = ''
            playable = False
            thumbnail = '4s.png'
            file = 'plugin://plugin.video.vietmediaF?action=play&url=' + url_input
    else:
        try:

            if "tinyurl.com/app/nospam" in url_input:
                alert("URL đã bị xóa hoặc không tồn tại")

                data = getMenu()
                loadlistitem.list_item_main(data)
                return data
            import requests
            try:
                r = requests.head(url_input, timeout=5, verify=False)
                if r.status_code != 200:
                    alert(f"URL không hợp lệ hoặc không tồn tại (Mã lỗi: {r.status_code})")

                    data = getMenu()
                    loadlistitem.list_item_main(data)
                    return data
            except requests.exceptions.RequestException as e:
                alert(f"Lỗi kết nối: {str(e)}")

                data = getMenu()
                loadlistitem.list_item_main(data)
                return data


            data = list_link(url_input)
            loadlistitem.list_item(data)
        except Exception as e:
            alert(f"Lỗi khi xử lý URL: {str(e)}")

            data = getMenu()
            loadlistitem.list_item_main(data)

    items = []
    item = {}
    item["label"] = '[COLOR yellow]' + name + '[/COLOR]'
    item["is_playable"] = playable
    item["path"] = file
    item["thumbnail"] = play_icon
    item["icon"] = play_icon
    item["label2"] = ""
    item["info"] = {'plot': '', 'size': file_size}
    items = [item]

    if 'fshare.vn' in url_input:
        SaveNumberHistory(name, url_input, thumbnail)
    else:
        SaveNumberHistory(name, file, thumbnail)

    data = {"content_type": "episodes", "items": ""}
    data.update({"items": items})
    return data

def PlayCode():
    """Hàm xử lý nhập code từ các dịch vụ rút gọn link"""

    history_file = os.path.join(PROFILE_PATH, 'history.dat')
    history = []

    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as file:
                history = [line.strip() for line in file.readlines() if line.strip()]
        except Exception as e:
            logError(f"Error reading history file: {e}")

    shorten_host = ADDON.getSetting('shorten_host')
    if not shorten_host:
        alert("Vui lòng thiết lập dịch vụ làm ngắn link trong Addon Setting")
        ADDON.openSettings()
        return {"content_type": "episodes", "items": []}

    if not history:
        return input_code_and_process(shorten_host)

    options = ["[Nhập code mới]", "[Xoá lịch sử nhập code]"] + [line.split(',')[0] for line in history if ',' in line]
    dialog = xbmcgui.Dialog()
    selected = dialog.select("Chọn code hoặc nhập code mới", options)

    if selected == -1:
        notify("Thao tác bị hủy")

        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "episodes", "items": []}
    elif selected == 0:
        return input_code_and_process(shorten_host)
    elif selected == 1:
        confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xoá lịch sử nhập code không?")
        if confirm:
            if os.path.exists(history_file):
                open(history_file, 'w').close()
                notify("Đã xoá lịch sử nhập code")

                xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        else:
            xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "episodes", "items": []}
    else:
        selected_history = history[selected - 2]
        parts = selected_history.split(',')
        if len(parts) >= 2:
            link = parts[1].strip()
            if link.startswith('plugin://plugin.video.vietmediaF?action=play&url='):
                real_url = link.replace('plugin://plugin.video.vietmediaF?action=play&url=', '')
                return process_url_input(real_url)
            else:
                return process_url_input(link)
        else:
            notify("Lịch sử không hợp lệ")
            return {"content_type": "episodes", "items": []}

def input_code_and_process(shorten_host):
    """Hàm nhập code và xử lý"""
    keyboardHandle = xbmc.Keyboard('', 'Dịch vụ rút gọn link [COLOR yellow]' + shorten_host + '[/COLOR] đang được sử dụng')
    keyboardHandle.doModal()

    if not keyboardHandle.isConfirmed() or not keyboardHandle.getText().strip():
        notify("Không có dữ liệu được nhập")
        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "episodes", "items": []}

    code = keyboardHandle.getText().strip()
    shortern_site = 'https://' + shorten_host + '/'
    shortern_link = shortern_site + code
    status_code, url_final = getTinyCC(shortern_link)

    if status_code != 200:
        alert("Xin vui lòng kiểm tra lại link hoặc thiết lập đúng dịch vụ rút gọn link trong Addon Setting")
        ADDON.openSettings()
        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "episodes", "items": []}

    if "tinyurl.com/app/nospam" in url_final:
        alert("URL đã bị xóa hoặc không tồn tại")
        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "episodes", "items": []}

    return process_url_input(url_final)
def SaveNumberHistory(name, link, thumb):
    """Lưu lịch sử nhập code với xử lý trùng lặp tốt hơn"""

    if link.startswith('plugin://plugin.video.vietmediaF?action=play&url='):
        link = link.replace('plugin://plugin.video.vietmediaF?action=play&url=', '')


    entry = name + ',' + link

    if thumb and thumb.strip():
        entry += ',' + thumb

    filename = os.path.join(PROFILE_PATH, 'history.dat')
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(entry)
        return
    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()


        lines = [line.strip() for line in lines if line.strip()]
        base_link = link.split('[]')[0] if '[]' in link else link
        updated_lines = []
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                line_link = parts[1].strip()
                line_base_link = line_link.split('[]')[0] if '[]' in line_link else line_link
                if line_base_link == base_link:
                    continue

            updated_lines.append(line)
        updated_lines.insert(0, entry)


        with open(filename, "w", encoding="utf-8") as f:
            f.write('\n'.join(updated_lines))

    except Exception as e:
        logError(f"Error in SaveNumberHistory: {e}")

def search_content(search_type, query=None):

    try:
        if search_type == 'fshare':

            if query:
                data = search.searchvmf(query)
                save_search_history(query)
                loadlistitem.list_item_main(data)
            else:
                FshareSearchQuery()
                return
        elif search_type == '4share':

            if query:
                data = search.searchFourshare(query, 1)
                save_fshare_history(query)
                loadlistitem.list_item_main(data)
            else:
                FourshareSearchQuery(page=1)
                return
        elif search_type == 'tvhd':

            if query:
                search.searchtvhd(query)
            else:
                keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    query = keyboard.getText()
                    search.searchtvhd(query)
                else:
                    notify("Đã hủy tìm kiếm")
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                return
        else:
            notify("Loại tìm kiếm không hợp lệ")
            return
    except Exception as e:
        notify(f"Lỗi khi tìm kiếm: {str(e)}")
        return None

def timkiemMenu():
    search_icon = ADDON_PATH + "/resources/images/search.png"
    top_icon = ADDON_PATH + "/resources/images/top.png"

    menu_items = [
        {
            "label": "[COLOR yellow]Tìm kiếm[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF?action=_timtrenfshare_",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên Fshare"
        },
        {
            "label": "[COLOR yellow]Tìm kiếm TMDB[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF?action=tmdbsearch",
            "icon": search_icon,
            "plot": "Tìm kiếm phim và TV series qua TMDB API"
        },
        {
            "label": "[COLOR yellow]Tìm kiếm trên TVHD[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF?action=__searchTVHD__",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên TVHD"
        },
        {
            "label": "[COLOR yellow]Tìm kiếm trên thuviencine[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF/?action=browse&url=https://thuviencine.com/timkiem/",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên thuviencine"
        },
        {
            "label": "[COLOR yellow]Tìm kiếm trên hdvietnam[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF/?action=browse&url=https://www.hdvietnam.xyz/timkiem/",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên hdvietnam"
        },
        {
            "label": "[COLOR yellow]timfshare.com[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF?action=browse&url=__TIMFSHARE__",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên timfshare.com"
        },
        {
            "label": "Top 100 link tìm kiếm",
            "path": "plugin://plugin.video.vietmediaF?action=_topsearch100_",
            "icon": top_icon,
            "plot": "Xem danh sách 100 link Fshare được xem nhiều nhất"
        },
        {
            "label": "[COLOR yellow]Tìm kiếm trên 4share[/COLOR]",
            "path": "plugin://plugin.video.vietmediaF?action=_timtren4share_",
            "icon": search_icon,
            "plot": "Tìm kiếm nội dung trên 4share"
        },
        {
            "label": "Addon Timfshare",
            "path": "plugin://plugin.video.timfshare/",
            "icon": search_icon,
            "plot": "Mở addon Timfshare"
        }
    ]


    for item in menu_items:
        list_item = xbmcgui.ListItem(label=item["label"])
        list_item.setArt({"icon": item["icon"], "thumb": item["icon"]})
        info_tag = list_item.getVideoInfoTag()
        info_tag.setPlot(item["plot"])
        xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url=item["path"],
            listitem=list_item,
            isFolder=True
        )
    xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)

def watchedHistoryList():
    if not check_watched_history():
        notify("Chưa có lịch sử xem phim")
        return {"content_type": "episodes", "items": []}

    items = []
    try:
        history = get_watched_history()

        for entry in history:
            parts = entry.strip().split(",")
            if len(parts) < 2:
                continue

            if len(parts) >= 3:
                name, link, size = map(str.strip, parts[:3])

            else:
                name, link = map(str.strip, parts[:2])
                size = "0"


            if "File không tồn tại" in name:
                continue

            link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % link
            playable = True


            item = {
                "label": name,
                "is_playable": playable,
                "path": link,
                "thumbnail": "",
                "icon": xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'images', 'fsvideo.png')),
                "label2": "",
                "info": {'plot': 'Giữ nút OK 2s trên điều khiển để xoá lịch sử xem', 'size': size}

            }

            items.append(item)
    except Exception as e:

        logError(f"Error in watchedHistoryList: {e}")

    return {"content_type": "files", "items": items}
def watchingHistory(link):
    """Lưu lịch sử xem phim"""
    if "fshare.vn" in link:
        try:

            name, file_type, size_file = fshare.get_fshare_file_info(link)


            save_watched_history(name, link, size_file)
        except Exception as e:
            logError(f"Error in watchingHistory: {e}")
            alert(f"Error in watchingHistory: {e}")

def list_link(url_input):
    """
    Phân tích nội dung từ URL và trả về danh sách các mục
    """
    import requests
    from six.moves import urllib_parse

    try:
        useragent = ("User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0")
        headers = {'User-Agent': useragent}
        r = requests.get(url_input, headers=headers, verify=False, timeout=10)


        if r.status_code != 200:
            alert(f"URL không hợp lệ hoặc không tồn tại (Mã lỗi: {r.status_code})")
            xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
            return {"content_type": "movies", "items": []}

        r = r.text
        r = r.replace('\n', '').replace('\r', '')
        lines = r.split('*')


        if len(lines) <= 1:
            alert("URL không chứa nội dung hợp lệ")
            xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
            return {"content_type": "movies", "items": []}

        t = len(lines)
        items = []
        name = ''

        for i in range(1, t):
            item = {}
            line = (lines[i])
            line = line.split("|")


            if len(line) < 1:
                continue

            name = line[0]
            try: href = line[1]
            except: href = ''
            sub = ''
            try: sub = line[2]
            except: sub = ''
            href = href+'[]'+sub
            thumb = ''
            if len(line) > 3: thumb = line[3]
            info = ''
            if len(line) > 4: info = line[4].strip()


            name = urllib_parse.unquote_plus(name)

            if '@' in name or 'folder' in href or "pastebin.com" in href or '"docs.google.com"' in href:
                playable = False
                link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % href
            else:
                playable = True
                link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % href


            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = thumb
            item["icon"] = "https://i.imgur.com/8wyaJKv.png"
            item["label2"] = ""
            item["info"] = {'plot': info}
            items.append(item)


        if not items:
            alert("Không tìm thấy nội dung hợp lệ trong URL")
            xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
            return {"content_type": "movies", "items": []}

        data = {"content_type": "movies", "items": ""}
        data.update({"items": items})
        return data

    except requests.exceptions.RequestException as e:

        alert(f"Lỗi kết nối: {str(e)}")
        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "movies", "items": []}
    except Exception as e:

        alert(f"Lỗi khi xử lý URL: {str(e)}")
        xbmc.executebuiltin("Container.Update(plugin://plugin.video.vietmediaF, replace)")
        return {"content_type": "movies", "items": []}
def fourshare_folder(url):
    folder_id = re.search(r"d/(.+)",url).group(1)
    list_file_url = 'https://api.4share.vn/api/v1/?cmd=list_file_in_folder_share&folder_id=%s&page=0&limit=100' % folder_id
    response = urlquick.get(list_file_url)
    jdata = json.loads(response.content)
    items = []
    for file in jdata["payload"]:
        item = {}
        typef = file["type"]
        if typef == "file":
            playable = True
        else:playable = False
        size = file["size"]
        item["label"] = file["name"]
        item["is_playable"] = playable
        item["path"] = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % file["link"]
        item["thumbnail"] = 'https://4share.vn/template/4s/images/logo4s.png'
        item["icon"] = "https://4share.vn/template/4s/images/logo4s.png"
        item["label2"] = ""
        item["info"] = {'plot': '','size':size}
        items += [item]

    data = {"content_type": "episodes", "items": ""}
    data.update({"items": items})

    return data

def updateAcc():
    session_id = ADDON.getSetting("session_id")
    if fshare.isvalid(session_id):
        fshare.logout()
    token, session_id = fshare.login()
    vDialog.create(ADDON_NAME+" " +VERSION, "Kiểm tra tài khoản thông tin tài khoản")
    header = {'Cookie': 'session_id=' + session_id}
    r = requests.get('https://api.fshare.vn/api/user/get', headers=header, verify=False)
    jstr = json.loads(r.content)
    acc_type = jstr['account_type']
    if "Download" in acc_type:
        acc_type = "Download (No Cloud)"

    if "Bundle" in acc_type or "Forever" in acc_type or "ADSL2plus" in acc_type:
        expiredDate = str("4102444799")
    else:
        expiredDate = jstr["expire_vip"]
    point = jstr['totalpoints']
    mail = jstr['email']

    webspace = float(jstr['webspace']) / float(1073741824)
    webspace_used = '{0:.2f}'.format(float(jstr['webspace_used']) / float(1073741824))
    filename = os.path.join(PROFILE_PATH, 'expired.dat')
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            f.write(expiredDate)
    else:
        with open(filename, "wb") as f:
            f.write(expiredDate.encode("UTF-8"))
    if acc_type == "Member":


        image_path = "https://i.imgur.com/NNFY9qW.png"
        xbmc.executebuiltin('ShowPicture(%s)'%(image_path))

    else:
        if "Download" in acc_type:
            acc_type = "Vip-Download"
            webspace = '0'
            webspace_used = '0'


        line = 'E-mail: [COLOR yellow]%s[/COLOR] - ' % mail
        line += 'Loại tài khoản: [COLOR yellow]%s[/COLOR]\n' % acc_type
        line += 'Point: [COLOR yellow]%s[/COLOR]\n' % point
        line += 'Dung lượng lưu trữ: [COLOR yellow]%s Gb[/COLOR] / ' % webspace
        line += 'Đã sử dụng [COLOR yellow]%s Gb[/COLOR]\n' % webspace_used

        vDialog.close()
        alert(line, title='Fshare vip - [COLOR yellow]zalo.me/0915134560[/COLOR]')

def fsharegetFolder(url):
    return fshare.fsharegetFolder(url)
def FshareSearchQuery():


    history = get_search_history()


    if not history:
        keyboard = xbmc.Keyboard("", "Nhập từ khóa để tìm kiếm")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
        else:
            notify("Đã hủy tìm kiếm")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
            return
    else:
        options = ["[Nhập từ khóa mới]", "[Xóa lịch sử tìm kiếm]"] + history
        dialog = xbmcgui.Dialog()
        selected = dialog.select("Chọn từ khóa tìm kiếm", options)

        if selected == -1:
            notify("Đã hủy tìm kiếm")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
            return
        elif selected == 0:
            keyboard = xbmc.Keyboard("", "Nhập từ khóa để tìm kiếm")
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                query = keyboard.getText()
            else:
                notify("Đã hủy tìm kiếm")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                return
        elif selected == 1:
            confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch sử tìm kiếm không?")
            if confirm:
                delete_search_history()
                xbmc.executebuiltin("Container.Refresh")
            return
        else:
            query = options[selected]


    save_search_history(query)


    try:
        data = search.searchvmf(query)
        loadlistitem.list_item_search_history(data)
    except Exception as e:
        notify(f"Lỗi khi tìm kiếm: {str(e)}")


def searchHistory():

    if not check_history():
        FshareSearchQuery()
    else:
        items = []
        items1 = [{
            'label': '[COLOR yellow]Tìm kiếm Fshare[/COLOR]',
            'is_playable': False,
            'path': 'plugin://plugin.video.vietmediaF?action=_timtrenfshare1_',
            'thumbnail': 'https://i.imgur.com/F5582QW.png',
            'icon': 'https://i.imgur.com/F5582QW.png',
            'label2': '',
            'info': {
                'plot': 'Tìm kiếm nên gõ tiếng Anh để được kết quả chính xác nhất'},
            }]
        items2 = [{
            'label': '[COLOR yellow][I]Xoá lịch sử tìm kiếm[/I][/COLOR]',
            'is_playable': False,
            'path': 'plugin://plugin.video.vietmediaF?action=__removeAllSearchHistory__',
            'thumbnail': 'https://i.imgur.com/oS0Humg.png',
            'icon': 'https://i.imgur.com/oS0Humg.png',
            'label2': '',
            'info': {
                'plot': 'Xoá toàn bộ lịch sử tìm kiếm'}
            }]


        history = get_search_history()
        t = len(history)

        if t > 60:
            notify("Có vẻ danh sách tìm kiếm quá nhiều. Xoá đê")

        for name in history:
            item={}
            keyword = urllib_parse.quote_plus(name)
            playable = False
            item["label"] = "[I]"+name+"[/I]"
            item["is_playable"] = playable
            item["path"] = 'plugin://plugin.video.vietmediaF?action=_timtrenfshare1_&keyword=%s' % keyword
            item["thumbnail"] = "https://i.imgur.com/lwX6Kup.png"
            item["icon"] = "https://i.imgur.com/lwX6Kup.png"
            item["label2"] = ""
            item["info"] = {'plot': 'Kết quả tìm kiếm [COLOR yellow]'+name+'[/COLOR]'}
            items += [item]

        items=items1+items2+items
        data = {"content_type": "", "items": ""}
        data.update({"items": items})

        return data
def search4sHistory():

    if not check_fshare_history():
        FourshareSearchQuery(page=1)
    else:
        items = []
        items1 = [{
            'label': '[COLOR yellow]Tìm kiếm 4share[/COLOR]',
            'is_playable': False,
            'path': 'plugin://plugin.video.vietmediaF?action=_timtren4share1_',
            'thumbnail': 'https://i.imgur.com/F5582QW.png',
            'icon': 'https://i.imgur.com/F5582QW.png',
            'label2': '',
            'info': {
                'plot': 'Tìm kiếm nên gõ tiếng Anh để được kết quả chính xác nhất'},

            }]
        items2 = [{
            'label': '[COLOR yellow][I]Xoá lịch sử tìm kiếm[/I][/COLOR]',
            'is_playable': False,
            'path': 'plugin://plugin.video.vietmediaF?action=__removeAllSearchHistory4share__',
            'thumbnail': 'https://i.imgur.com/WE9wi4n.png',
            'icon': 'https://i.imgur.com/WE9wi4n.png',
            'label2': '',
            'info': {
                'plot': 'Xoá toàn bộ lịch sử tìm kiếm'}

                }]


        history = get_fshare_history()
        t = len(history)

        if t > 60:
            notify("Có vẻ danh sách tìm kiếm quá nhiều. Xoá đê")

        for name in history:
            item={}
            keyword = urllib_parse.quote_plus(name)
            playable = False
            item["label"] = "[I]"+name+"[/I]"
            item["is_playable"] = playable
            item["path"] = 'plugin://plugin.video.vietmediaF?action=_timtren4share1_&keyword=%s' % keyword
            item["thumbnail"] = "https://i.imgur.com/lwX6Kup.png"
            item["icon"] = "https://i.imgur.com/lwX6Kup.png"
            item["label2"] = ""
            item["info"] = {'plot': 'Kết quả tìm kiếm [COLOR yellow]'+name+'[/COLOR]'}

            items += [item]
        items=items1+items2+items
        data = {"content_type": "", "items": ""}
        data.update({"items": items})

        return data

def FourshareSearchQuery(page):


    history = get_fshare_history()


    if not history:
        keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
        else:
            notify("Đã hủy tìm kiếm")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
            return
    else:

        options = ["[Nhập từ khóa mới]", "[Xóa lịch sử tìm kiếm]"] + history
        dialog = xbmcgui.Dialog()
        selected = dialog.select("Chọn từ khóa tìm kiếm", options)

        if selected == -1:

            notify("Đã hủy tìm kiếm")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
            return
        elif selected == 0:

            keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm")
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                query = keyboard.getText()
            else:
                notify("Đã hủy tìm kiếm")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                return
        elif selected == 1:

            confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch sử tìm kiếm không?")
            if confirm:
                delete_fshare_history()
                notify("Đã xóa lịch sử tìm kiếm")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
            return
        else:

            query = options[selected]


    save_fshare_history(query)


    try:
        data = search.searchFourshare(query, page)
        loadlistitem.list_item_search_history(data)
    except Exception as e:
        notify(f"Lỗi khi tìm kiếm: {str(e)}")

def backup():
    import zipfile
    username_backup,password_backup = fshare.getBackupAcc()

    USERDATA = os.path.join(xbmcvfs.translatePath('special://home/'), 'userdata')
    favourite_file = xbmcvfs.translatePath(USERDATA+"/favourites.xml")
    sources_file=xbmcvfs.translatePath(USERDATA+"/sources.xml")

    backup_file = os.path.join(USERDATA, "backup.zip")
    progress = xbmcgui.DialogProgress()
    progress.create('Backup', 'Starting backup...')

    backup_zip = zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED)
    try:

        for root, dirs, files in os.walk(USERDATA):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, USERDATA)
                    backup_zip.write(file_path, arcname=arcname)

        for root, dirs, files in os.walk(PROFILE_PATH):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, USERDATA)
                backup_zip.write(file_path, arcname=arcname)

        backup_zip.close()

    except Exception as e:
        alert(f'Error while creating backup zip: {e}')


    filesize = os.path.getsize(backup_file)
    filename = os.path.basename(backup_file)
    backup_service = ADDON.getSetting('service.backup')

    if "fshare" in backup_service:
        payload = '{"app_key":"dMnqMMZMUnN5YpvKENaEhdQQ5jxDqddt","user_email":"'+username_backup+'","password":"'+password_backup+'"}'
        headers = {'cache-control': "no-cache", 'User-Agent': 'kodivietmediaf-K58W6U'}
        response = requests.post('https://api.fshare.vn/api/user/login', data=payload, headers=headers)
        if response.status_code == 200:
            progress.update(10, 'Uploading backup file to Fshare...')
            jStr = json.loads(response.content)
            token = jStr['token']
            session_id = jStr['session_id']
            headers = {'accept': 'application/json','User-Agent': 'kodivietmediaf-K58W6U','Cookie': 'session_id='+session_id,'Content-Type': 'application/json; charset=UTF-8'}
            json_data = {'name': filename,'size': str(filesize),'path': '/','token': token,'secured': 1}
            cookies = {'session_id':session_id}

            r = requests.get('https://api.fshare.vn/api/fileops/list?pageIndex=0&dirOnly=0&limit=60', headers=headers, verify=False)
            jdata = json.loads(r.content)

            for i in jdata:
                if i["name"] == "backup.zip":

                    linkcode = i["linkcode"]
                    delete_api = "https://api.fshare.vn/api/fileops/delete"
                    payload = {"token": token,"items": [linkcode]}
                    cookies = {'session_id': session_id}
                    headers = {
                      'Content-Type': 'application/json; charset=UTF-8',
                      'User-Agent': 'kodivietmediaf-K58W6U',
                      'Fshare-Session-ID': session_id
                    }
                    r = requests.post(delete_api, cookies=cookies, headers=headers, json=payload)
                    '''
                    if r.status_code == 200:
                        notify("Đã xoá file cũ")
                    '''
                    break
            progress.update(80, 'Uploading backup file to Fshare...')
            response = requests.post('https://api.fshare.vn/api/session/upload', cookies=cookies, headers=headers, json=json_data)
            r = json.loads(response.content)
            upload_link = r["location"]

            with open(backup_file, 'rb') as f:
                binary_data = f.read()
            r = requests.post(upload_link, data=binary_data, headers=headers)
            if r.status_code == 200:
                os.remove(backup_file)
                headers = {'Cookie': 'session_id=' + session_id}
                r = urlquick.get("https://api.fshare.vn//api/user/logout", headers=headers)
                if response.status_code == 200:
                    progress.update(100, 'Lưu trữ thành công...')

        elif response.status_code == 424:
            alert("Bạn đăng nhập sai quá 3 lần. Vui lòng đăng nhập lại")
        elif response.status_code == 409:
            alert("Account đã bị khoá login")
        else:
            alert("Kiểm tra lại tài khoản của bạn")
    elif "4share" in backup_service:

        alert("Phiên bản tiếp")
    progress.close()
def restore():
    import zipfile
    username_backup,password_backup = fshare.getBackupAcc()

    USERDATA = os.path.join(xbmcvfs.translatePath('special://home/'), 'userdata')

    if len(username_backup) > 0 and len(username_backup) > 0:
        progress = xbmcgui.DialogProgress()
        progress.create('Restore', 'Starting restore...')
        payload = '{"app_key":"dMnqMMZMUnN5YpvKENaEhdQQ5jxDqddt","user_email":"'+username_backup+'","password":"'+password_backup+'"}'
        headers = {'cache-control': "no-cache", 'User-Agent': 'kodivietmediaf-K58W6U'}
        response = requests.post('https://api.fshare.vn/api/user/login', data=payload, headers=headers)
        if response.status_code == 200:
            progress.update(0, 'Đang login tài khoản...')
            jStr = json.loads(response.content)
            token = jStr['token']
            session_id = jStr['session_id']
            headers = {'accept': 'application/json','User-Agent': 'kodivietmediaf-K58W6U','Cookie': 'session_id='+session_id,'Content-Type': 'application/json; charset=UTF-8'}
            cookies = {'session_id':session_id}

            r = requests.get('https://api.fshare.vn/api/fileops/list?pageIndex=0&dirOnly=0&limit=60', headers=headers, verify=False)
            jdata = json.loads(r.content)

            progress.update(1, 'Đang tìm kiếm file backup...')
            for i in jdata:

                if i["name"] == "backup.zip":
                    progress.update(20, 'Đã tìm thấy file backup...')
                    linkcode = i["linkcode"]

                    get_link = 'https://api2.fshare.vn/api/session/download'
                    link_backup = "https://www.fshare.vn/file/"+linkcode

                    data   = '{"token" : "%s", "url" : "%s", "password" : ""}'
                    data   = data % (token, link_backup)
                    header = {'Cookie' : 'session_id=' + session_id}
                    result = requests.post(get_link, headers=header, data=data)
                    jStr = json.loads(result.content)
                    backup_url = jStr['location']
                    backup_file_path = xbmcvfs.translatePath(USERDATA+"/backup.zip")
                    progress.update(40, 'Tải file backup...')
                    urllib.request.urlretrieve(backup_url, backup_file_path)
                    progress.update(60, 'Extract đữ liệu...')
                    with zipfile.ZipFile(backup_file_path, 'r') as backup_zip:
                        for item in backup_zip.infolist():
                            try:
                                if item.filename.endswith('.xml') or 'addon_data' in item.filename:
                                    backup_zip.extract(item, path=USERDATA)
                            except PermissionError:
                                if item.filename == 'guisettings.xml':
                                    continue
                                else:
                                    raise
                    progress.update(90, 'Xoá file tải về...')
                    os.remove(backup_file_path)

                    backup_file_temp = xbmcvfs.translatePath(PROFILE_PATH+"/backup.zip")
                    if os.path.exists(backup_file_temp):os.remove(backup_file_temp)

                    r = urlquick.get("https://api.fshare.vn//api/user/logout", headers=headers)
                    if response.status_code == 200:
                        progress.update(100, 'Phục hồi thành công...')
                        progress.close()
                        vmf.exit_kodi()
    else:
        alert("Bạn chưa nhập tài khoản để lưu trữ dữ liệu")

def downloadfile(url):
    download.downloadfile(url)
def showDownload():
    try:
        download_path = xbmcvfs.translatePath(ADDON.getSetting("download_path"))
        if not download_path:
            dialog = xbmcgui.Dialog()
            choice = dialog.yesno('Thiết lập đường dẫn', 'Đường dẫn lưu trữ chưa được thiết lập. Bạn có muốn thiết lập ngay bây giờ?')
            if choice:
                download_path = dialog.browse(3, 'Chọn đường dẫn lưu trữ', 'files')
                if not download_path:
                    return
                ADDON.setSetting("download_path", download_path)
            else:
                return

        items = os.listdir(download_path)
        for item in items:
            item_path = os.path.join(download_path, item)
            if os.path.isfile(item_path):
                # Hiển thị tất cả các file, không giới hạn định dạng
                file_size = os.path.getsize(item_path)
                list_item = xbmcgui.ListItem(label=item, path=item_path)
                list_item.setProperty("size", str(file_size))
                xbmcplugin.addDirectoryItem(handle=HANDLE, url=item_path, listitem=list_item)

        xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)
    except Exception as e:
        xbmc.log("Lỗi: " + str(e), level=xbmc.LOGERROR)

def delete_settings_file():
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    user_data_path = xbmcvfs.translatePath('special://userdata')
    addon_data_path = os.path.join(user_data_path, 'addon_data', addon_id)
    settings_file_path = os.path.join(addon_data_path, 'settings.xml')

    if os.path.exists(settings_file_path):
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Xoá Thông Tin Setting', 'Bạn có muốn xoá thông tin liên quan đến tài khoản cài đặt addon không?')
        if ret:
            try:
                os.remove(settings_file_path)
                return True
            except Exception as e:
                alert("Lỗi xoá file setting:", str(e))
                return False
        else:
            alert("Bạn đã huỷ xoá file")
            return False
    else:
        alert("File setting.xml không tồn tại")
        return False

def play(data):
    link = data["url"]

    if link is None or len(link) == 0:
        notify('Không lấy được link')
        return

    if 'text' in link or 'Text' in link:
        content = str(link).replace("text", "")
        TextBoxes(ADDON_NAME, content)
        return

    # Xử lý FShare folder URL
    if 'fshare' in link and 'folder' in link:
        xbmc.log(f"[VietmediaF] Processing FShare folder URL: {link}", xbmc.LOGINFO)
        data = cache_utils.cache_data(link)
        if data is not None:
            xbmc.log(f"[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main", xbmc.LOGINFO)
            loadlistitem.list_item_main(data)
        else:
            xbmc.log(f"[VietmediaF] FShare folder data is None, showing error", xbmc.LOGERROR)
            notify('Không thể tải danh sách folder')
        return

    if 'vtvgo' in link:
        link = getlink.get(link)
        item = xbmcgui.ListItem(path=link)
        xbmcplugin.setResolvedUrl(HANDLE, True, item)
        return


    from_history = False
    if "fshare.vn" in link and check_watched_history():

        history = get_watched_history()

        for entry in history:
            parts = entry.strip().split(",")
            if len(parts) >= 2 and link in parts[1]:
                from_history = True
                break

    try:
        if "fshare.vn" in link:
            OnOffHistoryWatching = xbmcaddon.Addon().getSettingBool("OnOffHistoryWatching")
            if OnOffHistoryWatching and not from_history:
                watchingHistory(link)


            if from_history:
                for entry in history:
                    parts = entry.strip().split(",")
                    if len(parts) >= 2 and link in parts[1]:
                        name = parts[0]
                        size = parts[2] if len(parts) > 2 else 0
                        break

            else:
                name, file_type, size = fshare.get_fshare_file_info(link)

                # Không kiểm tra loại file để cho phép phát tất cả các định dạng mà Kodi hỗ trợ
                # Bao gồm cả file .ts và .flac



        link = getlink.get(link)
        if not link:
            alert("Không lấy được link. Thử lại sau.")
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
            return

        subtitle = ''
        links = link.split('[]')

        if len(links) == 2:
            subtitle = links[1]
        elif data.get('subtitle'):
            subtitle = data.get('subtitle')

        if "qc" in subtitle:
            subtitle = ''

        link = links[0]

        def check_and_get_subtitle(name):
            subtitle_file_path = xbmcvfs.translatePath('special://userdata/phude.vmf')

            with xbmcvfs.File(subtitle_file_path, 'r') as file:
                content = file.read()
                lines = content.splitlines()

                for line in lines:
                    parts = line.split('|')

                    if len(parts) >= 2:
                        subtitle_name = parts[0].strip()
                        subtitle_name = os.path.splitext(subtitle_name)[0]
                        subtitle_link = parts[1].strip()

                        if subtitle_name == name:
                            return True, subtitle_link
                            break

            return False, None

        def download_and_set_subtitle(subtitle_url):
            useragent = ("User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0")
            headers = {'User-Agent': useragent}
            xbmc_temp = xbmcvfs.translatePath('special://temp')
            tempdir = os.path.join(xbmc_temp, 'phudeVMF')
            tmp_file = os.path.join(tempdir, "phude.srt")

            r = requests.get(subtitle_url, headers=headers)
            writesub(r.text)

            xbmc.sleep(500)
            filename = os.path.join(PROFILE_PATH, 'phude.srt')
            xbmc.Player().setSubtitles(filename)

        def resolve_and_notify(link, subtitle_url=None):
            try:
                if '4share' in link:
                    notify("Đang tạo cache cho 4share")


                use_external_player = ADDON.getSetting("external_player_enabled") == "true"

                if use_external_player:



                    dummy_item = xbmcgui.ListItem(path="special://home/addons/plugin.video.vietmediaF/resources/dummy.mp4")

                    xbmcplugin.setResolvedUrl(HANDLE, True, dummy_item)


                    success = advanced_settings_menu.launch_external_player(link, name)
                    exit()
                    if not success:
                        notify("Lỗi khi mở external player")
                        return
                    return


                item = xbmcgui.ListItem(path=link)
                if "fshare.vn" in link:
                    item.setMimeType('video/mp4')
                    item.setContentLookup(False)
                    info = {
                        'title': name,
                        'size': size,
                        'mediatype': 'video'
                    }
                    item.setInfo('video', info)

                xbmcplugin.setResolvedUrl(HANDLE, True, item)

                if subtitle_url:
                    download_and_set_subtitle(subtitle_url)
                elif "fshare.vn" in link:
                    found_subtitle, subtitle_link = check_and_get_subtitle(name)
                    if found_subtitle:
                        token, session_id = fshare.check_session()
                        subtitle_link = fshare.get_download_link(token, session_id, subtitle_link)
                        download_and_set_subtitle(subtitle_link)
                        notify("Đã tải phụ đề thành công.")
            except Exception as e:
                alert(f"Lỗi khi play video: {str(e)}")
                xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
                return

        if "fshare.vn" in link or "4share.vn" in link:
            resolve_and_notify(link, subtitle if len(subtitle) > 0 else None)

    except Exception as e:
        alert(f"Lỗi khi xử lý video: {str(e)}")
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return
def phim_list(url):
        response = requests.get(url)
        data = response.text

        start_index = data.index('{')
        end_index = data.rindex('}') + 1
        json_data = data[start_index:end_index]
        data = json.loads(json_data)
        items = [(row["c"][0]["v"], row["c"][1]["v"]) for row in data["table"]["rows"]]
        return(items)
def install_repo(url):
    """
    Cài đặt addon từ repository

    Args:
        url (str): URL của repository hoặc addon cần cài đặt
    """
    try:

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create("Đang cài đặt addon", "Đang cài đặt addon từ repository...")
        progress_dialog.update(50)


        xbmc.executebuiltin(f'InstallAddon({url})')


        xbmc.sleep(2000)

        progress_dialog.update(100, "Hoàn tất cài đặt addon!")
        progress_dialog.close()


        notify("Đã cài đặt addon thành công")

        return True

    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi cài đặt addon: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi khi cài đặt addon: {str(e)}")
        return False

def select_source(setting_key):
    sources = {
        'phimle_url': ('https://docs.google.com/spreadsheets/d/1OQkv_XDA4xdI16pedQuWDuEfnHYKgJf_nsi92y3UWLs/gviz/tq?gid=0&headers=1', 'Chọn một nguồn phim lẻ'),
        'phimbo_url': ('https://docs.google.com/spreadsheets/d/1OQkv_XDA4xdI16pedQuWDuEfnHYKgJf_nsi92y3UWLs/gviz/tq?gid=1057024371&headers=1', 'Chọn một nguồn phim bộ')
    }

    if setting_key not in sources:
        raise ValueError("Invalid setting key")

    url, dialog_title = sources[setting_key]

    response = requests.get(url)
    data = response.text

    start_index = data.index('{')
    end_index = data.rindex('}') + 1
    json_data = data[start_index:end_index]
    data = json.loads(json_data)
    items = [(row["c"][0]["v"], row["c"][1]["v"]) for row in data["table"]["rows"]]
    choices = [item[0] for item in items]

    selected = xbmcgui.Dialog().select(dialog_title, choices)

    if selected != -1:
        phim_url = items[selected][1]
        ADDON.setSetting(setting_key, phim_url)
        alert("Đã thiết lập thành công nguồn. Đợi một lúc để cập nhật mới danh sách.")
        if xbmcvfs.exists(CACHE_PATH):
            cache_utils.clean_old_json_files()


def parse_menu_data(data):

    hotsale_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'hotsale.png')
    search_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'search_.png')
    watch_history_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'history.png')
    speedtest_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'speedtest_.png')
    codeplay_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'codeplay_.png')
    utility_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'utilities_.png')
    account_profile_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'account_.png')
    iptv_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'iptv.png')
    share_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'sharing.png')
    fourshare_icon = os.path.join(ADDON_PATH, 'resources', 'images', '4share.png')
    web_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'web_fshare.png')
    theloai_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'genres.png')
    hot_movie_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'hot_movies_.png')
    source1_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'movies.png')
    source2_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'series.png')


    icon_map = {
        'promotion_icon': hotsale_icon,
        'search_icon': search_icon,
        'watch_history_icon': watch_history_icon,
        'speedtest_icon': speedtest_icon,
        'codeplay_icon': codeplay_icon,
        'utility_icon': utility_icon,
        'account_profile_icon': account_profile_icon,
        'iptv_icon': iptv_icon,
        'share_icon': share_icon,
        'fourshare_icon': fourshare_icon,
        'web_icon': web_icon,
        'theloai_icon': theloai_icon,
        'hot_movie_icon': hot_movie_icon,
        'source1_icon': source1_icon,
        'source2_icon': source2_icon
    }

    start_index = data.index('{')
    end_index = data.rindex('}') + 1
    json_data = data[start_index:end_index]
    parsed_data = json.loads(json_data)

    items = []
    for row in parsed_data['table']['rows']:
        label = row['c'][0]['v']
        path = row['c'][1]['v']
        playable = row['c'][2]['v']
        thumbnail_key = row['c'][3].get('v', '')
        icon_key = row['c'][4].get('v', '')
        label2 = row['c'][5].get('v', '')
        plot = row['c'][6].get('v', '')
        visible = row['c'][7]['v'] if len(row['c']) > 7 else "On"


        thumbnail = icon_map.get(thumbnail_key, '')
        icon = icon_map.get(icon_key, '')


        if not thumbnail:
            thumbnail = search_icon
        if not icon:
            icon = search_icon

        if visible == "On":
            item = {
                "label": label,
                "is_playable": False,
                "path": path,
                "thumbnail": thumbnail,
                "icon": icon,
                "label2": label2,
                "info": {"plot": plot},
                "art": {
                    "fanart": ''
                }
            }
            items.append(item)

    return items

def getMenu():

    url = 'https://docs.google.com/spreadsheets/d/1GjvqQgbLeMSXULB64BhLi4poxVv4V-PWCgeRBj3Zq4k/gviz/tq?gid=0&headers=1'
    response = urlquick.get(url, max_age=60 * 60)
    data = response.text
    items = parse_menu_data(data)
    return {"content_type": "", "items": items}


def getFshareMenu():
    max_age = 60 * 60
    max_retry = 3
    retry_count = 0

    while retry_count < max_retry:
        try:
            response = urlquick.get('https://docs.google.com/spreadsheets/d/1utbPZh4jNvm1U2xdrnWJpnq6RRZAnGNlmaNRCnjwKus/gviz/tq?gid=173971263&headers=1', max_age=max_age)
            data = response.text
            items = parse_menu_data(data)
            return {"content_type": "episodes", "items": items}
        except Exception as e:
            retry_count += 1
            notify("GoogleSheet Error:", e)
            time.sleep(5)



def FshareHost():
    tvhd_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'tvhd.jpeg')
    tvcn_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'tvcn.jpeg')
    hdvn_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'hdvn.jpeg')

    items = [
        {
            "label": "thuviencine.com",
            "is_playable": False,
            "path": "plugin://plugin.video.vietmediaF?action=browse&url=https://thuviencine.com/menu",
            "thumbnail": tvcn_icon,
            "icon": tvcn_icon,
            "label2": "thuviencine.com",
            "info": {"plot": "Dữ liệu được lấy từ thuviencine.com"},
            "art": {
                "thumb": tvcn_icon,
                "icon": tvcn_icon,
                "poster": tvcn_icon
            },
            "properties": {}
        },
        {
            "label": "thuvienhd.top",
            "is_playable": False,
            "path": "plugin://plugin.video.vietmediaF?action=browse&url=https://thuvienhd.top/menu",
            "thumbnail": tvhd_icon,
            "icon": tvhd_icon,
            "label2": "thuvienhd.top",
            "info": {"plot": "Dữ liệu được lấy từ thuvienhd.top"},
            "art": {
                "thumb": tvhd_icon,
                "icon": tvhd_icon,
                "poster": tvhd_icon
            },
            "properties": {}
        },
        {
            "label": "hdvietnam.xyz",
            "is_playable": False,
            "path": "plugin://plugin.video.vietmediaF?action=browse&url=https://hdvietnam/menu",
            "thumbnail": hdvn_icon,
            "icon": hdvn_icon,
            "label2": "hdvietnam.xyz",
            "info": {"plot": "Phim trên hdvietnam.xyz"},
            "art": {
                "thumb": hdvn_icon,
                "icon": hdvn_icon,
                "poster": hdvn_icon
            },
            "properties": {}
        }
    ]

    return {"content_type": "episodes", "items": items}
def getTienich():

    from resources.utils import get_tienich_data
    return get_tienich_data()
def getAccFshare():
    items = []

    password_icon = ADDON_PATH + '/resources/images/password_.png'
    settings_icon = ADDON_PATH + '/resources/images/setting_.png'
    refresh_icon = ADDON_PATH + '/resources/images/refresh_.png'
    favourite_icon = ADDON_PATH + '/resources/images/favourite_.png'
    top_icon = ADDON_PATH + '/resources/images/top_.png'
    home_icon = ADDON_PATH + '/resources/images/home_.png'
    fourshare_icon = ADDON_PATH + '/resources/images/4share.png'


    menu_items = [
        {
            "label": "Nhập tài khoản",
            "path": "plugin://plugin.video.vietmediaF?action=quick_account_menu",
            "icon": password_icon,
            "info": {"plot": "Nhập nhanh tài khoản Fshare bằng mã QR hoặc Code"}
        },
        {
            "label": "Account Settings",
            "path": "plugin://plugin.video.vietmediaF?action=__settings__",
            "icon": settings_icon,
            "info": {"plot": "Truy cập Addon settings"}
        },
        {
            "label": "Cập nhập thông tin tài khoản",
            "path": "plugin://plugin.video.vietmediaF?action=account_fshare",
            "icon": refresh_icon,
            "info": {"plot": "Kiểm tra và xem trạng thái tài khoản"}
        },
        {
            "label": "Fshare Favourites",
            "path": "plugin://plugin.video.vietmediaF?action=action=folderxxx",
            "icon": favourite_icon,
            "info": {"plot": "Xem thông tin các thư mục yêu thích"}
        },
        {
            "label": "Fshare Top Follow",
            "path": "plugin://plugin.video.vietmediaF?action=top_follow_share",
            "icon": top_icon,
            "info": {"plot": "Danh sách các file được follow nhiều nhất."}
        },
        {
            "label": "Home Fshare Acc",
            "path": "plugin://plugin.video.vietmediaF?action=home_fshare",
            "icon": home_icon,
            "info": {"plot": "Xem danh sách các file trong thư mục Home"}
        },
        {
            "label": "Xem thông tin tài khoản 4share",
            "path": "plugin://plugin.video.vietmediaF?action=get_user_information_fourshare",
            "icon": fourshare_icon,
            "info": {"plot": "Thông tin tài khoản 4share.vn"}
        },
    ]


    for i, item in enumerate(menu_items):
        menu_item = {
            "label": item["label"],
            "is_playable": False,
            "path": item["path"],
            "thumbnail": item["icon"],
            "icon": item["icon"],
            "label2": "",
            "info": item["info"]
        }
        items.append(menu_item)

    return {"content_type": "", "items": items}
def handle_google_docs_url(url):
        if ADDON.getSetting('gochiase') == 'false':
            dialog = xbmcgui.Dialog()
            confirmed = dialog.yesno("Cảnh báo", f"Đây là nội dung được lấy từ [COLOR yellow]danh sách chia sẻ file[/COLOR] của người sử dụng Fshare hoặc 4share. Lưu ý rằng VietmediaF không chịu trách nhiệm tính chính xác hoặc hợp pháp của nội dung từ [COLOR yellow]các danh sách này[/COLOR].\nNhấn YES/ĐỒNG Ý để tiếp tục hoặc NO/KHÔNG để hủy bỏ.")

            if confirmed:
                ADDON.setSetting('gochiase', 'true')
                data = cache_utils.cache_data(url)
                if data is not None:
                    loadlistitem.list_item_main(data)
            else:
                xbmc.executebuiltin("Action(Back)")

        else:
            data = cache_utils.cache_data(url)
            if data is not None:
                loadlistitem.list_item_main(data)
def go():

    url = sys.argv[0]+ sys.argv[2]
    xbmc.log(f"[VietmediaF] Processing URL in go(): {url}", xbmc.LOGINFO)

    if not "thread_id" in url:
        url = urllib_parse.unquote_plus(url)
        xbmc.log(f"[VietmediaF] Unquoted URL: {url}", xbmc.LOGINFO)

    # Parse URL parameters
    args = {}
    if '?' in url:
        query_string = url.split('?', 1)[1]
        args = dict(urllib_parse.parse_qsl(query_string))


    if 'action=thuviencine_top' in url:
        data = thuviencine.get_thuviencine_top()
        loadlistitem.list_item_main(data)
        return

    if url == 'plugin://plugin.video.vietmediaF/':
        url += '?action=menu'


    if '_debug_' in url:
        xbmc.executebuiltin('RunAddon("script.kodi.loguploader")')
        return
    if 'tkFshare' in url:
        ADDON.openSettings()
        exit()
    if '__download__' in url:
        downloadfile(url)
        return
    if '__showdownload__' in url:
        showDownload()
        exit()
    if "_showtkfs_" in url:
        password = ADDON.getSetting("fshare_password")
        if len(password) > 0:
            alert("Mật khẩu của bạn là: [COLOR yellow]%s[/COLOR]" % password)
        else:
            alert("Sau khi nhập thông tin phải nhấn OK để lưu giữ")
        return
    if '__speedtest__' in url:
        speedfs.sppedfs()
        exit()
    if '_resetsetting_' in url:
        if delete_settings_file():
            alert("Đã xoá file setting.xml thành công.")
        exit()
    if 'select_source_phimle' in url:
        select_source('phimle_url')
    if 'select_source_phimbo' in url:
        select_source('phimbo_url')

    if '_dellink_' in url:
        filename = os.path.join(PROFILE_PATH, 'yourlink.dat')
        if not os.path.exists(filename):notify('Bạn chưa có link nào được lưu.')
        else:
            with open(filename, "w") as f:
                lines = f.write('')
                notify('Done')
        return
    if '_number_' in url:

        data = PlayCode()
        loadlistitem.list_item_main(data)
        return
    if '_number1_' in url:

        shorten_host = ADDON.getSetting('shorten_host')
        if not shorten_host:
            alert("Vui lòng thiết lập dịch vụ làm ngắn link trong Addon Setting")
            ADDON.openSettings()
            return

        data = input_code_and_process(shorten_host)
        loadlistitem.list_item_main(data)
        return
    if "__forbiddenZone__" in url:
        lock_icon = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'images', 'lock.png'))
        lock_dir = os.path.join(PROFILE_PATH, 'lock_dir.dat')
        if not os.path.exists(lock_dir):
            notify("Chưa có gì bí mật để giấu")

        items = []
        with open(lock_dir, "r") as f:
            lines = f.readlines()
            t = (len(lines))

            for line in lines:
                item={}

                if "/folder/" in line or "/d/" in line or "browse" in line or "docs.google.com" in line or "episodes" in line:
                    playable = False
                    line = line.replace("url=plugin://plugin.video.vietmediaF?action=play&","")

                else: playable = True
                if "thread_id" in line or "node_id" in line:
                    regex = r"(\?action.*)"
                else:
                    regex = r"url=(https?://\S+)"
                match = re.search(regex,link)
                if match:
                    link = match.group(1)
                    link = "?url="+link
                link = link.replace("\n","")
                name = "[COLOR yellow][I]Mục bị khoá[/I][/COLOR]"

                size = ""
                item["label"] = name
                item["is_playable"] = playable

                item["path"] = 'plugin://plugin.video.vietmediaF%s' % link
                item["icon"] = "https://i.imgur.com/pHbuVqt.png"
                item["info"] = {'plot': 'Mục lưu trữ cần mật khẩu mở khoá'}
                item["label2"] = ""
                item["thumbnail"] = lock_icon
                item["art"] = {
                    "fanart":lock_icon,
                    "icon"  :lock_icon,
                    "poster":lock_icon,
                    "thumb":lock_icon
                    }
                items += [item]
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        loadlistitem.list_item_main(data)
        return
    if "__backup__" in url:
        backup()
        exit()
    if "__restore__" in url:
        restore()
        return
    if 'textbox' in url or 'Textbox' in url:
        import requests
        url = url.replace(VIETMEDIA_HOST + '/?action=textbox&', '')
        url = urllib_parse.unquote_plus(url)
        content = requests.get(url).text
        TextBoxes(ADDON_NAME, content)
        exit()
    if '_banggia_' in url:
        xbmc.executebuiltin(f"ShowPicture({re.search(r'__PIC__(.*)', getadv()['path']).group(1)})")

    if '_hdnhaptkfs_' in url:
        content = '''
        Nếu bạn có tài khoản là [COLOR yellow]tenban@gmail.com[/COLOR] thì bạn chọn "domain" là [COLOR yellow]gmail.com[/COLOR],\nmục "id mail" điền là [COLOR yellow]tenban[/COLOR].\n
        Nếu bạn có tài khoản là [COLOR yellow]tenban@xyz.com[/COLOR], mà không có trong danh sách domain thì bạn điền đủ ở mục "id mail" là [COLOR yellow]tenban@xyz.com[/COLOR],\nkhông cần chọn ở mục domain nữa.
        '''
        TextBoxes(ADDON_NAME, content)

    if '_topsearch100_' in url:
        data = search.top100search()
        loadlistitem.list_item_main(data)

    if 'addon' in url:
        url = url.replace(VIETMEDIA_HOST + '/?action=addon&', '')
        url = urllib_parse.unquote(url)
        install_repo(url)
        exit()
    if 'clearCache' in url:

        try:
            cache_utils.clear_cache_manual()

            xbmc.sleep(2000)
        except Exception as e:
            logError(f"Lỗi khi xóa cache: {str(e)}")
            alert(f"Lỗi khi xóa cache: {str(e)}")
        exit()
    if '__exitKodi__' in url:
        os._exit(1)
    if 'viewlog' in url:
        from resources.utils import viewlog
        viewlog()
        exit()
    if 'action=tienich' in url:
        from resources.utils import display_tienich_menu
        display_tienich_menu()
        return
    if 'action=subtitle_fonts' in url:
        from resources.subtitle_fonts import list_subtitle_fonts
        data = list_subtitle_fonts()
        loadlistitem.list_item_main(data)
        return
    if 'action=install_subtitle_font' in url:
        font = re.search(r'font=(.+?)(?:&|$)', url).group(1)
        from resources.subtitle_fonts import install_font
        install_font(font)

        loadlistitem.list_item_main({"content_type": "", "items": []})
        return
    if 'action=install_arctic_zephyr' in url:
        from resources.skin_installer import install_arctic_zephyr
        install_arctic_zephyr()

        loadlistitem.list_item_main({"content_type": "", "items": []})
        return
    if 'action=show_skin_install_guide' in url:
        from resources.skin_installer import show_skin_install_guide
        show_skin_install_guide()

        loadlistitem.list_item_main({"content_type": "", "items": []})
        return
    if "__history__" in url:
        data = PlayCode()
        loadlistitem.list_item_main(data)
        return
    if "__removeAllHistoryPlayCode__" in url:
            file = os.path.join(PROFILE_PATH, 'history.dat')
            open(file, 'w').close()
            notify("Đã xoá lịch sử nhập code")
            exit()
    if "__removeHistory__" in url:
        link = re.search(r"url=(http.*?)&d", url).group(1)
        file = os.path.join(PROFILE_PATH, 'history.dat')
        filetam = os.path.join(PROFILE_PATH, 'temp.dat')
        if os.path.exists(file):
            with open(file, "r") as input_file, open(filetam, "w") as output_file:
                for line in input_file:
                    if link not in line.strip("\n"):
                        output_file.write(line)
            os.replace(filetam, file)
            alert("Đã xoá xong")
        else:
            alert("Không tìm thấy tệp history.dat")
        if os.path.exists(file):
            file_size = os.path.getsize(file)
            if (int(file_size)) > 0:
                xbmc.executebuiltin("Container.Refresh")
        exit()
    if '__settings__' in url:
        ADDON.openSettings()

        exit()
    if 'addon' in url:
        install_repo(url)
        return
    if "__PIC__" in url:
        image_url = re.search(r"__PIC__(.*)",url).group(1)
        xbmc.executebuiltin('ShowPicture(%s)'%(image_url))
        exit()
    if "__timkiem__" in url:
        timkiemMenu()
        exit()
    if "tmdbsearch" in url:
        tmdb_search.show_search_form()
        exit()
    if "tmdb_movie_detail" in url:
        # Lấy tham số từ URL
        tmdb_id = args.get('tmdb_id', '')
        media_type = args.get('media_type', 'movie')
        
        if tmdb_id:
            # Lấy thông tin chi tiết từ TMDB
            movie_data = tmdb_search.get_movie_details(int(tmdb_id), media_type)
            if movie_data:
                # Lấy thông tin download từ backend
                download_info = tmdb_search.get_backend_download_info(int(tmdb_id), media_type)
                
                # Hiển thị thông tin chi tiết
                tmdb_search.display_movie_detail(movie_data, media_type, int(tmdb_id), download_info)
            else:
                xbmcgui.Dialog().ok('Lỗi', f'Không tìm thấy thông tin {media_type} với ID: {tmdb_id}')
        else:
            xbmcgui.Dialog().ok('Lỗi', 'Thiếu tham số TMDB ID')
        exit()
    
    if "_timtrenfshare_" in url:

        search_content('fshare')
        exit()

    if "_timtrenfshare1_" in url:
        if not "keyword" in url:
            search_content('fshare')
        else:
            match = re.search(r"keyword=(.*)",url)
            if match:
                query = match.group(1)
                search_content('fshare', query)
                exit()
            else:
                alert("Không lấy được từ khoá tìm kiếm")
                exit()
    if "__TIMFSHARE__" in url:
        HISTORY_FILE = os.path.join(PROFILE_PATH, 'timfshare.dat')
        if "keyword" in url:
            match = re.search(r"keyword=(.*)", url)
            if match:
                query = match.group(1)
        else:
            if not os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                    pass

            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = file.readlines()
            history = [line.strip() for line in history if line.strip()]

            if not history:
                keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    query = keyboard.getText()
                else:
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                    return
            else:
                options = ["[Nhập từ khóa mới]", "[Xóa lịch sử tìm kiếm]"] + history
                dialog = xbmcgui.Dialog()
                selected = dialog.select("Chọn từ khóa tìm kiếm", options)

                if selected == -1:
                    notify("Đã hủy tìm kiếm")
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                    return
                elif selected == 0:
                    keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
                    keyboard.doModal()
                    if keyboard.isConfirmed() and keyboard.getText():
                        query = keyboard.getText()
                    else:
                        notify("Đã hủy tìm kiếm")
                        return
                elif selected == 1:
                    confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch sử tìm kiếm không?")
                    if confirm:
                        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                            pass
                        notify("Đã xóa lịch sử tìm kiếm")
                        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                    return
                else:
                    query = options[selected]

        if "ref" in url:
            try:
                data = search.timfshare(query)
                loadlistitem.list_item_main(data)
            except Exception as e:
                notify(f"Lỗi khi tìm kiếm: {str(e)}")
        else:

            if query not in history:
                history.insert(0, query)
                with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                    file.write('\n'.join(history))


            try:
                data = search.timfshare(query)
                loadlistitem.list_item_main(data)
            except Exception as e:
                notify(f"Lỗi khi tìm kiếm: {str(e)}")

    if "__searchTVHD__" in url:

        search_content('tvhd')
        exit()
    if '__TIMTVHD__' in url:
        match = re.search(r"keyword=(.*)",url)
        if match:
            query = match.group(1)
            search_content('tvhd', query)
        else:
            alert("Không lấy được từ khoá tìm kiếm")
        exit()
    if "_timtren4share_" in url:

        search_content('4share')
        exit()

    if "_timtren4share1_" in url:
        if "keyword" in url:
            url = url.replace('%0a', '')
            search_regex = r'keyword=([\w%]+)'
            search_match = re.search(search_regex, url)
            if search_match:
                query = search_match.group(1)

                if "page" in url:
                    regex = r'page=(\d+)'
                    match = re.search(regex,url)
                    if match:
                        page = match.group(1)
                        data=search.searchFourshare(query,page)
                        loadlistitem.list_item_main(data)
                else:

                    search_content('4share', query)
            else:
                alert("Không lấy được từ khoá tìm kiếm")
        else:
            search_content('4share')
        exit()

    if '__search__' in url:
        keyboardHandle = xbmc.Keyboard('', 'VietmediaF')
        keyboardHandle.doModal()
        if (keyboardHandle.isConfirmed()):
            queryText = keyboardHandle.getText()
            if len(queryText) == 0:
                exit()
            queryText = urllib_parse.quote_plus(queryText)
            url = url.replace('__search__', queryText)
        else:exit()

    if '__searchphongblack__' in url:

        search_content('phongblack')
        exit()

    if '__searchphongblack1__' in url:
        match = re.search(r"search=(.*)&",url)
        if match:
            keyword = match.group(1)
            url = "http://phongblack.online/search.php?author=phongblack&search="+keyword
        else:
            url = searchPhongblack()
    if '__removeAllSearchHistory__' in url:
        delete_search_history()
        xbmc.executebuiltin("Container.Refresh")
        exit()
    if "__removeAllSearchHistory4share__" in url:
        delete_fshare_history()
        xbmc.executebuiltin("Container.Refresh")
        exit()
    if 'getfolderfiles' in url:
        notify("external service")
        current = url.replace('http://vietmediaf.net/kodi1.php/?action=getfolderfiles&url=', '')
        url = "http://kodi.s2lsolutions.com/get-folder-files.php?author=cGhvbmdibGFjaw&url=" + current
        url = urllib_parse.unquote(url)
    if '__addtofav__' in url:
        if "fshare.vn" in url:
            regex = r"(https://www.fshare.vn.*)&d"
            match = re.search(regex,url)
            link = match.group(1)
            fshare.add_remove_favourite(link,"1")
            return
        else:
            notify("Đây không phải là link fshare")
            return False
    if '__removeFromfav__' in url:
        if "fshare.vn" in url:
            regex = r"(https://www.fshare.vn.*)&d"
            match = re.search(regex,url)
            link = match.group(1)
            fshare.add_remove_favourite(link,"0")
            return
        else:
            notify("Đây không phải là link Fshare")
            return False
    if '__subtitle__' in url:
        match = re.search(r"file_name=(.+)", url)
        name = match.group(1)
        name = name.replace('.', ' ')
        subtitle_searching(name)
        return
    if '__lock__' in url:
        add_lock_dir(url)
        return
    if '__unlock__' in url:
        remove_lock_dir(url)
        return
    if '__watchedHistoryList__' in url:
        data=watchedHistoryList()
        loadlistitem.list_item_watched_history(data)

        return
    if '__removeAllWatchedHistory__' in url:
        delete_watched_history()
        notify("Đã xoá lịch sử xem phim")
        xbmc.executebuiltin("Container.Refresh")
        exit()
    if '__qrlink__' in url:
        qrlink(url)
        exit()
    if '__mobileScan__' in url:
        mobileScan(url)
        exit()

    if check_lock(url):
        dialog = xbmcgui.Dialog()
        result = dialog.input('Nhập mã khoá', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        if len(result) == 0 or result != LOCK_PIN:
            alert('Sai mật mã, vui lòng nhập lại')
            exit()
    if 'account_fshare' in url:
        updateAcc()
        exit()
    if 'action=quick_account_menu' in url:
        quick_account.display_quick_account_menu()
        exit()
    if 'action=quick_account_code' in url:
        if xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('Addon_Settings_Open') == 'true':
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
        quick_account.quick_account_code()
        exit()
    if 'action=quick_account_qr' in url:
        if xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('Addon_Settings_Open') == 'true':
            xbmc.executebuiltin('Addon.OpenSettings(%s)' % ADDON_ID)
        quick_account.quick_account_qr()
        exit()

    if 'get_user_information_fourshare' in url:
        import requests
        url_get_user_information='https://api.4share.vn/api/v1/?cmd=get_user_info'
        token_4s = getlink.check_token_4s()
        headers = {"accesstoken01":token_4s}
        r = requests.get(url_get_user_information,headers=headers)
        json_data = json.loads(r.content)
        errorNumber = list(json_data.values())[0]
        if "100" in str(errorNumber):
            alert("Tài khoản không phải là vip hoặc user/mật khẩu sai")
            sys.exit()
        else:
            mail_fourshare = list(json_data.values())[1]["email"]
            expire_date = list(json_data.values())[1]["vip_time"]
            line = 'E-mail: [COLOR yellow]%s[/COLOR]\n' % mail_fourshare
            line+= "Loại tài khoản: VIP\n"
            line+= "Thời gian hết hạn: %s" % expire_date
            alert(line,title="4share account")
            sys.exit()
    elif 'add_file' in url:

        keyboardHandle = xbmc.Keyboard('','[COLOR yellow]Nhập link Folder hoặc File Fshare của bạn:[/COLOR] [I]Nhập ID của Fshare[/I]')
        keyboardHandle.doModal()
        if (keyboardHandle.isConfirmed()):
            queryText = keyboardHandle.getText()
            if len(queryText) == 0:
                sys.exit()
        if "fshare.vn" in queryText:
            url_input = queryText.replace("http://", "https://")
            if 'token' in url_input:
                match = re.search(r"(\?.+?\d+)", url_input)
                _token = match.group(1)
                url_input = url_input.replace(_token, '')
            elif len(queryText) == 12 or len(queryText) == 15:

                queryText = queryText.upper()
                url_input = 'https://www.fshare.vn/file/' + queryText
        else:
            url_input = queryText

            url_input = url_input.strip()
            if 'fshare' in url_input:
                if 'folder' in url_input:
                    regex = r"folder\/(.+)"
                else:
                    regex = r"file\/(.+)"
                    match = re.search(regex, url_input)
                    f_id = match.group(1)
            file_type, name, file_size = getlink.check_file_info(url_input)

            if file_type == '0':
                file = 'https://www.fshare.vn/folder/' + f_id
            elif file_type == '1':
                file = 'https://www.fshare.vn/file/' + f_id
            elif file_type == '404':
                alert("File bạn nhập không có thực")
                return
            else:
                file = url_input

                url = 'Size:' + file_size + 'Name:' + urllib_parse.quote_plus(name.encode("utf8")) + 'Link:' + file

                filename = os.path.join(PROFILE_PATH, 'yourlink.dat')
                if not os.path.exists(filename):
                    with open(filename, "w+") as f:
                        f.write(url + '*')
                else:
                    with open(filename, "r+") as f:
                        lines = f.read()
                        f.seek(0, 0)
                        f.write(url.rstrip('\r\n') + '*' + lines)
                        notify('Đã lưu link của bạn.')
                return
    elif 'load_file' in url:

        filename = os.path.join(PROFILE_PATH, 'yourlink.dat')
        if not os.path.exists(filename):alert('Bạn chưa có link lưu trữ. Xin vui lòng thêm link.')
        else:
            with open(filename, "r") as f:
                lines = f.read()
                lines = lines.rstrip('*')
                if str(len(lines)) == '0':
                    alert('Bạn chưa có link lưu trữ. Xin vui lòng thêm link.')
                    return
            lines = lines.split('*')
            t = len(lines)
            items = []
            for i in range(0, t):
                item = {}
                line = (lines[i])
                link = re.search(r"Link:(.+)", line).group(1)
                name = re.search(r"Name:(.+?)Link", line).group(1)
                size = re.search(r"Size:(.+?)Name", line).group(1)
                name = urllib_parse.unquote_plus(name)
                if 'fshare' in link:
                    if 'folder' in link:
                        playable = False
                        link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % link
                    elif 'file' in link:
                        playable = True
                        link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % link
                    else:
                        playable = True
                        link = link

                        item["label"] = size + ' GB - ' + name
                        item["is_playable"] = playable
                        item["path"] = link
                        item["thumbnail"] = ''
                        item["icon"] = ""
                        item["label2"] = ""
                        item["info"] = {'plot': ''}
                        items += [item]
                data = {"content_type": "episodes", "items": ""}
                data.update({"items": items})
                loadlistitem.list_item(data)
    elif 'home_fshare' in url:
        notify("Đang tải home fshare...")
        data = fshare_favourite('https://api.fshare.vn/api/fileops/list?pageIndex=0&dirOnly=0&limit=60')
        data = json.loads(data)
        loadlistitem.list_item_main(data)
        return
    elif 'follow_fshare' in url:
        data = fshare_favourite('https://api.fshare.vn/api/fileops/getListFollow')
        data = json.loads(data)

        loadlistitem.list_item(data)

    elif 'folderxxx' in url:
        data = fshare_favourite('https://api.fshare.vn/api/Fileops/ListFavorite')
        data = json.loads(data)
        loadlistitem.list_item_main(data)
        return
    elif 'TopFollowMovie' in url:
        data = fshare_favourite('https://api.fshare.vn//api/fileops/getTopFollowMovie')
        data = json.loads(data)
        loadlistitem.list_item_main(data)
        return
    elif "top_follow_share" in url:
        data = fshare_top_follow()
        data = json.loads(data)
        loadlistitem.list_item_main(data)
        return
    elif "vtvgo" in url:
        regex = r"url=(.+)"
        match = re.search(regex, url)
        link = match.group(1)
        subtitle = ''
        data = {"url": "", "subtitle": ""}
        data.update({"url": link, "subtitle": subtitle})
        play(data)
    elif '4share.vn/f/' in url or 'fshare.vn/file/' in url or 'fshare.vn/folder/' in url or 'ok.ru' in url or 'drive.google.com' in url:
        regex = r"url=(.+)"
        match = re.search(regex, url)
        links = match.group(1)
        if match:
            subtitle = ''
            links = links.split('[]')
            if len(links) == 2:
                subtitle = links[1]
            link = links[0]
            data = {"url": "", "subtitle": ""}
            data.update({"url": link, "subtitle": subtitle})
            play(data)
        else:
            alert("Lỗi không xác định được link 01. Báo dev xử lí :-((")
            exit()
    elif '4share.vn/d/' in url or 'api.4share.vn' in url or 'thread_id' in url and '4share.vn' in url:
        regex = r"url=(.+)"
        match = re.search(regex,url)
        link = match.group(1)
        if match:
            link = urllib.parse.unquote(link)
            data = fourshare_folder(link)
            loadlistitem.list_item_main(data)
        else:
            alert("Lỗi mục xác định link 02. Báo dev xử lí :-((")
            exit()
    # Xóa bỏ xử lý FShare folder riêng biệt - để action play xử lý
    # elif 'fshare' in url and 'folder' in url:
    #     data = cache_utils.cache_data(url)
    #     if data is not None:
    #         loadlistitem.list_item_main(data)
    #     return


    elif "docs.google.com" in url:
        handle_google_docs_url(url)
        return
    elif "showWindow" in url:
        show_window("https://i.imgur.com/ytoQpHG.png")
        return
    elif 'VMF' in url and not 'action=fetch_espisode' in url:
        url = urllib_parse.unquote_plus(url)
        url = url.replace('VMF-', '')
        regex = r"url=(.+)"
        match = re.search(regex, url)
        links = match.group(1)
        data = list_link(links)
        loadlistitem.list_item(data)
        return

    def process_url(url, site_name, receive_function, setting_key):
        addon = xbmcaddon.Addon()
        setting = f'fsharesite_{setting_key}'

        xbmc.log(f"[VietmediaF] Processing URL: {url} for site {site_name}", xbmc.LOGINFO)

        if addon.getSetting(setting) == 'false':
            dialog = xbmcgui.Dialog()
            confirmed = dialog.yesno("Cảnh báo", f"Đây là nội dung được lấy từ web [COLOR yellow]{site_name}[/COLOR]. Lưu ý rằng Addon không chịu trách nhiệm tính chính xác hoặc hợp pháp của nội dung từ [COLOR yellow]{site_name}[/COLOR].\nNhấn YES/ĐỒNG Ý để tiếp tục hoặc NO/KHÔNG để hủy bỏ.")

            if confirmed:
                addon.setSetting(setting, 'true')
                match = re.search(r"url=(.*)", url)
                if match:
                    url = match.group(1)
                xbmc.log(f"[VietmediaF] Extracted URL: {url}", xbmc.LOGINFO)
                data = receive_function(url)
                loadlistitem.list_item_main(data)
                return
            else:
                exit()
        else:
            match = re.search(r"url=(.*)", url)
            if match:
                url = match.group(1)
            xbmc.log(f"[VietmediaF] Extracted URL: {url}", xbmc.LOGINFO)
            data = receive_function(url)
            loadlistitem.list_item_main(data)
            return
    def handle_url(url):
        plugin_url = f"plugin://plugin.video.vietmediaF?action=browse&url={url}"

        try:
            if "thuviencine" in url:
                process_url(plugin_url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')
            elif "thuvienhd" in url:
                process_url(plugin_url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')
            elif "docs.google.com" in url:
                handle_google_docs_url(plugin_url)
        except Exception as e:
            xbmcgui.Dialog().notification("Lỗi", "Có lỗi xảy ra, vui lòng chọn nguồn khác.", xbmcgui.NOTIFICATION_ERROR)
            xbmc.log(f"Error handling URL {url}: {str(e)}", xbmc.LOGERROR)

    if "thuviencine" in url:
        process_url(url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')

    elif "thuvienhd" in url:
        process_url(url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')

    elif "hdvietnam" in url:
        process_url(url, 'hdvietnam.xyz', hdvn.receive, 'hdvietnam.xyz')

    if 'show_input_form' in url:
        server.show_input_form()
        return
    if '_urlinput_' in url:
        try:
            server_url.show_input_form()
        except Exception as e:
            notify("Đã xảy ra lỗi:", str(e))
            exit()
    if 'advanced_settings_menu' in url:
        advanced_settings_menu.display_advanced_settings_menu()
        exit()
    if 'optimize_cache' in url:
        advanced_settings_menu.optimize_cache()
        exit()
    if 'optimize_network' in url:
        advanced_settings_menu.optimize_network()
        exit()
    if 'manage_advanced_settings' in url:
        advanced_settings_menu.manage_advanced_settings()
        exit()
    if 'view_advancedsettings' in url:
        advanced_settings_menu.view_advancedsettings()
        exit()
    if 'reset_advancedsettings' in url:
        advanced_settings_menu.reset_advancedsettings()
        exit()
    if 'auto_vietnamese_subtitle' in url:
        advanced_settings_menu.auto_vietnamese_subtitle()
        exit()
    if 'external_player_settings' in url:
        advanced_settings_menu.external_player_settings()
        exit()
    if 'set_external_player' in url:
        advanced_settings_menu.set_external_player()
        exit()
    if 'reset_to_default_player' in url:
        advanced_settings_menu.reset_to_default_player()
        exit()
    if '_resetdownload_' in url:
        reset_code = ADDON.getSetting('reset_code')
        resetfs.checkvalid(reset_code)
        exit()
    if 'reset_kodi' in url:
        from resources.kodi_cleaner import show_menu
        show_menu()
        exit()

    if 'install_vmf_source' in url:
        source_installer.install_vmf_source()
        exit()

    if 'm3uhttp' in url:
        data = iptv.receive(url)
        loadlistitem.list_item_main(data)
        return

    if '__phimle__' in url:

        phim_setting = ADDON.getSetting('phimle_url')
        if not phim_setting:
            data = phim_list("https://docs.google.com/spreadsheets/d/1OQkv_XDA4xdI16pedQuWDuEfnHYKgJf_nsi92y3UWLs/gviz/tq?gid=0&headers=1")
            choices = [item[0] for item in data]
            selected = xbmcgui.Dialog().select('Chọn một nguồn phim', choices)
            if selected != -1:
                phimle_url = data[selected][1]
                ADDON.setSetting('phimle_url', phimle_url)
                handle_url(phimle_url)

            else:
                xbmcgui.Dialog().ok('Thông báo', 'Bạn cần phải chọn một nguồn phim lẻ.')
                xbmc.executebuiltin('Addon.Close()')
        else:
            phimle_url = ADDON.getSetting('phimle_url')
            handle_url(phimle_url)


    if '__phimbo__' in url:

        phim_setting = ADDON.getSetting('phimbo_url')
        if not phim_setting:
            data = phim_list("https://docs.google.com/spreadsheets/d/1OQkv_XDA4xdI16pedQuWDuEfnHYKgJf_nsi92y3UWLs/gviz/tq?gid=1057024371&headers=1")
            choices = [item[0] for item in data]
            selected = xbmcgui.Dialog().select('Chọn một nguồn phim', choices)
            if selected != -1:
                phimbo_url = data[selected][1]
                ADDON.setSetting('phimbo_url', phimbo_url)
                handle_url(phimbo_url)

            else:

                xbmcgui.Dialog().ok('Thông báo', 'Bạn cần phải chọn một nguồn phim lẻ.')
                xbmc.executebuiltin('Addon.Close()')
        else:
            phimbo_url = ADDON.getSetting('phimbo_url')
            handle_url(phimbo_url)



    data = fetch_data_default(url)

    if not data:

        exit()
    if data.get('error'):
        alert(data['error'])
        sys.exit()
    if data.get("url"):
        alert(str(data.get))
        play(data)
        sys.exit()
    if not data.get("items"):return

    loadlistitem.list_item_main(data)



def main():
    check_and_clear_cache()

    args = urllib.parse.parse_qs(sys.argv[2][1:])
    action = args.get('action', None)
    url = args.get('url', [''])[0]

    go()

if __name__ == '__main__':
    main()



