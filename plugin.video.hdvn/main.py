import sys
import json
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode, parse_qsl
from xbmcvfs import translatePath

# Lấy thông tin addon
ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')  # Thư mục của addon
LOCAL_PIN_FILE = os.path.join(ADDON_PATH, 'local_pins.json')
SEARCH_JSON_FILE = os.path.join(ADDON_PATH, 'search.json')  # Đường dẫn tới file JSON
SETTINGS_FILE = os.path.join(ADDON_PATH, 'settings.json')  # File cấu hình

# Định nghĩa ADDON_HANDLE
ADDON_HANDLE = int(sys.argv[1])

# Lấy thông tin từ addon
_url = sys.argv[0]
_handle = int(sys.argv[1])

# URL chứa thông tin thư viện và thông tin mã PIN
LIBRARY_DETAILS_URL = "https://a-z.azdata.workers.dev/kodimain.json"
PIN_CODES_URL = "https://a-z.azdata.workers.dev/kodiprivate.json"

# Thêm FALLBACK_URL vào đầu file
FALLBACK_URL = "https://a-z.azdata.workers.dev/kodiupdate.mp4"

def load_json(json_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        request = Request(json_url, headers=headers)
        xbmc.log(f"Trying to load JSON data from: {json_url}", xbmc.LOGINFO)
        
        with urlopen(request) as response:
            data = json.load(response)
            xbmc.log("Successfully loaded JSON data.", xbmc.LOGINFO)
            return data
    except Exception as e:
        xbmc.log(f"Error loading JSON: {str(e)}", xbmc.LOGERROR)
        return {}

def load_local_pins():
    """Tải mã PIN từ file local"""
    try:
        if os.path.exists(LOCAL_PIN_FILE):
            with open(LOCAL_PIN_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        xbmc.log(f"Error loading local pins: {str(e)}", xbmc.LOGERROR)
    return {}

def save_local_pins(pins):
    """Lưu mã PIN vào file local"""
    try:
        with open(LOCAL_PIN_FILE, 'w') as f:
            json.dump(pins, f, indent=4)
        return True
    except Exception as e:
        xbmc.log(f"Error saving local pins: {str(e)}", xbmc.LOGERROR)
        return False

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

# Lấy mã PIN quản trị
def get_admin_pin():
    local_pins = load_local_pins()
    return local_pins.get("admin_pin", "1234")  # Mặc định là "1234" nếu chưa có

# Thay đổi mã PIN quản trị
def change_admin_pin():
    dialog = xbmcgui.Dialog()

    # Yêu cầu nhập mã PIN quản trị hiện tại
    current_admin_pin = get_admin_pin()
    entered_pin = dialog.numeric(0, "Nhập mã PIN quản trị hiện tại:")
    
    if entered_pin != current_admin_pin:
        dialog.notification("Truy cập bị từ chối", "Mã PIN không đúng", xbmcgui.NOTIFICATION_ERROR)
        return

    # Nhập mã PIN quản trị mới
    new_pin = dialog.numeric(0, "Nhập mã PIN quản trị mới:")
    
    # Xác nhận mã PIN
    confirm_pin = dialog.numeric(0, "Xác nhận mã PIN quản trị mới:")
    
    if new_pin != confirm_pin:
        dialog.notification("Lỗi", "Mã PIN không khớp", xbmcgui.NOTIFICATION_ERROR)
        return

    # Lưu mã PIN quản trị mới
    local_pins = load_local_pins()
    local_pins["admin_pin"] = new_pin
    if save_local_pins(local_pins):
        dialog.notification("Thành công", "Đã thay đổi mã PIN quản trị", xbmcgui.NOTIFICATION_INFO)
    else:
        dialog.notification("Lỗi", "Không thể lưu mã PIN", xbmcgui.NOTIFICATION_ERROR)

# Thay đổi mã PIN thư viện
def change_pin():
    """Chức năng thay đổi mã PIN với bảo vệ."""
    dialog = xbmcgui.Dialog()
    
    # Yêu cầu nhập mã PIN quản trị để truy cập
    admin_pin = get_admin_pin()
    entered_pin = dialog.numeric(0, "Nhập mã PIN quản trị để tiếp tục:")
    
    if entered_pin != admin_pin:
        dialog.notification("Truy cập bị từ chối", "Mã PIN không đúng", xbmcgui.NOTIFICATION_ERROR)
        return  # Thoát nếu mã PIN không đúng

    # Nếu mã PIN đúng, tiếp tục với logic thay đổi mã PIN
    library_details = load_json(LIBRARY_DETAILS_URL)
    libraries = list(library_details.keys())
    library_index = dialog.select("Chọn thư viện để thay đổi PIN", libraries)
    
    if library_index == -1:  # Người dùng hủy
        return
    
    selected_library = libraries[library_index]
    
    # Nhập mã PIN mới
    new_pin = dialog.numeric(0, f"Nhập mã PIN mới cho {selected_library}:")
    
    # Xác nhận mã PIN
    confirm_pin = dialog.numeric(0, "Xác nhận mã PIN mới:")
    
    if new_pin != confirm_pin:
        dialog.notification("Lỗi", "Mã PIN không khớp", xbmcgui.NOTIFICATION_ERROR)
        return
    
    # Lấy mã PIN local hiện tại
    local_pins = load_local_pins()
    
    # Cập nhật mã PIN mới
    local_pins[selected_library] = new_pin
    
    # Lưu mã PIN mới
    if save_local_pins(local_pins):
        dialog.notification("Thành công", f"Đã thay đổi PIN cho {selected_library}", xbmcgui.NOTIFICATION_INFO)
    else:
        dialog.notification("Lỗi", "Không thể lưu mã PIN", xbmcgui.NOTIFICATION_ERROR)

def ask_for_pin(library_name):
    """Kiểm tra và yêu cầu mã PIN"""
    # Ưu tiên kiểm tra mã PIN local trước
    local_pins = load_local_pins()
    pin_codes = load_json(PIN_CODES_URL)
    
    # Kiểm tra mã PIN local
    local_pin = local_pins.get(library_name)
    
    # Nếu không có mã PIN local, sử dụng mã PIN từ URL
    if not local_pin:
        local_pin = pin_codes.get(library_name)
    
    # Nếu không yêu cầu mã PIN
    if not local_pin:
        return True

    dialog = xbmcgui.Dialog()
    pin = dialog.numeric(0, f"Nhập mã PIN cho {library_name}:")
    
    # So sánh mã PIN
    if str(pin) == str(local_pin):
        return True
    else:
        dialog.notification("Truy cập bị từ chối", "Mã PIN không đúng", xbmcgui.NOTIFICATION_ERROR)
        return False


def save_search_results(results):
    """
    Lưu kết quả tìm kiếm vào file search.json trong thư mục addon.
    """
    try:
        # Lưu dữ liệu vào file JSON
        with open(SEARCH_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        xbmc.log(f"Successfully saved search results to {SEARCH_JSON_FILE}.", xbmc.LOGINFO)
        xbmcgui.Dialog().notification(
            "Lưu kết quả", 
            "Đã lưu kết quả tìm kiếm thành công.", 
            xbmcgui.NOTIFICATION_INFO
        )
    except Exception as e:
        xbmc.log(f"Lỗi khi lưu kết quả tìm kiếm: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Lưu kết quả", 
            "Không thể lưu kết quả tìm kiếm.", 
            xbmcgui.NOTIFICATION_ERROR
        )
def search_videos():
    """Chức năng tìm kiếm video trên toàn bộ thư viện"""
    dialog = xbmcgui.Dialog()
    progress_dialog = xbmcgui.DialogProgress()
    
    # Hiển thị bàn phím để nhập từ khóa tìm kiếm
    search_term = dialog.input("Nhập từ khóa tìm kiếm")
    
    if not search_term:
        return
    
    # Chuyển từ khóa về chữ thường để tìm kiếm không phân biệt hoa thường
    search_term = search_term.lower()
    
    # Danh sách kết quả tìm kiếm
    search_results = []
    
    # Lấy danh sách thư viện
    libraries = build_libraries()
    
    # Tải mã PIN từ URL
    pin_codes = load_json(PIN_CODES_URL)
    
    # Đếm số kết quả tìm được
    total_results = 0
    total_libraries = len(libraries)
    
    # Kiểm tra mã PIN quản trị một lần
    admin_pin = get_admin_pin()  # Lấy mã PIN quản trị
    entered_admin_pin = dialog.numeric(0, "Nhập mã PIN quản trị để tìm kiếm trong tất cả các kho phim.")
    
    if entered_admin_pin != admin_pin:
        dialog.notification(
            "Không nhập mã PIN quản trị nên chỉ tìm kiếm trong kho phim không có mã PIN", 
            "Chỉ tìm kiếm trong các danh mục không yêu cầu mã PIN.", 
            xbmcgui.NOTIFICATION_ERROR
        )
        entered_admin_pin = None  # Nếu sai mã PIN, không cho phép truy cập danh mục yêu cầu mã PIN
    
    # Hiển thị dialog tiến trình
    progress_dialog.create('Đang tìm kiếm', f'Tìm kiếm: {search_term}')
    
    # Duyệt qua từng thư viện để tìm kiếm
    for index, (library_name, json_url) in enumerate(libraries.items(), 1):
        # Kiểm tra hủy bỏ
        if progress_dialog.iscanceled():
            progress_dialog.close()
            return
        
        # Cập nhật tiến trình
        percent = int((index / total_libraries) * 100)
        progress_dialog.update(percent, f'Đang tìm kiếm trong thư viện: {library_name}')
        
        # Kiểm tra xem thư viện này có yêu cầu mã PIN không
        required_pin = pin_codes.get(library_name)
        if required_pin:
            # Nếu thư viện yêu cầu mã PIN và mã PIN quản trị không đúng, bỏ qua thư viện
            if entered_admin_pin != admin_pin:
                xbmc.log(f"Bỏ qua thư viện {library_name} vì mã PIN quản trị không đúng.", xbmc.LOGINFO)
                continue  # Bỏ qua thư viện này nếu không có mã PIN hợp lệ
        
        try:
            # Tải dữ liệu video từ thư viện
            videos = load_json(json_url)
            
            # Tìm kiếm trong từng video
            for video in videos:
                # Kiểm tra từ khóa trong tên phim
                if search_term in video['name'].lower():
                    search_results.append(video)
                    total_results += 1
        except Exception as e:
            xbmc.log(f"Lỗi khi tìm kiếm trong thư viện {library_name}: {str(e)}", xbmc.LOGERROR)
    
    # Đóng dialog tiến trình
    progress_dialog.close()
    
    # Lưu kết quả tìm kiếm vào file search.json
    try:
        with open(SEARCH_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(search_results, f, ensure_ascii=False, indent=4)
        xbmc.log(f"Nội dung của search.json: {json.dumps(search_results, ensure_ascii=False, indent=4)}", xbmc.LOGINFO)
    except Exception as e:
        xbmc.log(f"Lỗi khi lưu kết quả tìm kiếm: {str(e)}", xbmc.LOGERROR)
    
    # Thông báo số lượng kết quả
    dialog.notification(
        "Tìm kiếm", 
        f"Tìm thấy {total_results} kết quả trong {total_libraries} thư viện", 
        xbmcgui.NOTIFICATION_INFO
    )
    
    # Điều hướng tới action 'list_search_results' để hiển thị danh sách
    if search_results:
        xbmc.log("Điều hướng để hiển thị danh sách kết quả tìm kiếm.", xbmc.LOGINFO)
        xbmc.executebuiltin(f"Container.Update({get_url(action='list_search_results')})")
    else:
        dialog.notification("Tìm kiếm", "Không tìm thấy kết quả nào.", xbmcgui.NOTIFICATION_INFO)

def list_search_results():
    """Hiển thị danh sách kết quả tìm kiếm từ search.json"""
    try:
        # Đọc file search.json từ đường dẫn thực
        with open(SEARCH_JSON_FILE, 'r', encoding='utf-8') as f:
            search_results = json.load(f)

        xbmc.log("Successfully loaded JSON data.", xbmc.LOGINFO)

        if not search_results:
            xbmcgui.Dialog().notification(
                "Kết quả tìm kiếm", 
                "Không có kết quả nào phù hợp.", 
                xbmcgui.NOTIFICATION_INFO
            )
            return

        # Tạo danh sách kết quả tìm kiếm
        list_items = []
        for video in search_results:
            # Lấy fanart và poster từ video
            fanart_url = video.get('fanart_url', video.get('poster_url'))
            poster_url = video.get('poster_url', '')

            # Lấy thông tin video
            video_description = video.get('description', 'Không có mô tả')

            # Duyệt qua tất cả các links trong video
            if 'links' in video:
                for link in video['links']:
                    # Lấy thông tin từng link
                    video_url = link.get('url', '')
                    quality = link.get('quality', 'Unknown Quality')
                    file_name = link.get('file_name', 'Unknown File Name')

                    # Tạo label hiển thị tên file và chất lượng
                    label = f"{file_name} - [COLOR yellow]{quality}[/COLOR]"

                    # Tạo ListItem cho từng link
                    item = xbmcgui.ListItem(label=label)
                    item.setArt({'poster': poster_url, 'thumb': poster_url, 'fanart': fanart_url})
                    
                    # Sử dụng InfoTagVideo để thiết lập thông tin
                    info_tag = item.getVideoInfoTag()
                    info_tag.setTitle(file_name)
                    info_tag.setPlot(video_description)

                    item.setPath(video_url)

                    # Thêm vào danh sách
                    list_items.append((video_url, item, False))

        # Thêm các mục vào thư mục KODI
        xbmcplugin.addDirectoryItems(handle=_handle, items=list_items, totalItems=len(list_items))
        xbmcplugin.endOfDirectory(_handle)

    except Exception as e:
        xbmc.log(f"Lỗi khi hiển thị kết quả tìm kiếm: {str(e)}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            "Kết quả tìm kiếm", 
            "Lỗi khi hiển thị kết quả tìm kiếm.", 
            xbmcgui.NOTIFICATION_ERROR
        )


def list_search_links(video_name):
    """Hiển thị các link của video tìm kiếm được"""
    try:
        with open(SEARCH_JSON_FILE, 'r', encoding='utf-8') as f:
            search_results = json.load(f)
    except Exception as e:
        xbmc.log(f"Lỗi khi đọc kết quả tìm kiếm: {str(e)}", xbmc.LOGERROR)
        return

    for video in search_results:
        if video['name'] == video_name and 'links' in video:
            fanart_url = video.get('fanart_url', video.get('poster_url'))
            for link in video['links']:
                file_name = link['file_name']
                quality_colored = f"[COLOR yellow]{link['quality']}[/COLOR]"
                label = f"{file_name} - {quality_colored}"
                
                li = xbmcgui.ListItem(label)
                li.setArt({'poster': video['poster_url'], 'fanart': fanart_url})
                li.setInfo('video', {'title': video['name'], 'plot': video['description']})
                li.setProperty('IsPlayable', 'true')
                
                url = get_url(action='play', video_url=link['url'])
                xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)
    
    xbmcplugin.endOfDirectory(_handle)

def load_settings():
    """Tải cài đặt từ file settings.json"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        xbmc.log(f"Error loading settings: {str(e)}", xbmc.LOGERROR)
    return {"videos_per_page": 30}  # Giá trị mặc định

def save_settings(settings):
    """Lưu cài đặt vào file settings.json"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        xbmc.log(f"Error saving settings: {str(e)}", xbmc.LOGERROR)
        return False

def change_videos_per_page():
    """Chức năng thay đổi số lượng video hiển thị trên mỗi trang"""
    dialog = xbmcgui.Dialog()
    
    # Yêu cầu nhập mã PIN quản trị để truy cập
    admin_pin = get_admin_pin()
    entered_pin = dialog.numeric(0, "Nhập mã PIN quản trị để tiếp tục:")
    
    if entered_pin != admin_pin:
        dialog.notification("Truy cập bị từ chối", "Mã PIN không đúng", xbmcgui.NOTIFICATION_ERROR)
        return

    # Lấy cài đặt hiện tại
    settings = load_settings()
    current_value = settings.get("videos_per_page", 30)
    
    # Hiển thị bàn phím để nhập số lượng mới
    new_value = dialog.input("Nhập số lượng video hiển thị trên mỗi trang", str(current_value))
    
    if not new_value:
        return
    
    try:
        new_value = int(new_value)
        if new_value < 1:
            dialog.notification("Lỗi", "Số lượng phải lớn hơn 0", xbmcgui.NOTIFICATION_ERROR)
            return
    except ValueError:
        dialog.notification("Lỗi", "Vui lòng nhập một số hợp lệ", xbmcgui.NOTIFICATION_ERROR)
        return

    # Cập nhật cài đặt
    settings["videos_per_page"] = new_value
    if save_settings(settings):
        dialog.notification("Thành công", f"Đã thay đổi số lượng video hiển thị thành {new_value}", xbmcgui.NOTIFICATION_INFO)
    else:
        dialog.notification("Lỗi", "Không thể lưu cài đặt", xbmcgui.NOTIFICATION_ERROR)

def main_menu():
    """Hiển thị menu chính."""
    library_details = load_json(LIBRARY_DETAILS_URL)
    if not library_details:
        xbmcgui.Dialog().notification("Error", "Failed to load library details.", xbmcgui.NOTIFICATION_ERROR)
        return

    # Thêm mục TÌM KIẾM vào đầu menu
    li = xbmcgui.ListItem("[COLOR green]TÌM KIẾM TRONG TOÀN BỘ CÁC KHO PHIM CỦA ADDON[/COLOR]")
    li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
    li.setInfo('video', {'title': 'TÌM KIẾM', 'plot': 'Tìm kiếm phim từ toàn bộ các kho phim hiện có của addon. Bạn sẽ phải nhập mã PIN quản trị để tìm kiếm trong kho phim có mã pin. Nếu không nhập mã PIN thì sẽ không tìm trong kho phim đó. Nếu bạn không thay đổi mã PIN quản trị thì mặc định là 1234'})
    url = get_url(action='search')  # Gọi action='search'
    xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)

    # Các mục khác trong menu...
    for library_name, details in library_details.items():
        li = xbmcgui.ListItem(library_name)
        li.setArt({'poster': details.get('poster', '')})
        li.setInfo('video', {'title': library_name, 'plot': details.get('description', '')})
        url = get_url(action='list_library', library_name=library_name)
        xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=True)

    # Thêm mục thay đổi mã PIN quản trị
    li = xbmcgui.ListItem("[COLOR yellow]THAY ĐỔI MÃ PIN QUẢN TRỊ[/COLOR]")
    li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
    li.setInfo('video', {'title': 'THAY ĐỔI MÃ PIN QUẢN TRỊ', 'plot': 'Cần phải nhập mã pin cũ, nếu là lần đầu thiết lập thì mã PIN mặc định là 1234'})
    url = get_url(action='change_admin_pin')
    xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)

    # Thêm mục thay đổi PIN thư viện
    li = xbmcgui.ListItem("[COLOR yellow]THAY ĐỔI MÃ PIN THƯ VIỆN[/COLOR]")
    li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
    url = get_url(action='change_pin')
    li.setInfo('video', {'title': 'THAY ĐỔI MÃ PIN CỦA CÁC THƯ VIỆN', 'plot': 'Cần phải nhập mã pin của QUẢN TRỊ, mã PIN mặc định của các kho phim là 1234'})
    xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)

    # Thêm mục thay đổi số lượng video hiển thị
    settings = load_settings()
    current_value = settings.get("videos_per_page", 30)
    li = xbmcgui.ListItem(f"[COLOR yellow]THAY ĐỔI SỐ LƯỢNG VIDEO HIỂN THỊ (Hiện tại: {current_value})[/COLOR]")
    li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
    li.setInfo('video', {'title': 'THAY ĐỔI SỐ LƯỢNG VIDEO HIỂN THỊ', 'plot': f'Thay đổi số lượng video hiển thị trên mỗi trang. Giá trị hiện tại: {current_value}'})
    url = get_url(action='change_videos_per_page')
    xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)

    xbmcplugin.endOfDirectory(_handle)

def build_libraries():
    """Xây dựng danh sách LIBRARIES từ LIBRARY_DETAILS_URL."""
    library_details = load_json(LIBRARY_DETAILS_URL)
    if not library_details:
        xbmc.log("Failed to load library details for building LIBRARIES.", xbmc.LOGERROR)
        return {}

    libraries = {}
    for library_name, details in library_details.items():
        data_json = details.get("data_json")
        if data_json:
            libraries[library_name] = data_json
    return libraries

def list_videos(library_name):
    """Hiển thị danh sách video từ thư viện được chọn."""
    # Kiểm tra mã PIN cho thư viện trước khi tiếp tục
    if not ask_for_pin(library_name):
        return

    libraries = build_libraries()
    json_url = libraries.get(library_name, "")
    if not json_url:
        xbmc.log(f"Library {library_name} not found.", xbmc.LOGERROR)
        return

    # Lấy tham số trang từ URL
    params = dict(parse_qsl(sys.argv[2][1:]))
    current_page = int(params.get('page', 1))
    
    # Lấy số lượng video trên mỗi trang từ cài đặt
    settings = load_settings()
    videos_per_page = settings.get("videos_per_page", 30)

    videos = load_json(json_url)
    if not videos:
        xbmc.log(f"No videos found in {library_name}.", xbmc.LOGINFO)
        return

    # Tính toán phân trang
    total_videos = len(videos)
    total_pages = (total_videos + videos_per_page - 1) // videos_per_page
    start_idx = (current_page - 1) * videos_per_page
    end_idx = min(start_idx + videos_per_page, total_videos)

    # Hiển thị thông tin trang hiện tại
    xbmc.log(f"Displaying page {current_page} of {total_pages} for {library_name}", xbmc.LOGINFO)

    # Thêm nút về Danh sách kho phim
    back_to_libraries_li = xbmcgui.ListItem("[COLOR blue]← Về Danh sách kho phim[/COLOR]")
    back_to_libraries_li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
    back_to_libraries_url = get_url(action='main_menu')
    xbmcplugin.addDirectoryItem(handle=_handle, url=back_to_libraries_url, listitem=back_to_libraries_li, isFolder=True)

    # Thêm nút về trang đầu nếu không ở trang đầu tiên
    if current_page > 1:
        first_page_li = xbmcgui.ListItem("[COLOR green]Về trang đầu[/COLOR]")
        first_page_li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
        first_page_url = get_url(action='list_library', library_name=library_name, page=1)
        xbmcplugin.addDirectoryItem(handle=_handle, url=first_page_url, listitem=first_page_li, isFolder=True)

    # Thêm nút điều hướng trang trước
    if current_page > 1:
        prev_li = xbmcgui.ListItem(f"[COLOR yellow]← Trang trước ({current_page-1}/{total_pages})[/COLOR]")
        prev_li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
        prev_url = get_url(action='list_library', library_name=library_name, page=current_page-1)
        xbmcplugin.addDirectoryItem(handle=_handle, url=prev_url, listitem=prev_li, isFolder=True)

    # Hiển thị video cho trang hiện tại
    for video in videos[start_idx:end_idx]:
        if 'url' in video:
            fanart_url = video.get('fanart_url', video.get('poster_url'))
            li = xbmcgui.ListItem(video['name'])
            li.setArt({'poster': video['poster_url'], 'fanart': fanart_url})
            
            # Sử dụng InfoTagVideo thay vì setInfo
            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(video['name'])
            info_tag.setPlot(video['description'])
            
            li.setProperty('IsPlayable', 'true')
            url = get_url(action='play', video_url=video['url'])
            xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)
        elif 'links' in video:
            fanart_url = video.get('fanart_url', video.get('poster_url'))
            li = xbmcgui.ListItem(video['name'])
            li.setArt({'poster': video['poster_url'], 'fanart': fanart_url})
            
            # Sử dụng InfoTagVideo thay vì setInfo
            info_tag = li.getVideoInfoTag()
            info_tag.setTitle(video['name'])
            info_tag.setPlot(video['description'])
            
            url = get_url(action='list_links', video_name=video['name'], library_name=library_name)
            xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=True)

    # Thêm nút điều hướng trang sau
    if current_page < total_pages:
        next_li = xbmcgui.ListItem(f"[COLOR yellow]Trang tiếp theo ({current_page+1}/{total_pages}) →[/COLOR]")
        next_li.setArt({'poster': 'https://i.imgur.com/CE0yUIW.png'})
        next_url = get_url(action='list_library', library_name=library_name, page=current_page+1)
        xbmcplugin.addDirectoryItem(handle=_handle, url=next_url, listitem=next_li, isFolder=True)

    xbmcplugin.endOfDirectory(_handle)

def list_links(video_name, library_name):
    """Hiển thị danh sách các liên kết trong video."""
    libraries = build_libraries()
    json_url = libraries.get(library_name, "")
    videos = load_json(json_url)
    keywords = ["vietsub", "viet_sub", "sub viet", "viet sub", "phụ đề", "sub", "viet", "hardsub"]
    for video in videos:
        if video['name'] == video_name and 'links' in video:
            fanart_url = video.get('fanart_url', video.get('poster_url'))
            for link in video['links']:
                file_name = link['file_name']
                quality_colored = f"[COLOR yellow]{link['quality']}[/COLOR]"
                highlighted_name = file_name
                for keyword in keywords:
                    highlighted_name = highlighted_name.replace(
                        keyword, f"[COLOR yellow]{keyword}[/COLOR]"
                    ).replace(
                        keyword.capitalize(), f"[COLOR yellow]{keyword.capitalize()}[/COLOR]"
                    ).replace(
                        keyword.upper(), f"[COLOR yellow]{keyword.upper()}[/COLOR]"
                    )
                label = f"{highlighted_name} - {quality_colored}"
                li = xbmcgui.ListItem(label)
                li.setArt({'poster': video['poster_url'], 'fanart': fanart_url})
                li.setInfo('video', {'title': video['name'], 'plot': video['description']})
                li.setProperty('IsPlayable', 'true')
                url = get_url(action='play', video_url=link['url'])
                xbmcplugin.addDirectoryItem(handle=_handle, url=url, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(_handle)

def play_video(video_url):
    """Phát video với headers xác thực và timeout."""
    xbmc.log(f"Playing video: {video_url}", xbmc.LOGINFO)
    
    # Tạo ListItem với headers
    li = xbmcgui.ListItem(path=video_url)
    
    # Xác định định dạng video và thiết lập MIME type phù hợp
    if video_url.endswith('.mkv'):
        li.setMimeType("video/x-matroska")
    elif video_url.endswith('.mp4'):
        li.setMimeType("video/mp4")
    elif video_url.endswith('.m3u8'):
        li.setMimeType("application/x-mpegURL")
        # Thiết lập cho HLS stream
        li.setProperty('inputstream.adaptive.manifest_type', 'hls')
        li.setProperty('inputstream.adaptive.stream_type', 'hls')
    else:
        # Mặc định là mp4 nếu không xác định được định dạng
        li.setMimeType("video/mp4")
    
    li.setProperty('IsPlayable', 'true')
    
    # Thêm headers xác thực
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://a-z.azdata.workers.dev/',
        'Origin': 'https://a-z.azdata.workers.dev',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'video',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'version': '1.2.3',
        'Cache-Control': 'no-cache'
    }
    
    # Chuyển headers thành chuỗi
    header_string = '&'.join([f"{k}={v}" for k, v in headers.items()])
    
    # Thêm thông tin về headers vào ListItem
    li.setProperty('inputstream.adaptive.stream_headers', header_string)
    li.setProperty('inputstream.adaptive.manifest_headers', header_string)
    
    # Thêm timeout
    li.setProperty('inputstream.adaptive.connection_timeout', '60')
    li.setProperty('inputstream.adaptive.manifest_timeout', '60')
    li.setProperty('inputstream.adaptive.stream_timeout', '60')
    
    # Thêm fallback URL
    li.setProperty('inputstream.adaptive.fallback_url', FALLBACK_URL)
    
    # Thêm các thuộc tính để cải thiện việc phát video
    li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    
    # Thêm các thuộc tính cho adaptive streaming
    li.setProperty('inputstream.adaptive.max_bandwidth', '0')  # Không giới hạn băng thông
    li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    li.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
    
    # Phát video
    xbmcplugin.setResolvedUrl(_handle, True, li)

# list_search_results()
def router(paramstring):
    """Điều hướng yêu cầu."""
    params = dict(parse_qsl(paramstring))
    action = params.get('action')
    
    if  action == 'change_admin_pin':
        change_admin_pin()
    elif action == 'change_pin':
        change_pin()
    elif action == 'search':
        search_videos()
    elif action == 'list_search_results':
        list_search_results()
    elif action == 'list_search_links':
        video_name = params.get('video_name')
        list_search_links(video_name)
    elif action == 'list_library':
        library_name = params.get('library_name')
        list_videos(library_name)
    elif action == 'list_links':
        video_name = params.get('video_name')
        library_name = params.get('library_name')
        list_links(video_name, library_name)
    elif action == 'play':
        video_url = params.get('video_url')
        play_video(video_url)
    elif action == 'change_videos_per_page':
        change_videos_per_page()
    else:
        main_menu()

# Điều hướng yêu cầu từ Kodi
router(sys.argv[2][1:])
