import requests, re, os
from .addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE, CACHE_PATH, save_to_json, load_from_json, get_file_name, PROFILE_PATH, addon_url
import xbmcgui, xbmc, xbmcvfs
from datetime import datetime

CHANNEL_FILE = os.path.join(PROFILE_PATH, "channel.json")

def getListm3u(url, file_path):
    playlist = requests.get(url, verify=False).text
    channels = playlist.split("#EXTINF")[1:]
    items = []
    for channel in channels:
        match = re.search(r'tvg-logo="(.*?)"', channel)
        if match:
            logo = match.group(1)
        else:
            logo = ''

        cleaned_data = re.sub(r'(tvg|group)-[^\s]+="[^"]*"', '', channel)
        cleaned_channel_info = re.sub(r"((.*,))", '', cleaned_data)
        match = re.search(r"(?:https?|udp|rtp):\/\/[^ \n]+\n", cleaned_channel_info)
        if match:
            link = match.group(0).strip()
            match = re.search(r"^(.+)\n", cleaned_channel_info)
            if match:
                channel_name = match.group(1).strip()

                item = {}
                item["label"] = channel_name
                item["is_playable"] = True
                item["path"] = link
                item["thumbnail"] = logo
                item["icon"] = logo
                item["label2"] = ""
                item["info"] = {'plot': channel_name}
                item["art"] = {'fanart': logo}
                items.append(item)

    data = {"content_type": "episodes", "items": items}
    save_to_json(data, file_path)
    return data

def receive(url):
    if 'm3uhttp' in url or 'M3Uhttp' in url:
        url = url.replace('m3uhttp','http')
        url = url.replace('M#Uhttp','http')
        file_name = get_file_name(url)
        file_path = os.path.join(CACHE_PATH, file_name)
        if os.path.exists(file_path):
            saved_data = load_from_json(file_path)
            if saved_data:
                return saved_data
        
        return getListm3u(re.search(r"url=(.*)", url).group(1), file_path)
