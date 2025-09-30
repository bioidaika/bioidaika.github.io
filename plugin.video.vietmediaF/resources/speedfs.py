import requests
import xbmcgui
import xbmc
import xbmcvfs
import os
import time
import random
import base64
from resources import fshare
from .addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE, USERDATA, DOWNLOAD_PATH, headers

def get_public_ip_and_isp():
    try:
        response = requests.get('http://ip-api.com/json/')
        response.raise_for_status()
        data = response.json()
        public_ip = data.get('query')
        isp = data.get('isp')
        return public_ip, isp
    except Exception as e:
        return None, None

def sppedfs():
    fshare.check_session()
    session_id = ADDON.getSetting('sessionfshare')
    token = ADDON.getSetting('tokenfshare')

    folder_url = base64.b64decode(
        'aHR0cHM6Ly93d3cuZnNoYXJlLnZuL2ZvbGRlci8yOVZDVFZMMjdLWFQ=').decode('utf-8')
    headers['Cookie'] = f'session_id={session_id}'

    payload = {
        'token': token,
        'url': folder_url,
        'dirOnly': 0,
        'pageIndex': 0,
        'limit': 60,
    }

    response = requests.post("https://api.fshare.vn/api/fileops/getFolderList", headers=headers, json=payload)

    if response:
        response_data = response.json()
        file_urls = [item['furl'] for item in response_data]

        if not file_urls:
            notify("No files found in folder.")
            return

        test_file_url = random.choice(file_urls)
        download_link = fshare.get_download_link(token, session_id, test_file_url)
        file_head = requests.head(download_link)
        file_size = int(file_head.headers.get("Content-Length", 0))

        
        temp_path = os.path.join(xbmcvfs.translatePath("special://temp"), "speedtest_temp")
        
        
        if xbmcvfs.exists(temp_path):
            xbmcvfs.delete(temp_path)

        public_ipv4, isp = get_public_ip_and_isp()
        
        dialog = xbmcgui.DialogProgress()
        dialog.create("Testing Fshare Speed...", "")

        def download_and_measure():
            start_time = time.time()
            downloaded_size = 0
            chunk_size = 8192
            
            try:
                with requests.get(download_link, stream=True) as r:
                    r.raise_for_status()
                    with open(temp_path, "wb") as file:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if not chunk:
                                continue

                            file.write(chunk)
                            downloaded_size += len(chunk)

                            percent_complete = int(downloaded_size / file_size * 100)
                            speed = downloaded_size / (time.time() - start_time)
                            remaining_time = (file_size - downloaded_size) / speed if speed > 0 else 0

                            dialog.update(
                                percent_complete,
                                f"Current Speed: [COLOR yellow]{speed * 8 / 1024 / 1024:.2f} Mbps[/COLOR]\n"
                                f"Progress: {percent_complete}%\n"
                                f"Remaining Time: {time.strftime('%H:%M:%S', time.gmtime(remaining_time))}\n"
                                f"Your ip: [COLOR yellow]{public_ipv4}[/COLOR] {isp}"
                            )

                            if dialog.iscanceled():
                                dialog.close()
                                xbmcgui.Dialog().ok(
                                    "Thông báo",
                                    f"Speed test đã hủy. Tốc độ ghi nhận: [COLOR yellow]{speed * 8 / 1024 / 1024:.2f} Mbps[/COLOR]"
                                )
                                return

                dialog.close()
                total_time = time.time() - start_time
                final_speed = (downloaded_size / total_time) * 8 / 1024 / 1024
                recommend_quality(final_speed)

            finally:
                
                if xbmcvfs.exists(temp_path):
                    xbmcvfs.delete(temp_path)

        def recommend_quality(speed):
            quality = "360p SD"

            if speed >= 100:
                quality = "ISO 8K UHD"
            elif speed >= 50:
                quality = "Video 4K UHD"
            elif speed >= 35:
                quality = "Bluray 4K"
            elif speed >= 25:
                quality = "Bluray 1080p"
            elif speed >= 20:
                quality = "Video 1440p QHD"
            elif speed >= 10:
                quality = "Video 1080p FHD"
            elif speed >= 5:
                quality = "Video 720p HD"
            elif speed >= 3:
                quality = "480p SD"
            elif speed >= 1.5:
                quality = "360p SD"

            xbmcgui.Dialog().ok(
                "Chất lượng video đề nghị",
                f"Your ip: [COLOR yellow]{public_ipv4}[/COLOR] - {isp}\n"
                f"Chất lượng video đề nghị [COLOR yellow]{speed:.2f} Mbps[/COLOR] là: [COLOR yellow]{quality}[/COLOR]\n"
                f"[I]Kết quả đến Fshare sẽ khác với speedtest đến ISP[/I]"
            )

        download_and_measure()
