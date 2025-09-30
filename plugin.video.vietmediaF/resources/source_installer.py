import os
import xbmc
import xbmcgui
import xbmcvfs
import shutil
from resources.addon import notify, alert, ADDON_PATH

def install_vmf_source():
    """
    Copy file source.xml vào thư mục userdata để thêm source repo VMF
    """
    try:
        # Lấy đường dẫn đến thư mục userdata
        userdata_path = xbmcvfs.translatePath('special://userdata')
        
        # Đường dẫn đến file source.xml trong addon
        source_file_path = os.path.join(ADDON_PATH, 'resources', 'sources', 'source.xml')
        
        # Đường dẫn đến file source.xml trong userdata
        dest_file_path = os.path.join(userdata_path, 'sources.xml')
        
        # Kiểm tra xem file source.xml có tồn tại trong addon không
        if not os.path.exists(source_file_path):
            alert("Không tìm thấy file source.xml trong addon.")
            return False
        
        # Kiểm tra xem file sources.xml đã tồn tại trong userdata chưa
        if os.path.exists(dest_file_path):
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Xác nhận", "File sources.xml đã tồn tại trong thư mục userdata.\n\nBạn có muốn ghi đè lên file này không?"):
                # Tạo bản sao lưu của file sources.xml hiện tại
                backup_file_path = os.path.join(userdata_path, 'sources.xml.bak')
                shutil.copy2(dest_file_path, backup_file_path)
                xbmc.log(f"[VietmediaF] Đã tạo bản sao lưu của sources.xml tại {backup_file_path}", xbmc.LOGINFO)
                
                # Copy file source.xml từ addon vào userdata
                shutil.copy2(source_file_path, dest_file_path)
                xbmc.log(f"[VietmediaF] Đã copy source.xml vào {dest_file_path}", xbmc.LOGINFO)
                
                alert("Đã thêm source repo VMF thành công.\n\nBản sao lưu của file sources.xml cũ đã được lưu tại:\n" + backup_file_path)
                return True
            else:
                alert("Đã hủy thao tác.")
                return False
        else:
            # Copy file source.xml từ addon vào userdata
            shutil.copy2(source_file_path, dest_file_path)
            xbmc.log(f"[VietmediaF] Đã copy source.xml vào {dest_file_path}", xbmc.LOGINFO)
            
            alert("Đã thêm source repo VMF thành công.")
            return True
            
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi thêm source repo VMF: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi khi thêm source repo VMF: {str(e)}")
        return False
