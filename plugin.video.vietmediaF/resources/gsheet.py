
import requests, re, json, os
from six.moves import urllib_parse, html_parser
from .addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, logError, PROFILE, headers, addon_url
import xbmcvfs
from resources import fshare
from resources.utils import save_fshare_metadata, get_cached_metadata

def getdata(url):
    url = urllib_parse.unquote_plus(url)
    id_sheet = re.search(r"/d\/([a-zA-Z0-9-_]+)",url).group(1)
    if "gid" in url:
        gid = re.search(r"gid=(\d.*)",url).group(1)
    else:gid=0
    url = "https://docs.google.com/spreadsheets/d/" + id_sheet + "/gviz/tq?gid=" + str(gid) + "&headers=1"
    r = requests.get(url, headers=headers, verify=False, timeout=30)
    nd = re.search(r'\((.*?)}\)', r.text).group(1) + '}'
    nd = json.loads(nd)


    items1 = []
    if nd["table"]["cols"]:
        name = ''
        link = ''
        thumb = ''
        info = ''
        fanart = ''
        genre = ''
        rating = ''


        if len(nd["table"]["cols"]) > 0:
            name_data = nd["table"]["cols"][0]
            name = name_data.get("label", "")
            if "|" in name:
                name_parts = name.split("|")
                name = name_parts[0].replace("*", "").replace("@", "")
                link = name_parts[1] if len(name_parts) > 1 else ""


        if len(nd["table"]["cols"]) > 1:
            link_data = nd["table"]["cols"][1]
            link = link_data.get("label", "")
            if "token" in link:
                link = re.search(r"(https.+?)\/\?token", link).group(1) if match else ""


        if len(nd["table"]["cols"]) > 2:
            thumb = nd["table"]["cols"][2].get("label", "")


        if len(nd["table"]["cols"]) > 3:
            info = nd["table"]["cols"][3].get("label", "")

        if len(nd["table"]["cols"]) > 4:
            fanart = nd["table"]["cols"][4].get("label", "")

        if len(nd["table"]["cols"]) > 5:
            genre = nd["table"]["cols"][5].get("label", "")

        if len(nd["table"]["cols"]) > 6:
            rating = nd["table"]["cols"][6].get("label", "")

        playable = not (("folder" in link or "menu" in link or "docs.google.com" in link or "m3uhttp" in link) or \
                ("4share.vn" in link and "/d/" in link) or ("api.4share.vn" in link and "/d/" in link))

        if name and any(substring in link for substring in ['http', 'udp', 'rtp', 'plugin', 'acestream']):
            # Cập nhật cấu trúc dữ liệu để phù hợp với loadlistitem.py
            try:
                rating_value = float(rating) if rating and rating.replace('.', '', 1).isdigit() else 0.0
            except:
                rating_value = 0.0

            items1 = [{
                'label': name,
                'is_playable': playable,
                'path': f'{addon_url}action=play&url={link}',
                'thumbnail': thumb,
                'icon': thumb,
                'label2': name,  # Thêm tên phim vào label2 để hiển thị ở các mục đặc biệt
                'info': {
                    'title': name,
                    'plot': info,
                    'genre': genre,
                    'rating': rating_value,
                    'mediatype': 'movie'
                },
                'art': {
                    "fanart": fanart,
                    "poster": thumb,
                    "thumb": thumb,
                    "icon": thumb
                }
            }]
        else:
            items1 = []

    js = nd["table"]["rows"]
    items = items1 if items1 else []

    for link in js:
        item = {}
        row = link["c"]
        try:
            name = row[0]["v"].replace("||", "|")
        except Exception as e:

            name = 'Lỗi tên'

        if "|" in name:
            lis = name.split("|")
            name = lis[0].replace("*", "").replace("@", "")
            link = lis[1] if len(lis) > 1 else ""
            thumb = lis[2] if len(lis) > 2 else ""
            info = lis[3] if len(lis) > 3 else ""
            fanart = lis[4] if len(lis) > 4 else ""
        else:
            try:
                link = row[1]["v"]
                if "token" in link:
                    regex = r"(https.+?)\/\?token"
                    match = re.search(regex, link)
                    if match:
                        link = match.group(1)
            except:
                link = ""
            try:
                thumb = row[2]["v"]
            except:
                thumb = ""
            try:
                info = row[3]["v"]
            except:
                info = ""
            try:
                fanart = row[4]["v"]
            except:
                fanart = thumb
            try:
                genre = row[5]["v"]
            except:
                genre = ""
            try:
                rating = row[6]["v"]
            except:
                rating = ""

        playable = not (("folder" in link or "docs.google.com" in link or "pastebin.com" in link or "m3uhttp" in link or "menu" in link) or ("4share.vn" in link and "/d/" in link) or ("api.4share.vn" in link and "/d/" in link))
        if "fshare.vn/folder" in link:
            save_fshare_metadata(link, thumb, info)
        if any(substring in link for substring in ["http", "rtp", "udp", "acestream", "plugin"]):
            # Cập nhật cấu trúc dữ liệu để phù hợp với loadlistitem.py
            item["label"] = name if link else name + " - no link"
            item["is_playable"] = playable
            item["path"] = f'{addon_url}action=play&url={link}'
            item["thumbnail"] = thumb
            item["icon"] = thumb
            item["label2"] = name  # Thêm tên phim vào label2 để hiển thị ở các mục đặc biệt

            # Thông tin chi tiết cho video
            try:
                rating_value = float(rating) if rating and rating.replace('.', '', 1).isdigit() else 0.0
            except:
                rating_value = 0.0

            item["info"] = {
                'title': name,
                'plot': info,
                'genre': genre,
                'rating': rating_value,
                'mediatype': 'movie'
            }

            # Thông tin hình ảnh
            item["art"] = {
                "fanart": fanart,
                "poster": thumb,
                "thumb": thumb,
                "icon": thumb
            }

            items.append(item)

    data = {"content_type": "movies", "items": items}


    return data