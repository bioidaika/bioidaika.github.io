
import datetime
import os
import pathlib
import requests
import zipfile
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE
VERSION = ADDON.getAddonInfo("version")

def exit_kodi():
    countdown_time = 3
    for i in range(countdown_time, 0, -1):
        notify(f"Thoát KODI trong {i} giây...")
        xbmc.sleep(1000)
    os._exit(1)

def check_new_version():
    addon_id = xbmcaddon.Addon().getAddonInfo('id')
    addon_path = xbmcaddon.Addon().getAddonInfo('path')

    
    now = datetime.datetime.now()
    
    
    last_check_time = xbmcaddon.Addon().getSetting('checkDate')

    
    if last_check_time is None:
        last_check_time = now
        xbmcaddon.Addon().setSetting('checkDate',str(now))

    
    if last_check_time:
        last_check_datetime = datetime.datetime.fromtimestamp(int(last_check_time))
    else:
        last_check_datetime = datetime.datetime.min

    
    if (now - last_check_datetime).total_seconds() > 86400:
        
        
        url = 'https://raw.githubusercontent.com/ducnn/vietmediaf/main/version.txt'
        headers = {'Cache-Control': 'no-cache'}
        response = requests.get(url,headers=headers)
        new_version = response.text.strip()

        
        if new_version > VERSION:

            
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('Update Available', 'Đã có phiên bản mới %s của [COLOR yellow]Addon VietmediaF[/COLOR]. Bạn có muốn update luôn không?' % new_version)
            if ret:

                
                url = 'https://github.com/ducnn/vietmediaf/raw/main/plugin.video.vietmediaF.zip'
                response = requests.get(url)
                path = xbmcvfs.translatePath('special://temp/plugin.video.vietmediaF.zip')
                with open(path, 'wb') as f:
                    f.write(response.content)
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(str(output_path.parent))
                
                xbmcvfs.delete(addon_path)
                exit_kodi()

    else:
        alert("Không cần update")

    return