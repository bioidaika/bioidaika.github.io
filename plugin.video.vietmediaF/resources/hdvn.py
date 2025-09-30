import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests, json, random
from bs4 import BeautifulSoup
import re, os
import urllib.parse
from resources import fshare, cache_utils
import htmlement
from .addon import alert, notify, TextBoxes, getadv, ADDON, ADDON_ID, CACHE_PATH, PROFILE_PATH
import xbmcgui, xbmc, xbmcvfs
import concurrent.futures
import getlink
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading
from xbmcgui import DialogProgress
from collections import OrderedDict
from resources import hdvnsearch

url_hdvn = "https://www.hdvietnam.xyz/"
cookie = "xf_user=1983091%2C8cdb6cf90d618349958e40ea9b57b628dffd971c"
HISTORY_FILE = os.path.join(PROFILE_PATH, 'hdvn.dat')

def save(content, filename):
    filename = os.path.join(PROFILE_PATH, filename)
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    #notify(f"Dữ liệu đã được lưu vào file {filename}")
    
def create_item(name, playable, path, thumbnail, info, fanart,size_file):
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
def get_token():
    url = "https://www.hdvietnam.xyz/"
    headers = {
        "authority": "www.hdvietnam.xyz",
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
    }
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    if status_code == 200:
        regex = r"\"_xfToken\" value=\"(.*)\""
        match = re.search(regex,response.text)
        _xfToken = match.group(1)
        return(_xfToken)

def get_img(url):
    headers = {
        "authority": "www.hdvietnam.xyz",
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
    }
    success = False
    for _ in range(3):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            success = True
            break
        except Exception as e:
            image_path = ''
    if not success:
        image_path = ''
        return
        
    soup = BeautifulSoup(response.content, "html.parser")
    div = soup.find("div", class_="messageInfo primaryContent")
    img_tags = div.find_all('img') if div else []
    image_urls = []
    if img_tags:
        for img_tag in img_tags:
            if 'data-url' in img_tag.attrs:
                image_url = img_tag['data-url']
                image_urls.append(image_url)
            elif 'src' in img_tag.attrs:
                image_url = img_tag['src']
                image_urls.append(image_url)

    image_path = image_urls[0] if image_urls else None
    return image_path

def create_list(url):
    prefix_title = ""
    if "4share-vn" in url:
        prefix_title = "4share-vn"
    
    headers = {
        "authority": "www.hdvietnam.xyz",
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
    }
    def getlisthdvn(url):
        success = False
        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, verify=False, timeout=30)
                success = True
                break
            except Exception as e:
                xbmcgui.Dialog().notification('Lỗi', 'Không lấy được nội dung từ web', xbmcgui.NOTIFICATION_ERROR)
        if not success:
            alert("Không lấy được nội dung từ trang web")
            return
            
        soup = BeautifulSoup(response.content, "html.parser")
        discussion_list = soup.find("ol", class_="discussionListItems")
        thread_items = discussion_list.find_all("li", id=lambda value: value and value.startswith("thread-"))
        items = []
        
        def process_thread_item(thread_item):
            sticky = thread_item.find("span", class_="sticky")
            if not sticky:
                link = thread_item.find("a")
                href = link["href"]
                text = link.get_text()
                h3 = thread_item.find("h3", class_="title")
                a_tag = h3.find('a', class_='PreviewTooltip')
                href = a_tag['href']
                name = a_tag.get_text()
                href = "https://www.hdvietnam.xyz/" + href
                image_path = get_img(href)
                href = prefix_title+href
                item = create_item(name,False,f"plugin://plugin.video.vietmediaF?action=browse&url={href}",image_path,"",image_path,"")
                return item
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_item = {executor.submit(process_thread_item, thread_item): thread_item for thread_item in thread_items}
            for future in concurrent.futures.as_completed(future_to_item):
                try:
                    item = future.result()
                    if item:
                        items.append(item)
                except Exception as e:
                    alert(f"An error occurred: {e}")
                    
        
        #Next page
        if not "page" in url:
            base_url=url
            current_page = 1
        else:
            base_url = re.search(r"(.*)page",url).group(1)
            current_page = re.search(r"page-(\d+)",url).group(1)
        next_page = int(current_page)+1
        url_next_page = f"vmf{prefix_title}{base_url}page-{next_page}"
        #url_next_page = f"vmf{base_url}page-{next_page}"
        item_nextpage = create_item(f"[COLOR yellow]Trang {next_page}[/COLOR]",False,f"plugin://plugin.video.vietmediaF?action=browse&url={url_next_page}","https://i.imgur.com/yCGoDHr.png",f"Trang {next_page}","https://i.imgur.com/yCGoDHr.png","")
        items.append(item_nextpage)
        
        adv_data = getadv()
        _item_adv = create_item(
            name=adv_data["label"],
            playable=adv_data["is_playable"],
            path=adv_data["path"],
            thumbnail=adv_data["thumbnail"],
            info=adv_data["info"]["plot"],
            fanart=adv_data["art"]["fanart"],
            size_file="")
        items.insert(0, _item_adv)
        return items
    # Kiểm tracache
    cache_filename = hashlib.md5(url.encode()).hexdigest() + '_cache.json'
    cache_path = os.path.join(CACHE_PATH, cache_filename)
    if cache_utils.check_cache(cache_path):
        # Đọc nội dung từ file cache
        with open(cache_path, 'r') as cache_file:
            cache_content = json.load(cache_file)
            #notify("cached")
        return cache_content
    else:
        data = getlisthdvn(url)
        with open(cache_path, "w") as f:
            json.dump(data, f)
            #notify("fresh data")
        return data
        
def dolike(url):
    
    _xfToken = get_token()
    headers = {
        "authority": "www.hdvietnam.xyz",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
        "x-requested-with": "XMLHttpRequest"
    }
    data = {
        #"_xfRequestUri": "/threads/hanh-dong-phantom-2023-bluray-1080p-dts-hdma-5-1-x265-10bit-dreamhd-dac-vu-bong-ma.1866102/",
        "_xfNoRedirect": "1",
        "_xfToken": _xfToken,
        "_xfResponseType": "json"
        }
    response = requests.post(url, headers=headers, data=data)

def get_content(url):
    def get_content_hdvn(url):
        headers = {
            "authority": "www.hdvietnam.xyz",
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
        }
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        span_tag = soup.find('span', class_='LikeLabel')
        if span_tag and span_tag.get_text() == 'Cảm ơn':
            a_tag = soup.find('a', class_='LikeLink item control like')
            url_post = url_hdvn+a_tag['href']
            dolike(url_post)
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("ol", class_="messageList")
        
        img_tags = div.find_all('img') if div else []
        image_urls = []
        if img_tags:
            for img_tag in img_tags:
                if 'data-url' in img_tag.attrs:
                    image_url = img_tag['data-url']
                    image_urls.append(image_url)
                elif 'src' in img_tag.attrs:
                    image_url = img_tag['src']
                    image_urls.append(image_url)

        image_path = image_urls[1] if image_urls else None
        
        if div:
            content = div.find("div", class_="messageContent")
            
            if content:
                links = content.find_all("a")
                items = []
                count = 0
                for link in links:
                    href = link.get("href")
                    if href and "fshare.vn" in href:
                        name,file_type,size_file = fshare.get_fshare_file_info(href)
                        if "folder" in href: playable = False
                        else: playable = True
                        if count ==0: name = f"[COLOR yellow]{name}[/COLOR]"
                        if size_file is not None and size_file.isnumeric() and int(size_file) > 0:item = create_item(name,playable,f"plugin://plugin.video.vietmediaF?action=browse&url={href}",image_path,'',image_path,size_file)
                        else:
                            name = "Files đã bị xoá"
                            item = create_item(name, playable, f"plugin://plugin.video.vietmediaF?action=browse&url={href}", "https://i.imgur.com/1wxUwaE.png", '', "https://i.imgur.com/lrynDXs.png", size_file)
                        items.append(item)
                        count +=1
                        if count ==5:break
                #find more
                urls = re.findall(r'\[url=(.*?)\]', str(content))
                fshare_urls = [url for url in urls if 'fshare.vn' in url]
                for href in fshare_urls:
                    name,file_type,size_file = fshare.get_fshare_file_info(href)
                    if "folder" in href: playable = False
                    else: playable = True
                    if size_file is not None and size_file.isnumeric() and int(size_file) > 0:item = create_item(name,playable,f"plugin://plugin.video.vietmediaF?action=browse&url={href}",image_path,'',image_path,size_file)
                    else:
                        name = "Files đã bị xoá"
                        item = create_item(name, playable, f"plugin://plugin.video.vietmediaF?action=browse&url={href}", "https://i.imgur.com/1wxUwaE.png", '', "https://i.imgur.com/lrynDXs.png", size_file)
                    items.append(item)
                data = {"content_type": "episodes", "items": ""}
                data.update({"items": items})
                return data
        else:
            alert("Lỗi trang")
            exit()
    # Kiểm tracache
    cache_filename = hashlib.md5(url.encode()).hexdigest() + '_cache.json'
    cache_path = os.path.join(CACHE_PATH, cache_filename)
    if cache_utils.check_cache(cache_path):
        # Đọc nội dung từ file cache
        with open(cache_path, 'r') as cache_file:
            cache_content = json.load(cache_file)
            #notify("cached")
        return cache_content
    else:
        data = get_content_hdvn(url)
        with open(cache_path, "w") as f:
            json.dump(data, f)
            #notify("fresh data")
        return data
        
def get_content_4s(url):
    def getcontent_4share(url):
        headers = {
            "authority": "www.hdvietnam.xyz",
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0"
        }
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        span_tag = soup.find('span', class_='LikeLabel')
        if span_tag and span_tag.get_text() == 'Cảm ơn':
            a_tag = soup.find('a', class_='LikeLink item control like')
            url_post = url_hdvn+a_tag['href']
            dolike(url_post)
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("ol", class_="messageList")
        
        img_tags = div.find_all('img') if div else []
        image_urls = []
        if img_tags:
            for img_tag in img_tags:
                if 'data-url' in img_tag.attrs:
                    image_url = img_tag['data-url']
                    image_urls.append(image_url)
                elif 'src' in img_tag.attrs:
                    image_url = img_tag['src']
                    image_urls.append(image_url)

        image_path = image_urls[1] if image_urls else None
        if div:
            content = div.find("div", class_="messageContent")
            if content:
                links = content.find_all("a")
                items = []
                size_file = ''
                for link in links:
                    href = link.get("href")
                    if href and "4share.vn" in href:
                        if "/d/" in href: 
                            playable = False
                            name = href
                        else: 
                            playable = True
                            name,size_file = getlink.get_4file_information(href)
                        
                        item = create_item(name, playable, f"plugin://plugin.video.vietmediaF?action=browse&url={href}", "https://i.imgur.com/ytoQpHG.png", '', "https://i.imgur.com/ytoQpHG.png", size_file)
                        items.append(item)
                #find more
                urls = re.findall(r'\[url=(.*?)\]', str(content))
                share_urls = [url for url in urls if '4share.vn' in url]

                for href in share_urls:
                    if "/d/" in href: 
                            playable = False
                            name = href
                    else: 
                        playable = True
                        name,size_file = getlink.get_4file_information(href)
                            
                    item = create_item(href, playable, f"plugin://plugin.video.vietmediaF?action=browse&url={href}", "https://i.imgur.com/ytoQpHG.png", '', "https://i.imgur.com/ytoQpHG.png", size_file)
                    items.append(item)
                data = {"content_type": "episodes", "items": ""}
                data.update({"items": items})
                return data
    # Kiểm tracache
    cache_filename = hashlib.md5(url.encode()).hexdigest() + '_cache.json'
    cache_path = os.path.join(CACHE_PATH, cache_filename)
    if cache_utils.check_cache(cache_path):
        # Đọc nội dung từ file cache
        with open(cache_path, 'r') as cache_file:
            cache_content = json.load(cache_file)
            #notify("cached")
        return cache_content
    else:
        data = getcontent_4share(url)
        with open(cache_path, "w") as f:
            json.dump(data, f)
            #notify("fresh data")
        return data
def check_history():
    # Kiểm tra xem file lịch sử tìm kiếm đã tồn tại hay chưa
    if not os.path.exists(HISTORY_FILE):
        return False
    else:
        if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
            return True
        else:
            return False
            
            
def save_search_history(query):
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = [line.strip() for line in f if line.strip()]
    except:
        history = []
    
    if query not in history:
        history.insert(0, query)
    with open(HISTORY_FILE, 'w') as f:
        f.write('\n'.join(history[:50]))
        
def search_list(url_redirect):
    headers = {
            "authority": "www.hdvietnam.xyz",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": cookie,
            "origin": "https://www.hdvietnam.xyz",
            "referer": "https://www.hdvietnam.xyz/search/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
            "x-ajax-referer": "https://www.hdvietnam.xyz/search/",
            "x-requested-with": "XMLHttpRequest",
        }
    r = requests.get(url_redirect, headers=headers, verify=False, timeout=30)
    soup = BeautifulSoup(r.content, "html.parser")
    #Next page
    page = soup.find("span", class_="pageNavHeader")
    max_page = 1
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
            #Next page url:
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
            if page:
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

def process_item(item):
    href = item.find('a')['href']
    href = f'https://www.hdvietnam.xyz/{href}'
    href = href.replace('unread','')
    path = f"plugin://plugin.video.vietmediaF?action=browse&url={href}"
    name = item.find('a').get_text().strip()
    image_path = get_img(href)
    return create_item(name,False,path,image_path,name,image_path,'')

def getLastest():
    headers = {
        "authority": "www.hdvietnam.xyz",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "origin": "https://www.hdvietnam.xyz",
        "referer": "https://www.hdvietnam.xyz/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
        "x-ajax-referer": "https://www.hdvietnam.xyz/",
        "x-requested-with": "XMLHttpRequest"
    }

    data = {
        "tab_id": "0",
        "modern_statistic_id": "1",
        "hard_reload": "false",
        "_xfRequestUri": "/",
        "_xfNoRedirect": "1",
        "_xfToken": get_token(),
        "_xfResponseType": "json"
    }
    response = requests.post("https://www.hdvietnam.xyz/brms-statistic/statistics.json", headers=headers, data=data)
    jsdata = json.loads(response.content)
    tabContentHtml = jsdata['tabContentHtml']
    soup = BeautifulSoup(tabContentHtml, "html.parser")
    items = soup.find_all("div", class_="listBlock itemTitle")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        item_futures = []
        for item in items:
            item_futures.append(executor.submit(process_item, item))
        
        items = [item.result() for item in item_futures]

    data = {"content_type": "", "items": ""}
    data.update({"items": items})
    return data
        
        

def search(keywords,custom_data=None):
    url = "https://www.hdvietnam.xyz/search/search"
    headers = {
        "authority": "www.hdvietnam.xyz",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "origin": "https://www.hdvietnam.xyz",
        "referer": "https://www.hdvietnam.xyz/search/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
        "x-ajax-referer": "https://www.hdvietnam.xyz/search/",
        "x-requested-with": "XMLHttpRequest",
    }

    if custom_data is None:
        data = {
            'keywords': keywords,
            'title_only': '1',
            'users': '',
            'date': '',
            'nodes[]': ['6', '337', '116', '33', '57', '123', '149', '150'],
            'child_nodes': '1',
            'order': 'date',
            '_xfToken': get_token(),
            '_xfRequestUri': '/search/',
            '_xfNoRedirect': '1',
            '_xfResponseType': 'json'
        }
    else:
        data = custom_data
    response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
    jsondata = json.loads(response.content)
    url_redirect = jsondata["_redirectTarget"]
    data = search_list(url_redirect)
    
    return data
def receive(url):
    
    import random
    if "menu" in url:
        names = ["Tìm kiếm","Mới nhất","Phim lẻ","Phim bộ - Series","Phim hoạt hình","Phim theo phân loại","Phim tài liệu - Documentaries","Phim 4K","Thư viện link film"]
        links = [f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}timkiem/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}lastest/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phimle",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phimbo",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phimhoathinh",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phimtheophanloai",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phimtailieu",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}phim4K",
                f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/thu-vien-link-phim.150/"
                ]
        items = []
        backgrounds = ["https://i.imgur.com/JOjvenW.jpg","https://i.imgur.com/i9xJ8G7.jpg","https://i.imgur.com/17rC84l.jpg","https://i.imgur.com/kgES8v1.jpg","https://i.imgur.com/w9FEM05.jpg","https://i.imgur.com/c5JkgO7.jpg","https://i.imgur.com/9xYGdxn.jpg"]
        fanart = random.choice(backgrounds)
        
        for name, link in zip(names, links):
            item = create_item(name, False, link, None, "", fanart,"")
            items.append(item)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phimbo" in url:
        item1 = create_item("[COLOR yellow]Phim bộ chất lượng mHD, SD[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/mhd-sd.104/", '','Phim bộ mHD, SD','','')
        
        items = create_list(url_hdvn+"forums/phim-bo-series.57/")
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "vmf" in url or "forums" in url:
        url = url.replace("vmf","")
        items = create_list(url)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phimle" in url:
        item1 = create_item("[COLOR yellow]Phim WEB-DL, HDTV[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/web-dl-hdtv.271/", '','Phim webdl','','')
        item2 = create_item("[COLOR yellow]Bluray Remux[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-remux.324/", '','Phim bluray remux','','')
        item3 = create_item("[COLOR yellow]Phim mHD, SD[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/mhd-sd.77/", '','Phim mHD, SD','','')
        item4 = create_item("[COLOR yellow]Phim Bluray nguyên gốc[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-nguyen-goc.78/", '','Phim Bluray nguyên gốc','','')
        items = create_list("https://www.hdvietnam.xyz/forums/fshare-vn.33/")
        items.insert(0, item4)
        items.insert(0, item3)
        items.insert(0, item2)
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phim4K" in url:
        item1 = create_item("[COLOR yellow]WEB-DL, HDTV 4K[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/web-dl-hdtv-4k.344/", '','WEB-DL, HDTV 4K','','')
        item2 = create_item("[COLOR yellow]Bluray Remux 4K[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-remux-4k.345/", '','Bluray Remux 4K','','')
        item3 = create_item("[COLOR yellow]Bluray Nguyên Gốc 4K[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-nguyen-goc-4k.346/", '','Bluray Remux 4K','','')
        items = create_list("https://www.hdvietnam.xyz/forums/4k.337/")
        items.insert(0, item3)
        items.insert(0, item2)
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phimtailieu" in url:
        item1 = create_item("[COLOR yellow]Phim Tài Liệu - Thuyết Minh[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/phim-tai-lieu-thuyet-minh.347/", '','Phim Tài Liệu - Thuyết Minh','','')
        items = create_list("https://www.hdvietnam.xyz/forums/phim-tai-lieu-documentaries.116/")
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phimhoathinh" in url:
        item1 = create_item("[COLOR yellow]Phim HH mHD, SD[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/mhd-sd.124/", '','Phim Tài Liệu - Thuyết Minh','','')
        items = create_list("https://www.hdvietnam.xyz/forums/phim-hoat-hinh.123/")
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "phimtheophanloai" in url:
        item1 = create_item("[COLOR yellow]Phim có audio Việt[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/phim-co-audio-viet.265/", '','Phim có audio Việt','','')
        item2 = create_item("[COLOR yellow]Phim 3D[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/3d.110/", '','Phim 3D','','')
        item3 = create_item("[COLOR yellow]Phim cho iOS/Android[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/phim-cho-ios-android.157/", '','Phim cho iOS/Android','','')
        items = []
        items.insert(0, item3)
        items.insert(0, item2)
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    
    elif "/timkiem/" in url:
        if not check_history():  # Kiểm tra nếu lịch sử trống (lần đầu tiên nhấn tìm kiếm)
            keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                query = keyboard.getText()
                query = urllib.parse.unquote(query)
                save_search_history(query)  # Lưu lịch sử tìm kiếm
                data = search(query)  # Gửi yêu cầu tìm kiếm
                return data
            else:
                alert("Không có gì được nhập vào.")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                
        else:  # Nếu đã có lịch sử, hiển thị menu tìm kiếm
            items = []
            items1 = [{
                'label': '[COLOR yellow]Tìm kiếm mới[/COLOR]',
                'is_playable': False,
                'path': "plugin://plugin.video.vietmediaF?action=browse&url=hdvietnam.xyz/tim_kiem_moi",
                'thumbnail': 'https://i.imgur.com/F5582QW.png',
                'icon': 'https://i.imgur.com/F5582QW.png',
                'label2': '',
                'info': {
                    'plot': 'Nhập từ khóa tìm kiếm mới'}
            }]
            items2 = [{
                'label': '[COLOR yellow][I]Xoá lịch sử tìm kiếm[/I][/COLOR]',
                'is_playable': False,
                'path': f"plugin://plugin.video.vietmediaF?action=browse&url=hdvietnam.xyz/xoa_tk",
                'thumbnail': 'https://i.imgur.com/oS0Humg.png',
                'icon': 'https://i.imgur.com/oS0Humg.png',
                'label2': '',
                'info': {
                    'plot': 'Xoá toàn bộ lịch sử tìm kiếm'}
            }]
            with open(HISTORY_FILE, 'r') as file:
                history = file.read().splitlines()
                if history:
                    for query in history:
                        item = create_item(query, False, f"plugin://plugin.video.vietmediaF?action=browse&url=hdvietnam.xyz/tim_kiemkeyword={query}", "https://i.imgur.com/F5582QW.png", f"Tìm kiếm [COLOR yellow]{query}[/COLOR] trên HDVN", "https://i.imgur.com/F5582QW.png", "")
                        items.append(item)
            
            items = items1 + items2 + items  # Kết hợp các mục vào danh sách
            data = {"content_type": "", "items": ""}
            data.update({"items": items})
            return data
    
    elif "tim_kiem" in url:
        
        if "keyword" in url:
            match = re.search(r"keyword=(.*)",url)
            if match:
                query = match.group(1)
                query = urllib.parse.unquote(query)
                data = search(query)
                return data
            else:
                alert("Có lỗi xảy ra. Thử lại")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)  
        else:
            
            keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                query = keyboard.getText()
                query = urllib.parse.unquote(query)
                save_search_history(query)
                data = search(query)
                return data
            else:
                alert("Không có gì được nhập vào.")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)  
    elif "/tkseries/" in url:
        
        keyboard = xbmc.Keyboard("", "Nhập tên phim")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
            query = urllib.parse.unquote(query)
            save_search_history(query)
            data = {
              'keywords': query,
              'title_only': '1',
              'users': '',
              'date': '',
              'nodes[]': ['57'],
              'child_nodes': '1',
              'order': 'date',
              '_xfToken': get_token(),
              '_xfRequestUri': '/search/',
              '_xfNoRedirect': '1',
              '_xfResponseType': 'json'
            }
            data = search(query,data)
            return data
        else:
            alert("Không có gì được nhập vào.")
            exit()
    
    elif "/search/" in url:
        match = re.search(r"url=(.*)",url)
        if match:
            url = match.group(1)
        data = search_list(url)
        return data
    elif "xoa_tk" in url:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'w') as file:
                file.write('')
        notify("Đã xoá lịch sử tìm kiếm")
        #xbmc.executebuiltin("Container.Refresh")
        exit()
    elif "/4share/" in url:
        item1 = create_item("[COLOR yellow]WEB-DL, HDTV[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/web-dl-hdtv.277/", '','WEB-DL, HDTV','','')
        item2 = create_item("[COLOR yellow]Bluray nguyên gốc[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-nguyen-goc.342/", '','Bluray nguyên gốc','','')
        item3 = create_item("[COLOR yellow]Bluray Remux[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/bluray-remux.343/", '','Bluray Remux','','')
        item4 = create_item("[COLOR yellow]mHD, SD[/COLOR]", False, f"plugin://plugin.video.vietmediaF?action=browse&url={url_hdvn}forums/mhd-sd.147/", '','mHD, SD','','')
        items = create_list("https://www.hdvietnam.xyz/forums/4share-vn.146/")
        items.insert(0, item4)
        items.insert(0, item3)
        items.insert(0, item2)
        items.insert(0, item1)
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "/lastest/" in url:
        data = getLastest()
        return data
    if "/threads/" in url:
        if "4share-vnhttps" in url:
            url = url.replace("4share-vnhttps","https")
            return (get_content_4s(url))
        else:return (get_content(url))