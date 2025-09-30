import re, json, os, sys
import requests, xbmcvfs
import time
import hashlib
import xbmcplugin, xbmcgui, xbmc, xbmcvfs
from resources.addon import *
from resources import resetfs
import urllib.parse
from urllib.parse import urlencode
from resources.lib.constants import CACHE_PATH, USER_AGENT
from resources.cache_utils import check_cache, get_cache, set_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


login_api = 'https://api.fshare.vn/api/user/login'
profile_api = 'https://api.fshare.vn/api/user/get'
download_api = "https://api.fshare.vn/api/session/download"
folder_api = "https://api.fshare.vn/api/fileops/getFolderList"


useragent = 'kodivietmediaf-K58W6U'
domainfs = ADDON.getSetting('domainforfs')
username = ADDON.getSetting('fshare_username')
password = ADDON.getSetting('fshare_password')


next_icon = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'images', 'nextpage.png'))
fvideo_icon = xbmcvfs.translatePath(os.path.join(ADDON_PATH, 'resources', 'images', 'fsvideo.png'))


def create_session():
    session = requests.Session()


    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )


    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)


    session.headers.update({
        "User-Agent": useragent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    })

    return session


session = create_session()
def debug(text):
    filename = os.path.join(PROFILE_PATH, "fshare.dat")
    if not os.path.exists(filename):
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(text)
    else:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(text + '\n')

def login():

    domainfs = ADDON.getSetting('domainforfs')
    username = ADDON.getSetting('fshare_username')
    password = ADDON.getSetting('fshare_password')
    if not username or not password:
        from resources.quick_account import display_quick_account_menu
        alert("Bạn chưa nhập tài khoản Fshare. Nhập thông tin tài khoản")
        
        try:
            dialog = xbmcgui.Dialog()
            choice = dialog.select(
                "Chọn cách nhập tài khoản",
                ["Nhập bằng mã QR", "Nhập bằng mã Code", "Nhập trực tiếp trong Addon Settings", "Hủy"]
            )

            if choice == 0:  
                try:
                    from resources.quick_account import quick_account_qr
                    quick_account_qr()
                    
                    username = ADDON.getSetting('fshare_username')
                    password = ADDON.getSetting('fshare_password')
                    if not username or not password:
                        notify("Không nhận được thông tin tài khoản từ mã QR")
                        return None, None
                except Exception as e:
                    logError(f"Lỗi khi nhập bằng mã QR: {str(e)}")
                    notify("Lỗi khi nhập bằng mã QR")
                    return None, None
            elif choice == 1:  
                try:
                    from resources.quick_account import quick_account_code
                    quick_account_code()
                    
                    username = ADDON.getSetting('fshare_username')
                    password = ADDON.getSetting('fshare_password')
                    if not username or not password:
                        notify("Không nhận được thông tin tài khoản từ mã Code")
                        return None, None
                except Exception as e:
                    logError(f"Lỗi khi nhập bằng mã Code: {str(e)}")
                    notify("Lỗi khi nhập bằng mã Code")
                    return None, None
            elif choice == 2:  
                try:
                    ADDON.openSettings()
                    
                    username = ADDON.getSetting('fshare_username')
                    password = ADDON.getSetting('fshare_password')
                    if not username or not password:
                        notify("Chưa nhập thông tin tài khoản trong Addon Settings")
                        return None, None
                except Exception as e:
                    logError(f"Lỗi khi mở Addon Settings: {str(e)}")
                    notify("Lỗi khi mở Addon Settings")
                    return None, None
            else:  
                notify("Đã hủy nhập tài khoản")
                return None, None
        except Exception as e:
            logError(f"Lỗi khi hiển thị menu lựa chọn: {str(e)}")
            notify("Lỗi khi hiển thị menu lựa chọn")
            return None, None
    if not "@" in username:
        username = username+domainfs
    username = username.strip()
    password = password.strip()
    payload = '{"app_key":"dMnqMMZMUnN5YpvKENaEhdQQ5jxDqddt","user_email":"'+username+'","password":"'+password+'"}'
    headers = {'cache-control': "no-cache", 'User-Agent': 'kodivietmediaf-K58W6U'}
    r = requests.post('https://api.fshare.vn/api/user/login', data=payload, headers=headers, verify=False)
    jStr = json.loads(r.content)
    msg = jStr['msg']
    notify(msg)
    if r.status_code == 406:
        alert("Account chưa được kích hoạt. Bạn vào e-mail rồi kíchh hoạt tài khoản")
    if r.status_code == 409:
        alert("Tài khoản đã bị khoá login")
    if r.status_code == 410:
        alert("Tài khoản đã bị khoá")
    if r.status_code == 424:
        alert("Tài khoản đã bị khoá do nhập sai mật khẩu quá 3 lần. Kiểm tra thông tin và đợi 10 phút sau thử lại\nE-mail: [COLOR yellow]%s[/COLOR]\nPassword: [COLOR yellow]%s[/COLOR]" % (username,password))
        exit()
    if r.status_code == 403:
        image_path = "https://i.imgur.com/AfXfxGx.png"
        xbmc.executebuiltin('ShowPicture(%s)'%(image_path))
    if r.status_code == 405:
        line = "Có thể đã nhập sai email hoặc mật khẩu.\n"
        line += "[COLOR yellow]Email:[/COLOR] %s\n" % username
        line += "[COLOR yellow]Mật khẩu:[/COLOR] %s\n" % password
        line += "[I]Đừng cố thử lại. Nếu mới cài addon hãy khởi động lại thiết bị.[/I]"
        alert(line)
        exit()

    if r.status_code == 200:
        token = jStr['token']
        session_id = jStr['session_id']
        ADDON.setSetting(id="tokenfshare",value=token)
        ADDON.setSetting(id="sessionfshare",value=session_id)
        current_time = int(time.time())
        timenow = str(current_time)
        ADDON.setSetting(id="timelog",value=timenow)
        return(token,session_id)
def logout(session_id=None):
    if not session_id:
        session_id = ADDON.getSetting('sessionfshare')
    if not session_id:
        return False

    try:
        header = {'Cookie' : 'session_id=' + session_id}
        r = requests.get('https://api.fshare.vn/api/user/logout',headers=header)
        return r.status_code == 200
    except Exception as e:
        logError(f"Lỗi khi logout: {str(e)}")
        return False

def getUserInfo(token,session_id):
    headers = {'useragent': useragent, 'Cookie': 'session_id=%s' % session_id}
    r = requests.get("https://api.fshare.vn/api/user/get",headers=headers, verify=False)
    jstr = json.loads(r.content)
    expiredDate = jstr["expire_vip"]
    point = jstr['totalpoints']
    mail = jstr['email']
    acc_type = jstr['account_type']
    webspace = float(jstr['webspace']) / float(1073741824)
    webspace_used = '{0:.2f}'.format(float(jstr['webspace_used']) / float(1073741824))
    line = 'E-mail: [COLOR yellow]%s[/COLOR] - ' % mail
    line += 'Loại tài khoản: [COLOR yellow]%s[/COLOR]\n' % acc_type
    line += 'Point: [COLOR yellow]%s[/COLOR]\n' % point
    line += 'Dung lượng lưu trữ: [COLOR yellow]%s Gb[/COLOR] / ' % webspace
    line += 'Đã sử dụng [COLOR yellow]%s Gb[/COLOR]\n' % webspace_used
    alert(line, title='Fshare vip - [COLOR yellow]zalo.me/0915134560[/COLOR]')
def get_download_link(token=None, session_id=None, link=None, max_reset_attempts=2):
    
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Fshare', 'Đang lấy link')

    if not token or not session_id:
        token, session_id = check_session()
        if not token or not session_id:
            pDialog.close()
            notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
            return None
    if not link:
        pDialog.close()
        notify("Không có link để tải")
        return None
    def try_download(password=""):

        modified_link = link
        if "?" not in modified_link:
            modified_link = modified_link + "?share=3053519"
        else:
            modified_link = modified_link + "&share=3053519"

        payload = json.dumps({"zipflag": 0, "url": modified_link, "password": password, "token": token})
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'kodivietmediaf-K58W6U',
            'Cookie': 'session_id=' + session_id
        }
        return payload, headers

    def retrieve_download_link(reset_attempts=0, password=""):
        payload, headers = try_download(password)
        r = requests.post(download_api, headers=headers, data=payload, verify=False)
        logError("Download link response: " + str(r.status_code) + " - " + str(r.content))
        jstr = json.loads(r.content)

        if r.status_code == 404:
            alert("Link này không tồn tại hoặc bị xoá")
        if r.status_code == 201:
            alert("Tài khoản chưa đăng nhập")
        if r.status_code == 471:
            alert("Phiên tải quá nhiều. Vào [COLOR yellow]fshare.vn[/COLOR]/Thông tin tài khoản/Bảo mật/Xoá phiên tải và phiên đăng nhập")
        if r.status_code == 200:
            if jstr.get("code") == 123:
                dialog = xbmcgui.Dialog()
                password = dialog.input('Nhập mật khẩu cho file này', type=xbmcgui.INPUT_ALPHANUM)
                if password:
                    return retrieve_download_link(reset_attempts, password)
                else:
                    alert("Bạn chưa nhập mật khẩu")
                    return None
            link_download = jstr["location"]
            logError("Download link: " + link_download)
            return link_download
    pDialog.close()
    return retrieve_download_link()

def api_request(url, headers=None, method="GET", data=None, timeout=30):
    """Gọi API với xử lý lỗi"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        else:
            response = requests.post(url, headers=headers, data=data, timeout=timeout, verify=False)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        logError(f"Lỗi khi gọi API {url}: {str(e)}")
        return None
def homeFolder(token=None, session_id=None):
    """Hiển thị thư mục gốc của tài khoản"""
    try:
        
        if not token or not session_id:
            token, session_id = check_session()
            if not token or not session_id:
                notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
                return

        url_template = "https://api.fshare.vn/api/fileops/list?pageIndex={page}&dirOnly=0&limit=100&path="
        headers = {
            'User-Agent': USER_AGENT,
            'Cookie': f'session_id={session_id}'
        }

        page = 0
        while True:
            url = url_template.format(page=page)
            response = api_request(url, headers=headers)

            if not response or len(response) == 0:
                break

            for item in response:
                name = item["name"]
                link = item["linkcode"]
                is_folder = item["type"] == 0
                size = item.get("size", 0)

                list_item = xbmcgui.ListItem(label=name, path=link)
                list_item.setInfo(type='Video', infoLabels={'size': size})
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=list_item, isFolder=is_folder)

            page += 1

        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except Exception as e:
        logError(f"Lỗi khi hiển thị thư mục gốc: {str(e)}")
        notify("Lỗi khi hiển thị thư mục gốc")

from resources.utils import get_cached_metadata

def parse_plugin_url(url):
    """Parse thông tin từ plugin URL"""
    from urllib.parse import urlparse, parse_qs, unquote_plus

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    info = {
        "fshare_url": unquote_plus(params.get("url", [""])[0]) if params.get("url") else "",
        "name": unquote_plus(params.get("name", [""])[0]) if params.get("name") else "",
        "name2": unquote_plus(params.get("name2", [""])[0]) if params.get("name2") else "",
        "poster": unquote_plus(params.get("poster", [""])[0]) if params.get("poster") else "",
        "backdrop": unquote_plus(params.get("backdrop", [""])[0]) if params.get("backdrop") else "",
        "plot": unquote_plus(params.get("plot", [""])[0]) if params.get("plot") else "",
        "year": params.get("year", [""])[0] if params.get("year") else "",
        "genres": unquote_plus(params.get("genres", [""])[0]) if params.get("genres") else "",
        "rating": float(params.get("rating", [0])[0]) if params.get("rating") else 0.0
    }

    
    if "Season" in info["name"]:
        title_parts = info["name"].split(" - ")
        info["series_name"] = title_parts[0]  
        info["season_name"] = title_parts[1]  
        info["viet_name"] = title_parts[2] if len(title_parts) > 2 else ""

        import re
        season_match = re.search(r"Season (\d+)", info["season_name"])
        info["season"] = int(season_match.group(1)) if season_match else 1

    return info

def fsharegetFolder(url):
    
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Fshare', 'Kiểm tra cache...')
    page_index = 0  
    page_match = re.search(r'pageIndex=([0-9]+)', url)
    if page_match:
        page_index = int(page_match.group(1))
        
        url = re.sub(r'[?&]pageIndex=[0-9]+', '', url)
        if url.endswith('&') or url.endswith('?'):
            url = url[:-1]
    
    display_page = page_index + 1
    folder_code = re.search(r"folder\/([a-zA-Z0-9]+)", url)
    if folder_code:
        folder_code = folder_code.group(1)
        
        cache_key = f"fshare_folder_{folder_code}_page{page_index}"

        if check_cache(cache_key, 30):
            pDialog.update(50, 'Lấy dữ liệu từ cache...')
            cache_data = get_cache(cache_key)
            if cache_data:
                pDialog.update(100, 'Đã lấy dữ liệu từ cache')
                pDialog.close()
                return cache_data

    pDialog.update(10, 'Đang tải danh sách thư mục...')

    f_icon = fvideo_icon
    folder_description = ""

    folder_metadata = get_cached_metadata(url)
    if folder_metadata:
        f_icon = folder_metadata.get("image", f_icon)
        folder_description = folder_metadata.get("description", "")

    token, session_id = check_session()
    if not token or not session_id:
        pDialog.close()
        notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
        return {"content_type": "movies", "items": []}

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': useragent,
        'Cookie': 'session_id=' + session_id
    }
    
    
    payload = json.dumps({
        "token": token,
        "url": url,
        "dirOnly": 0,  # 0 = cả file và folder, 1 = chỉ folder
        "pageIndex": page_index,  
        "limit": 100
    })

    try:
        pDialog.update(30, 'Gửi yêu cầu đến Fshare...')
        r = session.post("https://api.fshare.vn/api/fileops/getFolderList", headers=headers, data=payload, verify=False)

        if "[]" in str(r.content) or r.status_code == 404:
            pDialog.close()
            alert("Thư mục không tồn tại hoặc đã bị xóa.")
            return {"content_type": "movies", "items": []}

        try:
            r.raise_for_status()
        except Exception as e:
            pDialog.close()
            alert(f"Lỗi khi tải thư mục: {str(e)}")
            return {"content_type": "movies", "items": []}
        
        pDialog.update(50, 'Xử lý dữ liệu...')

        try:
            f_items = json.loads(r.content)
            log(f"[VietmediaF] Fshare Folder: API trả về {len(f_items) if f_items else 0} items")
            if f_items:
                for i, item in enumerate(f_items[:3]):  # Log 3 items đầu tiên
                    log(f"[VietmediaF] Fshare Folder: Item {i+1}: {item.get('name', 'Unknown')} (type: {item.get('type', 'Unknown')})")
        except json.JSONDecodeError as e:
            pDialog.close()
            alert(f"Lỗi parse JSON: {str(e)}")
            return {"content_type": "movies", "items": []}

        if not f_items or len(f_items) == 0:
            log(f"[VietmediaF] Fshare Folder: Không có items, thử với dirOnly=1")
            # Thử lại với dirOnly=1 để chỉ lấy folder
            payload_dir_only = json.dumps({
                "token": token,
                "url": url,
                "dirOnly": 1,  # Chỉ lấy folder
                "pageIndex": page_index,  
                "limit": 100
            })
            
            try:
                r_dir = session.post("https://api.fshare.vn/api/fileops/getFolderList", headers=headers, data=payload_dir_only, verify=False)
                if r_dir.status_code == 200:
                    f_items = json.loads(r_dir.content)
                    log(f"[VietmediaF] Fshare Folder: Với dirOnly=1, API trả về {len(f_items) if f_items else 0} items")
                    if f_items:
                        for i, item in enumerate(f_items[:3]):
                            log(f"[VietmediaF] Fshare Folder: Item {i+1}: {item.get('name', 'Unknown')} (type: {item.get('type', 'Unknown')})")
            except Exception as e:
                logError(f"[VietmediaF] Fshare Folder: Lỗi khi thử dirOnly=1: {str(e)}")
            
            if not f_items or len(f_items) == 0:
                pDialog.close()
                notify("Thư mục trống hoặc không có quyền truy cập")
                return {"content_type": "movies", "items": []}

        items = []
        for f_item in f_items:
            name = f_item["name"]
            linkcode = f_item["linkcode"]
            size = str(f_item["size"])
            item = {}

            full_url = f"https://www.fshare.vn/{'folder' if f_item['type'] == '0' else 'file'}/{linkcode}"

            if f_item["type"] == "0":
                link = ('plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/%s' % linkcode)
                playable = False
            else:
                link = ('plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/%s' % linkcode)
                playable = True

            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = f_icon
            item["icon"] = f_icon
            item["label2"] = name
            item["info"] = {'plot': folder_description if folder_description else name, 'size': size}
            items.append(item)

        
        if len(f_items) >= 100:
            
            base_url = url
            if '?' not in base_url:
                base_url += '?'
            elif not base_url.endswith('&'):
                base_url += '&'
                
            next_page_index = page_index + 1
            next_url = f"{base_url}pageIndex={next_page_index}"
            
            
            next_display_page = next_page_index + 1

            nextpage = {
                "label": f'[COLOR yellow]Trang tiếp ({next_display_page})[/COLOR]',
                "is_playable": False,
                "path": f'plugin://plugin.video.vietmediaF?action=play&url={urllib.parse.quote_plus(next_url)}',
                "thumbnail": next_icon,
                "icon": next_icon,
                "label2": "",
                "info": {'plot': f'Xem trang {next_display_page}'}
            }
            items.append(nextpage)

        data = {"content_type": "tvshows", "items": items}

        
        if folder_code:
            pDialog.update(90, 'Lưu dữ liệu vào cache...')
            set_cache(cache_key, data)

        pDialog.update(100, 'Hoàn tất')
        pDialog.close()
        return data

    except Exception as e:
        pDialog.close()
        alert(f"Lỗi xử lí thư mục: {str(e)}")

    pDialog.close()
    return {"content_type": "movies", "items": []}

def fileInFolder(url):
    folder_code = re.search(r"folder\/([a-zA-Z0-9]+)", url)
    if folder_code:
        folder_code = folder_code.group(1)
        cache_key = f"fshare_folder_count_{folder_code}"

        if check_cache(cache_key, 30):
            cache_data = get_cache(cache_key)
            if cache_data:
                return cache_data.get('total', '-')

    token, session_id = check_session()
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': useragent,
        'Cookie': 'session_id=' + session_id
    }

    json_data = {'token': token, 'url': url}

    try:
        r = session.post('https://api.fshare.vn/api/fileops/getTotalFileInFolder', headers=headers, json=json_data, verify=False)
        r.raise_for_status()

        jsdata = json.loads(r.content)
        total = jsdata.get("total", "-")


        if folder_code:
            cache_data = {'total': total}
            set_cache(cache_key, cache_data)

        return total
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi lấy số lượng file trong thư mục: {str(e)}", xbmc.LOGERROR)
        return "-"

def isvalid(session_id):
    headers = {'useragent': 'kodivietmediaf-K58W6U', 'Cookie': 'session_id=%s' % session_id}
    try:
        r = requests.get("https://api.fshare.vn/api/user/get", headers=headers, verify=False)
        r.raise_for_status()
        jStr = r.json()
    except requests.exceptions.RequestException as e:

        return False
    except json.JSONDecodeError as e:

        return False

    if "error" in jStr:

        return False

    account_type = jStr.get('account_type')
    if not account_type:
        return False

    if account_type == "Member":
        alert("Tài khoản của bạn hiện tại là [COLOR yellow]MEMBER[/COLOR]. Để nâng cấp VIP vui lòng liên hệ Zalo số [COLOR yellow]0915134560[/COLOR]")

    if r.status_code == 200:

        return True

    return False
def getAccFshare():
    username = ADDON.getSetting('fshare_username')
    password = ADDON.getSetting('fshare_password')
    if not username or not password:
        alert("Bạn chưa nhập tài khoản Fshare.")
        ADDON.openSettings()
        username = ADDON.getSetting('fshare_username')
        password = ADDON.getSetting('fshare_password')
    if "@" not in username:
        domainforfs = ADDON.getSetting('domainforfs')
        username = username + domainforfs

    return (username,password)
def getBackupAcc():
    username_backup = ADDON.getSetting('username_backup')
    password_backup = ADDON.getSetting('password_backup')
    backup_option_fshare = ADDON.getSetting('backup_option_fshare')
    if backup_option_fshare == "true":
            username_backup,password_backup = getAccFshare()

    else:
        if not username_backup or not password_backup:
            alert("Bạn chưa nhập [COLOR yellow]tài khoản Backup[/COLOR]. Nhập thông tin tài khoản")
            ADDON.openSettings()
            backup_option_fshare = ADDON.getSetting('backup_option_fshare')
            if backup_option_fshare == "true":
                username_backup,password_backup = getAccFshare()

            else:
                username_backup = ADDON.getSetting('username_backup')
                password_backup = ADDON.getSetting('password_backup')
                if "@" not in username_backup:
                    domainforbackup = ADDON.getSetting('domainforbackup')
                    username_backup = username_backup+domainforbackup

    return (username_backup,password_backup)

def updateAcc():
    try:
        session_id = ADDON.getSetting("sessionfshare")
        if isvalid(session_id):
            try:
                logout()
            except Exception as e:
                logError(f"Lỗi khi logout: {str(e)}")
                pass

        try:
            token, session_id = login()
            if not token or not session_id:
                notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
                return False
        except Exception as e:
            notify(f"Lỗi đăng nhập: {str(e)}")
            return False

        vDialog.create(ADDON_NAME+" " +VERSION, "Kiểm tra tài khoản thông tin tài khoản")

        try:
            header = {'Cookie': 'session_id=' + session_id, 'User-Agent': useragent}
            r = requests.get('https://api.fshare.vn/api/user/get', headers=header, verify=False)
            r.raise_for_status()
            jstr = json.loads(r.content)
        except Exception as e:
            vDialog.close()
            notify(f"Lỗi khi lấy thông tin tài khoản: {str(e)}")
            return False

        try:
            acc_type = jstr.get('account_type', 'Unknown')
            if "Download" in acc_type:
                acc_type = "Vip-Download"

            if "Bundle" in acc_type or "Forever" in acc_type or "ADSL2plus" in acc_type:
                expiredDate = str("4102444799")
            else:
                expiredDate = jstr.get("expire_vip", "Unknown")

            point = jstr.get('totalpoints', '0')
            mail = jstr.get('email', 'Unknown')

            webspace = float(jstr.get('webspace', 0)) / float(1073741824)
            webspace_used = '{0:.2f}'.format(float(jstr.get('webspace_used', 0)) / float(1073741824))

            filename = os.path.join(PROFILE_PATH, 'expired.dat')
            try:
                if not os.path.exists(filename):
                    with open(filename, "w+") as f:
                        f.write(expiredDate)
                else:
                    with open(filename, "wb") as f:
                        f.write(expiredDate.encode("UTF-8"))
            except Exception as e:
                logError(f"Lỗi khi lưu expired.dat: {str(e)}")

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

            return True
        except Exception as e:
            vDialog.close()
            notify(f"Lỗi khi xử lý thông tin tài khoản: {str(e)}")
            return False
    except Exception as e:
        if vDialog:
            vDialog.close()
        notify(f"Lỗi khi cập nhật tài khoản: {str(e)}")
        return False


def check_session():
    try:
        username = ADDON.getSetting('fshare_username')
        password = ADDON.getSetting('fshare_password')
        token = ADDON.getSetting('tokenfshare')
        session_id = ADDON.getSetting('sessionfshare')

        if not username or not password:
            
            token, session_id = login()
            if not token or not session_id:
                
                return None, None

        
        if username and "@" not in username:
            domainfs = ADDON.getSetting('domainforfs')
            username = username + domainfs

        if not token or not session_id:
            token, session_id = login()
            if not token or not session_id:
                
                return None, None
            ADDON.setSetting(id="tokenfshare", value=token if token else "")
            ADDON.setSetting(id="sessionfshare", value=session_id if session_id else "")
        elif not isvalid(session_id):
            token, session_id = login()
            if not token or not session_id:
                
                return None, None
            ADDON.setSetting(id="tokenfshare", value=token if token else "")
            ADDON.setSetting(id="sessionfshare", value=session_id if session_id else "")

        return (token, session_id)
    except Exception as e:
        logError(f"Lỗi trong check_session: {str(e)}")
        return None, None
def get_fshare_file_info(url):

    if "plugin" in url:
        regex = r"url=([^&]+)"
        match = re.search(regex,url)
        if match:
            url = match.group(1)


    file_code = re.search(r"file\/([a-zA-Z0-9]+)", url)
    if file_code:
        file_code = file_code.group(1)
        cache_key = f"fshare_file_info_{file_code}"


        if check_cache(cache_key, 30):
            cache_data = get_cache(cache_key)
            if cache_data:
                return (cache_data.get('name', ''), cache_data.get('file_type', ''), cache_data.get('size', ''))


    token, session_id = check_session()
    data = '{"token" : "%s", "url" : "%s"}' % (token, url)
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': useragent,
        'Cookie': 'session_id=' + session_id
    }

    try:

        r = session.post('https://api.fshare.vn/api/fileops/get', headers=headers, data=data, verify=False)
        r.raise_for_status()

        jstr = json.loads(r.content)
        name = jstr.get('name', '')
        file_type = jstr.get('file_type', '')
        size = jstr.get('size', '')


        if file_code:
            cache_data = {
                'name': name,
                'file_type': file_type,
                'size': size
            }
            set_cache(cache_key, cache_data)

        return (name, file_type, size)
    except json.JSONDecodeError:
        return ("File không tồn tại", "", "")
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi lấy thông tin file: {str(e)}", xbmc.LOGERROR)
        return ("Lỗi khi lấy thông tin file", "", "")

def mobileScan(url):
    try:
        match = re.search(r"url=([^&]+)", url)
        if match:
            url = match.group(1)
            token, session_id = check_session()
            if not token or not session_id:
                notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
                return False

            download_url = get_download_link(token, session_id, url)
            if not download_url:
                notify("Không thể lấy link tải")
                return False

            image_url = f"https://api.qrserver.com/v1/create-qr-code/?color=000000&bgcolor=FFFFFF&data={download_url}&qzone=1&margin=1&size=400x400&ecc=L"
            userdata_path = xbmcvfs.translatePath('special://userdata')
            filename = 'qr_code.png'
            image_path = os.path.join(userdata_path, filename)

            urllib.request.urlretrieve(image_url, image_path)
            notify("Kodi và điện thoại phải cùng một mạng")
            xbmc.executebuiltin('ShowPicture(%s)'%(image_path))
            return True
        else:
            notify("URL không hợp lệ")
            return False
    except Exception as e:
        logError(f"Lỗi khi tạo mã QR: {str(e)}")
        notify("Lỗi khi tạo mã QR")
        return False

def add_remove_favourite(url, status):
    try:
        if "folder" in url:
            linkcode = re.search(r"folder\/(.+)",url).group(1)
        elif "file" in url:
            linkcode = re.search(r"file\/(.+)",url).group(1)
        else:
            notify("URL không hợp lệ")
            return False

        token, session_id = check_session()
        if not token or not session_id:
            notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
            return False

        api_change_favourite = 'https://api.fshare.vn/api/fileops/ChangeFavorite'
        header = {'User-Agent': "kodivietmediaf-K58W6U", 'Cookie' : 'session_id=%s' % session_id}
        data = '{"items":["%s"],"status":%s,"token":"%s"}' % (linkcode,status,token)

        r = requests.post(api_change_favourite, data=data, headers=header, verify=False, timeout=10)
        r.raise_for_status()

        if r.status_code == 200:
            notify('Đã thành công')
            return True
        else:
            notify(f"Lỗi: {r.status_code}")
            return False
    except Exception as e:
        logError(f"Lỗi khi thay đổi trạng thái yêu thích: {str(e)}")
        notify("Lỗi khi thay đổi trạng thái yêu thích")
        return False

def fshare_top_follow():
    top_follow_url = 'https://api.fshare.vn/api/fileops/getTopFollowMovie'
    token, session_id = check_session()
    if not token or not session_id:
        notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
        data = {"content_type": "episodes", "items": []}
        return json.dumps(data)

    try:
        header = {'User-Agent': 'Vietmediaf /Kodi1.1.99-092019','Cookie' : 'session_id=' + session_id }
        r = requests.get(top_follow_url, headers=header, verify=False)
        r.raise_for_status()
        f_items = json.loads(r.text)
    except Exception as e:
        logError(f"Lỗi khi lấy top follow: {str(e)}")
        data = {"content_type": "episodes", "items": []}
        return json.dumps(data)
    items = []
    for i in f_items:
        item = {}
        name = i["name"]
        linkcode = i["linkcode"]
        item["label"] = name
        item["is_playable"] = False
        item["path"] = 'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/%s' % linkcode
        item["thumbnail"] = ''
        item["icon"] = "https://i.imgur.com/8wyaJKv.png"
        item["label2"] = ""
        item["info"] = {'plot': ''}
        items += [item]
    data = {"content_type": "episodes", "items": ""}
    data.update({"items": items})
    return json.dumps(data)

def fshare_favourite(url):
    token, session_id = check_session()
    if not token or not session_id:
        notify("Không thể đăng nhập vào Fshare hoặc người dùng đã hủy nhập tài khoản")
        data = {"content_type": "episodes", "items": []}
        return json.dumps(data)

    try:
        header = {'User-Agent': "kodivietmediaf-K58W6U", 'Cookie' : 'session_id=%s' % session_id }
        r = requests.get(url, headers=header, verify=False, timeout=10)
        r.raise_for_status()
        f_items = json.loads(r.text)
    except Exception as e:
        logError(f"Lỗi khi lấy danh sách yêu thích: {str(e)}")
        data = {"content_type": "episodes", "items": []}
        return json.dumps(data)
    items = []
    for i in f_items:
        item = {}
        name = i["name"]
        filesize = str(i["size"])
        if name == None:
            item["label"] = "[COLOR yellow]Top thư mục được xem nhiều nhất[/COLOR]"
            item["is_playable"] = False
            item["path"] = 'plugin://plugin.video.vietmediaF?action=play&url=top_follow_share'
            item["thumbnail"] = ''
            item["icon"] = play_icon
            item["label2"] = ""
            item["info"] = {'plot': '','size':filesize}
        else:
            linkcode = i["linkcode"]
            type_f = i["type"]
            if type_f == '0':
                link = ('plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/%s' % linkcode)
                playable = False
            else:
                link = ('plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/%s' % linkcode)
                playable = True
            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = play_icon
            item["icon"] = play_icon
            item["label2"] = ""
            item["info"] = {'plot': '','size':filesize}

        items += [item]


    try:
        nextpage_url = f_items["_links"]["next"]
        nextpage_url = "https://www.fshare.vn/api"+nextpage_url
        nextpage_url = urlencode(nextpage_url)
        nextpage_url = "plugin://plugin.video.vietmediaF?action=play&url=" + (nextpage_url)
        nextpage = {"label": '[COLOR yellow]Next Page[/COLOR]', "is_playable": False,
            "path": nextpage_url, "thumbnail": '', "icon": "", "label2": "", "info": {'plot': ''}}
        items.append(nextpage)

    except: items = items
    data = {"content_type": "episodes", "items": ""}
    data.update({"items": items})
    return json.dumps(data)

