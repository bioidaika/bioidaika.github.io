import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET
import json
import subprocess
import platform
from resources.addon import notify

ADDON = xbmcaddon.Addon()
USERDATA_PATH = xbmcvfs.translatePath('special://userdata/')
ADVANCEDSETTINGS_PATH = os.path.join(USERDATA_PATH, 'advancedsettings.xml')
PROFILE_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))


LOW_END_CONFIG = '''
<advancedsettings>
  <videocache>
    <memorysize>31457280</memorysize> <!-- 30MB -->
    <buffermode>2</buffermode> <!-- Đệm chỉ mạng Internet -->
    <readfactor>3</readfactor>
  </videocache>
  <loglevel>0</loglevel> <!-- Không ghi log -->
  <gui>
    <algorithmdirtyregions>1</algorithmdirtyregions> <!-- Mặc định -->
  </gui>
  <network>
    <curlclienttimeout>30</curlclienttimeout>
    <readbufferfactor>4</readbufferfactor>
    <disableipv6>true</disableipv6>
  </network>
</advancedsettings>
'''


HIGH_END_CONFIG = '''
<advancedsettings>
  <videocache>
    <memorysize>104857600</memorysize> <!-- 100MB -->
    <buffermode>3</buffermode> <!-- Đệm tất cả + đệm trước -->
    <readfactor>5</readfactor>
  </videocache>
  <loglevel>1</loglevel> <!-- Bình thường -->
  <gui>
    <algorithmdirtyregions>3</algorithmdirtyregions> <!-- Đầy đủ -->
  </gui>
  <network>
    <curlclienttimeout>20</curlclienttimeout>
    <readbufferfactor>5</readbufferfactor>
  </network>
  <videolibrary>
    <cleanonupdate>true</cleanonupdate>
    <backgroundupdate>true</backgroundupdate>
  </videolibrary>
</advancedsettings>
'''


SLOW_NETWORK_CONFIG = '''
<advancedsettings>
  <videocache>
    <memorysize>62914560</memorysize> <!-- 60MB -->
    <buffermode>3</buffermode> <!-- Đệm tất cả + đệm trước -->
    <readfactor>8</readfactor>
  </videocache>
  <network>
    <curlclienttimeout>60</curlclienttimeout>
    <readbufferfactor>8</readbufferfactor>
    <disableipv6>true</disableipv6>
  </network>
</advancedsettings>
'''

def display_advanced_settings_menu():
    """Hiển thị menu thiết lập nâng cao"""
    
    import sys
    import xbmcplugin
    from resources.utils import add_menu_item, settings_icon

    handle = int(sys.argv[1])

    
    add_menu_item(handle, "Tối ưu bộ nhớ đệm",
                 "plugin://plugin.video.vietmediaF?action=optimize_cache",
                 False, settings_icon,
                 "Tối ưu bộ nhớ đệm cho Kodi")

    add_menu_item(handle, "Tối ưu hóa mạng",
                 "plugin://plugin.video.vietmediaF?action=optimize_network",
                 False, settings_icon,
                 "Tối ưu hóa mạng cho Kodi")
    '''
    add_menu_item(handle, "Tự động phụ đề tiếng Việt",
                 "plugin://plugin.video.vietmediaF?action=auto_vietnamese_subtitle",
                 False, settings_icon,
                 "Bật/tắt tự động phụ đề tiếng Việt")
    '''
    add_menu_item(handle, "Lựa chọn Player ngoài",
                 "plugin://plugin.video.vietmediaF?action=external_player_settings",
                 False, settings_icon,
                 "Cài đặt trình phát video bên ngoài Kodi")

    add_menu_item(handle, "Quản lý cài đặt nâng cao",
                 "plugin://plugin.video.vietmediaF?action=manage_advanced_settings",
                 False, settings_icon,
                 "Quản lý cài đặt nâng cao của Kodi")

    xbmcplugin.endOfDirectory(handle)

def optimize_cache():
    """Tối ưu bộ nhớ đệm"""
    import os  
    dialog = xbmcgui.Dialog()
    options = [
        "Cấu hình cho máy yếu",
        "Cấu hình cho máy mạnh",
        "Cấu hình cho mạng chậm"
    ]

    selected = dialog.select("Chọn cấu hình tối ưu", options)

    if selected == -1:
        return

    
    if selected == 0:
        config_content = LOW_END_CONFIG
    elif selected == 1:
        config_content = HIGH_END_CONFIG
    elif selected == 2:
        config_content = SLOW_NETWORK_CONFIG

    
    import xml.etree.ElementTree as ET
    try:
        
        new_config = ET.fromstring(config_content)

        
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                
                for element in new_config:
                    
                    existing = root.find(element.tag)
                    if existing is not None:
                        
                        root.remove(existing)
                    
                    root.append(element)

                
                tree.write(ADVANCEDSETTINGS_PATH)
            except Exception:
                
                with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                    f.write(config_content)
        else:
            
            with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                f.write(config_content)

        notify(f"Đã áp dụng {options[selected]}")
        if dialog.yesno("Cài đặt nâng cao", "Đã áp dụng cấu hình thành công. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
            xbmc.executebuiltin('XBMC.RestartApp()')
            import os
            os._exit(1)
    except Exception as e:
        xbmc.log(f"Lỗi khi tạo file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi tạo file advancedsettings.xml: {str(e)}")

def optimize_network():
    """Tối ưu hóa mạng"""
    import os  
    import xml.etree.ElementTree as ET  
    dialog = xbmcgui.Dialog()

    
    ipv6_disabled = False
    if os.path.exists(ADVANCEDSETTINGS_PATH):
        try:
            tree = ET.parse(ADVANCEDSETTINGS_PATH)
            root = tree.getroot()
            network = root.find('network')
            if network is not None:
                disable_ipv6 = network.find('disableipv6')
                if disable_ipv6 is not None and disable_ipv6.text.lower() == 'true':
                    ipv6_disabled = True
        except Exception:
            pass

    options = [
        f"{'Bật' if ipv6_disabled else 'Tắt'} IPv6 (Hiện tại: {'Tắt' if ipv6_disabled else 'Bật'})",
        "Tối ưu hiệu suất"
    ]

    selected = dialog.select("Tối ưu hóa mạng", options)

    if selected == -1:
        return

    if selected == 0:
        
        new_ipv6_disabled = not ipv6_disabled

        
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                
                network = root.find('network')
                if network is None:
                    network = ET.SubElement(root, 'network')

                
                disable_ipv6 = network.find('disableipv6')
                if disable_ipv6 is None:
                    disable_ipv6 = ET.SubElement(network, 'disableipv6')

                disable_ipv6.text = 'true' if new_ipv6_disabled else 'false'

                
                tree.write(ADVANCEDSETTINGS_PATH)
                notify(f"Đã {'tắt' if new_ipv6_disabled else 'bật'} IPv6")
                if dialog.yesno("Cài đặt nâng cao", f"Đã {'tắt' if new_ipv6_disabled else 'bật'} IPv6. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
                    xbmc.executebuiltin('XBMC.RestartApp()')
                    import os
                    os._exit(1)
            except Exception as e:
                
                create_ipv6_config(new_ipv6_disabled, dialog)
        else:
            
            create_ipv6_config(new_ipv6_disabled, dialog)

    elif selected == 1:
        
        performance_config = '''
<advancedsettings>
  <loglevel>0</loglevel> <!-- Không ghi log -->
  <gui>
    <algorithmdirtyregions>3</algorithmdirtyregions> <!-- Đầy đủ -->
  </gui>
</advancedsettings>
'''
        try:
            
            new_config = ET.fromstring(performance_config)

            
            if os.path.exists(ADVANCEDSETTINGS_PATH):
                try:
                    
                    tree = ET.parse(ADVANCEDSETTINGS_PATH)
                    root = tree.getroot()

                    
                    for element in new_config:
                        
                        existing = root.find(element.tag)
                        if existing is not None:
                            
                            root.remove(existing)
                        
                        root.append(element)

                    
                    tree.write(ADVANCEDSETTINGS_PATH)
                except Exception:
                    
                    with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                        f.write(performance_config)
            else:
                
                with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                    f.write(performance_config)

            notify("Đã bật tối ưu hiệu suất")
            if dialog.yesno("Cài đặt nâng cao", "Đã áp dụng cấu hình tối ưu hiệu suất. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
                xbmc.executebuiltin('XBMC.RestartApp()')
                import os
                os._exit(1)
        except Exception as e:
            xbmc.log(f"Lỗi khi tạo file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
            dialog.ok("Lỗi", f"Lỗi khi tạo file advancedsettings.xml: {str(e)}")

def create_ipv6_config(disable_ipv6, dialog):
    """Tạo file advancedsettings.xml với cấu hình IPv6"""
    import xml.etree.ElementTree as ET
    config = f'''
<advancedsettings>
  <network>
    <disableipv6>{str(disable_ipv6).lower()}</disableipv6>
  </network>
</advancedsettings>
'''
    try:
        
        new_config = ET.fromstring(config)

        
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                
                network = root.find('network')
                if network is None:
                    network = ET.SubElement(root, 'network')

                
                disable_ipv6_elem = network.find('disableipv6')
                if disable_ipv6_elem is None:
                    disable_ipv6_elem = ET.SubElement(network, 'disableipv6')

                disable_ipv6_elem.text = 'true' if disable_ipv6 else 'false'

                
                tree.write(ADVANCEDSETTINGS_PATH)
            except Exception:
                
                with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                    f.write(config)
        else:
            
            with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                f.write(config)

        notify(f"Đã {'tắt' if disable_ipv6 else 'bật'} IPv6")
        if dialog.yesno("Cài đặt nâng cao", f"Đã {'tắt' if disable_ipv6 else 'bật'} IPv6. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
            xbmc.executebuiltin('XBMC.RestartApp()')
            import os
            os._exit(1)
    except Exception as e:
        xbmc.log(f"Lỗi khi tạo file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi tạo file advancedsettings.xml: {str(e)}")

def auto_vietnamese_subtitle():
    """Bật/tắt tự động phụ đề tiếng Việt"""
    import os
    import xml.etree.ElementTree as ET
    dialog = xbmcgui.Dialog()

    
    subtitle_enabled = False
    if os.path.exists(ADVANCEDSETTINGS_PATH):
        try:
            tree = ET.parse(ADVANCEDSETTINGS_PATH)
            root = tree.getroot()
            subtitles = root.find('subtitles')
            if subtitles is not None:
                languages = subtitles.find('languages')
                if languages is not None and 'Vietnamese' in languages.text:
                    subtitle_enabled = True
        except Exception:
            pass

    
    if subtitle_enabled:
        if dialog.yesno("Tự động phụ đề tiếng Việt", "Phụ đề tiếng Việt đang được bật. Bạn có muốn tắt không?"):
            
            disable_vietnamese_subtitle()
    else:
        if dialog.yesno("Tự động phụ đề tiếng Việt", "Phụ đề tiếng Việt đang bị tắt. Bạn có muốn bật không?"):
            
            enable_vietnamese_subtitle()

def enable_vietnamese_subtitle():
    """Bật tự động phụ đề tiếng Việt"""
    import os
    import xml.etree.ElementTree as ET
    dialog = xbmcgui.Dialog()

    try:
        
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                
                subtitles = root.find('subtitles')
                if subtitles is None:
                    subtitles = ET.SubElement(root, 'subtitles')

                
                languages = subtitles.find('languages')
                if languages is None:
                    languages = ET.SubElement(subtitles, 'languages')
                    languages.text = "Vietnamese"
                else:
                    
                    if 'Vietnamese' not in languages.text:
                        languages.text = languages.text + ",Vietnamese" if languages.text else "Vietnamese"

                
                tree.write(ADVANCEDSETTINGS_PATH)
                notify("Đã bật tự động phụ đề tiếng Việt")
                if dialog.yesno("Cài đặt nâng cao", "Đã bật tự động phụ đề tiếng Việt. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
                    xbmc.executebuiltin('XBMC.RestartApp()')
                    import os
                    os._exit(1)
            except Exception as e:
                
                create_subtitle_config(True)
        else:
            
            create_subtitle_config(True)
    except Exception as e:
        xbmc.log(f"Lỗi khi bật phụ đề tiếng Việt: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi bật phụ đề tiếng Việt: {str(e)}")

def disable_vietnamese_subtitle():
    """Tắt tự động phụ đề tiếng Việt"""
    import os
    import xml.etree.ElementTree as ET
    dialog = xbmcgui.Dialog()

    try:
        
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                
                subtitles = root.find('subtitles')
                if subtitles is not None:
                    
                    languages = subtitles.find('languages')
                    if languages is not None and languages.text:
                        
                        langs = languages.text.split(',')
                        if 'Vietnamese' in langs:
                            langs.remove('Vietnamese')
                            languages.text = ','.join(langs)

                            
                            if not languages.text:
                                subtitles.remove(languages)

                                
                                if len(list(subtitles)) == 0:
                                    root.remove(subtitles)

                
                tree.write(ADVANCEDSETTINGS_PATH)
                notify("Đã tắt tự động phụ đề tiếng Việt")
                if dialog.yesno("Cài đặt nâng cao", "Đã tắt tự động phụ đề tiếng Việt. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
                    xbmc.executebuiltin('XBMC.RestartApp()')
                    import os
                    os._exit(1)
            except Exception as e:
                xbmc.log(f"Lỗi khi tắt phụ đề tiếng Việt: {str(e)}", xbmc.LOGERROR)
                dialog.ok("Lỗi", f"Lỗi khi tắt phụ đề tiếng Việt: {str(e)}")
        else:
            dialog.ok("Thông báo", "Không tìm thấy file advancedsettings.xml")
    except Exception as e:
        xbmc.log(f"Lỗi khi tắt phụ đề tiếng Việt: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi tắt phụ đề tiếng Việt: {str(e)}")

def create_subtitle_config(enable):
    """Tạo file advancedsettings.xml với cấu hình phụ đề"""
    import os
    import xml.etree.ElementTree as ET
    dialog = xbmcgui.Dialog()

    if enable:
        config = '''
<advancedsettings>
  <subtitles>
    <languages>Vietnamese</languages>
    <subtitleonplay>true</subtitleonplay>
    <forcedsubtitleson>true</forcedsubtitleson>
    <subtitlelanguage>Vietnamese</subtitlelanguage>
    <subtitlecharset>CP1258</subtitlecharset>
  </subtitles>
</advancedsettings>
'''
    else:
        config = '''
<advancedsettings>
</advancedsettings>
'''

    try:
        # Parse cấu hình mới
        new_config = ET.fromstring(config)

        # Nếu file đã tồn tại
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            try:
                # Đọc file hiện tại
                tree = ET.parse(ADVANCEDSETTINGS_PATH)
                root = tree.getroot()

                # Cập nhật hoặc thêm mới các thẻ
                for element in new_config:
                    # Tìm thẻ hiện có
                    existing = root.find(element.tag)
                    if existing is not None:
                        # Xóa thẻ cũ
                        root.remove(existing)
                    # Thêm thẻ mới
                    root.append(element)

                # Ghi lại file
                tree.write(ADVANCEDSETTINGS_PATH)
            except Exception:
                # Nếu có lỗi khi đọc/ghi file, ghi đè file mới
                with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                    f.write(config)
        else:
            # Nếu file chưa tồn tại, tạo file mới
            with open(ADVANCEDSETTINGS_PATH, 'w', encoding='utf-8') as f:
                f.write(config)

        notify(f"Đã {'bật' if enable else 'tắt'} tự động phụ đề tiếng Việt")
        if dialog.yesno("Cài đặt nâng cao", f"Đã {'bật' if enable else 'tắt'} tự động phụ đề tiếng Việt. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
            xbmc.executebuiltin('XBMC.RestartApp()')
            import os
            os._exit(1)
    except Exception as e:
        xbmc.log(f"Lỗi khi tạo file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi tạo file advancedsettings.xml: {str(e)}")

def manage_advanced_settings():
    """Quản lý cài đặt nâng cao"""
    
    import sys
    import xbmcplugin
    from resources.utils import add_menu_item, settings_icon

    handle = int(sys.argv[1])

    
    add_menu_item(handle, "Xem nội dung file advancedsettings.xml",
                 "plugin://plugin.video.vietmediaF?action=view_advancedsettings",
                 False, settings_icon,
                 "Xem nội dung file advancedsettings.xml hiện tại")

    add_menu_item(handle, "Khôi phục về cài đặt mặc định",
                 "plugin://plugin.video.vietmediaF?action=reset_advancedsettings",
                 False, settings_icon,
                 "Xóa file advancedsettings.xml hiện tại")

    xbmcplugin.endOfDirectory(handle)

def reset_advancedsettings():
    """Xóa file advancedsettings.xml hiện tại"""
    import os  
    dialog = xbmcgui.Dialog()

    if not dialog.yesno("Xác nhận", "Bạn có chắc muốn khôi phục về cài đặt mặc định không?"):
        return

    try:
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            os.remove(ADVANCEDSETTINGS_PATH)
            notify("Đã xóa file advancedsettings.xml")
            if dialog.yesno("Cài đặt nâng cao", "Đã xóa file advancedsettings.xml. Bạn có muốn khởi động lại Kodi ngay bây giờ để áp dụng các thay đổi?"):
                xbmc.executebuiltin('XBMC.RestartApp()')
                import os
                os._exit(1)
        else:
            dialog.ok("Thông báo", "Không tìm thấy file advancedsettings.xml")
    except Exception as e:
        xbmc.log(f"Lỗi khi xóa file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi xóa file advancedsettings.xml: {str(e)}")

def view_advancedsettings():
    """Xem nội dung file advancedsettings.xml"""
    import os  
    dialog = xbmcgui.Dialog()

    try:
        if os.path.exists(ADVANCEDSETTINGS_PATH):
            with open(ADVANCEDSETTINGS_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            dialog.textviewer("Nội dung file advancedsettings.xml", content)
        else:
            dialog.ok("Thông báo", "Không tìm thấy file advancedsettings.xml")
    except Exception as e:
        xbmc.log(f"Lỗi khi đọc file advancedsettings.xml: {str(e)}", xbmc.LOGERROR)
        dialog.ok("Lỗi", f"Lỗi khi đọc file advancedsettings.xml: {str(e)}")


def external_player_settings():
    """Hiển thị menu cài đặt external player"""
    import sys
    import xbmcplugin
    from resources.utils import add_menu_item, settings_icon

    handle = int(sys.argv[1])

    
    from platform import get_platform
    os_info = get_platform()
    os_name = os_info.get('os', 'unknown')

    
    add_menu_item(handle, "Chọn trình phát video ngoài",
                 "plugin://plugin.video.vietmediaF?action=set_external_player",
                 False, settings_icon,
                 "Chọn trình phát video bên ngoài Kodi")

    add_menu_item(handle, "Khôi phục về trình phát mặc định của Kodi",
                 "plugin://plugin.video.vietmediaF?action=reset_to_default_player",
                 False, settings_icon,
                 "Sử dụng trình phát mặc định của Kodi")

    xbmcplugin.endOfDirectory(handle)

def set_external_player():
    """Cài đặt external player"""
    dialog = xbmcgui.Dialog()

    
    from platform import get_platform
    os_info = get_platform()
    os_name = os_info.get('os', 'unknown')

    
    players = {}

    if os_name == 'windows':
        players = {
            "VLC Media Player": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "MPC-HC": "C:\\Program Files\\MPC-HC\\mpc-hc64.exe",
            "PotPlayer": "C:\\Program Files\\DAUM\\PotPlayer\\PotPlayerMini64.exe",
            "Windows Media Player": "C:\\Program Files\\Windows Media Player\\wmplayer.exe",
            "Khác (Tự nhập đường dẫn)": "custom"
        }
    elif os_name == 'darwin':  
        players = {
            "VLC Media Player": "/Applications/VLC.app/Contents/MacOS/VLC",
            "IINA": "/Applications/IINA.app/Contents/MacOS/IINA",
            "QuickTime Player": "/Applications/QuickTime Player.app/Contents/MacOS/QuickTime Player",
            "Khác (Tự nhập đường dẫn)": "custom"
        }
    elif os_name == 'linux':
        players = {
            "VLC Media Player": "/usr/bin/vlc",
            "MPV": "/usr/bin/mpv",
            "MPlayer": "/usr/bin/mplayer",
            "Khác (Tự nhập đường dẫn)": "custom"
        }
    elif os_name == 'android':
        players = {
            "VLC for Android": "org.videolan.vlc",
            "MX Player": "com.mxtech.videoplayer.ad",
            "MX Player Pro": "com.mxtech.videoplayer.pro",
            "Just (Video) Player": "com.brouken.player",
            "mpv-android": "is.xyz.mpv",
            "Nova Video Player": "org.nova.video",
            "Kodi": "org.xbmc.kodi",
            "BSPlayer": "com.bsplayer.bspandroid.full",
            "XPlayer": "video.player.videoplayer",
            "KMPlayer": "com.kmplayer",
            "Khác (Tự nhập package name)": "custom"
        }
    else:
        dialog.ok("Thông báo", f"Hệ điều hành {os_name} chưa được hỗ trợ. Vui lòng nhập đường dẫn thủ công.")
        players = {"Tự nhập đường dẫn": "custom"}

    
    player_names = list(players.keys())
    selected = dialog.select("Chọn trình phát video", player_names)

    if selected == -1:
        return

    player_name = player_names[selected]
    player_path = players[player_name]

    
    if player_path == "custom":
        if os_name == 'android':
            keyboard = xbmc.Keyboard('', 'Nhập package name của ứng dụng (ví dụ: org.videolan.vlc)')
        else:
            keyboard = xbmc.Keyboard('', 'Nhập đường dẫn đầy đủ đến trình phát video')
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            player_path = keyboard.getText()
            player_name = "Custom Player"
        else:
            notify("Đã hủy cài đặt trình phát video")
            return

    
    ADDON.setSetting("external_player_enabled", "true")
    ADDON.setSetting("external_player_name", player_name)
    ADDON.setSetting("external_player_path", player_path)

    notify(f"Đã cài đặt {player_name} làm trình phát video ngoài")

def reset_to_default_player():
    """Reset về player mặc định của Kodi"""
    dialog = xbmcgui.Dialog()

    if not dialog.yesno("Xác nhận", "Bạn có chắc muốn khôi phục về trình phát mặc định của Kodi không?"):
        return

    
    ADDON.setSetting("external_player_enabled", "false")
    ADDON.setSetting("external_player_name", "")
    ADDON.setSetting("external_player_path", "")

    notify("Đã khôi phục về trình phát mặc định của Kodi")

def launch_external_player(video_url, title="Video"):
    
    
    if ADDON.getSetting("external_player_enabled") != "true":
        return False

    player_path = ADDON.getSetting("external_player_path")
    if not player_path:
        notify("Chưa cài đặt đường dẫn trình phát video ngoài")
        return False

    
    from platform import get_platform
    os_info = get_platform()
    os_name = os_info.get('os', 'unknown')

    try:
        if os_name == 'android':
            if player_path == "org.videolan.vlc":
                intent = "android.intent.action.VIEW"
                notify("Mở video bằng VLC Player...")
                xbmc.executebuiltin(f'StartAndroidActivity("{player_path}","{intent}","video/*","{video_url}","position=0")')
            elif player_path == "com.mxtech.videoplayer.ad" or player_path == "com.mxtech.videoplayer.pro":
                intent = "android.intent.action.VIEW"
                notify("Mở video bằng MX Player...")
                xbmc.executebuiltin(f'StartAndroidActivity("{player_path}","{intent}","video/*","{video_url}","start_position=0")')
            elif player_path == "com.brouken.player":
                intent = "android.intent.action.VIEW"
                notify("Mở video bằng Just Player...")
                xbmc.executebuiltin(f'StartAndroidActivity("{player_path}","{intent}","video/*","{video_url}")')
            elif player_path == "is.xyz.mpv":
                
                intent = "android.intent.action.VIEW"
                notify("Mở video bằng mpv-android...")
                xbmc.executebuiltin(f'StartAndroidActivity("{player_path}","{intent}","video/*","{video_url}")')
            else:
                
                intent = "android.intent.action.VIEW"
                notify("Mở video bằng external player...")
                xbmc.executebuiltin(f'StartAndroidActivity("{player_path}","{intent}","video/*","{video_url}")')

            
            xbmc.sleep(2000)
        elif os_name == 'windows':
            
            subprocess.Popen([player_path, video_url], shell=True)
        elif os_name == 'darwin' or os_name == 'linux':
            
            subprocess.Popen([player_path, video_url])
        else:
            
            subprocess.Popen([player_path, video_url], shell=True)

        return True
    except Exception as e:
        xbmc.log(f"Lỗi khi mở external player: {str(e)}", xbmc.LOGERROR)
        notify(f"Lỗi khi mở external player: {str(e)}")
        return False
