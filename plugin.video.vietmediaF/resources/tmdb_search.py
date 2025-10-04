#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import xbmcaddon
import xbmcgui
import xbmc
import xbmcplugin
import requests
import json
import urllib.parse
from .addon import ADDON, ADDON_NAME, notify, alert, logError
from .history_utils import HistoryManager

# TMDB Search sử dụng List View đơn giản

# Khởi tạo HistoryManager cho TMDB search
try:
    tmdb_search_history = HistoryManager('tmdb_search.dat')
    xbmc.log(f"[VietmediaF] TMDB search history manager initialized successfully", xbmc.LOGINFO)
except Exception as e:
    xbmc.log(f"[VietmediaF] Error initializing TMDB search history manager: {str(e)}", xbmc.LOGERROR)
    tmdb_search_history = None

def get_tmdb_search_history():
    """Lấy lịch sử tìm kiếm TMDB"""
    if tmdb_search_history is None:
        xbmc.log(f"[VietmediaF] TMDB search history manager is None", xbmc.LOGERROR)
        return []
    history = tmdb_search_history.get_history()
    xbmc.log(f"[VietmediaF] Getting TMDB search history: {history}", xbmc.LOGINFO)
    return history

def save_tmdb_search_history(query):
    """Lưu từ khóa tìm kiếm TMDB vào lịch sử"""
    if tmdb_search_history is None:
        xbmc.log(f"[VietmediaF] TMDB search history manager is None, cannot save", xbmc.LOGERROR)
        return
    xbmc.log(f"[VietmediaF] Saving TMDB search history: {query}", xbmc.LOGINFO)
    tmdb_search_history.save_history(query)

def delete_tmdb_search_history():
    """Xóa lịch sử tìm kiếm TMDB"""
    if tmdb_search_history is None:
        xbmc.log(f"[VietmediaF] TMDB search history manager is None, cannot delete", xbmc.LOGERROR)
        return
    tmdb_search_history.delete_history()

def check_tmdb_search_history():
    """Kiểm tra xem có lịch sử tìm kiếm TMDB không"""
    if tmdb_search_history is None:
        return False
    return tmdb_search_history.check_history()

def set_list_view():
    """
    Thiết lập view mode list cho TMDB search results
    """
    try:
        # Kiểm tra setting có bật list view không
        if ADDON.getSettingBool('tmdb_list_view'):
            xbmc.log(f"[VietmediaF] Setting list view mode for TMDB search", xbmc.LOGINFO)
            xbmc.executebuiltin("Container.SetViewMode(50)")
        else:
            xbmc.log(f"[VietmediaF] List view disabled for TMDB search", xbmc.LOGINFO)
            
    except Exception as e:
        xbmc.log(f"[VietmediaF] Error setting list view: {str(e)}", xbmc.LOGERROR)

# TMDB API Configuration - sẽ được lấy từ settings
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def get_tmdb_api_key():
    """Lấy TMDB API key từ settings"""
    return ADDON.getSetting('tmdb_api_key') or "YOUR_TMDB_API_KEY_HERE"

def get_tmdb_language():
    """Lấy ngôn ngữ TMDB từ settings"""
    return ADDON.getSetting('tmdb_language') or "vi-VN"

def get_tmdb_timeout():
    """Lấy timeout TMDB từ settings"""
    return int(ADDON.getSetting('tmdb_timeout') or "10")

# Backend API Configuration - sẽ được lấy từ settings

def check_backend_cache(tmdb_id, media_type):
    """
    Kiểm tra cache trong backend API
    
    Args:
        tmdb_id (int): ID của phim/TV trên TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        tuple: (is_cached, error_message) - True nếu có trong cache, False nếu cache miss, None nếu lỗi
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        backend_enabled = ADDON.getSettingBool('backend_api_enabled')
        xbmc.log(f"[VietmediaF] Backend API enabled: {backend_enabled}", xbmc.LOGINFO)
        
        if not backend_enabled:
            xbmc.log(f"[VietmediaF] Backend API disabled, skipping cache check for {media_type} {tmdb_id}", xbmc.LOGINFO)
            return True, None  # Nếu không bật, mặc định hiển thị tất cả
        
        # Lấy cấu hình từ settings
        backend_url = ADDON.getSetting('backend_api_url')
        if not backend_url:
            backend_url = "https://bioidaika.click"
        
        timeout = int(ADDON.getSetting('backend_api_timeout') or "3")
        
        # Tạo URL endpoint cho backend API theo cấu trúc thực tế
        endpoint = f"{backend_url}/api/{media_type}/{tmdb_id}"
        
        xbmc.log(f"[VietmediaF] Calling Backend API: {endpoint}", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] Backend URL: {backend_url}, Timeout: {timeout}s", xbmc.LOGINFO)
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json'
        }
        
        # Gọi API với timeout từ settings
        xbmc.log(f"[VietmediaF] Making request to Backend API...", xbmc.LOGINFO)
        response = requests.get(endpoint, headers=headers, timeout=timeout)
        xbmc.log(f"[VietmediaF] Backend API response: {response.status_code}", xbmc.LOGINFO)
        
        if response.status_code == 200:
            result = response.json()
            # Kiểm tra xem có sources không (có nghĩa là có trong cache)
            sources = result.get("sources", [])
            if sources and len(sources) > 0:
                # Kiểm tra xem có source nào có download_url không
                for source in sources:
                    if source.get("download_url") and source.get("download_url") != "None":
                        xbmc.log(f"[VietmediaF] Cache hit for {media_type} {tmdb_id}: {len(sources)} sources found", xbmc.LOGINFO)
                        return True, None
                # Nếu có sources nhưng không có download_url hợp lệ
                xbmc.log(f"[VietmediaF] Cache miss for {media_type} {tmdb_id}: sources found but no valid download_url", xbmc.LOGINFO)
                return False, None
            else:
                # Không có sources
                xbmc.log(f"[VietmediaF] Cache miss for {media_type} {tmdb_id}: no sources found", xbmc.LOGINFO)
                return False, None
        else:
            # Nếu API lỗi, báo lỗi
            error_msg = f"Backend API lỗi: {response.status_code}"
            xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
            return None, error_msg
            
    except requests.exceptions.Timeout:
        # Timeout - báo lỗi
        error_msg = f"Backend API timeout sau {timeout} giây"
        xbmc.log(f"[VietmediaF] {error_msg} for TMDB ID {tmdb_id}", xbmc.LOGERROR)
        return None, error_msg
    except requests.exceptions.ConnectionError:
        # Không kết nối được - báo lỗi
        error_msg = f"Không thể kết nối đến Backend API: {backend_url}"
        xbmc.log(f"[VietmediaF] {error_msg} for TMDB ID {tmdb_id}", xbmc.LOGERROR)
        return None, error_msg
    except Exception as e:
        # Lỗi khác - báo lỗi
        error_msg = f"Lỗi Backend API: {str(e)}"
        xbmc.log(f"[VietmediaF] {error_msg} for TMDB ID {tmdb_id}", xbmc.LOGERROR)
        return None, error_msg

def get_backend_download_info(tmdb_id, media_type):
    """
    Lấy thông tin download từ backend API
    
    Args:
        tmdb_id (int): ID của phim/TV trên TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        dict: Thông tin download hoặc None nếu không có
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        if not ADDON.getSettingBool('backend_api_enabled'):
            return None
        
        # Lấy cấu hình từ settings
        backend_url = ADDON.getSetting('backend_api_url')
        if not backend_url:
            backend_url = "https://bioidaika.click"
        
        timeout = int(ADDON.getSetting('backend_api_timeout') or "3")
        
        # Tạo URL endpoint cho backend API
        endpoint = f"{backend_url}/api/{media_type}/{tmdb_id}"
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json'
        }
        
        # Gọi API với timeout từ settings
        response = requests.get(endpoint, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            sources = result.get("sources", [])
            if sources and len(sources) > 0:
                # Tìm source có download_url hợp lệ
                for source in sources:
                    if source.get("download_url") and source.get("download_url") != "None":
                        return {
                            "tmdb_id": tmdb_id,
                            "media_type": media_type,
                            "sources": sources,
                            "best_source": source  # Source tốt nhất
                        }
            return None
        else:
            xbmc.log(f"[VietmediaF] Backend API error for download info: {response.status_code}", xbmc.LOGWARNING)
            return None
            
    except Exception as e:
        xbmc.log(f"[VietmediaF] Error getting download info for TMDB ID {tmdb_id}: {str(e)}", xbmc.LOGERROR)
        return None

def display_movie_detail(movie_data, media_type, tmdb_id, download_info=None):
    """
    Hiển thị thông tin chi tiết phim/TV với danh sách nguồn download
    
    Args:
        movie_data (dict): Dữ liệu phim/TV từ TMDB
        media_type (str): Loại media (movie hoặc tv)
        tmdb_id (int): ID TMDB
        download_info (dict): Thông tin download từ backend API
    """
    try:
        # Thiết lập content type cho Kodi
        content_type = "movies" if media_type == "movie" else "tvshows"
        xbmcplugin.setContent(int(sys.argv[1]), content_type)
        
        # Thêm các phương thức sắp xếp
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
        
        items = []
        
        # Tạo các item nguồn download nếu có
        if download_info and download_info.get("sources"):
            sources = download_info["sources"]
            
            for i, source in enumerate(sources, 1):
                uploader = source.get("uploader", "Unknown")
                sheet_name = source.get("sheet_name", "Unknown")
                download_url = source.get("download_url", "")
                vmf_code = source.get("vmf_code", "")
                size = source.get("size", "N/A")
                
                if download_url and download_url != "None":
                    # Xác định loại URL (folder hoặc file)
                    is_folder = download_url.endswith('/') or 'folder' in download_url.lower()
                    
                    # Tạo label2 cho nguồn với format mới
                    source_label2 = f"{uploader} | {sheet_name} | Size: {size}"
                    
                    # Tạo action URL cho nguồn - sử dụng action browse cho folder, play cho file
                    if is_folder:
                        action_path = f"plugin://plugin.video.vietmediaF?action=browse&url={download_url}"
                        is_playable = False  # Folder không playable
                    else:
                        action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
                        is_playable = True  # File playable
                    
                    # Tạo item nguồn với thông tin phim ở bên trái
                    source_item = {
                        "label": source_label2,
                        "is_playable": is_playable,
                        "path": action_path,
                        "thumbnail": movie_data.get("poster_path", ""),
                        "fanart": movie_data.get("backdrop_path", ""),
                        "label2": source_label2,
                        "info": {
                            "title": f"{uploader} | {sheet_name} | Size: {size}",
                            "plot": movie_data.get("overview", ""),
                            "year": movie_data.get("release_date", movie_data.get("first_air_date", "")).split("-")[0] if movie_data.get("release_date") or movie_data.get("first_air_date") else "",
                            "rating": movie_data.get("vote_average", 0),
                            "votes": movie_data.get("vote_count", 0),
                            "genre": ", ".join([genre.get("name", "") for genre in movie_data.get("genres", [])]),
                            "mediatype": "movie" if media_type == "movie" else "tvshow"
                        },
                        "art": {
                            "poster": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get("poster_path") else "",
                            "fanart": f"https://image.tmdb.org/t/p/w1280{movie_data.get('backdrop_path', '')}" if movie_data.get("backdrop_path") else "",
                            "thumb": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get("poster_path") else ""
                        },
                        "properties": {
                            "tmdb_id": str(tmdb_id),
                            "media_type": media_type,
                            "uploader": uploader,
                            "sheet_name": sheet_name,
                            "size": size,
                            "vmf_code": vmf_code,
                            "download_url": download_url,
                            "is_folder": str(is_folder).lower()
                        }
                    }
                    items.append(source_item)
        
        # Hiển thị kết quả
        if items:
            for item in items:
                # Tạo ListItem với label an toàn
                label = item.get("label", "Unknown")
                if not isinstance(label, str):
                    label = str(label)
                list_item = xbmcgui.ListItem(label=label)
                
                # Set artwork từ movie_data
                art_dict = {}
                if "art" in item and item["art"]:
                    try:
                        basic_art = ["poster", "fanart", "thumb", "banner", "landscape"]
                        for key, value in item["art"].items():
                            if value and key in basic_art:
                                if not isinstance(key, str):
                                    key = str(key)
                                if not isinstance(value, str):
                                    value = str(value)
                                art_dict[key] = value
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                if art_dict:
                    try:
                        list_item.setArt(art_dict)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set label2
                if "label2" in item and item["label2"]:
                    try:
                        label2 = item["label2"]
                        if not isinstance(label2, str):
                            label2 = str(label2)
                        list_item.setProperty("Label2", label2)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set info
                if "info" in item:
                    try:
                        info_tag = list_item.getVideoInfoTag()
                        
                        if "title" in item["info"] and item["info"]["title"]:
                            try:
                                info_tag.setTitle(item["info"]["title"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "plot" in item["info"] and item["info"]["plot"]:
                            try:
                                info_tag.setPlot(item["info"]["plot"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "mediatype" in item["info"] and item["info"]["mediatype"]:
                            try:
                                info_tag.setMediaType(item["info"]["mediatype"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set properties
                if "properties" in item:
                    for key, value in item["properties"].items():
                        try:
                            if not isinstance(key, str):
                                key = str(key)
                            if not isinstance(value, str):
                                value = str(value)
                            list_item.setProperty(key, value)
                        except (ValueError, TypeError, AttributeError):
                            pass
                
                # Set isPlayable
                if "is_playable" in item:
                    try:
                        is_playable = item["is_playable"]
                        if not isinstance(is_playable, bool):
                            is_playable = bool(is_playable)
                        list_item.setProperty("IsPlayable", str(is_playable).lower())
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set path
                if "path" in item and item["path"]:
                    try:
                        path = item["path"]
                        if not isinstance(path, str):
                            path = str(path)
                        list_item.setProperty("Path", path)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                xbmcplugin.addDirectoryItem(
                    handle=int(sys.argv[1]),
                    url=item.get("path", ""),
                    listitem=list_item,
                    isFolder=not item.get("is_playable", False)
                )
            
            # Thiết lập list view
            set_list_view()
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            notify("Không có thông tin chi tiết")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error displaying movie detail: {str(e)}")
        alert(f"Lỗi hiển thị chi tiết: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def filter_cached_results(movies_data, tv_data):
    """
    Lọc kết quả chỉ hiển thị những item có trong cache backend
    
    Args:
        movies_data (dict): Dữ liệu phim từ TMDB
        tv_data (dict): Dữ liệu TV series từ TMDB
    
    Returns:
        tuple: (filtered_movies_data, filtered_tv_data, error_message)
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        backend_enabled = ADDON.getSettingBool('backend_api_enabled')
        xbmc.log(f"[VietmediaF] Filtering cached results - Backend API enabled: {backend_enabled}", xbmc.LOGINFO)
        
        if not backend_enabled:
            xbmc.log(f"[VietmediaF] Backend API disabled, returning all results without filtering", xbmc.LOGINFO)
            return movies_data, tv_data, None  # Nếu không bật, trả về dữ liệu gốc
        
        filtered_movies = None
        filtered_tv = None
        total_checked = 0
        total_cached = 0
        errors = []
        
        # Lọc phim
        if movies_data and movies_data.get('results'):
            xbmc.log(f"[VietmediaF] Filtering {len(movies_data['results'])} movies", xbmc.LOGINFO)
            cached_movies = []
            for movie in movies_data['results']:
                tmdb_id = movie.get('id')
                total_checked += 1
                if tmdb_id:
                    xbmc.log(f"[VietmediaF] Checking cache for movie ID {tmdb_id}: {movie.get('title', 'Unknown')}", xbmc.LOGINFO)
                    is_cached, error = check_backend_cache(tmdb_id, "movie")
                    if is_cached is True:
                        cached_movies.append(movie)
                        total_cached += 1
                        xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} CACHE HIT", xbmc.LOGINFO)
                    elif is_cached is False:
                        xbmc.log(f"[VietmediaF] Movie TMDB ID {tmdb_id} CACHE MISS, hiding", xbmc.LOGINFO)
                    else:  # is_cached is None (có lỗi)
                        if error:
                            errors.append(f"Phim ID {tmdb_id}: {error}")
                        # Nếu có lỗi, vẫn hiển thị phim để không làm mất kết quả
                        cached_movies.append(movie)
                        total_cached += 1
                        xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} ERROR, showing anyway", xbmc.LOGINFO)
            
            if cached_movies:
                filtered_movies = movies_data.copy()
                filtered_movies['results'] = cached_movies
                filtered_movies['total_results'] = len(cached_movies)
        
        # Lọc TV series
        if tv_data and tv_data.get('results'):
            cached_tv = []
            for tv in tv_data['results']:
                tmdb_id = tv.get('id')
                total_checked += 1
                if tmdb_id:
                    is_cached, error = check_backend_cache(tmdb_id, "tv")
                    if is_cached is True:
                        cached_tv.append(tv)
                        total_cached += 1
                    elif is_cached is False:
                        xbmc.log(f"[VietmediaF] TV TMDB ID {tmdb_id} not in cache, hiding", xbmc.LOGINFO)
                    else:  # is_cached is None (có lỗi)
                        if error:
                            errors.append(f"TV ID {tmdb_id}: {error}")
                        # Nếu có lỗi, vẫn hiển thị TV để không làm mất kết quả
                        cached_tv.append(tv)
                        total_cached += 1
            
            if cached_tv:
                filtered_tv = tv_data.copy()
                filtered_tv['results'] = cached_tv
                filtered_tv['total_results'] = len(cached_tv)
        
        # Log thống kê
        xbmc.log(f"[VietmediaF] Cache check completed: {total_cached}/{total_checked} items cached", xbmc.LOGINFO)
        
        # Tạo thông báo lỗi nếu có
        error_message = None
        if errors:
            error_message = f"Backend API có lỗi:\n" + "\n".join(errors[:3])  # Chỉ hiển thị 3 lỗi đầu
            if len(errors) > 3:
                error_message += f"\n... và {len(errors) - 3} lỗi khác"
        
        return filtered_movies, filtered_tv, error_message
        
    except Exception as e:
        error_msg = f"Lỗi khi kiểm tra cache: {str(e)}"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        # Nếu có lỗi, trả về dữ liệu gốc
        return movies_data, tv_data, error_msg

def search_movies(query, page=1):
    """
    Tìm kiếm phim trên TMDB API
    
    Args:
        query (str): Từ khóa tìm kiếm
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim từ TMDB API
    """
    try:
        # Lấy API key từ settings
        api_key = get_tmdb_api_key()
        if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
            logError("TMDB API key chưa được cấu hình đúng")
            return None
            
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {
            'api_key': api_key,
            'query': query,
            'page': page,
            'language': get_tmdb_language(),
            'include_adult': 'false'
        }
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=get_tmdb_timeout())
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            logError("TMDB API key không hợp lệ. Vui lòng cấu hình API key thực tế.")
            return None
        else:
            logError(f"TMDB API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logError(f"Error searching movies: {str(e)}")
        return None

def search_tv_shows(query, page=1):
    """
    Tìm kiếm TV series trên TMDB API
    
    Args:
        query (str): Từ khóa tìm kiếm
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu TV series từ TMDB API
    """
    try:
        # Lấy API key từ settings
        api_key = get_tmdb_api_key()
        if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
            logError("TMDB API key chưa được cấu hình đúng")
            return None
            
        url = f"{TMDB_BASE_URL}/search/tv"
        params = {
            'api_key': api_key,
            'query': query,
            'page': page,
            'language': get_tmdb_language(),
            'include_adult': 'false'
        }
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=get_tmdb_timeout())
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            logError("TMDB API key không hợp lệ. Vui lòng cấu hình API key thực tế.")
            return None
        else:
            logError(f"TMDB API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logError(f"Error searching TV shows: {str(e)}")
        return None

def get_poster_url(poster_path, size="w500"):
    """
    Lấy URL poster đầy đủ từ TMDB với kích thước tùy chỉnh
    
    Args:
        poster_path (str): Đường dẫn poster từ TMDB
        size (str): Kích thước ảnh (w92, w154, w185, w342, w500, w780, original)
    
    Returns:
        str: URL poster đầy đủ
    """
    if poster_path:
        return f"https://image.tmdb.org/t/p/{size}{poster_path}"
    return ""

def get_language_name(lang_code):
    """
    Chuyển đổi mã ngôn ngữ thành tên ngôn ngữ
    
    Args:
        lang_code (str): Mã ngôn ngữ (vi, en, ja, ko, etc.)
    
    Returns:
        str: Tên ngôn ngữ
    """
    languages = {
        'vi': 'Tiếng Việt',
        'en': 'English',
        'ja': '日本語',
        'ko': '한국어',
        'zh': '中文',
        'fr': 'Français',
        'de': 'Deutsch',
        'es': 'Español',
        'it': 'Italiano',
        'pt': 'Português',
        'ru': 'Русский',
        'th': 'ไทย',
        'hi': 'हिन्दी',
        'ar': 'العربية'
    }
    return languages.get(lang_code, lang_code.upper())

def get_country_from_language(lang_code):
    """
    Lấy tên quốc gia từ mã ngôn ngữ
    
    Args:
        lang_code (str): Mã ngôn ngữ
    
    Returns:
        str: Tên quốc gia
    """
    countries = {
        'vi': 'Vietnam',
        'en': 'United States',
        'ja': 'Japan',
        'ko': 'South Korea',
        'zh': 'China',
        'fr': 'France',
        'de': 'Germany',
        'es': 'Spain',
        'it': 'Italy',
        'pt': 'Portugal',
        'ru': 'Russia',
        'th': 'Thailand',
        'hi': 'India',
        'ar': 'Saudi Arabia'
    }
    return countries.get(lang_code, 'Unknown')

def get_genre_names(genre_ids):
    """
    Chuyển đổi genre IDs thành tên thể loại
    
    Args:
        genre_ids (list): Danh sách genre IDs
    
    Returns:
        str: Tên thể loại phân cách bằng dấu phẩy
    """
    genre_map = {
        28: 'Hành động',
        12: 'Phiêu lưu',
        16: 'Hoạt hình',
        35: 'Hài',
        80: 'Tội phạm',
        99: 'Tài liệu',
        18: 'Drama',
        10751: 'Gia đình',
        14: 'Fantasy',
        36: 'Lịch sử',
        27: 'Kinh dị',
        10402: 'Âm nhạc',
        9648: 'Bí ẩn',
        10749: 'Lãng mạn',
        878: 'Khoa học viễn tưởng',
        10770: 'TV Movie',
        53: 'Thriller',
        10752: 'Chiến tranh',
        37: 'Miền Tây'
    }
    
    genres = []
    for genre_id in genre_ids:
        if genre_id in genre_map:
            genres.append(genre_map[genre_id])
    
    return ', '.join(genres) if genres else 'Unknown'


def format_release_date(release_date):
    """
    Định dạng ngày phát hành
    
    Args:
        release_date (str): Ngày phát hành từ TMDB
    
    Returns:
        str: Ngày phát hành đã định dạng
    """
    if release_date:
        try:
            from datetime import datetime
            date_obj = datetime.strptime(release_date, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return release_date
    return "N/A"

def create_movie_item(movie, media_type="movie"):
    """
    Tạo item phim cho Kodi với metadata đầy đủ từ TMDB
    
    Args:
        movie (dict): Dữ liệu phim từ TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        dict: Item phim cho Kodi
    """
    try:
        # Lấy thông tin cơ bản
        title = movie.get('title', 'Unknown Title')
        original_title = movie.get('original_title', '')
        if media_type == "tv":
            title = movie.get('name', 'Unknown Title')
            original_title = movie.get('original_name', '')
            
        overview = movie.get('overview', 'Không có mô tả')
        poster_path = movie.get('poster_path', '')
        backdrop_path = movie.get('backdrop_path', '')
        release_date = movie.get('release_date', '')
        if media_type == "tv":
            release_date = movie.get('first_air_date', '')
            
        vote_average = movie.get('vote_average', 0)
        vote_count = movie.get('vote_count', 0)
        popularity = movie.get('popularity', 0)
        genre_ids = movie.get('genre_ids', [])
        adult = movie.get('adult', False)
        original_language = movie.get('original_language', '')
        tmdb_id = movie.get('id', 0)
        
        # Tạo URL poster với chất lượng cao
        poster_url = get_poster_url(poster_path, size="w500")
        backdrop_url = get_poster_url(backdrop_path, size="w1280")
        
        # Tạo label với màu sắc và thông tin bổ sung
        release_year = release_date[:4] if release_date and len(release_date) >= 4 else ""
        
        # Tạo label chính với màu sắc và format đẹp như giao diện Kodi
        rating_text = f"[COLOR yellow]{vote_average:.1f}[/COLOR]" if vote_average and vote_average > 0 else ""
        popularity_text = f"[COLOR orange]{popularity:.0f}[/COLOR]" if popularity and popularity > 0 else ""
        adult_text = "[COLOR red]18+[/COLOR]" if adult else ""
        
        # Tạo label với format đẹp như giao diện Kodi
        if media_type == "movie":
            # Format: "Tên phim - Tên gốc - (Năm) | Rating | Popularity | Adult"
            if original_title and original_title != title:
                label = f"[COLOR white]{title}[/COLOR] - [COLOR lightgray]{original_title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"
            else:
                label = f"[COLOR white]{title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"
        else:
            # Format: "Tên TV - Tên gốc - (Năm) | Rating | Popularity | Adult"
            if original_title and original_title != title:
                label = f"[COLOR lightblue]{title}[/COLOR] - [COLOR lightgray]{original_title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"
            else:
                label = f"[COLOR lightblue]{title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"
        
        # Tạo plot với thông tin chi tiết và màu sắc cho cột trái
        plot_parts = []
        
        # Thông tin cơ bản - Tóm tắt phim
        if overview:
            plot_parts.append(f"[COLOR white]Tóm tắt:[/COLOR]\n[COLOR lightgray]{overview}[/COLOR]")
        
        # Thông tin đánh giá và phổ biến
        if vote_count and vote_count > 0:
            plot_parts.append(f"[COLOR yellow]Đánh giá:[/COLOR] [COLOR white]{vote_average:.1f}/10[/COLOR] [COLOR gray]({vote_count:,} lượt đánh giá)[/COLOR]")
        
        if popularity and popularity > 0:
            plot_parts.append(f"[COLOR orange]Độ phổ biến:[/COLOR] [COLOR white]{popularity:.0f}[/COLOR]")
        
        # Thông tin ngày phát hành
        if release_date:
            formatted_date = format_release_date(release_date)
            plot_parts.append(f"[COLOR lightblue]Ngày phát hành:[/COLOR] [COLOR white]{formatted_date}[/COLOR]")
        
        # Thông tin ngôn ngữ và quốc gia
        if original_language:
            lang_name = get_language_name(original_language)
            country_name = get_country_from_language(original_language)
            plot_parts.append(f"[COLOR lightgreen]Ngôn ngữ:[/COLOR] [COLOR white]{lang_name}[/COLOR]")
            plot_parts.append(f"[COLOR lightgreen]Quốc gia:[/COLOR] [COLOR white]{country_name}[/COLOR]")
        
        # Thông tin thể loại
        if genre_ids:
            genre_names = get_genre_names(genre_ids)
            plot_parts.append(f"[COLOR purple]Thể loại:[/COLOR] [COLOR white]{genre_names}[/COLOR]")
        
        # Thông tin ID TMDB
        plot_parts.append(f"[COLOR gray]TMDB ID:[/COLOR] [COLOR white]{tmdb_id}[/COLOR]")
        
        plot = "\n\n".join(plot_parts) if plot_parts else "Không có thông tin chi tiết"
        
        # Tạo path cho action
        action_path = f"plugin://plugin.video.vietmediaF?action=tmdb_movie_detail&tmdb_id={tmdb_id}&media_type={media_type}"
        
        # Tạo item với metadata đầy đủ và artwork tối ưu cho layout 3 cột
        item = {
            "label": label,
            "is_playable": False,
            "path": action_path,
            "thumbnail": poster_url,  # Ảnh bên phải
            "fanart": backdrop_url,   # Background
            "label2": f"TMDB ID: {tmdb_id}" if tmdb_id else "",
            "info": {
                "title": title,
                "originaltitle": original_title,
                "plot": plot,
                "plotoutline": overview[:200] + "..." if len(overview) > 200 else overview,
                "year": int(release_year) if release_year and release_year.isdigit() else 0,
                "rating": float(vote_average) if vote_average else 0.0,
                "votes": int(vote_count) if vote_count else 0,
                "popularity": float(popularity) if popularity else 0.0,
                "mediatype": "movie" if media_type == "movie" else "tvshow",
                "genre": get_genre_names(genre_ids),
                "country": get_country_from_language(original_language),
                "language": original_language,
                "adult": adult,
                "tmdb_id": tmdb_id,
                "premiered": release_date,
                "status": "Released" if media_type == "movie" else "Continuing",
                # Thêm thông tin chi tiết cho cột trái
                "director": "N/A",  # Sẽ được cập nhật nếu có
                "writer": "N/A",    # Sẽ được cập nhật nếu có
                "studio": "N/A",    # Sẽ được cập nhật nếu có
                "mpaa": "N/A",      # Sẽ được cập nhật nếu có
                "tagline": overview[:100] + "..." if len(overview) > 100 else overview,
                # Thêm thông tin bổ sung cho giao diện đẹp
                "duration": "N/A",  # Sẽ được cập nhật nếu có
                "episode": 1 if media_type == "tv" else 0,
                "season": 1 if media_type == "tv" else 0,
                "aired": release_date if media_type == "tv" else "",
                "dateadded": release_date,
                "lastplayed": "",
                "playcount": 0,
                "userrating": float(vote_average) if vote_average else 0.0
            },
            "art": {
                "poster": poster_url,        # Ảnh poster chính (cột phải)
                "fanart": backdrop_url,      # Background
                "thumb": poster_url,         # Thumbnail
                "banner": poster_url,        # Banner
                "landscape": backdrop_url    # Landscape
            },
            "properties": {
                "tmdb_id": str(tmdb_id) if tmdb_id else "0",
                "media_type": media_type,
                "vote_average": str(vote_average) if vote_average else "0",
                "vote_count": str(vote_count) if vote_count else "0",
                "popularity": str(popularity) if popularity else "0",
                # Thêm properties cho layout tối ưu
                "Fanart_Image": backdrop_url,
                "Poster_Image": poster_url,
                "Thumbnail_Image": poster_url,
                "Banner_Image": poster_url,
                "Landscape_Image": backdrop_url
            }
        }
        
        return item
        
    except Exception as e:
        logError(f"Error creating movie item: {str(e)}")
        return None

def display_search_results(movies_data, tv_data, query, page=1):
    """
    Hiển thị kết quả tìm kiếm trên Kodi
    
    Args:
        movies_data (dict): Dữ liệu phim từ TMDB
        tv_data (dict): Dữ liệu TV series từ TMDB
        query (str): Từ khóa tìm kiếm
        page (int): Trang hiện tại
    """
    try:
        # Thiết lập content type cho Kodi
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        
        # Thêm các phương thức sắp xếp
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
        
        items = []
        
        # Bỏ header kết quả tìm kiếm để giao diện gọn gàng hơn
        
        # Thêm phim trực tiếp không có header
        if movies_data and movies_data.get('results'):
            
            for i, movie in enumerate(movies_data['results'][:10], 1):  # Giới hạn 10 phim
                movie_item = create_movie_item(movie, "movie")
                if movie_item:
                    # Thêm số thứ tự vào label
                    movie_item["label"] = f"[COLOR gray]{i:2d}.[/COLOR] {movie_item['label']}"
                    items.append(movie_item)
        
        # Thêm TV series trực tiếp không có header
        if tv_data and tv_data.get('results'):
            
            for i, tv in enumerate(tv_data['results'][:10], 1):  # Giới hạn 10 TV series
                tv_item = create_movie_item(tv, "tv")
                if tv_item:
                    # Thêm số thứ tự vào label
                    tv_item["label"] = f"[COLOR gray]{i:2d}.[/COLOR] {tv_item['label']}"
                    items.append(tv_item)
        
        # Bỏ tất cả header và tùy chọn để giao diện gọn gàng
        
        # Hiển thị kết quả với metadata đầy đủ
        if items:
            for item in items:
                # Tạo ListItem với label an toàn
                label = item.get("label", "Unknown")
                if not isinstance(label, str):
                    label = str(label)
                list_item = xbmcgui.ListItem(label=label)
                
                # Set artwork tối ưu cho layout 3 cột (trái: thông tin, giữa: label, phải: poster)
                art_dict = {}
                
                # Thêm poster cho cột phải (thumbnail chính)
                if "thumbnail" in item and item["thumbnail"]:
                    try:
                        thumbnail = item["thumbnail"]
                        if not isinstance(thumbnail, str):
                            thumbnail = str(thumbnail)
                        art_dict["thumb"] = thumbnail  # Thumbnail chính (cột phải)
                        art_dict["poster"] = thumbnail  # Poster chính
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Thêm fanart cho background
                if "fanart" in item and item["fanart"]:
                    try:
                        fanart = item["fanart"]
                        if not isinstance(fanart, str):
                            fanart = str(fanart)
                        art_dict['fanart'] = fanart
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Thêm các loại artwork cơ bản cho layout đẹp
                if "art" in item and item["art"]:
                    try:
                        # Chỉ sử dụng các artwork cơ bản mà Kodi hỗ trợ
                        basic_art = ["poster", "fanart", "thumb", "banner", "landscape"]
                        for key, value in item["art"].items():
                            if value and key in basic_art:
                                if not isinstance(key, str):
                                    key = str(key)
                                if not isinstance(value, str):
                                    value = str(value)
                                art_dict[key] = value
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set artwork với tối ưu cho layout 3 cột
                if art_dict:
                    try:
                        list_item.setArt(art_dict)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set label2 nếu có (sử dụng setProperty thay vì setLabel2)
                if "label2" in item and item["label2"]:
                    try:
                        label2 = item["label2"]
                        if not isinstance(label2, str):
                            label2 = str(label2)
                        list_item.setProperty("Label2", label2)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set info với metadata đầy đủ theo chuẩn Kodi
                if "info" in item:
                    try:
                        info_tag = list_item.getVideoInfoTag()
                        
                        # Thông tin cơ bản cho layout 3 cột
                        if "title" in item["info"] and item["info"]["title"]:
                            try:
                                info_tag.setTitle(item["info"]["title"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "originaltitle" in item["info"] and item["info"]["originaltitle"]:
                            try:
                                info_tag.setOriginalTitle(item["info"]["originaltitle"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "year" in item["info"] and item["info"]["year"]:
                            try:
                                info_tag.setYear(item["info"]["year"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "rating" in item["info"] and item["info"]["rating"]:
                            try:
                                info_tag.setRating(item["info"]["rating"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "votes" in item["info"] and item["info"]["votes"]:
                            try:
                                info_tag.setVotes(item["info"]["votes"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "mediatype" in item["info"] and item["info"]["mediatype"]:
                            try:
                                info_tag.setMediaType(item["info"]["mediatype"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "plot" in item["info"] and item["info"]["plot"]:
                            try:
                                info_tag.setPlot(item["info"]["plot"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "plotoutline" in item["info"] and item["info"]["plotoutline"]:
                            try:
                                info_tag.setPlotOutline(item["info"]["plotoutline"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        
                        # Thông tin bổ sung cho cột trái
                        if "director" in item["info"] and item["info"]["director"]:
                            try:
                                info_tag.setDirectors([item["info"]["director"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "writer" in item["info"] and item["info"]["writer"]:
                            try:
                                info_tag.setWriters([item["info"]["writer"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "studio" in item["info"] and item["info"]["studio"]:
                            try:
                                info_tag.setStudios([item["info"]["studio"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "mpaa" in item["info"] and item["info"]["mpaa"]:
                            try:
                                info_tag.setMpaa(item["info"]["mpaa"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "tagline" in item["info"] and item["info"]["tagline"]:
                            try:
                                info_tag.setTagline(item["info"]["tagline"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        
                        # Thông tin bổ sung
                        if "genre" in item["info"] and item["info"]["genre"]:
                            try:
                                if isinstance(item["info"]["genre"], str):
                                    genres = [g.strip() for g in item["info"]["genre"].split(",") if g.strip()]
                                else:
                                    genres = [str(item["info"]["genre"])]
                                if genres:
                                    info_tag.setGenres(genres)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "country" in item["info"] and item["info"]["country"]:
                            try:
                                if isinstance(item["info"]["country"], str):
                                    countries = [c.strip() for c in item["info"]["country"].split(",") if c.strip()]
                                else:
                                    countries = [str(item["info"]["country"])]
                                if countries:
                                    info_tag.setCountries(countries)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "language" in item["info"] and item["info"]["language"]:
                            try:
                                if isinstance(item["info"]["language"], str):
                                    languages = [l.strip() for l in item["info"]["language"].split(",") if l.strip()]
                                else:
                                    languages = [str(item["info"]["language"])]
                                if languages:
                                    info_tag.setLanguages(languages)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "premiered" in item["info"] and item["info"]["premiered"]:
                            try:
                                info_tag.setPremiered(item["info"]["premiered"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "status" in item["info"] and item["info"]["status"]:
                            try:
                                info_tag.setStatus(item["info"]["status"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set properties tối ưu cho layout 3 cột
                if "properties" in item:
                    for key, value in item["properties"].items():
                        try:
                            if not isinstance(key, str):
                                key = str(key)
                            if not isinstance(value, str):
                                value = str(value)
                            list_item.setProperty(key, value)
                        except (ValueError, TypeError, AttributeError):
                            pass
                
                # Set properties đặc biệt cho layout 3 cột
                try:
                    # Properties cho cột phải (poster)
                    if "thumbnail" in item and item["thumbnail"]:
                        list_item.setProperty("ThumbnailImage", item["thumbnail"])
                    if "fanart" in item and item["fanart"]:
                        list_item.setProperty("FanartImage", item["fanart"])
                    
                    # Properties cho cột trái (thông tin)
                    if "info" in item:
                        info = item["info"]
                        if "year" in info and info["year"]:
                            list_item.setProperty("Year", str(info["year"]))
                        if "rating" in info and info["rating"]:
                            list_item.setProperty("Rating", str(info["rating"]))
                        if "votes" in info and info["votes"]:
                            list_item.setProperty("Votes", str(info["votes"]))
                        if "genre" in info and info["genre"]:
                            list_item.setProperty("Genre", str(info["genre"]))
                        if "country" in info and info["country"]:
                            list_item.setProperty("Country", str(info["country"]))
                        if "language" in info and info["language"]:
                            list_item.setProperty("Language", str(info["language"]))
                        if "premiered" in info and info["premiered"]:
                            list_item.setProperty("Premiered", str(info["premiered"]))
                        if "status" in info and info["status"]:
                            list_item.setProperty("Status", str(info["status"]))
                except (ValueError, TypeError, AttributeError):
                    pass
                
                # Set isPlayable nếu có (sử dụng setProperty thay vì setIsPlayable)
                if "is_playable" in item:
                    try:
                        is_playable = item["is_playable"]
                        if not isinstance(is_playable, bool):
                            is_playable = bool(is_playable)
                        list_item.setProperty("IsPlayable", str(is_playable).lower())
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set path nếu có (sử dụng setProperty thay vì setPath)
                if "path" in item and item["path"]:
                    try:
                        path = item["path"]
                        if not isinstance(path, str):
                            path = str(path)
                        list_item.setProperty("Path", path)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                xbmcplugin.addDirectoryItem(
                    handle=int(sys.argv[1]),
                    url=item.get("path", ""),
                    listitem=list_item,
                    isFolder=not item.get("is_playable", False)
                )
            
            # Thiết lập list view cho kết quả tìm kiếm
            set_list_view()
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            notify("Không tìm thấy kết quả nào")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error displaying search results: {str(e)}")
        alert(f"Lỗi hiển thị kết quả: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_search_form():
    """
    Hiển thị form nhập từ khóa tìm kiếm với lịch sử
    """
    xbmc.log(f"[VietmediaF] show_search_form() called", xbmc.LOGINFO)
    try:
        # Kiểm tra API key trước khi hiển thị form
        api_key = get_tmdb_api_key()
        if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
            alert("TMDB API key chưa được cấu hình!\n\nVui lòng:\n1. Đăng ký tài khoản tại https://www.themoviedb.org/\n2. Lấy API key từ https://www.themoviedb.org/settings/api\n3. Cập nhật TMDB API Key trong Settings\n\nXem hướng dẫn chi tiết trong file TMDB_API_SETUP.md")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            return
        
        # Lấy lịch sử tìm kiếm
        history = get_tmdb_search_history()
        xbmc.log(f"[VietmediaF] TMDB Search History: {history}", xbmc.LOGINFO)
        
        if not history:
            # Nếu không có lịch sử, hiển thị keyboard đơn giản
            keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm phim")
            keyboard.doModal()
            
            if keyboard.isConfirmed() and keyboard.getText().strip():
                query = keyboard.getText().strip()
                perform_search(query)
            else:
                notify("Đã hủy tìm kiếm")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            # Nếu có lịch sử, hiển thị dialog chọn
            options = ["[Nhập từ khóa mới]", "[Xóa lịch sử tìm kiếm]"] + history
            dialog = xbmcgui.Dialog()
            selected = dialog.select("Chọn từ khóa tìm kiếm TMDB", options)
            
            if selected == -1:
                notify("Đã hủy tìm kiếm")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
                return
            elif selected == 0:
                # Nhập từ khóa mới
                keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm phim")
                keyboard.doModal()
                
                if keyboard.isConfirmed() and keyboard.getText().strip():
                    query = keyboard.getText().strip()
                    perform_search(query)
                else:
                    notify("Đã hủy tìm kiếm")
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            elif selected == 1:
                # Xóa lịch sử tìm kiếm
                confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch sử tìm kiếm TMDB không?")
                if confirm:
                    delete_tmdb_search_history()
                    notify("Đã xóa lịch sử tìm kiếm TMDB")
                    xbmc.executebuiltin("Container.Refresh")
                return
            else:
                # Chọn từ lịch sử
                query = options[selected]
                perform_search(query)
            
    except Exception as e:
        logError(f"Error showing search form: {str(e)}")
        alert(f"Lỗi hiển thị form: {str(e)}")

def parse_special_keyword(query):
    """
    Xử lý keyword đặc biệt dạng số để chuyển đổi thành TMDB ID và type
    
    Args:
        query (str): Từ khóa tìm kiếm
    
    Returns:
        tuple: (tmdb_id, media_type) hoặc (None, None) nếu không phải keyword đặc biệt
    """
    try:
        # Kiểm tra nếu query là số và có ít nhất 3 chữ số
        if query.isdigit() and len(query) >= 3:
            # Kiểm tra bắt đầu bằng 11 (movie)
            if query.startswith('11'):
                tmdb_id = query[2:]  # Lấy phần sau "11"
                if tmdb_id.isdigit() and int(tmdb_id) > 0:
                    return int(tmdb_id), "movie"
            
            # Kiểm tra bắt đầu bằng 22 (tv)
            elif query.startswith('22'):
                tmdb_id = query[2:]  # Lấy phần sau "22"
                if tmdb_id.isdigit() and int(tmdb_id) > 0:
                    return int(tmdb_id), "tv"
        
        return None, None
        
    except Exception as e:
        logError(f"Error parsing special keyword: {str(e)}")
        return None, None

def get_movie_details(tmdb_id, media_type):
    """
    Lấy thông tin chi tiết phim/TV từ TMDB API
    
    Args:
        tmdb_id (int): ID của phim/TV trên TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        dict: Thông tin chi tiết phim/TV
    """
    try:
        # Lấy API key từ settings
        api_key = get_tmdb_api_key()
        if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
            logError("TMDB API key chưa được cấu hình đúng")
            return None
            
        # Xác định endpoint dựa trên media_type
        if media_type == "movie":
            url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
        else:
            url = f"{TMDB_BASE_URL}/tv/{tmdb_id}"
            
        params = {
            'api_key': api_key,
            'language': get_tmdb_language()
        }
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=get_tmdb_timeout())
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            logError("TMDB API key không hợp lệ. Vui lòng cấu hình API key thực tế.")
            return None
        elif response.status_code == 404:
            logError(f"Không tìm thấy {media_type} với ID: {tmdb_id}")
            return None
        else:
            logError(f"TMDB API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logError(f"Error getting movie details: {str(e)}")
        return None

def display_single_result(movie_data, media_type, tmdb_id):
    """
    Hiển thị kết quả tìm kiếm đơn lẻ từ TMDB ID
    
    Args:
        movie_data (dict): Dữ liệu phim/TV từ TMDB
        media_type (str): Loại media (movie hoặc tv)
        tmdb_id (int): ID TMDB
    """
    try:
        # Thiết lập content type cho Kodi
        content_type = "movies" if media_type == "movie" else "tvshows"
        xbmcplugin.setContent(int(sys.argv[1]), content_type)
        
        # Thêm các phương thức sắp xếp
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
        
        items = []
        
        # Tạo item từ dữ liệu chi tiết
        movie_item = create_movie_item(movie_data, media_type)
        if movie_item:
            # Thêm số thứ tự vào label
            movie_item["label"] = f"[COLOR gray]1.[/COLOR] {movie_item['label']}"
            items.append(movie_item)
        
        # Hiển thị kết quả
        if items:
            for item in items:
                # Tạo ListItem với label an toàn
                label = item.get("label", "Unknown")
                if not isinstance(label, str):
                    label = str(label)
                list_item = xbmcgui.ListItem(label=label)
                
                # Set artwork tối ưu cho layout 3 cột
                art_dict = {}
                
                # Thêm poster cho cột phải (thumbnail chính)
                if "thumbnail" in item and item["thumbnail"]:
                    try:
                        thumbnail = item["thumbnail"]
                        if not isinstance(thumbnail, str):
                            thumbnail = str(thumbnail)
                        art_dict["thumb"] = thumbnail
                        art_dict["poster"] = thumbnail
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Thêm fanart cho background
                if "fanart" in item and item["fanart"]:
                    try:
                        fanart = item["fanart"]
                        if not isinstance(fanart, str):
                            fanart = str(fanart)
                        art_dict['fanart'] = fanart
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Thêm các loại artwork cơ bản cho layout đẹp
                if "art" in item and item["art"]:
                    try:
                        # Chỉ sử dụng các artwork cơ bản mà Kodi hỗ trợ
                        basic_art = ["poster", "fanart", "thumb", "banner", "landscape"]
                        for key, value in item["art"].items():
                            if value and key in basic_art:
                                if not isinstance(key, str):
                                    key = str(key)
                                if not isinstance(value, str):
                                    value = str(value)
                                art_dict[key] = value
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set artwork với tối ưu cho layout 3 cột
                if art_dict:
                    try:
                        list_item.setArt(art_dict)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set label2 nếu có
                if "label2" in item and item["label2"]:
                    try:
                        label2 = item["label2"]
                        if not isinstance(label2, str):
                            label2 = str(label2)
                        list_item.setProperty("Label2", label2)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set info với metadata đầy đủ theo chuẩn Kodi
                if "info" in item:
                    try:
                        info_tag = list_item.getVideoInfoTag()
                        
                        # Thông tin cơ bản cho layout 3 cột
                        if "title" in item["info"] and item["info"]["title"]:
                            try:
                                info_tag.setTitle(item["info"]["title"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "originaltitle" in item["info"] and item["info"]["originaltitle"]:
                            try:
                                info_tag.setOriginalTitle(item["info"]["originaltitle"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "year" in item["info"] and item["info"]["year"]:
                            try:
                                info_tag.setYear(item["info"]["year"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "rating" in item["info"] and item["info"]["rating"]:
                            try:
                                info_tag.setRating(item["info"]["rating"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "votes" in item["info"] and item["info"]["votes"]:
                            try:
                                info_tag.setVotes(item["info"]["votes"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "mediatype" in item["info"] and item["info"]["mediatype"]:
                            try:
                                info_tag.setMediaType(item["info"]["mediatype"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "plot" in item["info"] and item["info"]["plot"]:
                            try:
                                info_tag.setPlot(item["info"]["plot"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "plotoutline" in item["info"] and item["info"]["plotoutline"]:
                            try:
                                info_tag.setPlotOutline(item["info"]["plotoutline"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        
                        # Thông tin bổ sung cho cột trái
                        if "director" in item["info"] and item["info"]["director"]:
                            try:
                                info_tag.setDirectors([item["info"]["director"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "writer" in item["info"] and item["info"]["writer"]:
                            try:
                                info_tag.setWriters([item["info"]["writer"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "studio" in item["info"] and item["info"]["studio"]:
                            try:
                                info_tag.setStudios([item["info"]["studio"]])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "mpaa" in item["info"] and item["info"]["mpaa"]:
                            try:
                                info_tag.setMpaa(item["info"]["mpaa"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "tagline" in item["info"] and item["info"]["tagline"]:
                            try:
                                info_tag.setTagline(item["info"]["tagline"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        
                        # Thông tin bổ sung
                        if "genre" in item["info"] and item["info"]["genre"]:
                            try:
                                if isinstance(item["info"]["genre"], str):
                                    genres = [g.strip() for g in item["info"]["genre"].split(",") if g.strip()]
                                else:
                                    genres = [str(item["info"]["genre"])]
                                if genres:
                                    info_tag.setGenres(genres)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "country" in item["info"] and item["info"]["country"]:
                            try:
                                if isinstance(item["info"]["country"], str):
                                    countries = [c.strip() for c in item["info"]["country"].split(",") if c.strip()]
                                else:
                                    countries = [str(item["info"]["country"])]
                                if countries:
                                    info_tag.setCountries(countries)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "language" in item["info"] and item["info"]["language"]:
                            try:
                                if isinstance(item["info"]["language"], str):
                                    languages = [l.strip() for l in item["info"]["language"].split(",") if l.strip()]
                                else:
                                    languages = [str(item["info"]["language"])]
                                if languages:
                                    info_tag.setLanguages(languages)
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "premiered" in item["info"] and item["info"]["premiered"]:
                            try:
                                info_tag.setPremiered(item["info"]["premiered"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                        if "status" in item["info"] and item["info"]["status"]:
                            try:
                                info_tag.setStatus(item["info"]["status"])
                            except (ValueError, TypeError, AttributeError):
                                pass
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set properties tối ưu cho layout 3 cột
                if "properties" in item:
                    for key, value in item["properties"].items():
                        try:
                            if not isinstance(key, str):
                                key = str(key)
                            if not isinstance(value, str):
                                value = str(value)
                            list_item.setProperty(key, value)
                        except (ValueError, TypeError, AttributeError):
                            pass
                
                # Set properties đặc biệt cho layout 3 cột
                try:
                    # Properties cho cột phải (poster)
                    if "thumbnail" in item and item["thumbnail"]:
                        list_item.setProperty("ThumbnailImage", item["thumbnail"])
                    if "fanart" in item and item["fanart"]:
                        list_item.setProperty("FanartImage", item["fanart"])
                    
                    # Properties cho cột trái (thông tin)
                    if "info" in item:
                        info = item["info"]
                        if "year" in info and info["year"]:
                            list_item.setProperty("Year", str(info["year"]))
                        if "rating" in info and info["rating"]:
                            list_item.setProperty("Rating", str(info["rating"]))
                        if "votes" in info and info["votes"]:
                            list_item.setProperty("Votes", str(info["votes"]))
                        if "genre" in info and info["genre"]:
                            list_item.setProperty("Genre", str(info["genre"]))
                        if "country" in info and info["country"]:
                            list_item.setProperty("Country", str(info["country"]))
                        if "language" in info and info["language"]:
                            list_item.setProperty("Language", str(info["language"]))
                        if "premiered" in info and info["premiered"]:
                            list_item.setProperty("Premiered", str(info["premiered"]))
                        if "status" in info and info["status"]:
                            list_item.setProperty("Status", str(info["status"]))
                except (ValueError, TypeError, AttributeError):
                    pass
                
                # Set isPlayable nếu có
                if "is_playable" in item:
                    try:
                        is_playable = item["is_playable"]
                        if not isinstance(is_playable, bool):
                            is_playable = bool(is_playable)
                        list_item.setProperty("IsPlayable", str(is_playable).lower())
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                # Set path nếu có
                if "path" in item and item["path"]:
                    try:
                        path = item["path"]
                        if not isinstance(path, str):
                            path = str(path)
                        list_item.setProperty("Path", path)
                    except (ValueError, TypeError, AttributeError):
                        pass
                
                xbmcplugin.addDirectoryItem(
                    handle=int(sys.argv[1]),
                    url=item.get("path", ""),
                    listitem=list_item,
                    isFolder=not item.get("is_playable", False)
                )
            
            # Thiết lập list view cho kết quả đơn lẻ
            set_list_view()
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)
        else:
            notify("Không tìm thấy kết quả nào")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error displaying single result: {str(e)}")
        alert(f"Lỗi hiển thị kết quả: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)


def perform_search(query):
    """
    Thực hiện tìm kiếm phim và TV series
    
    Args:
        query (str): Từ khóa tìm kiếm
    """
    try:
        # Lưu từ khóa vào lịch sử tìm kiếm
        save_tmdb_search_history(query)
        
        # Kiểm tra keyword đặc biệt (số bắt đầu bằng 11 hoặc 22)
        tmdb_id, media_type = parse_special_keyword(query)
        
        if tmdb_id and media_type:
            # Xử lý keyword đặc biệt
            notify(f"Đang tìm kiếm {media_type} với TMDB ID: {tmdb_id}")
            
            # Lấy thông tin chi tiết từ TMDB
            movie_data = get_movie_details(tmdb_id, media_type)
            
            if movie_data:
                # Kiểm tra cache backend trước khi hiển thị
                is_cached, error = check_backend_cache(tmdb_id, media_type)
                
                if is_cached is False:
                    # Cache miss - không hiển thị
                    alert(f"Phim/TV với ID {tmdb_id} không có trong cache backend.")
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
                elif is_cached is None and error:
                    # Có lỗi - hiển thị cảnh báo nhưng vẫn hiển thị
                    alert(f"⚠️ Backend API lỗi: {error}\n\nKết quả vẫn được hiển thị nhưng có thể không chính xác.")
                    display_single_result(movie_data, media_type, tmdb_id)
                else:
                    # Cache hit hoặc không bật kiểm tra cache
                    display_single_result(movie_data, media_type, tmdb_id)
            else:
                alert(f"Không tìm thấy {media_type} với ID: {tmdb_id}")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            # Tìm kiếm thông thường
            notify(f"Đang tìm kiếm: {query}")
            
            # Tìm kiếm phim và TV series song song
            movies_data = search_movies(query)
            tv_data = search_tv_shows(query)
            
            if movies_data or tv_data:
                # Lọc kết quả theo cache backend
                notify("Đang kiểm tra cache backend...")
                filtered_movies, filtered_tv, error_message = filter_cached_results(movies_data, tv_data)
                
                # Hiển thị thông báo lỗi nếu có
                if error_message:
                    alert(f"⚠️ {error_message}\n\nKết quả vẫn được hiển thị nhưng có thể không chính xác.")
                
                if filtered_movies or filtered_tv:
                    display_search_results(filtered_movies, filtered_tv, query)
                else:
                    alert("Không tìm thấy kết quả nào trong cache. Vui lòng thử từ khóa khác.")
                    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            else:
                alert("Không tìm thấy kết quả nào. Vui lòng thử từ khóa khác.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error performing search: {str(e)}")
        alert(f"Lỗi tìm kiếm: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
