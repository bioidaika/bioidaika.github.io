import requests
from bs4 import BeautifulSoup
import re, os, json
import hashlib
import urllib.parse
from resources import fshare, cache_utils
import htmlement
from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, CACHE_PATH, addon_url, ADDON_PATH
import xbmcgui, xbmc, xbmcvfs
#from concurrent.futures import ThreadPoolExecutor
import threading

from collections import OrderedDict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import ConnectionError, Timeout, RequestException
from resources.addon import log

# Lấy domain từ addon settings
default_domain = "thuvienhd.top"
thuvienhd_domain = ADDON.getSetting("thuvienhd_domain") or default_domain

BASE_URL_CF = "https://tvhd.kodi-d06.workers.dev/"
BASE_URL = f"https://{thuvienhd_domain}/"
nextpage_icon = os.path.join(ADDON_PATH, 'resources', 'images', 'nextpage.png')

def create_session():
    session = requests.Session()


    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "HEAD"]
    )


    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)


    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    })

    return session


session = create_session()

# Hàm quản lý lịch sử tìm kiếm
def get_search_history():
    """Lấy lịch sử tìm kiếm từ file"""
    history_file = os.path.join(CACHE_PATH, 'tvhd_search_history.txt')
    if not os.path.exists(history_file):
        return []

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            history = [line.strip() for line in f.readlines() if line.strip()]
        return history
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi đọc lịch sử tìm kiếm: {str(e)}", xbmc.LOGERROR)
        return []

def save_search_history(query):
    """Lưu từ khóa tìm kiếm vào lịch sử"""
    if not query or len(query.strip()) == 0:
        return

    history_file = os.path.join(CACHE_PATH, 'tvhd_search_history.txt')
    history = get_search_history()

    # Loại bỏ từ khóa nếu đã tồn tại (để đưa lên đầu danh sách)
    if query in history:
        history.remove(query)

    # Thêm từ khóa mới vào đầu danh sách
    history.insert(0, query)

    # Giới hạn số lượng từ khóa lưu trữ
    history = history[:20]  # Lưu tối đa 20 từ khóa

    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(history))
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi lưu lịch sử tìm kiếm: {str(e)}", xbmc.LOGERROR)

def clear_search_history():
    """Xóa toàn bộ lịch sử tìm kiếm"""
    history_file = os.path.join(CACHE_PATH, 'tvhd_search_history.txt')
    try:
        if os.path.exists(history_file):
            os.remove(history_file)
            return True
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi xóa lịch sử tìm kiếm: {str(e)}", xbmc.LOGERROR)
    return False

def show_search_history():
    """Hiển thị lịch sử tìm kiếm và cho phép người dùng chọn"""
    history = get_search_history()
    if not history:
        keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
            save_search_history(query)
            return search("1", query)
        return None

    # Thêm các tùy chọn đặc biệt
    options = ["[COLOR yellow]Tìm kiếm mới[/COLOR]", "[COLOR red]Xóa lịch sử tìm kiếm[/COLOR]"] + history
    dialog = xbmcgui.Dialog()
    selected = dialog.select("Lịch sử tìm kiếm", options)

    if selected == -1:  # Người dùng đã hủy
        return None
    elif selected == 0:  # Tìm kiếm mới
        keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm")
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText()
            save_search_history(query)
            return search("1", query)
        return None
    elif selected == 1:  # Xóa lịch sử
        confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ lịch sử tìm kiếm?")
        if confirm:
            clear_search_history()
            notify("Đã xóa lịch sử tìm kiếm")
        return show_search_history()
    else:  # Chọn một từ khóa từ lịch sử
        query = options[selected]
        save_search_history(query)  # Đưa từ khóa lên đầu danh sách
        return search("1", query)

def search(page, query):
    # Lưu từ khóa vào lịch sử nếu đây là trang đầu tiên
    if page == "1":
        save_search_history(query)

    search_url = f"{BASE_URL}page/{page}?s={query}"
    cache_key = hashlib.md5(search_url.encode()).hexdigest() + "_search"

    # Kiểm tra cache
    if cache_utils.check_cache(cache_key, 30):  # Cache có hiệu lực trong 30 phút
        cache_data = cache_utils.get_cache(cache_key)
        if cache_data:
            return cache_data

    try:
        response = session.get(search_url, verify=False, timeout=30)
        response.raise_for_status()
    except (ConnectionError, Timeout) as e:
        alert(f"Lỗi kết nối: {str(e)}")
        return None
    except RequestException as e:
        alert(f"Lỗi khi tìm kiếm: {str(e)}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    result_items = soup.find_all('div', class_='result-item')
    items = []

    for result_item in result_items:
        img_src = result_item.find('img')['src']
        href = result_item.find('a')['href']
        name = result_item.find('div', class_='title')
        if name:
            name = name.text.strip()
            name = re.sub(r'\s*\b(?:HD|SD)\b\s*', '', name, flags=re.IGNORECASE)
            name = name.strip()

        else:
            name = ""

        year = result_item.find('span', class_='year')
        if year:
            year = year.text.strip()
            name = name +" (%s)" % year
        else:
            name = name

        info = result_item.find('div', class_='contenido')
        if info:
            info = info.text.strip()
            info = re.sub(r'\s+', ' ', info)
            info = info.replace(thuvienhd_domain, '')
            info = info.replace('https://', '')
            info = info.strip()
        else:
            info = ""

        max_desc_length = 2000
        if len(info) > max_desc_length:
            info = info[:max_desc_length] + "..."

        encoded_desc = urllib.parse.quote_plus(info.encode('utf-8'))


        full_path = f"{addon_url}browse&url={href}&desc={encoded_desc}"

        item = {
            "label": name,
            "is_playable": False,
            "path": full_path,
            "thumbnail": img_src,
            "icon": img_src,
            "label2": "",
            "info": {"plot": info},
            "art": {"fanart": img_src}
        }

        items.append(item)

    next_page = int(page) + 1
    next_page_url = f"{BASE_URL}page/{next_page}?s={query}"

    try:

        response = session.head(next_page_url, verify=False, timeout=10)

        if response.status_code == 200:
            next_page_url = addon_url + "browse&url=" + next_page_url
            nextpage = {
                "label": '[COLOR yellow]Trang %s[/COLOR] ' % next_page,
                "is_playable": False,
                "path": next_page_url,
                "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
                "icon": "https://i.imgur.com/yCGoDHr.png",
                "label2": "",
                "info": {"plot": "Trang tiếp TVHD"}
            }
            items.append(nextpage)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi kiểm tra trang tiếp theo: {str(e)}", xbmc.LOGINFO)

    data = {"content_type": "episodes", "items": items}


    cache_utils.set_cache(cache_key, data)

    return data

def getlink(url, description=""):

    cache_key = hashlib.md5(url.encode()).hexdigest() + "_links"

    if cache_utils.check_cache(cache_key, 30):
        cache_data = cache_utils.get_cache(cache_key)
        if cache_data:

            return cache_data

    def getlink_(url):

        try:

            response = session.get(url, verify=False, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            try:
                description = soup.find('div', class_='cnnn').text.strip()

                description = description.replace(thuvienhd_domain, "")
                description = description.strip()
                description = description.replace("https://","")
            except:
                description = ''


            img_tag = soup.find("div", class_="poster").find("img")
            img_path = img_tag["src"]

            a_tag = soup.find("span", class_="box__download").find("a")
            href = a_tag["href"]

            response = session.get(href, verify=False, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            link_tags = soup.select('table.post_table a[href*="fshare.vn"]')
            links = [link['href'] for link in link_tags]

            items = []
            total_links = len(links)

            for index, href in enumerate(links, 1):
                name, file_type, size_file = fshare.get_fshare_file_info(href)
                item = {}
                if "folder" in href:
                    playable = False
                else:
                    playable = True
                item["label"] = name
                item["is_playable"] = playable
                item["path"] = 'plugin://plugin.video.vietmediaF?action=browse&url=%s' % href
                item["thumbnail"] = img_path
                item["icon"] = img_path
                item["label2"] = ""
                item["info"] = {'plot': description, 'size': size_file}
                item["art"] = {'fanart':img_path }
                items.append(item)

            data = {"content_type": "movies", "items": ""}

            data.update({"items": items})
            return data

        except (ConnectionError, Timeout) as e:
            alert(f"Lỗi kết nối: {str(e)}")
            return None
        except RequestException as e:
            alert(f"Lỗi khi tải trang: {str(e)}")
            return None
        except Exception as e:
            alert(f"Lỗi không xác định: {str(e)}")
            return None

    data = getlink_(url)

    if data:
        cache_utils.set_cache(cache_key, data)

    return data

def get_movie_info(article_id):
    api_url = f"{BASE_URL}?feed=fsharejson&id={article_id}"
    try:
        response = session.get(api_url, verify=False, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except (ConnectionError, Timeout) as e:
        alert(f"Lỗi kết nối: {str(e)}")
        return None
    except RequestException as e:
        alert(f"Lỗi khi tải trang: {str(e)}")
        return None
    except Exception as e:
        alert(f"Lỗi không xác định: {str(e)}")
        return None
def listGenre(url):

    cache_key = hashlib.md5(url.encode()).hexdigest() + "_genre"

    if cache_utils.check_cache(cache_key, 30):
        cache_data = cache_utils.get_cache(cache_key)
        if cache_data:

            return cache_data

    def listGenre_(url):
        try:
            response = session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")
            articles = soup.find_all("article", class_="item movies")

            items = []
            for article in articles:
                article_id = article.get("id")
                article_id = article_id.replace("post-","")
                movie_info = get_movie_info(article_id)
                name = movie_info.get("title", "")
                name = name.replace("&&","-")
                img = movie_info.get("image", "")
                fanart = img
                year = movie_info.get("year", "")
                description = movie_info.get("description", "")
                href = article.find("a").get("href") if article.find("a") else ""
                data = article.find('div', class_='data')

                year_int = int(year) if year and year.isdigit() else 0

                imdb_elem = article.find("span", class_="imdb")
                imdb = imdb_elem.text.strip() if imdb_elem else ""

                imdb_rating = 0.0
                if imdb:
                    try:

                        imdb_match = re.search(r'([\d.]+)', imdb)
                        if imdb_match:
                            imdb_rating = float(imdb_match.group(1))
                    except:
                        imdb_rating = 0.0

                if year:
                    name = f"{name} ({year})"

                genre_div = article.find("div", class_="genres")
                if genre_div:
                    links = genre_div.find_all('a')
                    genre = '/'.join(link.text.strip() for link in links)
                else:
                    genre = "N/A"


                item = {}
                item["label"] = name
                item["is_playable"] = False
                encoded_description = urllib.parse.quote_plus(description)
                item["path"] = addon_url + "browse&url=" + href + "&desc=" + encoded_description
                item["thumbnail"] = img
                item["icon"] = img
                item["label2"] = name


                item["info"] = {
                    'title': name,
                    'plot': description,
                    'genre': genre,
                    'year': year_int,
                    'rating': imdb_rating,
                    'mediatype': 'movie'
                }


                item["art"] = {
                    "fanart": fanart,
                    "poster": img,
                    "thumb": img,
                    "icon": img
                }

                items.append(item)



            try:
                pagination = soup.find("div", class_="pagination")
                if pagination:
                    current_page_span = pagination.find("span", class_="current")
                    current_page = int(current_page_span.text.strip())
                    next_page = current_page + 1

                    if "page" in url:
                        match = re.search(r"(.*)\/page",url)
                        if match:
                            next_url = match.group(1)
                    else:
                        next_url = url

                    next_url = "%s/page/%s" % (next_url,next_page)
                    next_page_url = addon_url + "browse&url=vmf"+next_url
                    nextpage = {
                        "label": f'[COLOR yellow]Trang {next_page}[/COLOR]',
                        "is_playable": False,
                        "path": next_page_url,
                        "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
                        "icon": "https://i.imgur.com/yCGoDHr.png",
                        "label2": "",
                        "info": {
                            'plot': 'Trang tiếp theo',
                            'mediatype': 'video'
                        },
                        "art": {
                            'thumb': 'https://i.imgur.com/yCGoDHr.png',
                            'icon': 'https://i.imgur.com/yCGoDHr.png',
                            'poster': 'https://i.imgur.com/yCGoDHr.png'
                        }
                    }
                    items.append(nextpage)
            except Exception as e:
                xbmc.log(f"[VietmediaF] Lỗi khi kiểm tra trang tiếp theo: {str(e)}", xbmc.LOGINFO)

            data = {"content_type": "movies", "items": ""}
            data.update({"items": items})
            return data

        except (ConnectionError, Timeout) as e:
            alert(f"Lỗi kết nối: {str(e)}")
            return None
        except RequestException as e:
            alert(f"Lỗi khi tải trang: {str(e)}")
            return None
        except Exception as e:
            alert(f"Lỗi không xác định: {str(e)}")
            return None

    data = listGenre_(url)


    if data:
        cache_utils.set_cache(cache_key, data)

    return data


def listMovie(url):
    # Create cache key based on URL
    cache_key = hashlib.md5(url.encode()).hexdigest() + '_movies_cache'

    # Check if we have valid cached data
    if cache_utils.check_cache(cache_key, 60):  # Cache valid for 60 minutes
        cache_data = cache_utils.get_cache(cache_key)
        if cache_data:
            return cache_data

    # If no valid cache, fetch and process data
    items = listMovie_(url)
    data = {"content_type": "movies", "items": ""}
    data.update({"items": items})

    # Save to cache
    cache_utils.set_cache(cache_key, data)

    return data

def listMovie_(url):
    success = False
    for _ in range(3):
        try:
            response = requests.get(url, verify=False, timeout=30)
            success = True
            break
        except Exception as e:
            alert('Không lấy được nội dung từ web')

    if not success:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article", class_="item movies")
    items = []

    for article in articles:
        try:
            article_id = article['id']
            article_id = article_id.replace("post-","")

            # Create movie-specific cache key
            movie_cache_key = f"movie_info_{article_id}"
            links_cache_key = f"movie_links_{article_id}"

            # Try to get movie info from cache first
            movie_info = None
            if cache_utils.check_cache(movie_cache_key, 120):  # Cache valid for 2 hours
                movie_info = cache_utils.get_cache(movie_cache_key)

            # If not in cache, fetch from API
            if not movie_info:
                movie_info = get_movie_info(article_id)
                if movie_info:
                    # Save to cache
                    cache_utils.set_cache(movie_cache_key, movie_info)

                    # Also cache the links separately for getlink function
                    if "link" in movie_info and movie_info["link"]:
                        cache_utils.set_cache(links_cache_key, movie_info["link"])

            if not movie_info:
                continue

            name = movie_info.get("title", "")
            name = name.replace("&&","-")
            img = movie_info.get("image", "")
            fanart = img
            year = movie_info.get("year", "")
            description = movie_info.get("description", "")
            href = article.find("a").get("href") if article.find("a") else ""
            genre = "|".join([c["name"] for c in movie_info.get("category", [])])

            item = {}
            item["label"] = name
            item["is_playable"] = False
            encoded_description = urllib.parse.quote_plus(description)
            item["path"] = addon_url + "browse&url=" + BASE_URL + "&article_id=" + article_id
            item["thumbnail"] = img
            item["icon"] = img
            item["label2"] = name
            item["info"] = {
                'title': name,
                'plot': description,
                'genre': genre,
                'year': int(year) if year and year.isdigit() else 0,
                'rating': '',
                'mediatype': 'movie'
            }
            item["art"] = {
                "fanart": fanart,
                "poster": img,
                "thumb": img,
                "icon": img
            }
            items.append(item)
        except Exception as e:
            alert(f'Không lấy được nội dung từ web: {str(e)}')

    # Thêm phân trang
    try:
        pagination = soup.find("div", class_="pagination")
        if pagination:
            current_page_span = pagination.find("span", class_="current")
            current_page = int(current_page_span.text.strip())
            next_page = current_page + 1

            if "page" in url:
                match = re.search(r"(.*)\/page",url)
                if match:
                    next_url = match.group(1)
            else:
                next_url = url

            next_url = "%s/page/%s" % (next_url,next_page)
            next_page_url = addon_url + "browse&url=vmf"+next_url
            nextpage = {
                "label": f'[COLOR yellow]Trang {next_page}[/COLOR]',
                "is_playable": False,
                "path": next_page_url,
                "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
                "icon": "https://i.imgur.com/yCGoDHr.png",
                "label2": "",
                "info": {
                    'plot': 'Trang tiếp theo',
                    'mediatype': 'video'
                },
                "art": {
                    'thumb': 'https://i.imgur.com/yCGoDHr.png',
                    'icon': 'https://i.imgur.com/yCGoDHr.png',
                    'poster': 'https://i.imgur.com/yCGoDHr.png'
                }
            }
            items.append(nextpage)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi kiểm tra trang tiếp theo: {str(e)}", xbmc.LOGINFO)

    return items

def listMovie_cf(url):
    """
    Lấy danh sách phim từ Cloudflare Worker API
    """
    # Xử lý URL
    if "trending" in url:
        api_url = f"{BASE_URL_CF}?type=trending"
        url_type = "trending"
    elif "recent" in url:
        api_url = f"{BASE_URL_CF}?type=recent"
        url_type = "recent"
    elif "genre" in url:
        api_url = url.replace(BASE_URL,BASE_URL_CF)
        url_type = "genre"

    # Thêm page nếu có
    page_match = re.search(r"page[=/](\d+)", url)
    if page_match:
        page = page_match.group(1)
        if url_type in ["trending", "recent"]:
            api_url = re.sub(r"page[=/]\d+", "", api_url)  # Xóa page cũ nếu có
            api_url += f"&page={page}"

    #xbmc.log(f"[VietmediaF] Fetching movies from CF Worker: {api_url}", xbmc.LOGINFO)

    # Tạo cache key từ URL
    cache_key = hashlib.md5(api_url.encode()).hexdigest()

    # Kiểm tra cache
    if cache_utils.check_cache(cache_key, 30):  # Cache 30 phút
        cache_data = cache_utils.get_cache(cache_key)
        if cache_data:
            xbmc.log(f"[VietmediaF] Lấy dữ liệu {api_url} từ cache", xbmc.LOGINFO)
            return cache_data

    try:
        # Gọi API
        response = session.get(api_url, verify=False, timeout=30)
        response.raise_for_status()
        data_movie = response.json()

        #xbmc.log(f"[VietmediaF] Lấy dữ liệu {api_url} từ web", xbmc.LOGINFO)

        items = []
        for movie in data_movie.get("movies", []):
            title = movie.get("title", "")
            title = title.replace("&&","-")
            year = movie.get("year", "")

            article_id = movie.get("article_id", "")
            description = movie.get("description", "")
            img = movie.get("image", "")
            genre = "|".join([c["name"] for c in movie.get("category", [])])
            links = movie.get("link", [])


            # Cache thông tin phim để dùng sau
            movie_cache_key = f"movie_info_{article_id}"
            cache_utils.set_cache(movie_cache_key, {
                "title": title,
                "description": description,
                "image": img,
                "links": links,
                "year": year,
                "genre": genre
            })

            item = {
                "label": f"{title} ({year})" if year else title,
                "is_playable": False,
                "path": addon_url + "browse&url=" + BASE_URL + "&article_id=" + article_id,
                "thumbnail": img,
                "icon": img,
                "label2": title,
                "info": {
                    "title": title,
                    "year": int(year) if year and year.isdigit() else 0,
                    "plot": description,
                    "mediatype": "movie",
                    "genre": genre
                },
                "art": {"fanart": img}
            }
            items.append(item)

        # Xử lý phân trang
        current_page = data_movie.get("page", 1)
        total_pages = data_movie.get("total_pages", 1)
        next_page = current_page + 1

        if next_page <= total_pages:
            # Tạo URL cho trang tiếp theo dựa vào loại URL
            if url_type == "genre":
                # URL dạng: /genre/phim-le/page/2
                if "/page/" in url:
                    next_url = re.sub(r"/page/\d+", f"/page/{next_page}", url)
                else:
                    next_url = url.rstrip("/") + f"/page/{next_page}"
            else:
                # URL dạng: ?type=trending&page=2
                if "page=" in url:
                    next_url = re.sub(r"page=\d+", f"page={next_page}", url)
                else:
                    next_url = url + f"&page={next_page}" if "?" in url else url + f"?page={next_page}"

            nextpage = {
                "label": f'[COLOR yellow]Trang {next_page}[/COLOR]',
                "is_playable": False,
                "path": addon_url + "browse&url=" + next_url,
                "thumbnail": nextpage_icon,
                "icon": nextpage_icon,
                "label2": "",
                "info": {
                    'plot': 'Trang tiếp theo',
                    'mediatype': 'video'
                },
                "art": {
                    'thumb': nextpage_icon,
                    'icon': nextpage_icon,
                    'poster': nextpage_icon
                }
            }
            items.append(nextpage)

        data = {"content_type": "movies", "items": items}
        cache_utils.set_cache(cache_key, data)
        return data

    except (ConnectionError, Timeout) as e:
        alert(f"Lỗi kết nối: {str(e)}")
        return None
    except RequestException as e:
        alert(f"Lỗi khi tải dữ liệu: {str(e)}")
        return None
    except Exception as e:
        alert(f"Lỗi không xác định: {str(e)}")
        return None

def receive(url):

    # Trích xuất URL từ tham số đầu vào nếu cần
    match = re.search(r"url=(.*)", url)
    if match:
        url = match.group(1)

    xbmc.log(f"[VietmediaF] TVHD receive URL: {url}", xbmc.LOGINFO)

    if "menu" in url:
        names = ['Tìm kiếm','Mới nhất','Xu hướng','Phim lẻ','Phim bộ','Phim lẻ thể loại','Phim Bộ theo quốc gia','Phim 18+','Phim H265','Phim TVB','Phim Thuyết Minh','Phim Lồng Tiếng']
        links = [addon_url+f"browse&url={BASE_URL}timkiem",
                addon_url+f"browse&url={BASE_URL}recent",
                addon_url+f"browse&url={BASE_URL}trending?get=movies",
                addon_url+f"browse&url=vmf{BASE_URL}genre/phim-le",
                addon_url+f"browse&url=vmf{BASE_URL}genre/series",
                addon_url+f"browse&url={BASE_URL}genre/theloai",
                addon_url+f"browse&url=vmf{BASE_URL}genre/quocgia",
                addon_url+f"browse&url=vmf{BASE_URL}genre/18",
                addon_url+f"browse&url=vmf{BASE_URL}genre/h265",
                addon_url+f"browse&url={BASE_URL}genre/tvb",
                addon_url+f"browse&url=vmf{BASE_URL}genre/thuyet-minh-tieng-viet",
                addon_url+f"browse&url=vmf{BASE_URL}genre/long-tieng-tieng-viet"]
        items = []

        for name, link in zip(names,links):
            if "phim-le" in link:
                fanart = f"{BASE_URL}wp-content/themes/dooplay/images/banner_phimle.jpg"
            elif "genre/18" in link:
                fanart = f"{BASE_URL}wp-content/themes/dooplay/images/phim18.jpg"
            elif "genre/series" in link:
                fanart = f"{BASE_URL}wp-content/themes/dooplay/images/banner_series.jpg"
            else:fanart = "https://i.imgur.com/dGv6Non.jpg"
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = link
            item["thumbnail"] = "https://i.imgur.com/5dFJGyW.png"
            item["icon"] = "https://i.imgur.com/5dFJGyW.png"
            item["label2"] = ""
            item["info"] = {'plot': 'Các phim trên thuvienhd'}
            item["art"] = {'fanart': fanart}
            items += [item]
        data = {"content_type": "files", "items": ""}
        data.update({"items": items})
        return data
    elif "trending" in url or "recent" in url or ("recent" in url and "vmf" in url):

        if "vmf" in url:
            url = url.replace("vmf","")
        match = re.search(r"url=(.*)",url)
        if match:
            url = match.group(1)
        try:data = listMovie_cf(url)
        except Exception as e:
            alert(f"Error processing div: {e}")
        return data
    elif "theloai" in url:
        names = ['Hành Động', 'Võ Thuật','Viễn Tưởng', 'Kinh Dị', 'Hàn Quốc', '3D', '4K', 'Ấn Độ', 'Hài', 'Cao Bồi', 'Chiến Tranh', 'Chính Kịch', 'Cổ Trang', 'Gia Đình', 'Giáng Sinh', 'Hình Sự', 'Phim Hoạt Hình', 'Hongkong', 'Huyền Bí', 'Lãng Mạn', 'Lịch Sử', 'Nhạc Kịch', 'Phiêu Lưu', 'Phim', 'Phim Tài Liệu', 'Rùng Rợn', 'Tâm Lý', 'Thần Thoại', 'Thể Thao', 'Thiếu Nhi', 'Tiểu Sử', 'Tình Cảm', 'Trinh Thám', 'Trung Quốc']
        links = ['vmfhttps://thuvienhd.top/genre/action',
            'vmfhttps://thuvienhd.top/genre/vo-thuat-phim-2',
            'vmfhttps://thuvienhd.top/genre/sci-fi', 'vmfhttps://thuvienhd.top/genre/horror', 'vmfhttps://thuvienhd.top/genre/korean', 'vmfhttps://thuvienhd.top/genre/3d', 'vmfhttps://thuvienhd.top/genre/4k', 'vmfhttps://thuvienhd.top/genre/india', 'vmfhttps://thuvienhd.top/genre/comedy', 'vmfhttps://thuvienhd.top/genre/western', 'vmfhttps://thuvienhd.top/genre/war', 'vmfhttps://thuvienhd.top/genre/chinh-kich', 'vmfhttps://thuvienhd.top/genre/co-trang-phim', 'vmfhttps://thuvienhd.top/genre/gia-dinh', 'vmfhttps://thuvienhd.top/genre/giang-sinh', 'vmfhttps://thuvienhd.top/genre/crime', 'vmfhttps://thuvienhd.top/genre/animation', 'vmfhttps://thuvienhd.top/genre/hongkong', 'vmfhttps://thuvienhd.top/genre/mystery', 'vmfhttps://thuvienhd.top/genre/romance', 'vmfhttps://thuvienhd.top/genre/history', 'vmfhttps://thuvienhd.top/genre/nhac-kich', 'vmfhttps://thuvienhd.top/genre/adventure', 'vmfhttps://thuvienhd.top/genre/phim', 'vmfhttps://thuvienhd.top/genre/documentary', 'vmfhttps://thuvienhd.top/genre/thriller', 'vmfhttps://thuvienhd.top/genre/drama', 'vmfhttps://thuvienhd.top/genre/fantasy', 'vmfhttps://thuvienhd.top/genre/the-thao', 'vmfhttps://thuvienhd.top/genre/family', 'vmfhttps://thuvienhd.top/genre/tieu-su', 'vmfhttps://thuvienhd.top/genre/tinh-cam', 'vmfhttps://thuvienhd.top/genre/trinh-tham', 'vmfhttps://thuvienhd.top/genre/trung-quoc-series']
        items = []
        for name, link in zip(names,links):
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = addon_url + "browse&url="+link
            item["thumbnail"] = "https://i.imgur.com/5dFJGyW.png"
            item["icon"] = "https://i.imgur.com/5dFJGyW.png"
            item["label2"] = ""
            item["info"] = {'plot': ''}
            item["art"] = {'fanart': "https://i.imgur.com/dGv6Non.jpg"}
            items += [item]
        data = {"content_type": "files", "items": ""}
        data.update({"items": items})
        return data
    elif "quocgia" in url:
        links =  [f'vmf{BASE_URL}genre/phim-bo-viet-nam',
        f'vmf{BASE_URL}genre/us-tv-series',
        f'vmf{BASE_URL}genre/korean-series',
        f'vmf{BASE_URL}genre/phim-bo-trung-quoc',
        f'vmf{BASE_URL}genre/hongkong-series',
        f'vmf{BASE_URL}genre/phi-bo-nigeria', f'vmf{BASE_URL}genre/phim-bo-a-rap', f'vmf{BASE_URL}genre/phim-bo-ai-cap', f'vmf{BASE_URL}genre/phim-bo-ai-nhi-lan-ireland', f'vmf{BASE_URL}genre/phim-bo-an-do', f'vmf{BASE_URL}genre/phim-bo-anh', f'vmf{BASE_URL}genre/phim-bo-ao', f'vmf{BASE_URL}genre/phim-bo-argentina', f'vmf{BASE_URL}genre/phim-bo-australia', f'vmf{BASE_URL}genre/phim-bo-ba-lan', f'vmf{BASE_URL}genre/phim-bo-bi', f'vmf{BASE_URL}genre/phim-bo-bo-dao-nha', f'vmf{BASE_URL}genre/phim-bo-brazil', f'vmf{BASE_URL}genre/phim-bo-canada', f'vmf{BASE_URL}genre/phim-bo-chile', f'vmf{BASE_URL}genre/phim-bo-colombia', f'vmf{BASE_URL}genre/phim-bo-dai-loan', f'vmf{BASE_URL}genre/phim-bo-dan-mach', f'vmf{BASE_URL}genre/phim-bo-duc', f'vmf{BASE_URL}genre/phim-bo-ha-lan',  f'vmf{BASE_URL}genre/phim-bo-iceland', f'vmf{BASE_URL}genre/phim-bo-ireland', f'vmf{BASE_URL}genre/phim-bo-israel', f'vmf{BASE_URL}genre/phim-bo-jordan', f'vmf{BASE_URL}genre/phim-bo-mexico',  f'vmf{BASE_URL}genre/phim-bo-na-uy', f'vmf{BASE_URL}genre/phim-bo-nam-phi', f'vmf{BASE_URL}genre/phim-bo-new-zealand', f'vmf{BASE_URL}genre/phim-bo-nga', f'vmf{BASE_URL}genre/phim-bo-nhat-ban', f'vmf{BASE_URL}genre/phim-bo-phan-lan', f'vmf{BASE_URL}genre/phim-bo-phap', f'vmf{BASE_URL}genre/phim-bo-philippines', f'vmf{BASE_URL}genre/phim-bo-romania', f'vmf{BASE_URL}genre/phim-bo-singapo', f'vmf{BASE_URL}genre/phim-bo-tay-ban-nha', f'vmf{BASE_URL}genre/phim-bo-thai-lan', f'vmf{BASE_URL}genre/phim-bo-tho-nhi-ky', f'vmf{BASE_URL}genre/phim-bo-thuy-dien',   f'vmf{BASE_URL}genre/phim-bo-y']
        names = ['Phim Bộ Việt Nam','Phim Bộ Mỹ','Phim Bộ Hàn','Phim Bộ Trung Quốc','Phim Bộ Hongkong','Phi Bộ Nigeria', 'Phim Bộ Ả Rập', 'Phim Bộ Ai Cập', 'Phim Bộ Ái Nhĩ Lan (Ireland', 'Phim Bộ Ấn Độ', 'Phim bộ Anh', 'Phim Bộ Áo', 'Phim Bộ Argentina', 'Phim Bộ Australia', 'Phim Bộ Ba Lan', 'Phim Bộ Bỉ', 'Phim Bộ Bồ Đào Nha', 'Phim Bộ Brazil', 'Phim Bộ Canada', 'Phim Bộ Chile', 'Phim Bộ Colombia', 'Phim Bộ Đài Loan', 'Phim Bộ Đan Mạch', 'Phim Bộ Đức', 'Phim Bộ Hà Lan','Phim Bộ Iceland', 'Phim Bộ Ireland', 'Phim Bộ Israel', 'Phim Bộ Jordan', 'Phim Bộ Mexico',  'Phim Bộ Na Uy', 'Phim Bộ Nam Phi', 'Phim Bộ New Zealand', 'Phim Bộ Nga', 'Phim Bộ Nhật Bản', 'Phim Bộ Phần Lan', 'Phim Bộ Pháp', 'Phim Bộ Philippines', 'Phim Bộ Romania', 'Phim Bộ Singapo', 'Phim Bộ Tây Ban Nha', 'Phim Bộ Thái Lan', 'Phim Bộ Thổ Nhĩ Kỳ', 'Phim Bộ Thụy Điển', 'Phim Bộ Ý']
        items = []
        for name, link in zip(names,links):
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = addon_url + "browse&url="+link
            item["thumbnail"] = "https://i.imgur.com/5dFJGyW.png"
            item["icon"] = "https://i.imgur.com/5dFJGyW.png"
            item["label2"] = ""
            item["info"] = {'plot': ''}
            item["art"] = {'fanart': "https://i.imgur.com/dGv6Non.jpg"}
            items += [item]
        data = {"content_type": "files", "items": ""}
        data.update({"items": items})
        return data
    elif "timkiem" in url:
        # Sử dụng chức năng lịch sử tìm kiếm mới
        data = show_search_history()
        if data:
            return data
        else:
            alert("Đã hủy tìm kiếm")
            return
    elif "?s=" in url:

        current_page = re.search(r"\/page\/(\d+)",url).group(1)
        query = re.search(r"s=(.*)",url).group(1)
        data = search(current_page,query)
        return data
    elif "genre" in url:
        if "vmf" in url:
            url = url.replace("vmf","")

        data = listMovie_cf(url)
        return data
    elif "article_id" in url:
        article_id = re.search(r"article_id=(\d+)",url).group(1)
        movie_cache_key = f"movie_info_{article_id}"
        movie_info = cache_utils.get_cache(movie_cache_key)
        if movie_info:
            description = movie_info["description"]
            description = description.replace("&&", "-")
            poster = movie_info["image"]
            if not movie_info["links"]:
                alert("Phim không có link")
                return
            items = []
            for link in movie_info["links"]:
                title = link["title"]
                path = link["link"]
                item = {}
                item["label"] = title

                if "fshare.vn" in path:
                    name, file_type, size_file = fshare.get_fshare_file_info(path)
                    if "/folder/" in path:
                        item["is_playable"] = False
                    else:
                        item["is_playable"] = True
                    item["info"] = {'plot': description,'size':size_file}
                    
                else:
                    item["info"] = {'plot': description}
                item["path"] = addon_url + "browse&url="+path
                item["thumbnail"] = poster
                item["icon"] = poster
                item["label2"] = ""
                item["art"] = {'fanart': poster}
                items += [item]
            data = {"content_type": "movies", "items": ""}
            data.update({"items": items})
            return data
    else:
        description = ""
        if "&desc=" in url:
            parts = url.split("&desc=")
            url = parts[0]
            description = urllib.parse.unquote_plus(parts[1])

        if "vmf" in url:
            url = url.replace("vmf","")

        match = re.search(r"url=(.*)",url)
        if match:
            url = match.group(1)


        data = getlink(url, description)
        return data
