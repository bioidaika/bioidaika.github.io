
import xbmc, xbmcvfs, xbmcgui,xbmcplugin, random
import urllib.parse
import os, sys, json, re
import urlquick,htmlement
from resources.addon import alert, notify, fetch_data, headers, getadv, TextBoxes, ADDON, ADDON_NAME, ADDON_ID, ADDON_PROFILE, LOG, PROFILE,CURRENT_PATH, VERSION, PROFILE_PATH

HISTORY_FILE = os.path.join(PROFILE_PATH, 'history.dat')
import requests
import getlink
from resources import fshare
def debug1(text):

    filename = os.path.join(PROFILE_PATH, 'search.dat')
    if not os.path.exists(filename):
        with open(filename, "w+") as f:
            f.write(text)
    else:
        with open(filename, "wb") as f:
            f.write(text.encode("UTF-8"))

def get_data(url, headers=None):
    if headers is None:
        headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36 VietMedia/1.0',
                'Referers': 'http://www.google.com'
                }
    try:
        req = requests.get(url, headers=headers)
        return json.loads(req.content)
    except:
        pass


def searchvmf(query):
    query = query.replace("\n", "")
    query = query.replace(".", " ")
    query = urllib.parse.unquote(query)

    url = "https://fshare.vip/s.php?keyword=" + query

    try:
        r = urlquick.get(url, headers=headers, max_age = 60*60, timeout=20)

        if r.status_code == 200:
            try:
                content = r.content.decode('utf-8')
                jsondata = json.loads(content)
                if jsondata['status'] != 'success' or 'data' not in jsondata:
                    alert("Dữ liệu trả về không hợp lệ.")
                    return

                items_data = jsondata['data']
            except json.JSONDecodeError as e:
                alert(f"Lỗi giải mã JSON: {str(e)}")
                return
        elif r.status_code == 429:
            alert(f"Yêu cầu gửi quá nhiều. Thử lại sau 60s")
        else:
            alert(f"Yêu cầu thất bại với mã lỗi: {r.status_code}")
            return
    except requests.exceptions.RequestException as e:
        alert(f"Không thể kết nối tới trang web. Lỗi: {str(e)}")
        return

    if not items_data:
        data = timfshare(query)
        return data
    else:

        items = []
        for i in items_data:
            item = {}
            owner = i.get('Owner', '')
            name = i.get('Name', 'Không có tên')
            name = name.replace('@', '')
            name = f"[COLOR yellow]{owner}[/COLOR] {name}"

            furl = i.get('Link', '')
            background_img = i.get('Background', '')
            poster = i.get('Poster', '')


            if '?' in furl:
                furl = re.search(r"(.*)\?", furl).group(1)


            type_f = 0 if '/folder/' in furl else 1
            link = f'plugin://plugin.video.vietmediaF?action=play&url={furl}'
            playable = type_f != 0


            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = poster
            item["icon"] = poster
            item["label2"] = ""
            item["info"] = {'plot': i.get('Pilot', 'Không có mô tả'), 'size': ''}
            item["art"] = {"fanart": background_img}
            items.append(item)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})

        item_timfshare= {
                'label': '[COLOR yellow][I]More on timfshare.com[/I][/COLOR]',
                'is_playable': False,
                'path': 'plugin://plugin.video.vietmediaF?action=__TIMFSHARE__&ref=ref&keyword='+query,
                'thumbnail': 'https://i.imgur.com/F5582QW.png',
                'icon': 'https://i.imgur.com/F5582QW.png',
                'label2': '',
                'info': {
                    'plot': 'Tìm tiếp trên mạng'},
                'art': {
                        "fanart":'https://i.imgur.com/F5582QW.png',
                        "icon"  :'https://i.imgur.com/F5582QW.png',
                        "poster":'https://i.imgur.com/F5582QW.png',
                        "thumb":'https://i.imgur.com/F5582QW.png'
                        }
                }

        item_adv= getadv()
        if item_adv:
            items_length = len(data["items"])
            random_position = random.randint(1, min(8, items_length + 1))
            data["items"].insert(random_position, item_adv)
            data['items'].append(item_timfshare)
        else:
            data['items'].append(item_timfshare)
        return data
def timfshare(query):
    query = query.replace("\n", "").replace(".", " ")
    query = query.replace('&ref=ref','')
    query = urllib.parse.quote_plus(query)
    api_timfshare = 'https://api.timfshare.com/v1/string-query-search?query='

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiZnNoYXJlIiwidXVpZCI6IjcxZjU1NjFkMTUiLCJ0eXBlIjoicGFydG5lciIsImV4cGlyZXMiOjAsImV4cGlyZSI6MH0.WBWRKbFf7nJ7gDn1rOgENh1_doPc07MNsKwiKCJg40U'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(api_timfshare + query, headers=headers, timeout=10)
            response.raise_for_status()
            jsondata = response.json()
            break
        except requests.exceptions.RequestException as e:
            notify(f"Lỗi kết nối (thử lần {attempt + 1}): {e}")
            sleep(2)
            if attempt == max_retries - 1:
                notify("Không thể kết nối tới API sau 3 lần thử.")
                return {"content_type": "episodes", "items": []}

    items = []
    for i in jsondata.get('data', []):
        item = {}
        name = i.get('name', '')
        furl = i.get('url', '')
        filesize = float(i.get("size", 0))
        type_f = i.get('file_type', '')


        if furl:
            furl = re.search(r"(.*)\?", furl).group(1) if '?' in furl else furl
            link = f'plugin://plugin.video.vietmediaF?action=play&url={furl}'
            playable = type_f != '0'
        else:
            continue

        item["label"] = name
        item["is_playable"] = playable
        item["path"] = link
        item["thumbnail"] = 'fshare.png'
        item["icon"] = "fshareicon.png"
        item["label2"] = ""
        item["info"] = {'plot': '', 'size': filesize}
        items.append(item)

    data = {"content_type": "episodes", "items": items}
    valid_extensions = ['.mkv', '.mp4', '.wmv', '.iso', '.ISO', '.ts']

    new_items = []
    for item in data['items']:
        label = item['label']
        extension = label[label.rfind('.'):].lower()
        if extension in valid_extensions:
            new_items.append(item)

    data['items'] = new_items
    t = len(data['items'])

    if t == 0:
        notify("Không tìm thấy kết quả phù hợp.")
    return data

def searchtvhd(query):
    query = query.replace("."," ")
    query = urllib.parse.unquote(query)
    query = query.replace("%0a","")


    url = "https://thuvienhd.top/?feed=fsharejson&search=" + query
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','Referers': 'http://www.google.com'}
    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create('Tìm kiếm...', 'Vui lòng đợi')
    r = urlquick.get(url, headers=headers,max_age=60*60)

    data = json.loads(r.content)
    i = 0
    for item in data:

        image = item['image']

        for link in item['links']:

            for ext in [".mkv", ".mp4", ".wmv", ".iso", ".ISO", ".ts"]:
                if ext in link["title"]:
                    furl = link['link']
                    label,file_type,size = fshare.get_fshare_file_info(furl)
                    path = 'plugin://plugin.video.vietmediaF?action=play&url='+furl
                    link_list_item = xbmcgui.ListItem(label=label)
                    link_list_item.setInfo(type='video', infoLabels={'Title': label,'Size': size})
                    link_list_item.setArt({'thumb': image, 'icon': image})
                    if not "File không tồn tại" in label:
                        i +=1
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=link_list_item,isFolder=False)
                    progress_dialog.update(int((i+1) * 100 / len(item['links'])), 'Kiểm tra link...')
                    if progress_dialog.iscanceled():

                        break
            if progress_dialog.iscanceled():
                break
        if progress_dialog.iscanceled():
            alert("Bạn vừa huỷ tìm kiếm")
            break
    notify("Tổng cộng có %s file khả dụng được tìm thấy" % str(i))
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True, updateListing=False, cacheToDisc=True)
    '''
    items = []
    for x in data:
        image = x["image"]

        for i in x['links']:
            item = {}
            name = i['title']
            flink = i['link']
            file_type, name, file_size = getlink.checkFileInfo(flink)
            if "file" in flink:
                link = ('plugin://plugin.video.vietmediaF?action=play&url=%s' % flink)
                playable = True
            else:
                link = ('plugin://plugin.video.vietmediaF?action=play&url=%s' % flink)
                playable = False
            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = image
            item["icon"] = image
            item["label2"] = ""
            item["info"] = {'plot': '','size':file_size}
            items += [item]
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        valid_extensions = ['.mkv', '.mp4', '.wmv', '.iso', '.ISO', '.ts']
        new_items = []

        for item in data['items']:
            label = item['label']
            extension = label[label.rfind('.'):].lower()
            if extension in valid_extensions:
                new_items.append(item)

        data['items'] = new_items
    return data
    '''

def top100search():
    response = requests.get("https://timfshare.com/api/key/data-top", headers=headers)
    if response.status_code == 200:
        content = response.json()
        video_extensions = ["mkv", "mp4", "avi", "mov", "flv", "wmv", "iso"]
        filtered_videos = [
            i for i in content.get("dataFile", [])
            if i.get("file_extension") in video_extensions
        ][:100]
        items = []
        for video in filtered_videos:
            item = {}
            name = video.get('name')
            furl = f"https://www.fshare.vn/file/{video.get('linkcode')}"
            link = f'plugin://plugin.video.vietmediaF?action=play&url={furl}'
            size = video.get('size')
            playable = True
            item["label"] = name
            item["is_playable"] = playable
            item["path"] = link
            item["thumbnail"] = 'fshare.png'
            item["icon"] = "fshareicon.png"
            item["label2"] = ""
            item["info"] = {'plot': '', 'size': size}
            item["art"] = {"fanart": ''}
            items.append(item)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        item_adv= getadv()
        items_length = len(data["items"])
        random_position = random.randint(1, min(8, items_length + 1))
        data["items"].insert(random_position, item_adv)
        return data
    else:
        alert(f"Failed to fetch data. Status Code: {response.status_code}, Response: {response.text}")

def searchFourshare(query,page):
    fourshare_search_api = "https://api.4share.vn/api/v1/?cmd=search_file_name&search_string="+query+"&ext=ts,mkv,iso,mp4,m2ts,avi,wmv,flv,mpeg,asf,flv,mka,m4a,aac&exactly=on"+"&page=" + str(page)

    r = urlquick.get(fourshare_search_api)
    jdata = json.loads(r.content)
    items = []
    for i in jdata["payload"]["links"]:
        item={}
        name = i["name"]
        size = i["size"]
        link = i["link"]
        file_id = i["file_id"]
        if "/f/" in link:
            link = ('plugin://plugin.video.vietmediaF?action=play&url=%s' % link)
            playable=True
        else:
            link = ('plugin://plugin.video.vietmediaF?action=play&url=%s' % link)
            playable=False
        item["label"] = name
        item["is_playable"] = playable
        item["path"] = link
        item["thumbnail"] = '4share.png'
        item["icon"] = "fourshareicon.png"
        item["label2"] = ""
        item["info"] = {'plot': '','size':size}
        items += [item]
    data = {"content_type": "episodes", "items": ""}
    data.update({"items": items})

    totalPage = jdata["payload"]["total_page"]
    nextpage = int(page)+1

    item_nextpage = {
            'label': '[COLOR yellow][I]Next page[/I][/COLOR]',
            'is_playable': False,
            'path': 'plugin://plugin.video.vietmediaF?action=_timtren4share1_&page='+str(nextpage)+'&keyword='+query,
            'thumbnail': 'https://i.imgur.com/pHbuVqt.png',
            'icon': 'https://i.imgur.com/pHbuVqt.png',
            'label2': '',
            'info': {
                'plot': 'Tìm tiếp trên mạng'},
            'art': {
                    "fanart":'https://i.imgur.com/pHbuVqt.png',
                    "icon"  :'https://i.imgur.com/pHbuVqt.png',
                    "poster":'https://i.imgur.com/pHbuVqt.png',
                    "thumb":'https://i.imgur.com/pHbuVqt.png'
                    }
            }
    if totalPage> 0 and nextpage <totalPage:
        data['items'].append(item_nextpage)
    return data