import os
import xbmcaddon
import xbmc
import xbmcvfs


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_PROFILE = ADDON.getAddonInfo("profile")
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)

def notify(message='', header=None, time=5000, image=None):
    if header is None:
        header = '[COLOR darkgoldenrod]'+ADDON_NAME+'[/COLOR]'
    xbmc.executebuiltin('Notification("%s", "%s", "%d", "%s")' % (header, message, time, image))

class HistoryManager:
    def __init__(self, history_file):
        self.history_file = os.path.join(PROFILE_PATH, history_file)
        self.max_history_size = 50

    def check_history(self):
        """Kiểm tra xem file lịch sử có tồn tại và có dữ liệu không"""
        if not os.path.exists(self.history_file):
            return False
        return os.path.exists(self.history_file) and os.path.getsize(self.history_file) > 0

    def get_history(self):
        """Lấy lịch sử tìm kiếm từ file"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def save_history(self, query):
        """Lưu một query mới vào lịch sử"""
        try:
            history = self.get_history()
            if query not in history:
                history.insert(0, query)
                history = history[:self.max_history_size]
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(history))
        except Exception as e:
            notify(f"Lỗi khi lưu lịch sử: {str(e)}")

    def delete_history(self):
        """Xóa toàn bộ lịch sử"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    f.write('')
                notify("Đã xoá lịch sử tìm kiếm")
        except Exception as e:
            notify(f"Lỗi khi xóa lịch sử: {str(e)}")

    def clear_history(self):
        """Xóa toàn bộ lịch sử"""
        self.delete_history()


search_history = HistoryManager('lstk.dat')
fshare_history = HistoryManager('lstk4s.dat')
hdvn_history = HistoryManager('hdvnsearch.dat')
tvcine_history = HistoryManager('search_history.json')
watched_history = HistoryManager('watched.dat')