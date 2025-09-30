#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import threading
import queue
import xbmc
import xbmcaddon
import xbmcgui
import requests
from urllib.parse import urlparse
import hashlib
import re

# Import các module cần thiết từ addon
from resources import cache_utils
from resources.thuviencine import parse_csv_data

# Tránh import vòng tròn (circular import)
# Sẽ import session và process_sheet_data_for_section khi cần sử dụng

# Lấy thông tin addon
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')

# Định nghĩa các URL cần preload và mức độ ưu tiên
PRELOAD_URLS = [
    {"url": "https://thuviencine.com/top/", "priority": 1},  # Ưu tiên cao nhất
    {"url": "https://thuviencine.com/movies/", "priority": 2},  # Ưu tiên trung bình
    {"url": "https://thuviencine.com/tv-series/", "priority": 3}  # Ưu tiên thấp nhất
]

# Thời gian cache hợp lệ (3 giờ)
CACHE_VALID_TIME = 3 * 60 * 60

# Số lần thử lại tối đa khi gặp lỗi
MAX_RETRIES = 3

# Thời gian chờ giữa các lần thử lại (giây)
RETRY_DELAY = 5

# Số lượng thread tối đa cho việc tải hình ảnh
MAX_IMAGE_THREADS = 2

# Thời gian chờ giữa các request hình ảnh (giây)
IMAGE_REQUEST_DELAY = 0.5

def log(message, level=xbmc.LOGINFO):
    """Ghi log với prefix để dễ dàng lọc"""
    try:
        xbmc.log(f"[VietmediaF Preload] {message}", level)
    except Exception:
        # Fallback nếu có lỗi với xbmc.log
        print(f"[VietmediaF Preload] {message}")

class PreloadManager:
    """Quản lý việc preload dữ liệu trong nền"""

    def __init__(self):
        """Khởi tạo PreloadManager"""
        self.preload_thread = None
        self.image_threads = []
        self.image_queue = queue.PriorityQueue()
        self.stop_event = threading.Event()
        self.preload_urls = sorted(PRELOAD_URLS, key=lambda x: x["priority"])

        # Import session từ tvcine để tránh import vòng tròn
        from resources.tvcine import session
        self.session = session

        log("PreloadManager initialized")

    def start(self):
        """Bắt đầu quá trình preload trong nền"""
        if self.preload_thread is not None and self.preload_thread.is_alive():
            log("Preload already running, skipping", xbmc.LOGWARNING)
            return

        # Reset stop event
        self.stop_event.clear()

        # Khởi tạo thread preload chính
        self.preload_thread = threading.Thread(target=self._preload_worker)
        self.preload_thread.daemon = True
        self.preload_thread.start()

        # Khởi tạo các thread tải hình ảnh
        for i in range(MAX_IMAGE_THREADS):
            thread = threading.Thread(target=self._image_worker, args=(i,))
            thread.daemon = True
            thread.start()
            self.image_threads.append(thread)

        log(f"Started preload with {len(self.image_threads)} image threads")

    def stop(self):
        """Dừng quá trình preload"""
        if self.preload_thread is None or not self.preload_thread.is_alive():
            return

        log("Stopping preload process")
        self.stop_event.set()

        # Chờ thread preload kết thúc
        if self.preload_thread:
            self.preload_thread.join(timeout=1.0)

        # Đảm bảo queue hình ảnh trống
        while not self.image_queue.empty():
            try:
                self.image_queue.get_nowait()
                self.image_queue.task_done()
            except queue.Empty:
                break

        # Chờ các thread hình ảnh kết thúc
        for thread in self.image_threads:
            thread.join(timeout=1.0)

        self.image_threads = []
        log("Preload process stopped")

    def _preload_worker(self):
        """Worker chính cho quá trình preload"""
        log("Starting preload worker")

        for url_info in self.preload_urls:
            if self.stop_event.is_set():
                log("Preload worker stopped by request")
                return

            url = url_info["url"]
            priority = url_info["priority"]

            log(f"Preloading URL: {url} (Priority: {priority})")

            # Kiểm tra xem dữ liệu đã được cache chưa và còn hợp lệ không
            cache_key = self._get_preload_cache_key(url)
            if self._is_cache_valid(cache_key):
                log(f"Using valid cache for {url}")
                continue

            # Thử tải dữ liệu với số lần thử lại
            for attempt in range(MAX_RETRIES):
                try:
                    # Tải dữ liệu
                    data = self._load_data(url)
                    if not data:
                        log(f"No data returned for {url}, attempt {attempt+1}/{MAX_RETRIES}", xbmc.LOGWARNING)
                        time.sleep(RETRY_DELAY)
                        continue

                    # Lưu vào cache
                    self._save_to_cache(cache_key, data)

                    # Thêm hình ảnh vào queue để tải
                    self._queue_images(data, priority)

                    log(f"Successfully preloaded {url}")
                    break
                except Exception as e:
                    log(f"Error preloading {url}, attempt {attempt+1}/{MAX_RETRIES}: {str(e)}", xbmc.LOGERROR)
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)

        # Hiển thị thông báo khi hoàn thành
        try:
            xbmcgui.Dialog().notification(
                ADDON_NAME,
                "Preload hoàn tất! Dữ liệu đã được tải trước.",
                xbmcgui.NOTIFICATION_INFO,
                3000,  # Hiển thị trong 3 giây
                False  # Không phát âm thanh
            )
        except Exception as e:
            log(f"Không thể hiển thị thông báo: {str(e)}", xbmc.LOGWARNING)

        log("Preload worker finished")

    def _image_worker(self, worker_id):
        """Worker cho việc tải hình ảnh"""
        log(f"Starting image worker {worker_id}")

        while not self.stop_event.is_set():
            try:
                # Lấy URL hình ảnh từ queue với timeout
                priority, img_url = self.image_queue.get(timeout=1.0)

                # Kiểm tra xem hình ảnh đã được cache chưa
                img_cache_key = self._get_image_cache_key(img_url)
                if self._is_image_cached(img_cache_key):
                    log(f"Image already cached: {img_url}", xbmc.LOGDEBUG)
                    self.image_queue.task_done()
                    continue

                # Tải hình ảnh
                try:
                    log(f"Worker {worker_id} downloading image: {img_url}", xbmc.LOGDEBUG)
                    response = self.session.get(img_url, timeout=10)
                    if response.status_code == 200:
                        # Lưu hình ảnh vào cache
                        self._save_image_to_cache(img_cache_key, response.content)
                        log(f"Image cached: {img_url}", xbmc.LOGDEBUG)
                    else:
                        log(f"Failed to download image {img_url}, status: {response.status_code}", xbmc.LOGWARNING)
                except Exception as e:
                    log(f"Error downloading image {img_url}: {str(e)}", xbmc.LOGWARNING)

                # Đánh dấu task hoàn thành
                self.image_queue.task_done()

                # Chờ một chút để không quá tải server
                time.sleep(IMAGE_REQUEST_DELAY)

            except queue.Empty:
                # Queue rỗng, chờ một chút
                time.sleep(0.5)
            except Exception as e:
                log(f"Error in image worker {worker_id}: {str(e)}", xbmc.LOGERROR)
                time.sleep(1.0)

        log(f"Image worker {worker_id} stopped")

    def _load_data(self, url):
        """Tải dữ liệu từ URL"""
        # Log URL để debug
        log(f"Loading data for URL: {url}", xbmc.LOGINFO)

        # Kiểm tra xem URL có kết thúc bằng / không
        if not url.endswith('/'):
            log(f"URL does not end with /, adding it: {url}/", xbmc.LOGWARNING)
            url = url + '/'

        # Log cache key để debug
        cache_key = self._get_preload_cache_key(url)
        log(f"Cache key for URL {url}: {cache_key}", xbmc.LOGINFO)

        # Kiểm tra xem URL có phải là một trong các mục chính không
        if url in [item["url"] for item in PRELOAD_URLS]:
            # Sử dụng process_sheet_data_for_section cho các mục chính
            try:
                # Import process_sheet_data_for_section để tránh import vòng tròn
                from resources.tvcine import process_sheet_data_for_section

                log(f"Using process_sheet_data_for_section for {url}")
                data = process_sheet_data_for_section(url)
                if data:
                    log(f"Successfully loaded data for {url} using process_sheet_data_for_section")
                    # Log cache key để debug
                    cache_key = self._get_preload_cache_key(url)
                    log(f"Will save data to cache with key: {cache_key}")
                    return data
                log(f"process_sheet_data_for_section returned no data for {url}, falling back to direct loading", xbmc.LOGWARNING)
            except Exception as e:
                log(f"Error in process_sheet_data_for_section for {url}: {str(e)}", xbmc.LOGERROR)

        # Fallback hoặc cho các URL khác, sử dụng listMovie trực tiếp
        try:
            # Import listMovie để tránh import vòng tròn
            from resources.tvcine import listMovie

            log(f"Using listMovie for {url}")
            data = listMovie(url)
            if data:
                log(f"Successfully loaded data for {url} using listMovie")
                # Log cache key để debug
                cache_key = self._get_preload_cache_key(url)
                log(f"Will save data to cache with key: {cache_key}")
            return data
        except Exception as e:
            log(f"Error in listMovie for {url}: {str(e)}", xbmc.LOGERROR)
            return None

    def _queue_images(self, data, priority):
        """Thêm các URL hình ảnh vào queue để tải"""
        if not data or "items" not in data:
            return

        for item in data["items"]:
            # Thêm thumbnail
            if "thumbnail" in item and item["thumbnail"]:
                self.image_queue.put((priority, item["thumbnail"]))

            # Thêm các hình ảnh từ art
            if "art" in item:
                for art_type, art_url in item["art"].items():
                    if art_url and isinstance(art_url, str):
                        self.image_queue.put((priority, art_url))

    def _get_preload_cache_key(self, url):
        """Tạo cache key cho dữ liệu preload"""
        return f"preload_{hashlib.md5(url.encode()).hexdigest()}"

    def _get_image_cache_key(self, img_url):
        """Tạo cache key cho hình ảnh"""
        return f"img_{hashlib.md5(img_url.encode()).hexdigest()}"

    def _save_to_cache(self, cache_key, data):
        """Lưu dữ liệu vào cache"""
        # Thêm timestamp để kiểm tra tính hợp lệ sau này
        cache_data = {
            "timestamp": int(time.time()),
            "data": data
        }

        # Kiểm tra xem có nên xóa cache cũ không
        should_remove_cache = False

        if cache_utils.check_cache(cache_key):
            try:
                old_cache = cache_utils.get_cache(cache_key)
                if not old_cache or not isinstance(old_cache, dict) or "data" not in old_cache:
                    should_remove_cache = True
                    log(f"Invalid cache format found for key: {cache_key}, will remove", xbmc.LOGINFO)
            except Exception as e:
                should_remove_cache = True
                log(f"Error checking old cache: {str(e)}, will remove", xbmc.LOGWARNING)

        # Xóa cache cũ nếu cần
        if should_remove_cache and cache_utils.check_cache(cache_key):
            try:
                cache_utils.remove_cache(cache_key)
                log(f"Removed old cache with key: {cache_key}", xbmc.LOGINFO)
            except Exception as e:
                log(f"Error removing old cache: {str(e)}", xbmc.LOGWARNING)

        # Lưu dữ liệu mới vào cache
        success = cache_utils.set_cache(cache_key, cache_data)
        if success:
            log(f"Successfully saved data to cache with key: {cache_key}")
        else:
            log(f"Failed to save data to cache with key: {cache_key}", xbmc.LOGWARNING)

    def _save_image_to_cache(self, cache_key, image_data):
        """Lưu hình ảnh vào cache"""
        # Sử dụng cache_utils để lưu dữ liệu nhị phân
        cache_utils.set_binary_cache(cache_key, image_data)

    def _is_cache_valid(self, cache_key):
        """Kiểm tra xem cache có hợp lệ không"""
        if not cache_utils.check_cache(cache_key):
            return False

        try:
            cache_data = cache_utils.get_cache(cache_key)
            if not cache_data or "timestamp" not in cache_data:
                return False

            # Kiểm tra thời gian
            timestamp = cache_data["timestamp"]
            current_time = int(time.time())

            # Cache hợp lệ nếu chưa quá hạn
            return (current_time - timestamp) < CACHE_VALID_TIME
        except Exception as e:
            log(f"Error checking cache validity: {str(e)}", xbmc.LOGWARNING)
            return False

    def _is_image_cached(self, img_cache_key):
        """Kiểm tra xem hình ảnh đã được cache chưa"""
        return cache_utils.check_binary_cache(img_cache_key)

# Singleton instance và trạng thái đã khởi động
_preload_manager = None
_preload_started = False
_preload_last_run = 0  # Thời gian lần cuối chạy preload

# Tạo cache key cho trạng thái preload
PRELOAD_STATUS_CACHE_KEY = "preload_status"

def save_preload_status():
    """Lưu trạng thái preload vào cache"""
    global _preload_started, _preload_last_run
    status = {
        "started": _preload_started,
        "last_run": _preload_last_run
    }
    try:
        cache_utils.set_cache(PRELOAD_STATUS_CACHE_KEY, status)
        log(f"Lưu trạng thái preload: {status}", xbmc.LOGINFO)
    except Exception as e:
        log(f"Lỗi khi lưu trạng thái preload: {str(e)}", xbmc.LOGWARNING)

def load_preload_status():
    """Tải trạng thái preload từ cache"""
    global _preload_started, _preload_last_run
    try:
        status = cache_utils.get_cache(PRELOAD_STATUS_CACHE_KEY)
        if status:
            _preload_started = status.get("started", False)
            _preload_last_run = status.get("last_run", 0)
            log(f"Tải trạng thái preload: {status}", xbmc.LOGINFO)
            return True
    except Exception as e:
        log(f"Lỗi khi tải trạng thái preload: {str(e)}", xbmc.LOGWARNING)
    return False

def get_preload_manager():
    """Lấy instance của PreloadManager (singleton)"""
    global _preload_manager
    if _preload_manager is None:
        _preload_manager = PreloadManager()
    return _preload_manager

def is_preload_started():
    """Kiểm tra xem preload đã được khởi động chưa"""
    global _preload_started
    return _preload_started

def should_run_preload():
    """Kiểm tra xem có nên chạy preload không"""
    global _preload_last_run

    # Tải trạng thái preload từ cache
    load_preload_status()

    # Lấy thời gian hiện tại
    current_time = int(time.time())

    # Nếu chưa bao giờ chạy preload hoặc đã quá 3 giờ kể từ lần cuối
    if _preload_last_run == 0 or (current_time - _preload_last_run) >= CACHE_VALID_TIME:
        log(f"Nên chạy preload: lần cuối chạy cách đây {(current_time - _preload_last_run)} giây", xbmc.LOGINFO)
        return True

    log(f"Không cần chạy preload: lần cuối chạy cách đây {(current_time - _preload_last_run)} giây", xbmc.LOGINFO)
    return False

def get_preloaded_data(url):
    """Lấy dữ liệu đã preload cho URL"""
    # Log URL để debug
    log(f"Trying to get preloaded data for URL: {url}", xbmc.LOGINFO)

    # Kiểm tra xem URL có kết thúc bằng / không
    if not url.endswith('/'):
        log(f"URL does not end with /, adding it: {url}/", xbmc.LOGWARNING)
        url = url + '/'

    # Kiểm tra xem URL có trong danh sách các URL cần preload không
    is_preload_url = url in [item["url"] for item in PRELOAD_URLS]
    log(f"URL {url} is in preload list: {is_preload_url}", xbmc.LOGINFO)

    # Tạo cache key giống với hàm _get_preload_cache_key
    cache_key = f"preload_{hashlib.md5(url.encode()).hexdigest()}"

    # Kiểm tra cache
    if not cache_utils.check_cache(cache_key):
        log(f"No cache found for key: {cache_key}", xbmc.LOGINFO)
        return None

    try:
        log(f"Cache found for key: {cache_key}, getting data", xbmc.LOGINFO)
        cache_data = cache_utils.get_cache(cache_key)
        if not cache_data or "data" not in cache_data:
            log("Cache data is invalid or missing 'data' key", xbmc.LOGWARNING)
            return None

        # Kiểm tra thời gian
        timestamp = cache_data.get("timestamp", 0)
        current_time = int(time.time())

        # Log thời gian để debug
        log(f"Cache timestamp: {timestamp}, current time: {current_time}, diff: {current_time - timestamp}s", xbmc.LOGINFO)

        # Nếu cache quá hạn, trả về None
        if (current_time - timestamp) >= CACHE_VALID_TIME:
            log(f"Cache expired, diff: {current_time - timestamp}s >= {CACHE_VALID_TIME}s", xbmc.LOGWARNING)
            return None

        log("Using valid preloaded data from cache", xbmc.LOGINFO)
        return cache_data["data"]
    except Exception as e:
        log(f"Error getting preloaded data: {str(e)}", xbmc.LOGWARNING)
        return None

def start_preload():
    """Bắt đầu quá trình preload"""
    global _preload_started, _preload_last_run

    # Kiểm tra xem có nên chạy preload không
    if not should_run_preload():
        log("Không cần chạy preload lúc này", xbmc.LOGINFO)
        return

    # Đánh dấu đã khởi động và cập nhật thời gian chạy
    _preload_started = True
    _preload_last_run = int(time.time())

    # Lưu trạng thái preload
    save_preload_status()

    # Khởi động preload manager
    manager = get_preload_manager()
    manager.start()
    log("Preload đã được khởi động", xbmc.LOGINFO)

def stop_preload():
    """Dừng quá trình preload"""
    global _preload_manager, _preload_started
    if _preload_manager is not None:
        _preload_manager.stop()
        _preload_manager = None

    # Đặt lại trạng thái khởi động
    _preload_started = False

    # Lưu trạng thái preload
    save_preload_status()

    log("Preload đã dừng", xbmc.LOGINFO)
