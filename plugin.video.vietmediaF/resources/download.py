import requests
import xbmcgui, xbmc, xbmcvfs
import time
import os, sys
import threading
import urllib.parse
import re

from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, PROFILE, log
from resources.fshare import get_download_link, check_session


def downloadfile(url):
    
    if url.startswith('plugin://') and 'url=' in url:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'url' in query_params and query_params['url']:
            url = query_params['url'][0]
            
            if '&d=__download__' in url:
                url = url.replace('&d=__download__', '')
    
    download_path = xbmcvfs.translatePath(ADDON.getSetting("download_path"))
    if not download_path:
        dialog = xbmcgui.Dialog()
        choice = dialog.yesno('Thiết lập đường dẫn', 'Đường dẫn lưu trữ chưa được thiết lập. Bạn có muốn thiết lập ngay bây giờ?')
        if choice:
            download_path = dialog.browse(3, 'Chọn đường dẫn lưu trữ', 'files')
            if download_path:
                ADDON.setSetting("download_path", download_path)
            else:
                return False
        else:
            return False
    
    
    direct_url = url
    if 'fshare.vn' in url.lower():
        log(f"Detected Fshare URL: {url}")
        notify("Đang lấy link trực tiếp từ Fshare...")
        
        
        token, session_id = check_session()
        if not token or not session_id:
            notify("Không thể đăng nhập vào Fshare. Vui lòng kiểm tra tài khoản.")
            return False
            
        
        direct_url = get_download_link(token, session_id, url)
        if not direct_url:
            notify("Không thể lấy link tải từ Fshare")
            return False
            
        log(f"Got Fshare direct URL: {direct_url}")
    
    log(f"Downloading file: {direct_url} to {download_path}")
    return download_file(direct_url, download_path)

def download_file(url, path):
    try:
        
        if not url.startswith(('http://', 'https://', 'ftp://')):
            notify('Lỗi URL', 'URL không hợp lệ: ' + url)
            return False
            
        response = requests.head(url, timeout=10)
        size = int(response.headers.get("Content-Length", 0))
        
        
        file_name = None
        if 'Content-Disposition' in response.headers:
            disposition = response.headers['Content-Disposition']
            file_name_match = re.search(r'filename="?([^"]+)"?', disposition)
            if file_name_match:
                file_name = file_name_match.group(1)
        
        if not file_name:
            file_name = url.split('/')[-1]
            
            if '?' in file_name:
                file_name = file_name.split('?')[0]
        
        
        if '.' not in file_name:
            file_name += '.mp4'  
            
        path = os.path.join(path, file_name)
        
        if xbmcvfs.exists(path):
            dialog = xbmcgui.Dialog()
            overwrite = dialog.yesno("File Exists", "Bạn có muốn xoá đè file cũ không?")
            if not overwrite:
                return False
                
        
        def download_thread():
            start_time = time.time()
            downloaded = 0
            last_update_time = 0
            download_method = int(ADDON.getSetting("download_method"))
            notification_interval = int(ADDON.getSetting("download_notification_interval"))
            
            
            progress_dialog = None
            if download_method == 1:  
                progress_dialog = xbmcgui.DialogProgress()
                progress_dialog.create(os.path.basename(path), "Tải xuống")
            
            try:
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                current_time = time.time()
                                
                                
                                if current_time - last_update_time >= notification_interval or download_method == 1:
                                    progress = int(downloaded / size * 100) if size > 0 else 0
                                    speed = downloaded / (current_time - start_time)
                                    time_left = (size - downloaded) / speed if speed > 0 else 0
                                    
                                    
                                    if speed < 1024:
                                        speed_str = f"{speed:.2f} B/s"
                                    elif speed < 1024 * 1024:
                                        speed_str = f"{speed/1024:.2f} KB/s"
                                    else:
                                        speed_str = f"{speed/(1024*1024):.2f} MB/s"
                                    
                                    
                                    if time_left < 60:
                                        time_left_str = f"{int(time_left)} giây"
                                    elif time_left < 3600:
                                        time_left_str = f"{int(time_left/60)} phút {int(time_left%60)} giây"
                                    else:
                                        time_left_str = f"{int(time_left/3600)} giờ {int((time_left%3600)/60)} phút"
                                    
                                    
                                    if size < 1024 * 1024:
                                        size_str = f"{size/1024:.2f} KB"
                                    else:
                                        size_str = f"{size/(1024*1024):.2f} MB"
                                    
                                    if downloaded < 1024 * 1024:
                                        downloaded_str = f"{downloaded/1024:.2f} KB"
                                    else:
                                        downloaded_str = f"{downloaded/(1024*1024):.2f} MB"
                                    
                                    
                                    if download_method == 0:  
                                        notify(f"Tải xuống: {progress}%")
                                    else:  
                                        
                                        message = f"Dung lượng: [COLOR orange]{size_str}[/COLOR]\n"
                                        message += f"Tiến độ: [COLOR orange]{downloaded_str}/{size_str} ({progress}%)[/COLOR]\n"
                                        message += f"Tốc độ: [COLOR orange]{speed_str}[/COLOR] | Còn lại: [COLOR orange]{time_left_str}[/COLOR]"
                                        
                                        
                                        progress_dialog.update(progress, message)
                                    
                                    last_update_time = current_time
                                
                                
                                if download_method == 1 and progress_dialog.iscanceled():
                                    progress_dialog.close()
                                    notify("Tải xuống đã hủy")
                                    if os.path.exists(path):
                                        os.remove(path)
                                    return
                                elif xbmc.Monitor().abortRequested():
                                    if download_method == 1:
                                        progress_dialog.close()
                                    notify("Tải xuống đã hủy")
                                    if os.path.exists(path):
                                        os.remove(path)
                                    return
                
                
                if download_method == 1 and progress_dialog:
                    progress_dialog.close()
                
                notify('Tải xuống hoàn tất', f'File {os.path.basename(path)} đã tải xong.')
                if xbmcgui.Dialog().yesno("Phát file?", "Bạn có muốn phát luôn video này không?"):
                    xbmc.Player().play(path)
            except Exception as e:
                if download_method == 1 and progress_dialog:
                    progress_dialog.close()
                notify('Lỗi tải xuống', str(e))
                log(f"Download error: {str(e)}")
                if os.path.exists(path):
                    os.remove(path)
                return
        
        
        download_thread = threading.Thread(target=download_thread)
        download_thread.start()
        return True
        
    except requests.exceptions.RequestException as e:
        notify('Connection Error', f"Không thể kết nối đến URL: {str(e)}")
        log(f"Connection error: {str(e)}")
        return False
    except Exception as e:
        notify('Error', f"Lỗi: {str(e)}")
        log(f"Error in download_file: {str(e)}")
        return False
