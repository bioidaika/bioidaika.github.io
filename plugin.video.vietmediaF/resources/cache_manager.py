import os
import time
import xbmc
import xbmcaddon
from datetime import datetime, timedelta
from resources.lib.constants import CACHE_PATH

ADDON = xbmcaddon.Addon()

def should_clear_cache():
    """Kiểm tra xem có nên xóa cache hay không dựa trên cài đặt và thời gian"""
    if not ADDON.getSettingBool('auto_clear_cache'):
        return False

    last_cleanup = ADDON.getSetting('last_cache_cleanup')
    if not last_cleanup:
        return True

    try:
        last_cleanup_time = datetime.strptime(last_cleanup, '%Y-%m-%d %H:%M:%S')
        expiry_days = int(ADDON.getSetting('cache_expiry_days'))
        next_cleanup = last_cleanup_time + timedelta(days=expiry_days)
        return datetime.now() >= next_cleanup
    except (ValueError, TypeError):
        return True

def clear_old_cache():
    """Xóa các file cache cũ hơn số ngày được cấu hình"""
    if not os.path.exists(CACHE_PATH):
        return

    try:
        expiry_days = int(ADDON.getSetting('cache_expiry_days'))
        now = time.time()
        cutoff = now - (expiry_days * 86400)  # 86400 giây = 1 ngày
        files_removed = 0
        total_size = 0

        for filename in os.listdir(CACHE_PATH):
            file_path = os.path.join(CACHE_PATH, filename)
            if os.path.isfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff:
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        files_removed += 1
                        total_size += file_size
                        xbmc.log(f"[VietmediaF] Đã xóa cache: {filename}", xbmc.LOGINFO)
                    except Exception as e:
                        xbmc.log(f"[VietmediaF] Lỗi khi xóa cache {filename}: {str(e)}", xbmc.LOGERROR)

        # Cập nhật thời gian xóa cache cuối cùng
        ADDON.setSetting('last_cache_cleanup', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if files_removed > 0:
            total_size_mb = total_size / (1024 * 1024)  # Chuyển đổi sang MB
            xbmc.log(f"[VietmediaF] Đã xóa {files_removed} file cache (tổng {total_size_mb:.2f}MB)", xbmc.LOGINFO)
            xbmc.executebuiltin(f'Notification(VietmediaF, Đã xóa {files_removed} file cache cũ ({total_size_mb:.2f}MB), 5000)')

    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi xóa cache: {str(e)}", xbmc.LOGERROR)
        xbmc.executebuiltin('Notification(VietmediaF, Lỗi khi xóa cache cũ, 5000)')

def check_and_clear_cache():
    """Kiểm tra và xóa cache nếu cần thiết"""
    if should_clear_cache():
        clear_old_cache() 