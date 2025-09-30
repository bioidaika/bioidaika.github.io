import sys
import re
import os
import json
import hashlib
import requests
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from urllib.parse import parse_qsl, urlencode
from resources import cache_utils
from resources.addon import alert

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
HANDLE = int(sys.argv[1])


PHIMHOT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1UbAo0JpJIUUkOTi8120yJ8nJkVh_pryhG3GBgCUZNZQ/edit?gid=1770537487"
PHIMHOT_SHEET_ID = "1UbAo0JpJIUUkOTi8120yJ8nJkVh_pryhG3GBgCUZNZQ"
PHIMHOT_SHEET_GID = "1770537487"

def log(msg, level=xbmc.LOGINFO):
    """Ghi log với prefix của addon"""
    xbmc.log(f"[{ADDON_ID}] {msg}", level)

def get_sheet_data():
    """Lấy dữ liệu từ Google Sheet dưới dạng CSV"""
    
    cache_key = hashlib.md5(f"{PHIMHOT_SHEET_ID}_{PHIMHOT_SHEET_GID}".encode()).hexdigest() + "_csv_data"

    
    if cache_utils.check_cache(cache_key):  
        cache_content = cache_utils.get_cache(cache_key)
        if cache_content:
            log("Lấy dữ liệu CSV từ cache")
            return cache_content

    try:
        
        csv_url = f"https://docs.google.com/spreadsheets/d/{PHIMHOT_SHEET_ID}/export?format=csv&gid={PHIMHOT_SHEET_GID}"

        log(f"Đang tải dữ liệu mới từ: {csv_url}")

        
        response = requests.get(csv_url)
        response.raise_for_status()  

        
        response.encoding = 'utf-8'

        
        csv_data = response.text
        if csv_data:
            cache_utils.set_cache(cache_key, csv_data)

        
        return csv_data
    except Exception as e:
        log(f"Lỗi khi lấy dữ liệu từ Google Sheet: {str(e)}", xbmc.LOGERROR)
        return None

def parse_csv_data(csv_data):
    """Phân tích dữ liệu CSV và chuyển đổi thành danh sách phim"""
    if not csv_data:
        return []

    movies = []
    lines = csv_data.splitlines()

    
    if len(lines) <= 1:  
        return []

    
    headers = lines[0].split(',')


    
    for i in range(1, len(lines)):
        line = lines[i]

        
        values = []
        in_quotes = False
        current_value = ""

        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                values.append(current_value.strip('"'))
                current_value = ""
            else:
                current_value += char

        
        values.append(current_value.strip('"'))

        
        while len(values) < len(headers):
            values.append("")

        
        movie = {}
        for j, header in enumerate(headers):
            if j < len(values):
                
                header_clean = header.strip()
                value_clean = values[j].strip()
                movie[header_clean] = value_clean

        
        if 'Movie Name' in movie and movie['Movie Name']:
            movies.append(movie)
        elif 'Name' in movie and movie['Name']:  
            movies.append(movie)

    return movies

def extract_runtime_minutes(runtime_str):
    """Trích xuất số phút từ chuỗi thời lượng (ví dụ: '105 phút' -> 105)"""
    if not runtime_str:
        return 0

    
    match = re.search(r'(\d+)', runtime_str)
    if match:
        return int(match.group(1))
    return 0

def create_list_items(movies):
    """Tạo danh sách các item để hiển thị trong Kodi"""
    items = []

    for movie in movies:
        
        name = str(movie.get('Movie Name', ''))
        name2 = str(movie.get('Original Title', ''))
        linkmovie = str(movie.get('Movie Link', ''))
        linkfshare = str(movie.get('Fshare Link', ''))
        genres = str(movie.get('Genre', ''))
        year = str(movie.get('Year', ''))
        runtime_str = str(movie.get('Runtime', ''))
        rating = str(movie.get('Rating', '0'))
        plot = str(movie.get('Overview', ''))
        poster = str(movie.get('Poster URL', ''))
        backdrop = str(movie.get('Backdrop URL', ''))
        tmdb_id = str(movie.get('TMDB ID', ''))

        
        runtime_minutes = extract_runtime_minutes(runtime_str)

        
        path_url = f"plugin://{ADDON_ID}/?action=browse&url={linkmovie}"
        log("path_url: " + path_url)

        
        properties = {
            "IsPlayable": "false",
            "TotalTime": str(runtime_minutes * 60),  
            "ResumeTime": "0"
        }

        
        item = {
            "label": name,
            "label2": name2,
            "path": path_url,
            "thumbnail": poster,
            "icon": poster,
            "is_playable": False,
            "info": {
                "title": name,
                "originaltitle": name2,
                "year": int(year) if year.isdigit() else 0,
                "genre": genres,
                "rating": float(rating) if rating and re.match(r'^\d+(\.\d+)?$', rating) else 0.0,
                "plot": plot,
                "duration": runtime_minutes*60,
                "mediatype": "movie"
            },
            "art": {
                "poster": poster,
                "fanart": backdrop,
                "thumb": poster,
                "icon": poster
            },
            "properties": properties  
        }

        items.append(item)

    return items

def get_thuviencine_top():
    """Hàm chính để lấy danh sách phim hot từ thuviencine.com/top"""
    log("Đang lấy danh sách phim hot từ thuviencine.com/top")

    
    cache_key = hashlib.md5("thuviencine_top".encode()).hexdigest() + "_phimhot"

    
    if cache_utils.check_cache(cache_key):
        cache_content = cache_utils.get_cache(cache_key)
        if cache_content:
            
            xbmc.sleep(500)
            return cache_content
    
    csv_data = get_sheet_data()
    if not csv_data:
        xbmcgui.Dialog().notification(ADDON_NAME, "Không thể tải dữ liệu phim", xbmcgui.NOTIFICATION_ERROR)
        return None
    
    movies = parse_csv_data(csv_data)
    if not movies:
        xbmcgui.Dialog().notification(ADDON_NAME, "Không tìm thấy phim nào", xbmcgui.NOTIFICATION_INFO)
        return None
    
    items = create_list_items(movies)
       
    next_page_url = "https://thuviencine.com/top/page/2/"
    nextpage = {
        "label": '[COLOR yellow]Trang 2[/COLOR]',
        "is_playable": False,
        "path": sys.argv[0] + "browse&url=vmf" + next_page_url,
        "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
        "icon": "https://i.imgur.com/yCGoDHr.png",
        "label2": "",
        "info": {'plot': 'Trang tiếp theo', 'mediatype': 'video'},
        "art": {
            'thumb': 'https://i.imgur.com/yCGoDHr.png',
            'icon': 'https://i.imgur.com/yCGoDHr.png',
            'poster': 'https://i.imgur.com/yCGoDHr.png'
        }
    }
    items.append(nextpage)
   
    data = {
        "content_type": "movies",
        "items": items
    }

    if data and len(items) > 0:
        cache_utils.set_cache(cache_key, data)
        xbmc.sleep(500)

    log(f"Đã tìm thấy {len(items)} phim")
    return data

def router(paramstring):
    """Router function để xử lý các tham số URL"""
    params = dict(parse_qsl(paramstring))

    if params.get('action') == 'thuviencine_top':
        
        data = get_thuviencine_top()

        
        from loadlistitem import list_item_main
        list_item_main(data)

    


if __name__ == '__main__':
    
    router(sys.argv[2][1:])


