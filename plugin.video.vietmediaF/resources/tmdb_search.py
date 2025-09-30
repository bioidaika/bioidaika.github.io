import requests
import json
import os
import time
import xbmcgui
import xbmcplugin
import xbmc
import xbmcvfs
from urllib.parse import quote_plus, unquote_plus
from .addon import ADDON_PATH, PROFILE_PATH, notify, alert, logError, log
from .cache_utils import cache_data, get_cache, set_cache

# TMDB API Configuration
TMDB_API_KEY = 'db55323b8d3e4154498498a75642b381'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
BACKEND_API_BASE = 'https://bioidaika.click/api'

# Cache configuration
CACHE_DIR = os.path.join(PROFILE_PATH, 'tmdb_cache')
CACHE_DURATION_TMDB = 30 * 60  # 30 minutes
CACHE_DURATION_BACKEND = 60 * 60  # 1 hour

def ensure_cache_dir():
    """Tạo thư mục cache nếu chưa có"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_cache_file_path(cache_key):
    """Lấy đường dẫn file cache"""
    return os.path.join(CACHE_DIR, f"{cache_key}.json")

def is_cache_valid(cache_file, duration):
    """Kiểm tra cache có còn hợp lệ không"""
    if not os.path.exists(cache_file):
        return False
    
    file_time = os.path.getmtime(cache_file)
    current_time = time.time()
    return (current_time - file_time) < duration

def load_from_cache(cache_key, duration):
    """Tải dữ liệu từ cache"""
    ensure_cache_dir()
    cache_file = get_cache_file_path(cache_key)
    
    if is_cache_valid(cache_file, duration):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logError(f"Lỗi đọc cache: {e}")
    return None

def save_to_cache(cache_key, data):
    """Lưu dữ liệu vào cache"""
    ensure_cache_dir()
    cache_file = get_cache_file_path(cache_key)
    
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logError(f"Lỗi lưu cache: {e}")

def search_tmdb(query, page=1):
    """Tìm kiếm trên TMDB API"""
    log(f"[VietmediaF] TMDB Search: Bắt đầu tìm kiếm '{query}' trang {page}")
    
    # Tạo cache key
    cache_key = f"tmdb_search_{quote_plus(query)}_{page}"
    
    # Kiểm tra cache trước
    cached_data = load_from_cache(cache_key, CACHE_DURATION_TMDB)
    if cached_data:
        log(f"[VietmediaF] TMDB Search: Cache hit cho '{query}' trang {page}")
        return cached_data
    
    try:
        # Gọi TMDB API cho cả movie và TV
        results = []
        
        # Tìm kiếm movies
        movie_url = f"{TMDB_BASE_URL}/search/movie"
        movie_params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'page': page,
            'language': 'vi-VN'
        }
        
        log(f"[VietmediaF] TMDB Search: Gọi API movie - {movie_url}")
        movie_response = requests.get(movie_url, params=movie_params, timeout=10)
        movie_data = movie_response.json()
        
        if movie_data.get('results'):
            log(f"[VietmediaF] TMDB Search: Tìm thấy {len(movie_data['results'])} movies")
            for item in movie_data['results']:
                item['media_type'] = 'movie'
                results.append(item)
        
        # Tìm kiếm TV shows
        tv_url = f"{TMDB_BASE_URL}/search/tv"
        tv_params = {
            'api_key': TMDB_API_KEY,
            'query': query,
            'page': page,
            'language': 'vi-VN'
        }
        
        log(f"[VietmediaF] TMDB Search: Gọi API TV - {tv_url}")
        tv_response = requests.get(tv_url, params=tv_params, timeout=10)
        tv_data = tv_response.json()
        
        if tv_data.get('results'):
            log(f"[VietmediaF] TMDB Search: Tìm thấy {len(tv_data['results'])} TV shows")
            for item in tv_data['results']:
                item['media_type'] = 'tv'
                results.append(item)
        
        # Sắp xếp theo popularity
        results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
        
        log(f"[VietmediaF] TMDB Search: Tổng cộng {len(results)} kết quả cho '{query}'")
        
        # Lưu vào cache
        save_to_cache(cache_key, results)
        
        return results
        
    except Exception as e:
        logError(f"Lỗi tìm kiếm TMDB: {e}")
        notify(f"Lỗi tìm kiếm TMDB: {str(e)}")
        return []

def get_backend_sources(media_type, tmdb_id):
    """Lấy danh sách nguồn từ backend API"""
    log(f"[VietmediaF] TMDB Backend: Lấy nguồn cho {media_type} {tmdb_id}")
    
    # Tạo cache key
    cache_key = f"backend_{media_type}_{tmdb_id}"
    
    # Kiểm tra cache trước
    cached_data = load_from_cache(cache_key, CACHE_DURATION_BACKEND)
    if cached_data:
        log(f"[VietmediaF] TMDB Backend: Cache hit cho {media_type} {tmdb_id}")
        return cached_data
    
    try:
        url = f"{BACKEND_API_BASE}/{media_type}/{tmdb_id}"
        log(f"[VietmediaF] TMDB Backend: Gọi API - {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            sources_count = len(data.get('sources', []))
            log(f"[VietmediaF] TMDB Backend: Nhận được {sources_count} nguồn cho {media_type} {tmdb_id}")
            # Lưu vào cache
            save_to_cache(cache_key, data)
            return data
        else:
            logError(f"[VietmediaF] TMDB Backend: Lỗi API {response.status_code} cho {media_type} {tmdb_id}")
            notify(f"Lỗi API backend: {response.status_code}")
            return None
            
    except Exception as e:
        logError(f"Lỗi gọi backend API: {e}")
        notify(f"Lỗi gọi backend API: {str(e)}")
        return None

def _tmdb_details_cache_key(media_type, tmdb_id):
    # include language to avoid mixing localized caches; details fetched in en-US
    return f"tmdb_details_enUS_{media_type}_{tmdb_id}"

def get_tmdb_runtime(media_type, tmdb_id):
    """Fetch and cache runtime (minutes) and canonical original_title for movie/tv."""
    try:
        key = _tmdb_details_cache_key(media_type, tmdb_id)
        cached = get_cache(key)
        if cached is not None:
            try:
                # cached structure: {'runtime': int, 'original': str, 'premiered': str}
                return int(cached.get('runtime', 0)), cached.get('original'), cached.get('premiered', '')
            except Exception:
                pass
        if media_type == 'movie':
            url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
        else:
            url = f"{TMDB_BASE_URL}/tv/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
        log(f"[VietmediaF] TMDB Details: {url}")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if media_type == 'movie':
                runtime = int(data.get('runtime') or 0)
                original = data.get('original_title') or ''
                premiered = data.get('release_date') or ''
            else:
                episode_run_time = data.get('episode_run_time') or []
                runtime = int(episode_run_time[0]) if episode_run_time else 0
                original = data.get('original_name') or ''
                premiered = data.get('first_air_date') or ''
            payload = {'runtime': runtime, 'original': original, 'premiered': premiered}
            set_cache(key, payload)
            return runtime, original, premiered
        else:
            logError(f"[VietmediaF] TMDB Details error {r.status_code} for {media_type} {tmdb_id}")
            return 0, None, ''
    except Exception as e:
        logError(f"[VietmediaF] TMDB Details exception: {e}")
        return 0, None, ''

def create_tmdb_item(item):
    """Tạo item từ TMDB data với thông tin đầy đủ"""
    try:
        tmdb_id = item.get('id')
        # Xác định media_type dựa trên có title hay name
        media_type = 'movie' if 'title' in item else 'tv'
        title = item.get('title') or item.get('name', 'Unknown')
        original_title = item.get('original_title') or item.get('original_name', '')
        overview = item.get('overview', '')
        release_date = item.get('release_date') or item.get('first_air_date', '')
        poster_path = item.get('poster_path', '')
        backdrop_path = item.get('backdrop_path', '')
        vote_average = item.get('vote_average', 0)
        runtime = item.get('runtime', 0)  # Thời lượng phim (phút)
        
        # Enrich runtime and canonical original title if missing in search results
        det_runtime, det_original, det_premiered = get_tmdb_runtime(media_type, tmdb_id)
        if not runtime or int(runtime) == 0:
            runtime = det_runtime
        # Prefer canonical original title from details if it differs from localized title
        if det_original and det_original.strip().lower() != (title or '').strip().lower():
            original_title = det_original
        # Fill release_date from details if missing in search payload
        if (not release_date) and det_premiered:
            release_date = det_premiered
        
        log(f"[VietmediaF] TMDB Item: Tạo item cho '{title}' (ID: {tmdb_id}, Type: {media_type})")
        
        # Tạo poster/backdrop URL
        poster_url = ''
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        backdrop_url = ''
        if backdrop_path:
            backdrop_url = f"https://image.tmdb.org/t/p/w780{backdrop_path}"
        
        # Tạo label với thông tin đầy đủ
        year = release_date[:4] if release_date else ''
        rating = f"⭐ {vote_average:.1f}" if vote_average > 0 else ""
        # Tạo label chính: <English> - <Vietnamese> (year)
        base_left = original_title.strip() if original_title else ''
        base_right = title.strip() if title else ''
        if base_left and base_right and base_left.lower() != base_right.lower():
            label = f"{base_left} - {base_right}"
        else:
            # fallback: chỉ có một tên
            label = base_right or base_left or "Unknown"
        if year:
            label += f" ({year})"
        
        # Thêm thời lượng vào label cạnh năm (format HH:MM:SS), phù hợp mọi skin
        if runtime and int(runtime) > 0:
            hours = int(runtime) // 60
            minutes = int(runtime) % 60
            if hours > 0:
                label += f" • {hours:02d}:{minutes:02d}:00"
            else:
                label += f" • {minutes:02d}:00"
        
        # Thêm rating vào label
        if vote_average and vote_average > 0:
            label += f" ⭐ {vote_average:.1f}"
        log(f"[VietmediaF] TMDB Item: Label = {label}")
        
        # Tạo path để gọi backend API
        path = f"plugin://plugin.video.vietmediaF?action=_tmdbsearch_sources&media_type={quote_plus(media_type)}&tmdb_id={quote_plus(str(tmdb_id))}"
        
        # Tạo info với nhiều thông tin hơn theo chuẩn Kodi (chỉ dùng key an toàn)
        info = {
            'plot': overview,
            'title': title,
            'originaltitle': original_title,
            'year': int(year) if year else 0,
            'rating': float(vote_average) if vote_average else 0,
            'votes': int(item.get('vote_count', 0) or 0),
            'mediatype': 'movie' if media_type == 'movie' else 'tvshow',
            'duration': (int(runtime) * 60) if runtime and int(runtime) > 0 else 0,
            'premiered': release_date or '',
            'uniqueids': {'tmdb': str(tmdb_id)}
        }
        
        # TV show: chỉ thêm tvshowtitle an toàn
        if media_type == 'tv':
            info.update({
                'tvshowtitle': title
            })
        
        return {
            'label': label,
            'is_playable': False,
            'path': path,
            'thumbnail': poster_url,
            'icon': poster_url,
            'label2': original_title if original_title and original_title != title else '',
            'info': info,
            'art': {
                'poster': poster_url,
                'fanart': backdrop_url or poster_url,
                'landscape': backdrop_url or poster_url
            }
        }
    except Exception as e:
        logError(f"[VietmediaF] TMDB Item: Lỗi tạo item: {str(e)}")
        # Trả về item đơn giản nếu có lỗi
        return {
            'label': f"Lỗi: {str(e)}",
            'is_playable': False,
            'path': '',
            'thumbnail': '',
            'icon': '',
            'label2': '',
            'info': {'plot': f"Lỗi khi tạo item: {str(e)}"},
            'art': {}
        }

def create_source_item(source, tmdb_id, media_type):
    """Tạo item từ backend source data"""
    uploader = source.get('uploader', 'Unknown')
    sheet_name = source.get('sheet_name', '')
    size = source.get('size', '')
    download_url = source.get('download_url', '')
    vmf_code = source.get('vmf_code', '')
    
    # Tạo label
    label = f"📁 {uploader}"
    if sheet_name:
        label += f" - {sheet_name}"
    if size:
        label += f" ({size})"
    
    # Tạo path để play
    if download_url:
        path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
        # Kiểm tra nếu là folder thì không playable
        playable = '/folder/' not in download_url
    elif vmf_code:
        path = f"plugin://plugin.video.vietmediaF?action=_tmdbsearch_vmf&vmf_code={vmf_code}"
        playable = True
    else:
        path = ""
        playable = False
    
    return {
        'label': label,
        'is_playable': playable,
        'path': path,
        'thumbnail': '',
        'icon': '',
        'label2': '',
        'info': {
            'plot': f"Uploader: {uploader}\nSheet: {sheet_name}\nSize: {size}" if size else f"Uploader: {uploader}\nSheet: {sheet_name}"
        }
    }


def tmdb_search(query=None):
    """Hàm chính để tìm kiếm TMDB"""
    if not query:
        # Hiển thị dialog nhập từ khóa
        keyboard = xbmc.Keyboard("", "Nhập tên phim/TV show để tìm kiếm")
        keyboard.doModal()
        
        if not keyboard.isConfirmed() or not keyboard.getText():
            notify("Đã hủy tìm kiếm")
            return {"content_type": "movies", "items": []}
        
        query = keyboard.getText().strip()
    
    if not query:
        notify("Vui lòng nhập từ khóa tìm kiếm")
        return {"content_type": "movies", "items": []}
    
    # Hiển thị progress dialog
    progress = xbmcgui.DialogProgress()
    progress.create("Tìm kiếm TMDB", f"Đang tìm kiếm: {query}")
    progress.update(50)
    
    # Tìm kiếm trên TMDB
    results = search_tmdb(query)
    
    progress.close()
    
    if not results:
        notify("Không tìm thấy kết quả nào")
        return {"content_type": "movies", "items": []}
    
    # Tạo danh sách items
    items = []
    for item in results:  # Hiển thị tất cả kết quả
        try:
            items.append(create_tmdb_item(item))
        except Exception as e:
            logError(f"[VietmediaF] TMDB Search: Lỗi tạo item: {str(e)}")
            continue
    
    log(f"[VietmediaF] TMDB Search: Tạo được {len(items)} items từ {len(results)} kết quả")
    
    return {
        "content_type": "movies",
        "items": items
    }

def tmdb_search_sources(media_type, tmdb_id):
    """Lấy danh sách nguồn từ backend cho một phim/TV show"""
    try:
        log(f"[VietmediaF] TMDB Sources: Bắt đầu lấy nguồn cho {media_type} {tmdb_id}")
        
        # Hiển thị progress dialog
        progress = xbmcgui.DialogProgress()
        progress.create("Tải nguồn", f"Đang tải nguồn cho {media_type} {tmdb_id}")
        progress.update(50)
        
        # Gọi backend API
        log(f"[VietmediaF] TMDB Sources: Gọi get_backend_sources({media_type}, {tmdb_id})")
        data = get_backend_sources(media_type, tmdb_id)
        
        progress.close()
        
        if not data or not data.get('sources'):
            log(f"[VietmediaF] TMDB Sources: Không tìm thấy nguồn cho {media_type} {tmdb_id}")
            notify("Không tìm thấy nguồn nào")
            return {"content_type": "files", "items": []}
        
        # Tạo danh sách items
        items = []
        for source in data['sources']:
            items.append(create_source_item(source, tmdb_id, media_type))
        
        log(f"[VietmediaF] TMDB Sources: Tạo được {len(items)} items cho {media_type} {tmdb_id}")
        return {
            "content_type": "files", 
            "items": items
        }
    except Exception as e:
        logError(f"[VietmediaF] TMDB Sources: Lỗi khi lấy nguồn cho {media_type} {tmdb_id}: {e}")
        notify(f"Lỗi khi lấy nguồn: {str(e)}")
        return {"content_type": "files", "items": []}
