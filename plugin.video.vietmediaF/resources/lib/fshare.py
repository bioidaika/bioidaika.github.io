


import os
import re
import json
import time
import requests
import urllib.parse
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

from resources.lib.constants import *
from resources.lib.utils import log, notify, alert, extract_fshare_code, load_from_cache, save_to_cache

class FshareAPI:
    """
    Class xử lý các tương tác với API của Fshare
    """
    def __init__(self):
        self.token = ADDON.getSetting('tokenfshare')
        self.session_id = ADDON.getSetting('sessionfshare')
        self.username = ADDON.getSetting('fshare_username')
        self.password = ADDON.getSetting('fshare_password')
        self.user_agent = USER_AGENT
        self.logged_in = False

        
        if self.token and self.session_id:
            self.logged_in = True

    def check_login(self):
        """
        Kiểm tra trạng thái đăng nhập

        Returns:
            Boolean: True nếu đã đăng nhập, False nếu chưa đăng nhập
        """
        if not self.logged_in:
            
            return self.login()

        
        try:
            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }
            response = requests.get(FSHARE_PROFILE_API, headers=headers)

            if response.status_code == 200:
                return True
            else:
                
                return self.login()
        except Exception as e:
            log(f"Lỗi khi kiểm tra đăng nhập: {str(e)}", xbmc.LOGERROR)
            return self.login()

    def login(self):
        """
        Đăng nhập vào tài khoản Fshare

        Returns:
            Boolean: True nếu đăng nhập thành công, False nếu thất bại
        """
        if not self.username or not self.password:
            notify("Vui lòng nhập tài khoản và mật khẩu Fshare", ADDON_NAME)
            ADDON.openSettings()
            self.username = ADDON.getSetting('fshare_username')
            self.password = ADDON.getSetting('fshare_password')

            if not self.username or not self.password:
                return False

        
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create('Đang đăng nhập', 'Đang kết nối đến Fshare...')
        progress_dialog.update(30)

        try:
            
            login_data = {
                'user_email': self.username,
                'password': self.password,
                'app_key': 'L2S7R6ZMagggC5wWkQhX2+aDi467PPuftWUMRFSn'
            }

            
            headers = {
                'User-Agent': self.user_agent
            }

            progress_dialog.update(60, 'Đang xác thực tài khoản...')

            response = requests.post(FSHARE_LOGIN_API, json=login_data, headers=headers)

            if response.status_code == 200:
                
                data = response.json()

                
                self.token = data.get('token', '')
                self.session_id = data.get('session_id', '')

                
                ADDON.setSetting('tokenfshare', self.token)
                ADDON.setSetting('sessionfshare', self.session_id)

                self.logged_in = True

                progress_dialog.update(100, 'Đăng nhập thành công')
                progress_dialog.close()

                return True
            else:
                
                progress_dialog.close()

                error_message = "Đăng nhập thất bại"
                try:
                    error_data = response.json()
                    if 'msg' in error_data:
                        error_message = error_data['msg']
                except:
                    pass

                notify(error_message, ADDON_NAME)
                return False
        except Exception as e:
            progress_dialog.close()
            log(f"Lỗi khi đăng nhập: {str(e)}", xbmc.LOGERROR)
            notify(f"Lỗi khi đăng nhập: {str(e)}", ADDON_NAME)
            return False

    def get_account_info(self):
        """
        Lấy thông tin tài khoản

        Returns:
            Dictionary: Thông tin tài khoản hoặc None nếu có lỗi
        """
        if not self.check_login():
            return None

        try:
            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            response = requests.get(FSHARE_PROFILE_API, headers=headers)

            if response.status_code == 200:
                data = response.json()

                
                account_info = {
                    'email': data.get('email', ''),
                    'account_type': 'VIP' if data.get('account_type', 0) > 0 else 'Free',
                    'expire_date': data.get('expire_vip', 'N/A'),
                    'traffic_used': float(data.get('traffic_used', 0)) / (1024 * 1024 * 1024),  
                    'webspace_used': float(data.get('webspace_used', 0)) / (1024 * 1024 * 1024),  
                    'webspace_total': float(data.get('webspace_total', 0)) / (1024 * 1024 * 1024)  
                }

                return account_info
            else:
                return None
        except Exception as e:
            log(f"Lỗi khi lấy thông tin tài khoản: {str(e)}", xbmc.LOGERROR)
            return None

    def get_direct_link(self, url):
        """
        Lấy link trực tiếp để phát media

        Args:
            url: URL Fshare

        Returns:
            String: Link trực tiếp hoặc None nếu có lỗi
        """
        if not self.check_login():
            return None

        
        file_code = extract_fshare_code(url)
        if not file_code:
            notify('URL không hợp lệ', ADDON_NAME)
            return None

        
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create('Đang lấy link phát', 'Đang kết nối đến Fshare...')
        progress_dialog.update(30)

        try:
            
            
            modified_url = url
            if "?" not in modified_url:
                modified_url = modified_url + "?share=3053519"
            else:
                modified_url = modified_url + "&share=3053519"

            download_data = {
                'url': modified_url,
                'token': self.token,
                'password': ''
            }

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            progress_dialog.update(60, 'Đang lấy link phát...')

            response = requests.post(FSHARE_DOWNLOAD_API, json=download_data, headers=headers)

            if response.status_code == 200:
                data = response.json()

                
                direct_link = data.get('location', '')

                if direct_link:
                    progress_dialog.update(100, 'Đã lấy link phát thành công')
                    progress_dialog.close()

                    return direct_link, progress_dialog
                else:
                    progress_dialog.close()
                    notify('Không thể lấy được link phát', ADDON_NAME)
                    return None
            else:
                progress_dialog.close()

                error_message = "Không thể lấy được link phát"
                try:
                    error_data = response.json()
                    if 'msg' in error_data:
                        error_message = error_data['msg']
                except:
                    pass

                notify(error_message, ADDON_NAME)
                return None
        except Exception as e:
            progress_dialog.close()
            log(f"Lỗi khi lấy link phát: {str(e)}", xbmc.LOGERROR)
            notify(f"Lỗi khi lấy link phát: {str(e)}", ADDON_NAME)
            return None

    def get_file_info(self, file_code):
        """
        Lấy thông tin chi tiết về file

        Args:
            file_code: Mã code Fshare

        Returns:
            Dictionary: Thông tin file hoặc None nếu có lỗi
        """
        if not self.check_login():
            return None

        try:
            
            api_url = f"https://api.fshare.vn/api/fileops/get?linkcode={file_code}"

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            log(f"Lỗi khi lấy thông tin file: {str(e)}", xbmc.LOGERROR)
            return None

    def search(self, keyword, page=1, limit=MAX_SEARCH_RESULTS):
        """
        Tìm kiếm nội dung trên Fshare

        Args:
            keyword: Từ khóa tìm kiếm
            page: Số trang (bắt đầu từ 1)
            limit: Số lượng kết quả tối đa

        Returns:
            List: Danh sách kết quả tìm kiếm hoặc [] nếu không có kết quả
        """
        if not self.check_login():
            return []

        
        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create('Đang tìm kiếm', f'Đang tìm kiếm "{keyword}"...')
        progress_dialog.update(30)

        try:
            
            search_data = {
                'token': self.token,
                'name': keyword,
                'dirOnly': 0,
                'pageIndex': page,
                'limit': limit
            }

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            progress_dialog.update(60, 'Đang xử lý kết quả tìm kiếm...')

            response = requests.post(FSHARE_SEARCH_API, json=search_data, headers=headers)

            if response.status_code == 200:
                data = response.json()

                progress_dialog.update(100, 'Đã tìm kiếm xong')
                progress_dialog.close()

                return data
            else:
                progress_dialog.close()
                notify('Không thể tìm kiếm', ADDON_NAME)
                return []
        except Exception as e:
            progress_dialog.close()
            log(f"Lỗi khi tìm kiếm: {str(e)}", xbmc.LOGERROR)
            notify(f"Lỗi khi tìm kiếm: {str(e)}", ADDON_NAME)
            return []

    def get_folder_list(self, url, dir_only=0, page_index=0, limit=100):
        """
        Lấy danh sách nội dung trong thư mục

        Args:
            url: URL thư mục Fshare
            dir_only: Chỉ lấy thư mục (0: lấy cả file và thư mục, 1: chỉ lấy thư mục)
            page_index: Số trang (bắt đầu từ 0)
            limit: Số lượng kết quả tối đa

        Returns:
            List: Danh sách nội dung trong thư mục hoặc [] nếu không có kết quả
        """
        if not self.check_login():
            return []

        
        folder_code = extract_fshare_code(url)
        if not folder_code:
            notify('URL không hợp lệ', ADDON_NAME)
            return []

        
        cache_key = f"folder_{folder_code}_{dir_only}_{page_index}_{limit}"

        
        cache_data = load_from_cache(cache_key, 3600)  
        if cache_data:
            return cache_data

        try:
            
            folder_data = {
                'token': self.token,
                'url': url,
                'dirOnly': dir_only,
                'pageIndex': page_index,
                'limit': limit
            }

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            response = requests.post(FSHARE_FOLDER_API, json=folder_data, headers=headers)

            if response.status_code == 200:
                data = response.json()           
                save_to_cache(cache_key, data)
                return data
            else:
                return []
        except Exception as e:
            log(f"Lỗi khi lấy danh sách thư mục: {str(e)}", xbmc.LOGERROR)
            return []

    def get_favourite(self, page=1):
        """
        Lấy danh sách yêu thích

        Args:
            page: Số trang (bắt đầu từ 1)

        Returns:
            List: Danh sách các mục yêu thích hoặc [] nếu không có kết quả
        """
        if not self.check_login():
            return []

        try:
            
            api_url = f"{FSHARE_FAVOURITE_API}?page={page}"

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            log(f"Lỗi khi lấy danh sách yêu thích: {str(e)}", xbmc.LOGERROR)
            return []

    def add_remove_favourite(self, linkcode, action):
        """
        Thêm hoặc xóa mục khỏi danh sách yêu thích

        Args:
            linkcode: Mã code Fshare
            action: Hành động (1: thêm, 0: xóa)

        Returns:
            Boolean: True nếu thành công, False nếu thất bại
        """
        if not self.check_login():
            return False

        try:
            
            api_url = "https://api.fshare.vn/api/fileops/changeFavourite"

            
            data = {
                'token': self.token,
                'linkcode': linkcode,
                'action': action
            }

            
            headers = {
                'User-Agent': self.user_agent,
                'Cookie': f'session_id={self.session_id}'
            }

            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            log(f"Lỗi khi thêm/xóa yêu thích: {str(e)}", xbmc.LOGERROR)
            return False

    def play_file(self, url):
        """
        Lấy link trực tiếp và chuẩn bị phát file

        Args:
            url: URL Fshare

        Returns:
            String: Link trực tiếp hoặc None nếu có lỗi
        """
        
        result = self.get_direct_link(url)

        if result:
            return result
        else:
            return None


fshare = FshareAPI()
