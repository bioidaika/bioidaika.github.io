import os
import xbmc, xbmcvfs
import xbmcgui
import urllib.parse
import requests, json
from bs4 import BeautifulSoup
import re
from .addon import alert, notify, TextBoxes, ADDON, ADDON_ID, PROFILE_PATH
from .history_utils import hdvn_history



def save(content, filename):
    filename = os.path.join(PROFILE_PATH, filename)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    

def search_list(url_redirect):
    headers = {
            "authority": "www.hdvietnam.xyz",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": "xf_user=2088313^%^2C10db5baa88340666d7f3fce6a98fae71a9bf3264",
            "origin": "https://www.hdvietnam.xyz",
            "referer": "https://www.hdvietnam.xyz/search/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
            "x-ajax-referer": "https://www.hdvietnam.xyz/search/",
            "x-requested-with": "XMLHttpRequest",
        }
    r = requests.get(url_redirect, headers=headers, verify=False, timeout=30)
    soup = BeautifulSoup(r.content, "html.parser")
    
    page = soup.find("span", class_="pageNavHeader")
    if page:
        max_page = (page.get_text(strip=True))
        match = re.search(r"(\d+)\strang",max_page)
        if match:
            max_page = match.group(1)


    divs = soup.find("ol", class_="searchResultsList")
    items = []
    if divs:

        threads = soup.find_all('li', id=lambda value: value and value.startswith('thread'))
        if threads:
            for thread in threads:
                h3 = thread.find('h3', class_='title')
                href = h3.a.get('href')
                href = "https://www.hdvietnam.xyz/"+href
                path = f"plugin://plugin.video.vietmediaF?action=browse&url={href}"
                name = h3.get_text(strip=True)
                blockquote = thread.find("blockquote", class_="snippet")
                snippet = blockquote.get_text(strip=True)
                snippet = snippet.replace("[img]","").replace("[IMG]","").replace("\n"," ")
                snippet = snippet.strip()
                snippet_list = snippet.split(',')
                snippet = ' '.join([info.strip() for info in snippet_list])
                meta = thread.find("div", class_="meta")
                metainfo = meta.get_text(strip=True)
                metainfo_list = metainfo.split(',')
                metainfo = ' '.join([info.strip() for info in metainfo_list])
                item = create_item(name, False, path, "https://i.imgur.com/9RyMjcw.png", f"{snippet}\n{metainfo}", "https://i.imgur.com/9RyMjcw.png","")
                items.append(item)
            
            if "page" in url_redirect:
                match = re.search(r"page=(\d+)",url_redirect)
                current_page = match.group(1)
                next_page = int(current_page)+1
                next_page_url = url_redirect.replace(current_page,str(next_page))

            else:
                current_page = 1
                next_page = int(current_page)+1
                match = re.search(r"^(.*?)(?:\?|$)",url_redirect)
                base_url = match.group(1)
                next_page_url = url_redirect.replace(base_url,f"{base_url}?page={next_page}")
                next_page_url = next_page_url.replace("?q","&q")
            if next_page < int(max_page):
                item_nextpage = create_item(f"[COLOR yellow]Trang {next_page}[/COLOR]",False,f"plugin://plugin.video.vietmediaF?action=browse&url={next_page_url}","https://i.imgur.com/yCGoDHr.png",f"Trang {next_page}","https://i.imgur.com/yCGoDHr.png","")
                items.append(item_nextpage)
            data = {"content_type": "episodes", "items": ""}
            data.update({"items": items})
            return data

        else:
            alert("Không có kết quả tìm kiếm")
            return
    else:
            alert("Không có kết quả tìm kiếm")
            return

def search(keywords,_xfToken):
    url = "https://www.hdvietnam.xyz/search/search"
    headers = {
        "authority": "www.hdvietnam.xyz",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "xf_user=2088313^%^2C10db5baa88340666d7f3fce6a98fae71a9bf3264",
        "origin": "https://www.hdvietnam.xyz",
        "referer": "https://www.hdvietnam.xyz/search/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
        "x-ajax-referer": "https://www.hdvietnam.xyz/search/",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
      'keywords': keywords,
      'title_only': '1',
      'users': '',
      'date': '',
      'nodes[]': ['6', '337', '116', '33', '57', '123', '149', '150'],
      'child_nodes': '1',
      'order': 'date',
      '_xfToken': _xfToken,
      '_xfRequestUri': '/search/',
      '_xfNoRedirect': '1',
      '_xfResponseType': 'json'
    }
    response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
    jsondata = json.loads(response.content)
    url_redirect = jsondata["_redirectTarget"]
    alert(url_redirect)
    data = search_list(url_redirect)
    save(str(data),"timkiem.txt")
    return data

def create_item(name, playable, path, thumbnail, info, fanart, size_file):
    item = {}
    item["label"] = name
    item["is_playable"] = playable
    item["path"] = path
    item["thumbnail"] = thumbnail
    item["icon"] = thumbnail
    item["label2"] = ""
    item["info"] = {'plot': info, 'size': size_file}
    item["art"] = {'fanart': fanart}
    return item

def get_search_history():
    """Lấy lịch sử tìm kiếm từ file"""
    return hdvn_history.get_history()

def save_search_history(history):
    """Lưu lịch sử tìm kiếm vào file"""
    for query in history:
        hdvn_history.save_history(query)

def show_search_history_dialog():
    
    history = get_search_history()
    
    if not history:
        return None

    
    selected_query = xbmcgui.Dialog().select('Lịch sử tìm kiếm', history)

    
    if selected_query >= 0:
        return history[selected_query]
    else:
        exit()
    return None

def timkiemhdvn(_xfToken):
    
    query = show_search_history_dialog()

    
    if not query:
        keyboard = xbmc.Keyboard("", "Nhập tên phim")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
            query = urllib.parse.unquote(query)
        else:
            xbmcgui.Dialog().ok("Thông báo", "Không có gì được nhập vào.")
            return None

    
    hdvn_history.save_history(query)

    
    data = search(query, _xfToken)
    return data

def delete_search_history():
    """Xóa toàn bộ lịch sử tìm kiếm"""
    hdvn_history.delete_history()