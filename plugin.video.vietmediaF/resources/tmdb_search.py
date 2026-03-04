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

# TMDB Image Base URL (vẫn cần để tạo URL poster/backdrop)
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Backend API Headers
BACKEND_HEADERS = {
    'User-Agent': 'VietMediaF/1.0',
    'Accept': 'application/json'
}

def get_backend_url():
    """URL backend API từ settings"""
    return ADDON.getSetting('backend_api_url') or "https://vietmediaf.store"

def get_backend_timeout():
    """Timeout backend API (hardcoded)"""
    return 22

def get_tmdb_language():
    """Lấy ngôn ngữ TMDB từ settings"""
    return ADDON.getSetting('tmdb_language') or "vi-VN"

def get_backend_batch_enabled():
    """Batch API luôn bật"""
    return True

def get_backend_batch_size():
    """Kích thước batch tối đa (hardcoded)"""
    return 50


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
        backend_enabled = True
        xbmc.log(f"[VietmediaF] Backend API enabled: {backend_enabled}", xbmc.LOGINFO)
        
        if not backend_enabled:
            xbmc.log(f"[VietmediaF] Backend API disabled, skipping cache check for {media_type} {tmdb_id}", xbmc.LOGINFO)
            return True, None  # Nếu không bật, mặc định hiển thị tất cả
        
        # Lấy cấu hình từ settings
        backend_url = get_backend_url()
        if not backend_url:
            backend_url = "https://vietmediaf.store"
        
        timeout = get_backend_timeout()
        
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
        if not True:
            return None
        
        # Lấy cấu hình từ settings
        backend_url = get_backend_url()
        if not backend_url:
            backend_url = "https://vietmediaf.store"
        
        timeout = get_backend_timeout()
        
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

# Batch API Functions
def check_backend_cache_batch(tmdb_ids, media_type):
    """
    Kiểm tra cache cho nhiều phim/TV cùng lúc bằng Batch API
    
    Args:
        tmdb_ids (list): Danh sách ID của phim/TV trên TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        dict: Kết quả cache cho từng ID {tmdb_id: (is_cached, error_message)}
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        if not True:
            return {tmdb_id: (True, None) for tmdb_id in tmdb_ids}
        
        # Lấy cấu hình từ settings
        backend_url = get_backend_url()
        if not backend_url:
            backend_url = "https://vietmediaf.store"
        
        timeout = get_backend_timeout()
        
        # Tạo URL endpoint cho Batch API
        endpoint = f"{backend_url}/api/batch/{media_type}"
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Tạo payload cho Batch API
        payload = {
            "tmdb_ids": tmdb_ids
        }
        
        xbmc.log(f"[VietmediaF] Calling Batch API for {len(tmdb_ids)} {media_type}s", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] Batch API endpoint: {endpoint}", xbmc.LOGINFO)
        
        # Gọi Batch API
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            batch_results = result.get("results", {})
            total_cached = result.get("total_cached", 0)
            total_processed = result.get("total_processed", 0)
            
            xbmc.log(f"[VietmediaF] Batch API success: {total_cached}/{total_processed} cached", xbmc.LOGINFO)
            
            # Xử lý kết quả cho từng ID
            results = {}
            for tmdb_id in tmdb_ids:
                tmdb_id_str = str(tmdb_id)
                if tmdb_id_str in batch_results:
                    item_result = batch_results[tmdb_id_str]
                    is_cached = item_result.get("cached", False)
                    results[tmdb_id] = (is_cached, None)
                else:
                    # Nếu không có trong kết quả, coi như cache miss
                    results[tmdb_id] = (False, None)
            
            return results
        else:
            error_msg = f"Batch API lỗi: {response.status_code}"
            xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
            return {tmdb_id: (None, error_msg) for tmdb_id in tmdb_ids}
            
    except requests.exceptions.Timeout:
        error_msg = f"Batch API timeout sau {timeout} giây"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        return {tmdb_id: (None, error_msg) for tmdb_id in tmdb_ids}
    except requests.exceptions.ConnectionError:
        error_msg = f"Không thể kết nối đến Batch API: {backend_url}"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        return {tmdb_id: (None, error_msg) for tmdb_id in tmdb_ids}
    except Exception as e:
        error_msg = f"Lỗi Batch API: {str(e)}"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        return {tmdb_id: (None, error_msg) for tmdb_id in tmdb_ids}

def check_backend_cache_mixed_batch(movie_ids, tv_ids):
    """
    Kiểm tra cache cho cả movies và TV shows cùng lúc bằng Mixed Batch API
    
    Args:
        movie_ids (list): Danh sách ID của movies
        tv_ids (list): Danh sách ID của TV shows
    
    Returns:
        dict: Kết quả cache cho từng ID {tmdb_id: (is_cached, error_message, media_type)}
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        if not True:
            results = {}
            for tmdb_id in movie_ids:
                results[tmdb_id] = (True, None, "movie")
            for tmdb_id in tv_ids:
                results[tmdb_id] = (True, None, "tv")
            return results
        
        # Lấy cấu hình từ settings
        backend_url = get_backend_url()
        if not backend_url:
            backend_url = "https://vietmediaf.store"
        
        timeout = get_backend_timeout()
        
        # Tạo URL endpoint cho Mixed Batch API
        endpoint = f"{backend_url}/api/batch/mixed"
        
        headers = {
            'User-Agent': 'VietMediaF/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Tạo payload cho Mixed Batch API
        payload = {
            "movies": movie_ids,
            "tv_shows": tv_ids
        }
        
        total_items = len(movie_ids) + len(tv_ids)
        xbmc.log(f"[VietmediaF] Calling Mixed Batch API for {len(movie_ids)} movies + {len(tv_ids)} TV shows", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] Mixed Batch API endpoint: {endpoint}", xbmc.LOGINFO)
        
        # Gọi Mixed Batch API
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            result = response.json()
            batch_results = result.get("results", {})
            total_cached = result.get("total_cached", 0)
            total_processed = result.get("total_processed", 0)
            
            xbmc.log(f"[VietmediaF] Mixed Batch API success: {total_cached}/{total_processed} cached", xbmc.LOGINFO)
            
            # Xử lý kết quả cho từng ID
            results = {}
            for tmdb_id in movie_ids + tv_ids:
                tmdb_id_str = str(tmdb_id)
                if tmdb_id_str in batch_results:
                    item_result = batch_results[tmdb_id_str]
                    is_cached = item_result.get("cached", False)
                    media_type = item_result.get("media_type", "movie")
                    results[tmdb_id] = (is_cached, None, media_type)
                else:
                    # Nếu không có trong kết quả, coi như cache miss
                    media_type = "movie" if tmdb_id in movie_ids else "tv"
                    results[tmdb_id] = (False, None, media_type)
            
            return results
        else:
            error_msg = f"Mixed Batch API lỗi: {response.status_code}"
            xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
            results = {}
            for tmdb_id in movie_ids:
                results[tmdb_id] = (None, error_msg, "movie")
            for tmdb_id in tv_ids:
                results[tmdb_id] = (None, error_msg, "tv")
            return results
            
    except requests.exceptions.Timeout:
        error_msg = f"Mixed Batch API timeout sau {timeout} giây"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        results = {}
        for tmdb_id in movie_ids:
            results[tmdb_id] = (None, error_msg, "movie")
        for tmdb_id in tv_ids:
            results[tmdb_id] = (None, error_msg, "tv")
        return results
    except requests.exceptions.ConnectionError:
        error_msg = f"Không thể kết nối đến Mixed Batch API: {backend_url}"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        results = {}
        for tmdb_id in movie_ids:
            results[tmdb_id] = (None, error_msg, "movie")
        for tmdb_id in tv_ids:
            results[tmdb_id] = (None, error_msg, "tv")
        return results
    except Exception as e:
        error_msg = f"Lỗi Mixed Batch API: {str(e)}"
        xbmc.log(f"[VietmediaF] {error_msg}", xbmc.LOGERROR)
        results = {}
        for tmdb_id in movie_ids:
            results[tmdb_id] = (None, error_msg, "movie")
        for tmdb_id in tv_ids:
            results[tmdb_id] = (None, error_msg, "tv")
        return results

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

def add_paging_nav(page, total_pages, next_url_template):
    """
    Thêm nút phân trang và nút về trang chính
    
    Args:
        page (int): Trang hiện tại
        total_pages (int): Tổng số trang
        next_url_template (str): URL trang tiếp (đã format sẵn page+1)
    """
    # Nút trang tiếp
    if page < total_pages:
        next_item = xbmcgui.ListItem(f"[COLOR yellow]Trang Tiếp ({page + 1}) →[/COLOR]")
        next_item.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), next_url_template, next_item, isFolder=True)
    
    # Nút về trang chính
    home_url = "plugin://plugin.video.vietmediaF?action=menu"
    home_item = xbmcgui.ListItem("[COLOR lime][HOME] Về trang chính[/COLOR]")
    home_item.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), home_url, home_item, isFolder=True)
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

def filter_cached_results(movies_data, tv_data):
    """
    Lọc kết quả tìm kiếm chỉ hiển thị những phim/TV có trong cache backend
    Sử dụng Batch API để tăng tốc độ lên 10-26 lần
    
    Args:
        movies_data (dict): Dữ liệu phim từ TMDB
        tv_data (dict): Dữ liệu TV series từ TMDB
    
    Returns:
        tuple: (filtered_movies_data, filtered_tv_data, error_message)
    """
    try:
        # Kiểm tra xem có bật kiểm tra cache không
        backend_enabled = True
        batch_enabled = get_backend_batch_enabled()
        xbmc.log(f"[VietmediaF] Filtering cached results - Backend API enabled: {backend_enabled}, Batch API enabled: {batch_enabled}", xbmc.LOGINFO)
        
        if not backend_enabled:
            xbmc.log(f"[VietmediaF] Backend API disabled, returning all results without filtering", xbmc.LOGINFO)
            return movies_data, tv_data, None  # Nếu không bật, trả về dữ liệu gốc
        
        # Thu thập tất cả TMDB IDs
        movie_ids = []
        tv_ids = []
        
        if movies_data and movies_data.get('results'):
            movie_ids = [movie.get('id') for movie in movies_data['results'] if movie.get('id')]
        
        if tv_data and tv_data.get('results'):
            tv_ids = [tv.get('id') for tv in tv_data['results'] if tv.get('id')]
        
        total_items = len(movie_ids) + len(tv_ids)
        xbmc.log(f"[VietmediaF] Batch filtering {len(movie_ids)} movies + {len(tv_ids)} TV shows = {total_items} total", xbmc.LOGINFO)
        
        if total_items == 0:
            xbmc.log(f"[VietmediaF] No items to filter", xbmc.LOGINFO)
            return movies_data, tv_data, None
        
        # Chọn phương pháp kiểm tra cache dựa trên settings
        if batch_enabled and total_items > 1:
            # Sử dụng Mixed Batch API để kiểm tra cache cho cả movies và TV
            xbmc.log(f"[VietmediaF] Using Batch API for {total_items} items", xbmc.LOGINFO)
            batch_results = check_backend_cache_mixed_batch(movie_ids, tv_ids)
        else:
            # Fallback về Single API nếu Batch API bị tắt hoặc chỉ có 1 item
            xbmc.log(f"[VietmediaF] Using Single API for {total_items} items", xbmc.LOGINFO)
            batch_results = {}
            
            # Kiểm tra cache cho từng movie
            for tmdb_id in movie_ids:
                is_cached, error = check_backend_cache(tmdb_id, "movie")
                batch_results[tmdb_id] = (is_cached, error, "movie")
            
            # Kiểm tra cache cho từng TV show
            for tmdb_id in tv_ids:
                is_cached, error = check_backend_cache(tmdb_id, "tv")
                batch_results[tmdb_id] = (is_cached, error, "tv")
        
        # Xử lý kết quả cho movies
        filtered_movies = None
        if movies_data and movies_data.get('results'):
            xbmc.log(f"[VietmediaF] Processing {len(movies_data['results'])} movies with Batch API results", xbmc.LOGINFO)
            cached_movies = []
            for movie in movies_data['results']:
                tmdb_id = movie.get('id')
                if tmdb_id and tmdb_id in batch_results:
                    is_cached, error, media_type = batch_results[tmdb_id]
                    if is_cached is True:
                        cached_movies.append(movie)
                        xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} CACHE HIT (Batch)", xbmc.LOGINFO)
                    elif is_cached is False:
                        xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} CACHE MISS, hiding (Batch)", xbmc.LOGINFO)
                    else:  # is_cached is None (có lỗi)
                        if error:
                            xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} ERROR: {error} (Batch)", xbmc.LOGWARNING)
                        # Nếu có lỗi, vẫn hiển thị phim để không làm mất kết quả
                        cached_movies.append(movie)
                        xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} ERROR, showing anyway (Batch)", xbmc.LOGINFO)
                else:
                    # Nếu không có trong batch results, coi như cache miss
                    xbmc.log(f"[VietmediaF] Movie ID {tmdb_id} NOT FOUND in batch results, hiding", xbmc.LOGINFO)
            
            if cached_movies:
                filtered_movies = movies_data.copy()
                filtered_movies['results'] = cached_movies
                filtered_movies['total_results'] = len(cached_movies)
                xbmc.log(f"[VietmediaF] Movies filtered: {len(cached_movies)}/{len(movies_data['results'])} cached", xbmc.LOGINFO)
        
        # Xử lý kết quả cho TV shows
        filtered_tv = None
        if tv_data and tv_data.get('results'):
            xbmc.log(f"[VietmediaF] Processing {len(tv_data['results'])} TV shows with Batch API results", xbmc.LOGINFO)
            cached_tv = []
            for tv in tv_data['results']:
                tmdb_id = tv.get('id')
                if tmdb_id and tmdb_id in batch_results:
                    is_cached, error, media_type = batch_results[tmdb_id]
                    if is_cached is True:
                        cached_tv.append(tv)
                        xbmc.log(f"[VietmediaF] TV ID {tmdb_id} CACHE HIT (Batch)", xbmc.LOGINFO)
                    elif is_cached is False:
                        xbmc.log(f"[VietmediaF] TV ID {tmdb_id} CACHE MISS, hiding (Batch)", xbmc.LOGINFO)
                    else:  # is_cached is None (có lỗi)
                        if error:
                            xbmc.log(f"[VietmediaF] TV ID {tmdb_id} ERROR: {error} (Batch)", xbmc.LOGWARNING)
                        # Nếu có lỗi, vẫn hiển thị TV để không làm mất kết quả
                        cached_tv.append(tv)
                        xbmc.log(f"[VietmediaF] TV ID {tmdb_id} ERROR, showing anyway (Batch)", xbmc.LOGINFO)
                else:
                    # Nếu không có trong batch results, coi như cache miss
                    xbmc.log(f"[VietmediaF] TV ID {tmdb_id} NOT FOUND in batch results, hiding", xbmc.LOGINFO)
            
            if cached_tv:
                filtered_tv = tv_data.copy()
                filtered_tv['results'] = cached_tv
                filtered_tv['total_results'] = len(cached_tv)
                xbmc.log(f"[VietmediaF] TV shows filtered: {len(cached_tv)}/{len(tv_data['results'])} cached", xbmc.LOGINFO)
        
        # Tính toán thống kê
        total_cached = 0
        total_errors = 0
        errors = []
        
        for tmdb_id, (is_cached, error, media_type) in batch_results.items():
            if is_cached is True:
                total_cached += 1
            elif is_cached is None and error:
                total_errors += 1
                errors.append(f"{media_type.title()} ID {tmdb_id}: {error}")
        
        # Tạo thông báo lỗi nếu có
        error_message = None
        if errors:
            if len(errors) <= 3:
                error_message = f"⚠️ Backend API có lỗi:\n" + "\n".join(errors)
            else:
                error_message = f"⚠️ Backend API có lỗi:\n" + "\n".join(errors[:3]) + f"\n... và {len(errors) - 3} lỗi khác"
        
        xbmc.log(f"[VietmediaF] Batch filtering completed: {total_cached}/{total_items} cached, {total_errors} errors", xbmc.LOGINFO)
        
        return filtered_movies, filtered_tv, error_message
        
    except Exception as e:
        xbmc.log(f"[VietmediaF] Error in filter_cached_results: {str(e)}", xbmc.LOGERROR)
        return movies_data, tv_data, f"Lỗi khi lọc kết quả: {str(e)}"

def parse_year_from_query(query):
    """
    Parse năm từ query tìm kiếm.
    Hỗ trợ: 'avatar 2009', 'avatar (2009)'
    
    Returns:
        tuple: (clean_query, year) - query đã bỏ năm và năm (int hoặc None)
    """
    import re
    year_match = re.search(r'\s\(?(19\d{2}|20\d{2})\)?$', query)
    if year_match:
        year = int(year_match.group(1))
        clean_query = query[:year_match.start()].strip()
        return clean_query, year
    return query, None

def search_movies(query, page=1):
    """
    Tìm kiếm phim trên TMDB qua Backend API
    Hỗ trợ tìm theo năm: 'avatar 2009' hoặc 'avatar (2009)'
    
    Args:
        query (str): Từ khóa tìm kiếm (có thể kèm năm)
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim từ TMDB API
    """
    try:
        lang = get_tmdb_language()
        clean_query, year = parse_year_from_query(query)
        endpoint = f"/api/tmdb/search/movie?q={requests.utils.quote(clean_query)}&page={page}&lang={lang}"
        if year:
            endpoint += f"&year={year}"
            xbmc.log(f"[VietmediaF] Search movies: '{clean_query}' year={year}", xbmc.LOGINFO)
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error searching movies: {str(e)}")
        return None

def search_tv_shows(query, page=1):
    """
    Tìm kiếm TV series trên TMDB qua Backend API
    Hỗ trợ tìm theo năm: 'breaking bad 2008' hoặc 'breaking bad (2008)'
    
    Args:
        query (str): Từ khóa tìm kiếm (có thể kèm năm)
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu TV series từ TMDB API
    """
    try:
        lang = get_tmdb_language()
        clean_query, year = parse_year_from_query(query)
        endpoint = f"/api/tmdb/search/tv?q={requests.utils.quote(clean_query)}&page={page}&lang={lang}"
        if year:
            endpoint += f"&year={year}"
            xbmc.log(f"[VietmediaF] Search TV: '{clean_query}' year={year}", xbmc.LOGINFO)
        return call_backend_tmdb(endpoint)
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
    Sử dụng backend API để lấy danh sách genres, fallback về hardcoded map
    
    Args:
        genre_ids (list): Danh sách genre IDs
    
    Returns:
        str: Tên thể loại phân cách bằng dấu phẩy
    """
    # Fallback genre map (Việt hóa)
    genre_map = {
        28: 'Hành động', 12: 'Phiêu lưu', 16: 'Hoạt hình',
        35: 'Hài', 80: 'Tội phạm', 99: 'Tài liệu',
        18: 'Drama', 10751: 'Gia đình', 14: 'Fantasy',
        36: 'Lịch sử', 27: 'Kinh dị', 10402: 'Âm nhạc',
        9648: 'Bí ẩn', 10749: 'Lãng mạn', 878: 'Khoa học viễn tưởng',
        10770: 'TV Movie', 53: 'Thriller', 10752: 'Chiến tranh',
        37: 'Miền Tây',
        # TV genres
        10759: 'Action & Adventure', 10762: 'Kids', 10763: 'News',
        10764: 'Reality', 10765: 'Sci-Fi & Fantasy', 10766: 'Soap',
        10767: 'Talk', 10768: 'War & Politics'
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
        
        # Tạo label2 với format: <tên phim> | <tên phim gốc> (năm) hoặc <tên phim> (năm)
        # Loại bỏ duplicate nếu tên gốc và tên địa phương trùng nhau
        label2_parts = []
        if title:
            label2_parts.append(title)
        if original_title and original_title != title and original_title.strip():
            label2_parts.append(original_title)
        
        # Thêm năm vào cuối
        if release_year:
            if len(label2_parts) > 1:  # Có cả tên và tên gốc
                label2_parts.append(f"({release_year})")
            else:  # Chỉ có tên
                label2_parts.append(f"({release_year})")
        
        label2 = " | ".join(label2_parts) if label2_parts else f"TMDB ID: {tmdb_id}" if tmdb_id else ""
        
        # Tạo item với metadata đầy đủ và artwork tối ưu cho layout 3 cột
        item = {
            "label": label,
            "is_playable": False,
            "path": action_path,
            "thumbnail": poster_url,  # Ảnh bên phải
            "fanart": backdrop_url,   # Background
            "label2": label2,
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

def display_search_results(movies_data, tv_data, query, page=1, close_directory=True):
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
            xbmc.log(f"[VietmediaF] display_search_results: Processing {len(movies_data['results'])} movies", xbmc.LOGINFO)
            for i, movie in enumerate(movies_data['results'], 1):  # Không giới hạn số phim
                movie_item = create_movie_item(movie, "movie")
                if movie_item:
                    # Thêm số thứ tự vào label
                    movie_item["label"] = f"[COLOR gray]{i:2d}.[/COLOR] {movie_item['label']}"
                    items.append(movie_item)
        
        # Thêm TV series trực tiếp không có header
        if tv_data and tv_data.get('results'):
            xbmc.log(f"[VietmediaF] display_search_results: Processing {len(tv_data['results'])} TV shows", xbmc.LOGINFO)
            for i, tv in enumerate(tv_data['results'], 1):  # Không giới hạn số TV series
                tv_item = create_movie_item(tv, "tv")
                if tv_item:
                    # Thêm số thứ tự vào label
                    tv_item["label"] = f"[COLOR gray]{i:2d}.[/COLOR] {tv_item['label']}"
                    items.append(tv_item)
        
        # Bỏ tất cả header và tùy chọn để giao diện gọn gàng
        
        # Hiển thị kết quả với metadata đầy đủ
        xbmc.log(f"[VietmediaF] display_search_results: Total items to display: {len(items)}", xbmc.LOGINFO)
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
            if close_directory:
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
    Lấy thông tin chi tiết phim/TV từ TMDB qua Backend API
    
    Args:
        tmdb_id (int): ID của phim/TV trên TMDB
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        dict: Thông tin chi tiết phim/TV
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/{media_type}/{tmdb_id}?lang={lang}"
        return call_backend_tmdb(endpoint)
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

def get_trending_movies(time_window="day", page=1):
    """
    Lấy danh sách phim trending từ TMDB qua Backend API (1 trang)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim trending
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/trending/movie?page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting trending movies: {str(e)}")
        return None

def get_trending_tv(time_window="day", page=1):
    """
    Lấy danh sách TV trending từ TMDB qua Backend API (1 trang)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu TV trending
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/trending/tv?page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting trending TV: {str(e)}")
        return None

def get_trending_movies_multiple_pages(time_window="day"):
    """
    Lấy danh sách phim trending từ TMDB API (nhiều trang theo setting)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
    
    Returns:
        dict: Dữ liệu phim trending từ TMDB API (tổng hợp nhiều trang)
    """
    try:
        # Lấy số lượng phim muốn lấy từ settings
        target_count = get_tmdb_trending_count()
        xbmc.log(f"[VietmediaF] Target trending count: {target_count}", xbmc.LOGINFO)
        
        # Tính số trang cần gọi (mỗi trang 20 phim)
        pages_needed = (target_count + 19) // 20  # Làm tròn lên
        xbmc.log(f"[VietmediaF] Pages needed: {pages_needed} for {target_count} movies", xbmc.LOGINFO)
        
        all_movies = []
        total_pages = 1
        total_results = 0
        
        for page in range(1, pages_needed + 1):
            xbmc.log(f"[VietmediaF] Fetching trending page {page}/{pages_needed}", xbmc.LOGINFO)
            
            # Gọi API cho trang hiện tại
            page_data = get_trending_movies(time_window, page)
            if not page_data:
                xbmc.log(f"[VietmediaF] Failed to get page {page}, stopping", xbmc.LOGERROR)
                break
                
            # Lấy thông tin tổng quan từ trang đầu tiên
            if page == 1:
                total_pages = page_data.get('total_pages', 1)
                total_results = page_data.get('total_results', 0)
                
                # Kiểm tra xem có đủ trang không
                if total_pages < pages_needed:
                    pages_needed = total_pages
                    xbmc.log(f"[VietmediaF] Adjusted pages needed to {pages_needed} (total available)", xbmc.LOGINFO)
            
            # Thêm phim từ trang này
            movies = page_data.get('results', [])
            all_movies.extend(movies)
            
            # Nếu đã đủ số lượng mong muốn thì dừng
            if len(all_movies) >= target_count:
                all_movies = all_movies[:target_count]  # Cắt bớt nếu thừa
                break
                
            # Nếu không còn trang nào thì dừng
            if page >= total_pages:
                break
        
        # Tạo response giống như TMDB API
        result = {
            'page': 1,
            'results': all_movies,
            'total_pages': total_pages,
            'total_results': total_results
        }
        
        xbmc.log(f"[VietmediaF] Fetched {len(all_movies)} trending movies from {pages_needed} pages (target: {target_count})", xbmc.LOGINFO)
        return result
        
    except Exception as e:
        logError(f"Error getting trending movies multiple pages: {str(e)}")
        return None

def get_trending_tv_multiple_pages(time_window="day"):
    """
    Lấy danh sách TV trending từ TMDB API (nhiều trang theo setting)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
    
    Returns:
        dict: Dữ liệu TV trending từ TMDB API (tổng hợp nhiều trang)
    """
    try:
        # Lấy số lượng TV muốn lấy từ settings
        target_count = get_tmdb_trending_count()
        xbmc.log(f"[VietmediaF] Target trending TV count: {target_count}", xbmc.LOGINFO)
        
        # Tính số trang cần gọi (mỗi trang 20 TV)
        pages_needed = (target_count + 19) // 20  # Làm tròn lên
        xbmc.log(f"[VietmediaF] Pages needed: {pages_needed} for {target_count} TV shows", xbmc.LOGINFO)
        
        all_tv_shows = []
        total_pages = 1
        total_results = 0
        
        for page in range(1, pages_needed + 1):
            xbmc.log(f"[VietmediaF] Fetching trending TV page {page}/{pages_needed}", xbmc.LOGINFO)
            
            # Gọi API cho trang hiện tại
            page_data = get_trending_tv(time_window, page)
            if not page_data:
                xbmc.log(f"[VietmediaF] Failed to get TV page {page}, stopping", xbmc.LOGERROR)
                break
                
            # Lấy thông tin tổng quan từ trang đầu tiên
            if page == 1:
                total_pages = page_data.get('total_pages', 1)
                total_results = page_data.get('total_results', 0)
                
                # Kiểm tra xem có đủ trang không
                if total_pages < pages_needed:
                    pages_needed = total_pages
                    xbmc.log(f"[VietmediaF] Adjusted pages needed to {pages_needed} (total available)", xbmc.LOGINFO)
            
            # Thêm TV từ trang này
            tv_shows = page_data.get('results', [])
            all_tv_shows.extend(tv_shows)
            
            # Nếu đã đủ số lượng mong muốn thì dừng
            if len(all_tv_shows) >= target_count:
                all_tv_shows = all_tv_shows[:target_count]  # Cắt bớt nếu thừa
                break
                
            # Nếu không còn trang nào thì dừng
            if page >= total_pages:
                break
        
        # Tạo response giống như TMDB API
        result = {
            'page': 1,
            'results': all_tv_shows,
            'total_pages': total_pages,
            'total_results': total_results
        }
        
        xbmc.log(f"[VietmediaF] Fetched {len(all_tv_shows)} trending TV shows from {pages_needed} pages (target: {target_count})", xbmc.LOGINFO)
        return result
        
    except Exception as e:
        logError(f"Error getting trending TV multiple pages: {str(e)}")
        return None

def show_trending_movies(time_window="day", page=1):
    """
    Hiển thị danh sách phim trending (sử dụng setting để lấy nhiều trang)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
        page (int): Trang hiện tại (không sử dụng, chỉ để tương thích)
    """
    try:
        # Debug: Kiểm tra settings
        language = get_tmdb_language()
        target_count = get_tmdb_trending_count()
        
        xbmc.log(f"[VietmediaF] TMDB Settings Debug:", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Backend URL: {get_backend_url()}", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Language: {language}", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Trending Count: {target_count}", xbmc.LOGINFO)
        
        # Lấy số lượng phim từ setting
        notify(f"Đang tải {target_count} phim trending ({time_window})...")
        
        # Lấy dữ liệu trending movies (nhiều trang)
        movies_data = get_trending_movies_multiple_pages(time_window)
        
        if movies_data and movies_data.get('results'):
            # Lọc kết quả theo cache backend
            notify("Đang kiểm tra cache backend...")
            filtered_movies, _, error_message = filter_cached_results(movies_data, None)
            
            # Hiển thị thông báo lỗi nếu có
            if error_message:
                alert(f"⚠️ {error_message}\n\nKết quả vẫn được hiển thị nhưng có thể không chính xác.")
            
            if filtered_movies and filtered_movies.get('results'):
                # Hiển thị kết quả trending movies (không phân trang)
                display_trending_results_simple(filtered_movies, time_window)
            else:
                alert("Không tìm thấy phim trending nào trong cache. Vui lòng thử lại sau.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert("Không tìm thấy phim trending nào. Vui lòng thử lại sau.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing trending movies: {str(e)}")
        alert(f"Lỗi hiển thị phim trending: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_trending_tv(time_window="day", page=1):
    """
    Hiển thị danh sách TV trending (sử dụng setting để lấy nhiều trang)
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
        page (int): Trang hiện tại (không sử dụng, chỉ để tương thích)
    """
    try:
        # Debug: Kiểm tra settings
        language = get_tmdb_language()
        target_count = get_tmdb_trending_count()
        
        xbmc.log(f"[VietmediaF] TMDB TV Settings Debug:", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Backend URL: {get_backend_url()}", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Language: {language}", xbmc.LOGINFO)
        xbmc.log(f"[VietmediaF] - Trending Count: {target_count}", xbmc.LOGINFO)
        
        # Lấy số lượng TV từ setting
        notify(f"Đang tải {target_count} TV trending ({time_window})...")
        
        # Lấy dữ liệu trending TV (nhiều trang)
        tv_data = get_trending_tv_multiple_pages(time_window)
        
        if tv_data and tv_data.get('results'):
            # Lọc kết quả theo cache backend
            notify("Đang kiểm tra cache backend...")
            _, filtered_tv, error_message = filter_cached_results(None, tv_data)
            
            # Hiển thị thông báo lỗi nếu có
            if error_message:
                alert(f"⚠️ {error_message}\n\nKết quả vẫn được hiển thị nhưng có thể không chính xác.")
            
            if filtered_tv and filtered_tv.get('results'):
                # Hiển thị kết quả trending TV (không phân trang)
                display_trending_tv_results_simple(filtered_tv, time_window)
            else:
                alert("Không tìm thấy TV trending nào trong cache. Vui lòng thử lại sau.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert("Không tìm thấy TV trending nào. Vui lòng thử lại sau.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing trending TV: {str(e)}")
        alert(f"Lỗi hiển thị TV trending: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def display_trending_results_simple(movies_data, time_window):
    """
    Hiển thị kết quả trending movies đơn giản (không phân trang)
    
    Args:
        movies_data (dict): Dữ liệu phim từ TMDB API
        time_window (str): Khoảng thời gian (day hoặc week)
    """
    try:
        results = movies_data.get('results', [])
        total_results = movies_data.get('total_results', 0)
        
        # Debug log
        xbmc.log(f"[VietmediaF] display_trending_results_simple: {len(results)} movies to display", xbmc.LOGINFO)
        
        # Hiển thị thông tin
        count_info = f"({len(results)}/{total_results} phim)"
        
        # Hiển thị kết quả phim
        display_search_results(movies_data, None, f"Trending Movies ({time_window}) - {count_info}")
        
    except Exception as e:
        logError(f"Error displaying trending results simple: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def display_trending_tv_results_simple(tv_data, time_window):
    """
    Hiển thị kết quả trending TV đơn giản (không phân trang)
    
    Args:
        tv_data (dict): Dữ liệu TV từ TMDB API
        time_window (str): Khoảng thời gian (day hoặc week)
    """
    try:
        results = tv_data.get('results', [])
        total_results = tv_data.get('total_results', 0)
        
        # Debug log
        xbmc.log(f"[VietmediaF] display_trending_tv_results_simple: {len(results)} TV shows to display", xbmc.LOGINFO)
        
        # Hiển thị thông tin
        count_info = f"({len(results)}/{total_results} TV shows)"
        
        # Hiển thị kết quả TV
        display_search_results(None, tv_data, f"Trending TV Shows ({time_window}) - {count_info}")
        
    except Exception as e:
        logError(f"Error displaying trending TV results simple: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_trending_unified(media_type="movies", page=1):
    """
    Hiển thị danh sách trending với paging (1 trang mỗi lần, 20 items/trang)
    
    Args:
        media_type (str): Loại media ("movies" hoặc "tv")
        page (int): Trang hiện tại
    """
    try:
        media_label = "phim" if media_type == "movies" else "TV series"
        notify(f"Đang tải {media_label} trending (trang {page})...")
        
        xbmc.log(f"[VietmediaF] Trending: media_type={media_type}, page={page}, backend={get_backend_url()}", xbmc.LOGINFO)
        
        # Gọi API 1 trang
        if media_type == "movies":
            data = get_trending_movies("day", page)
        else:
            data = get_trending_tv("day", page)
        
        if data and data.get('results'):
            # Lọc kết quả theo cache backend
            notify("Đang kiểm tra cache backend...")
            if media_type == "movies":
                filtered_data, _, error_message = filter_cached_results(data, None)
            else:
                _, filtered_data, error_message = filter_cached_results(None, data)
            
            if error_message:
                alert(f"⚠️ {error_message}")
            
            if filtered_data and filtered_data.get('results'):
                total_pages = data.get('total_pages', 1)
                total_results = data.get('total_results', 0)
                count_info = f"({len(filtered_data['results'])}/{total_results})"
                
                # Hiển thị kết quả
                if media_type == "movies":
                    display_search_results(filtered_data, None, f"Trending Movies - Trang {page} {count_info}", close_directory=False)
                else:
                    display_search_results(None, filtered_data, f"Trending TV - Trang {page} {count_info}", close_directory=False)
                
                # Thêm nút phân trang và nút về trang chính
                next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_trending&type={media_type}&page={page + 1}"
                add_paging_nav(page, total_pages, next_url)
            else:
                alert(f"Không tìm thấy {media_label} trending nào trong cache.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert(f"Không tìm thấy {media_label} trending.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing unified trending: {str(e)}")
        alert(f"Lỗi hiển thị {media_type} trending: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def display_trending_unified_results(data, media_type, time_window):
    """
    Hiển thị kết quả trending thống nhất (Movies hoặc TV)
    
    Args:
        data (dict): Dữ liệu từ TMDB API
        media_type (str): Loại media ("movies" hoặc "tv")
        time_window (str): Khoảng thời gian (day hoặc week)
    """
    try:
        results = data.get('results', [])
        total_results = data.get('total_results', 0)
        
        # Debug log
        media_label = "movies" if media_type == "movies" else "TV shows"
        xbmc.log(f"[VietmediaF] display_trending_unified_results: {len(results)} {media_label} to display", xbmc.LOGINFO)
        
        # Hiển thị thông tin
        count_info = f"({len(results)}/{total_results} {media_label})"
        
        # Hiển thị kết quả
        if media_type == "movies":
            display_search_results(data, None, f"Trending Movies ({time_window}) - {count_info}")
        else:
            display_search_results(None, data, f"Trending TV Shows ({time_window}) - {count_info}")
        
    except Exception as e:
        logError(f"Error displaying unified trending results: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def display_trending_results_with_pagination(movies_data, time_window, current_page):
    """
    Hiển thị kết quả trending movies với phân trang
    
    Args:
        movies_data (dict): Dữ liệu phim từ TMDB API
        time_window (str): Khoảng thời gian (day hoặc week)
        current_page (int): Trang hiện tại
    """
    try:
        results = movies_data.get('results', [])
        total_pages = movies_data.get('total_pages', 1)
        total_results = movies_data.get('total_results', 0)
        
        # Hiển thị thông tin phân trang
        page_info = f"Trang {current_page}/{total_pages} ({len(results)}/{total_results} phim)"
        
        # Hiển thị kết quả phim
        display_search_results(movies_data, None, f"Trending Movies ({time_window}) - {page_info}")
        
        # Thêm nút phân trang
        add_pagination_items(time_window, current_page, total_pages)
        
    except Exception as e:
        logError(f"Error displaying trending results with pagination: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def add_pagination_items(time_window, current_page, total_pages):
    """
    Thêm các nút phân trang
    
    Args:
        time_window (str): Khoảng thời gian (day hoặc week)
        current_page (int): Trang hiện tại
        total_pages (int): Tổng số trang
    """
    try:
        # Luôn hiển thị thông tin trang hiện tại
        info_url = f"plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window={time_window}&page={current_page}"
        info_item = xbmcgui.ListItem(f"[COLOR white]📄 Trang {current_page}/{total_pages}[/COLOR]")
        info_item.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), info_url, info_item, isFolder=False)
        
        # Nút trang trước
        if current_page > 1:
            prev_page = current_page - 1
            prev_url = f"plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window={time_window}&page={prev_page}"
            prev_item = xbmcgui.ListItem(f"[COLOR yellow]← Trang Trước ({prev_page})[/COLOR]")
            prev_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), prev_url, prev_item, isFolder=True)
        else:
            # Hiển thị nút disabled khi ở trang đầu
            disabled_item = xbmcgui.ListItem(f"[COLOR gray]← Trang Trước (Không có)[/COLOR]")
            disabled_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), info_url, disabled_item, isFolder=False)
        
        # Nút trang tiếp theo
        if current_page < total_pages:
            next_page = current_page + 1
            next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window={time_window}&page={next_page}"
            next_item = xbmcgui.ListItem(f"[COLOR yellow]Trang Tiếp ({next_page}) →[/COLOR]")
            next_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), next_url, next_item, isFolder=True)
        else:
            # Hiển thị nút disabled khi ở trang cuối
            disabled_item = xbmcgui.ListItem(f"[COLOR gray]Trang Tiếp (Không có) →[/COLOR]")
            disabled_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), info_url, disabled_item, isFolder=False)
        
        # Nút chuyển đến trang cụ thể (luôn hiển thị nếu có nhiều hơn 1 trang)
        if total_pages > 1:
            goto_url = f"plugin://plugin.video.vietmediaF?action=tmdb_trending_goto_page&time_window={time_window}&current_page={current_page}&total_pages={total_pages}"
            goto_item = xbmcgui.ListItem(f"[COLOR cyan]🔢 Chuyển đến trang...[/COLOR]")
            goto_item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), goto_url, goto_item, isFolder=True)
        
    except Exception as e:
        logError(f"Error adding pagination items: {str(e)}")

# ════════════════════════════════════════════════════════════════════
# NEW FEATURES: Discover, Now Playing, Upcoming, Top Rated
# ════════════════════════════════════════════════════════════════════

def get_discover(media_type, genre_id, page=1):
    """
    Lấy danh sách phim/TV theo thể loại từ Backend API
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
        genre_id (int): ID thể loại
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim/TV theo thể loại
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/discover/{media_type}?genre={genre_id}&page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting discover: {str(e)}")
        return None

def get_now_playing(page=1):
    """
    Lấy danh sách phim đang chiếu từ Backend API
    
    Args:
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim đang chiếu
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/now-playing?page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting now playing: {str(e)}")
        return None

def get_upcoming(page=1):
    """
    Lấy danh sách phim sắp chiếu từ Backend API
    
    Args:
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim sắp chiếu
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/upcoming?page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting upcoming: {str(e)}")
        return None

def get_top_rated(media_type, page=1):
    """
    Lấy danh sách phim/TV đánh giá cao nhất từ Backend API
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
        page (int): Trang kết quả
    
    Returns:
        dict: Dữ liệu phim/TV đánh giá cao
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/top-rated/{media_type}?page={page}&lang={lang}"
        return call_backend_tmdb(endpoint)
    except Exception as e:
        logError(f"Error getting top rated: {str(e)}")
        return None

def get_genres_list(media_type):
    """
    Lấy danh sách thể loại từ Backend API
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
    
    Returns:
        list: Danh sách thể loại [{id, name}, ...]
    """
    try:
        lang = get_tmdb_language()
        endpoint = f"/api/tmdb/genres/{media_type}?lang={lang}"
        data = call_backend_tmdb(endpoint)
        if data and 'genres' in data:
            return data['genres']
        return []
    except Exception as e:
        logError(f"Error getting genres: {str(e)}")
        return []

def show_discover_menu(media_type="movie"):
    """
    Hiển thị menu chọn thể loại để discover
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
    """
    try:
        media_label = "Phim" if media_type == "movie" else "TV Series"
        notify(f"Đang tải danh sách thể loại {media_label}...")
        
        genres = get_genres_list(media_type)
        if not genres:
            alert("Không thể tải danh sách thể loại. Vui lòng thử lại.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            return
        
        for genre in genres:
            genre_name = genre.get('name', 'Unknown')
            genre_id = genre.get('id', 0)
            
            url = f"plugin://plugin.video.vietmediaF?action=tmdb_discover_results&media_type={media_type}&genre_id={genre_id}&page=1"
            list_item = xbmcgui.ListItem(label=f"[COLOR yellow]{genre_name}[/COLOR]")
            list_item.setProperty('IsPlayable', 'false')
            info_tag = list_item.getVideoInfoTag()
            info_tag.setPlot(f"{media_label} thể loại {genre_name}")
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, list_item, isFolder=True)
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
        
    except Exception as e:
        logError(f"Error showing discover menu: {str(e)}")
        alert(f"Lỗi hiển thị discover menu: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_discover(media_type, genre_id, page=1):
    """
    Hiển thị kết quả discover theo thể loại
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
        genre_id (int): ID thể loại
        page (int): Trang kết quả
    """
    try:
        media_label = "phim" if media_type == "movie" else "TV series"
        notify(f"Đang tải {media_label} theo thể loại...")
        
        data = get_discover(media_type, genre_id, page)
        
        if data and data.get('results'):
            # Lọc kết quả theo cache backend
            notify("Đang kiểm tra cache backend...")
            if media_type == "movie":
                filtered_data, _, error_message = filter_cached_results(data, None)
            else:
                _, filtered_data, error_message = filter_cached_results(None, data)
            
            if error_message:
                alert(f"⚠️ {error_message}")
            
            if filtered_data and filtered_data.get('results'):
                total_pages = data.get('total_pages', 1)
                total_results = data.get('total_results', 0)
                count_info = f"({len(filtered_data['results'])}/{total_results})"
                
                display_search_results(
                    filtered_data if media_type == "movie" else None,
                    filtered_data if media_type == "tv" else None,
                    f"Discover {media_label} - {count_info}",
                    close_directory=False
                )
                
                # Thêm nút phân trang và nút về trang chính
                next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_discover_results&media_type={media_type}&genre_id={genre_id}&page={page + 1}"
                add_paging_nav(page, total_pages, next_url)
            else:
                alert(f"Không tìm thấy {media_label} nào trong cache cho thể loại này.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert(f"Không tìm thấy {media_label} nào.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing discover: {str(e)}")
        alert(f"Lỗi discover: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_now_playing(page=1):
    """
    Hiển thị danh sách phim đang chiếu
    Lọc cache vì phim đang chiếu đã phát hành, có thể có link download
    
    Args:
        page (int): Trang kết quả
    """
    try:
        notify("Đang tải phim đang chiếu...")
        
        data = get_now_playing(page)
        
        if data and data.get('results'):
            notify("Đang kiểm tra cache backend...")
            filtered_data, _, error_message = filter_cached_results(data, None)
            
            if error_message:
                alert(f"⚠️ {error_message}")
            
            if filtered_data and filtered_data.get('results'):
                total_pages = data.get('total_pages', 1)
                total_results = data.get('total_results', 0)
                count_info = f"({len(filtered_data['results'])}/{total_results})"
                
                display_search_results(filtered_data, None, f"Phim Đang Chiếu - {count_info}", close_directory=False)
                
                # Thêm nút phân trang và nút về trang chính
                next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_now_playing&page={page + 1}"
                add_paging_nav(page, total_pages, next_url)
            else:
                alert("Không tìm thấy phim đang chiếu nào trong cache.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert("Không tìm thấy phim đang chiếu.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing now playing: {str(e)}")
        alert(f"Lỗi phim đang chiếu: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_upcoming(page=1):
    """
    Hiển thị danh sách phim sắp chiếu
    Không lọc cache vì phim sắp chiếu chưa có link download
    
    Args:
        page (int): Trang kết quả
    """
    try:
        notify("Đang tải phim sắp chiếu...")
        
        data = get_upcoming(page)
        
        if data and data.get('results'):
            total_pages = data.get('total_pages', 1)
            total_results = data.get('total_results', 0)
            count_info = f"({len(data['results'])}/{total_results})"
            
            display_search_results(data, None, f"Phim Sắp Chiếu - {count_info}", close_directory=False)
            
            # Thêm nút phân trang và nút về trang chính
            next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_upcoming&page={page + 1}"
            add_paging_nav(page, total_pages, next_url)
        else:
            alert("Không tìm thấy phim sắp chiếu.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing upcoming: {str(e)}")
        alert(f"Lỗi phim sắp chiếu: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)

def show_top_rated(media_type="movie", page=1):
    """
    Hiển thị danh sách phim/TV đánh giá cao nhất
    
    Args:
        media_type (str): Loại media (movie hoặc tv)
        page (int): Trang kết quả
    """
    try:
        media_label = "phim" if media_type == "movie" else "TV series"
        notify(f"Đang tải {media_label} đánh giá cao nhất...")
        
        data = get_top_rated(media_type, page)
        
        if data and data.get('results'):
            notify("Đang kiểm tra cache backend...")
            if media_type == "movie":
                filtered_data, _, error_message = filter_cached_results(data, None)
            else:
                _, filtered_data, error_message = filter_cached_results(None, data)
            
            if error_message:
                alert(f"⚠️ {error_message}")
            
            if filtered_data and filtered_data.get('results'):
                total_pages = data.get('total_pages', 1)
                total_results = data.get('total_results', 0)
                count_info = f"({len(filtered_data['results'])}/{total_results})"
                
                display_search_results(
                    filtered_data if media_type == "movie" else None,
                    filtered_data if media_type == "tv" else None,
                    f"Top Rated {media_label} - {count_info}",
                    close_directory=False
                )
                
                # Thêm nút phân trang và nút về trang chính
                next_url = f"plugin://plugin.video.vietmediaF?action=tmdb_top_rated&media_type={media_type}&page={page + 1}"
                add_paging_nav(page, total_pages, next_url)
            else:
                alert(f"Không tìm thấy {media_label} nào trong cache.")
                xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
        else:
            alert(f"Không tìm thấy {media_label} nào.")
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing top rated: {str(e)}")
        alert(f"Lỗi top rated: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
