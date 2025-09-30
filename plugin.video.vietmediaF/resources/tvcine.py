import time, random
from bs4 import BeautifulSoup
import hashlib
import re, json, os
import urllib.parse
import sys
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from resources import fshare, cache_utils
from resources.addon import alert, notify, TextBoxes, getadv, ADDON, ADDON_ID, addon_url, ADDON_PATH
from resources.lib.constants import CACHE_PATH, USER_AGENT
import xbmcgui, xbmc, xbmcvfs, xbmcplugin
from datetime import timedelta
from resources.history_utils import tvcine_history
from resources.utils import save_fshare_metadata, get_cached_metadata, clear_specific_cache
from resources.search import timfshare
from resources.thuviencine import parse_csv_data

# Lấy domain từ addon settings
default_domain = "thuviencine.com"
thuviencine_domain = ADDON.getSetting("thuviencine_domain") or default_domain
BASE_URL = f"https://{thuviencine_domain}/"

def create_session():
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })

    return session

session = create_session()


SHEET_MAPPING = {
    f"{BASE_URL}movies/": {"sheet_id": "1UbAo0JpJIUUkOTi8120yJ8nJkVh_pryhG3GBgCUZNZQ", "gid": "0"},
    f"{BASE_URL}tv-series/": {"sheet_id": "1UbAo0JpJIUUkOTi8120yJ8nJkVh_pryhG3GBgCUZNZQ", "gid": "2116997407"},
    f"{BASE_URL}top/": {"sheet_id": "1UbAo0JpJIUUkOTi8120yJ8nJkVh_pryhG3GBgCUZNZQ", "gid": "1770537487"}
}

def get_sheet_data_for_section(url):
    """Lấy dữ liệu từ Google Sheet dựa trên URL section"""

    base_url = url.split('page/')[0] if 'page/' in url else url
    base_url = base_url.rstrip('/')
    base_url = base_url + '/'

    xbmc.log(f"[VietmediaF] Checking sheet data for URL: {base_url}", xbmc.LOGINFO)


    if base_url not in SHEET_MAPPING:
        xbmc.log(f"[VietmediaF] No sheet mapping found for URL: {base_url}", xbmc.LOGINFO)
        return None


    sheet_info = SHEET_MAPPING[base_url]
    sheet_id = sheet_info["sheet_id"]
    gid = sheet_info["gid"]


    cache_key = hashlib.md5(f"{sheet_id}_{gid}".encode()).hexdigest() + "_csv_data"


    from resources.utils import clear_specific_cache
    clear_specific_cache(cache_key)
    xbmc.log(f"[VietmediaF] Cleared cache for {base_url}", xbmc.LOGINFO)


    if cache_utils.check_cache(cache_key):
        cache_content = cache_utils.get_cache(cache_key)
        if cache_content:
            xbmc.log(f"[VietmediaF] Using cached CSV data for {base_url}", xbmc.LOGINFO)
            return cache_content

    try:

        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

        xbmc.log(f"[VietmediaF] Fetching data from: {csv_url}", xbmc.LOGINFO)


        response = session.get(csv_url, timeout=30)
        response.raise_for_status()


        response.encoding = 'utf-8'


        csv_data = response.text
        if csv_data:
            xbmc.log(f"[VietmediaF] Received {len(csv_data)} bytes of CSV data", xbmc.LOGINFO)
            cache_utils.set_cache(cache_key, csv_data)


        return csv_data
    except Exception as e:

        return None

def process_sheet_data_for_section(url):
    """Xử lý dữ liệu từ Google Sheet và chuyển đổi thành dạng phù hợp"""

    csv_data = get_sheet_data_for_section(url)
    if not csv_data:

        return None


    csv_preview = csv_data[:500] if csv_data else "Empty"

    movies = parse_csv_data(csv_data)
    if not movies:
        xbmc.log(f"[VietmediaF] No movies parsed from CSV data for URL: {url}", xbmc.LOGWARNING)

        if csv_data and '\n' in csv_data:
            headers = csv_data.splitlines()[0]
            xbmc.log(f"[VietmediaF] CSV headers: {headers}", xbmc.LOGWARNING)
        return None

    xbmc.log(f"[VietmediaF] Successfully parsed {len(movies)} movies from CSV", xbmc.LOGINFO)


    items = []
    for movie in movies:
        try:

            xbmc.log(f"[VietmediaF] Movie keys: {list(movie.keys())}", xbmc.LOGINFO)


            name = str(movie.get('Movie Name', '') or movie.get('Name', ''))
            name_en = str(movie.get('Original Title', '') or movie.get('OriginalTitle', ''))
            link = str(movie.get('Movie Link', '') or movie.get('Link', ''))
            year = str(movie.get('Year', ''))
            genre = str(movie.get('Genre', '') or movie.get('Genres', ''))
            rating_str = str(movie.get('Rating', '0'))
            description = str(movie.get('Overview', '') or movie.get('Plot', ''))
            poster = str(movie.get('Poster URL', '') or movie.get('Poster', ''))
            backdrop = str(movie.get('Backdrop URL', '') or movie.get('Backdrop', '') or movie.get('Fanart', ''))
            runtime = str(movie.get('Runtime', ''))


            xbmc.log(f"[VietmediaF] Poster: {poster}", xbmc.LOGINFO)
            xbmc.log(f"[VietmediaF] Backdrop: {backdrop}", xbmc.LOGINFO)


            try:
                rating = float(rating_str) if rating_str and re.match(r'^\d+(\.\d+)?$', rating_str) else 0.0
            except (ValueError, TypeError):
                rating = 0.0


            duration = 0
            if runtime:
                runtime_match = re.search(r'(\d+)', runtime)
                if runtime_match:
                    try:

                        duration = int(runtime_match.group(1)) * 60
                    except (ValueError, TypeError):
                        duration = 0


            properties = {
                "IsPlayable": "false",
                "TotalTime": str(duration),
                "ResumeTime": "0"
            }


            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = addon_url + "browse&url=" + link
            item["thumbnail"] = poster
            item["icon"] = poster
            item["label2"] = name_en


            item["info"] = {
                'title': name,
                'originaltitle': name_en,
                'year': int(year) if year and year.isdigit() else 0,
                'genre': genre,
                'plot': description,
                'rating': rating,
                'duration': duration,
                'mediatype': 'movie'
            }


            item["art"] = {
                'thumb': poster,
                'icon': poster,
                'poster': poster,
                'fanart': backdrop
            }


            item["properties"] = properties

            items.append(item)
        except Exception as e:
            xbmc.log(f"[VietmediaF] Error processing movie from CSV: {str(e)}", xbmc.LOGERROR)
            continue


    next_page = "2"
    base_url = url.rstrip('/')
    next_page_url = f"{base_url}/page/{next_page}/"

    try:
        response = session.head(next_page_url, verify=False, timeout=10)
        if response.status_code == 200:
            next_page_url = addon_url + "browse&url=vmf" + next_page_url
            nextpage = {
                "label": f'[COLOR yellow]Trang {next_page}[/COLOR] ',
                "is_playable": False,
                "path": next_page_url,
                "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
                "icon": "https://i.imgur.com/yCGoDHr.png",
                "label2": "",
                "info": {'plot': 'Trang tiếp theo', 'mediatype': 'video'},
                "art": {
                    'thumb': 'https://i.imgur.com/yCGoDHr.png',
                    'icon': 'https://i.imgur.com/yCGoDHr.png',
                    'poster': 'https://i.imgur.com/yCGoDHr.png'
                }
            }
            items.append(nextpage)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Error when checking next page: {str(e)}", xbmc.LOGINFO)


    data = {"content_type": "movies", "items": items}


    item_adv = getadv()
    items_length = len(data["items"])
    random_position = random.randint(1, min(5, items_length + 1))
    data["items"].insert(random_position, item_adv)

    return data

def getlink(url, img, description, english_name):
    def getlink_tvcn(url, img, description):
        start = time.time()
        try:
            response = session.get(url, verify=False, timeout=10)
            response.raise_for_status()

            if time.time() - start > 8:
                notify("Trang web phản hồi lâu, vui lòng thử lại sau!")
                return None

            soup = BeautifulSoup(response.content, "html.parser")
            items = []
            links = soup.find_all('a', href=lambda href: href and 'fshare.vn' in href)
            total_links = len(links)

        except (ConnectionError, Timeout) as e:
            notify(f"Lỗi kết nối: {str(e)}")
            return None
        except RequestException as e:
            notify(f"Lỗi khi tải trang: {str(e)}")
            return None
        
        combined_items = []
        
        for link in links:
            link = link.get('href')
            name, size_file, _ = fshare.get_fshare_file_info(link)
            save_fshare_metadata(link, img, description)

            item={}
            if "folder" in link:
                playable = False
        
                try:
                    # Tạo cache key cho thư mục Fshare
                    folder_code = re.search(r"folder\/([a-zA-Z0-9]+)", link)
                    if folder_code:
                        folder_code = folder_code.group(1)
                        folder_cache_key = f"tvcn_folder_{folder_code}"
                        
                        # Kiểm tra cache cho thư mục này
                        if cache_utils.check_cache(folder_cache_key, 30):
                            cached_folder_data = cache_utils.get_cache(folder_cache_key)
                            if cached_folder_data:
                                combined_items.extend(cached_folder_data)
                                continue
                    
                    folder_data = fshare.fsharegetFolder(link)
                    if folder_data and "items" in folder_data and folder_data["items"]:
                        
                        for item in folder_data["items"]:
                            if "label" in item:
                                item["label"] = f'[COLOR yellow]{item["label"]}[/COLOR]'
                        
                        combined_items.extend(folder_data["items"])
                                                
                        try:
                            from resources.search import timfshare
                            data_timfshare = timfshare(name)
                            if data_timfshare and "items" in data_timfshare and data_timfshare["items"]:
                    
                                filtered_items = []
                                name_lower = name.lower()
                                for item in data_timfshare["items"]:
                                    if "label" in item and name_lower in item["label"].lower():
                                        filtered_items.append(item)
                                
                       
                                combined_items.extend(filtered_items)
                                
                                # Lưu kết hợp của folder_data và filtered_items vào cache
                                if folder_code:
                                    # Tạo bản sao của các mục đã thêm vào combined_items
                                    items_to_cache = []
                                    for item in folder_data["items"]:
                                        items_to_cache.append(item.copy())
                                    for item in filtered_items:
                                        items_to_cache.append(item.copy())
                                    
                                    # Lưu vào cache
                                    cache_utils.set_cache(folder_cache_key, items_to_cache, 30)
                                    xbmc.log(f"[VietmediaF] Đã lưu {len(items_to_cache)} mục vào cache cho thư mục {folder_code}", xbmc.LOGINFO)
                        except Exception as e:
                            xbmc.log(f"[VietmediaF] Lỗi khi xử lý timfshare cho thư mục: {str(e)}", xbmc.LOGERROR)
                                            
                        continue
                except Exception as e:
                    xbmc.log(f"[VietmediaF] Lỗi khi xử lý thư mục Fshare: {str(e)}", xbmc.LOGERROR)
            else:
                playable = True

            item["label"] = name
            item["is_playable"] = playable
            item["path"] = 'plugin://plugin.video.vietmediaF?action=browse&url=%s' % link
            item["thumbnail"] = img
            item["icon"] = img
            item["label2"] = name
            item["info"] = {'plot': description,'size':size_file}
            combined_items.append(item)

        data = {"content_type": "movies", "items": ""}
        data.update({"items": combined_items})
        return data

    cache_key = hashlib.md5(url.encode()).hexdigest() + "_links"

    if cache_utils.check_cache(cache_key):
        cache_content = cache_utils.get_cache(cache_key)
        if cache_content:
            xbmc.sleep(500)
            return cache_content

    data = getlink_tvcn(url, img, description)

    if data:
        try:
            data_timfshare = timfshare(english_name)

            if data_timfshare and "items" in data_timfshare:
                year = None
                year_match = re.search(r'\((\d{4})\)\s*$', english_name)
                if year_match:
                    year = year_match.group(1)
                    english_name = re.sub(r'\s*\(\d{4}\)\s*$', '', english_name).strip()

                search_terms = set(word.lower() for word in re.findall(r'\w+', english_name))

                filtered_items = []
                for item in data_timfshare["items"]:
                    item_name = item["label"]
                    item_terms = set(word.lower() for word in re.findall(r'\w+', item_name))
                    year_match = True if not year else str(year) in item_name

                    if search_terms.issubset(item_terms) and year_match:
                        item["thumbnail"] = img
                        item["icon"] = img
                        if "info" in item:
                            item["info"]["plot"] = description
                        else:
                            item["info"] = {"plot": description}
                        item["art"] = {
                            "fanart": img,
                            "icon": img,
                            "thumb": img,
                            "poster": img
                        }
                        filtered_items.append(item)

                data_timfshare["items"] = filtered_items
                if data and data_timfshare["items"]:
                    data["items"] += data_timfshare["items"]

            # Lưu cache cho kết quả cuối cùng sau khi thêm data_timfshare
            if data:
                cache_utils.set_cache(cache_key, data)
                xbmc.sleep(500)

        except Exception as e:
            xbmc.log(f"[VietmediaF] Lỗi khi xử lý data_timfshare: {str(e)}", xbmc.LOGERROR)
            # Vẫn lưu cache cho data gốc nếu có lỗi với data_timfshare
            if data:
                cache_utils.set_cache(cache_key, data)
                xbmc.sleep(500)

    return data

def listMovie(url):
    def getlist(url):

        is_main_section = False
        is_first_page = True


        clean_url = url.rstrip('/')
        if 'page/' in clean_url:
            is_first_page = False
        else:
            clean_url = clean_url + '/'


        for section_url in SHEET_MAPPING.keys():
            if clean_url == section_url:
                is_main_section = True
                break


        if is_main_section and is_first_page:
            xbmc.log(f"[VietmediaF] Using Google Sheet data for URL: {url}", xbmc.LOGINFO)
            sheet_data = process_sheet_data_for_section(url)
            if sheet_data:
                return sheet_data
            else:
                xbmc.log(f"[VietmediaF] Failed to get data from Google Sheet, falling back to website scraping", xbmc.LOGWARNING)

        try:
            xbmc.log(f"[VietmediaF] Using website scraping for URL: {url}", xbmc.LOGINFO)
            response = session.get(url, verify=False, timeout=30)
            response.raise_for_status()
        except ConnectionError:
            alert('Không kết nối được đến web')
            return None
        except Timeout:
            alert('Yêu cầu đã vượt quá thời gian chờ')
            return None
        except RequestException as e:
            alert(f'Có lỗi xảy ra: {str(e)}')
            return None

        soup = BeautifulSoup(response.content, "html.parser")
        divs = soup.find_all("div", {"id": lambda x: x and x.startswith("post-")})
        items = []
        total_divs = len(divs)
        xbmc.log(f"[VietmediaF] Found {total_divs} movie items on page", xbmc.LOGINFO)
        for div in divs:
            try:

                title_elem = div.find('h2', class_='movie-title')
                if not title_elem:
                    continue

                full_title = title_elem.text.strip()
                name = full_title
                name_en = ""


                if " – " in full_title:
                    parts = full_title.split(" – ")
                    name = parts[0].strip()
                    name_en = parts[1].strip()
                elif " - " in full_title:
                    parts = full_title.split(" - ")
                    name = parts[0].strip()
                    name_en = parts[1].strip()


                year_elem = div.find("span", class_="movie-date")
                year = year_elem.text.strip() if year_elem else ""


                genre_elem = div.find("span", class_="genre")
                genre = genre_elem.text.strip() if genre_elem else "N/A"
                duration = 0
                rating_elem = div.find("div", class_="imdb-rating")
                rating = 0.0
                if rating_elem:
                    rating_text = rating_elem.text.strip()

                    rating_match = re.search(r'([\d.]+)', rating_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group(1))
                            xbmc.log(f"[VietmediaF] Đã trích xuất đánh giá IMDB: {rating} từ chuỗi: {rating_text}", xbmc.LOGINFO)
                        except ValueError:
                            rating = 0.0


                quality_elem = div.find("span", class_=lambda value: value and value.startswith("item-quality"))
                quality = quality_elem.text.strip() if quality_elem else "No sub"
                desc_elem = div.find("p", class_="movie-description")
                description = desc_elem.text.strip() if desc_elem else ""
                runtime_elem = div.find("span", class_="runtime")
                runtime = runtime_elem.text.strip() if runtime_elem else ""

                if runtime:
                    runtime_match = re.search(r'(\d+)', runtime)
                    if runtime_match:
                        try:
                            duration = int(runtime_match.group(1)) * 60
                            xbmc.log(f"[VietmediaF] Đã chuyển đổi thời lượng: {runtime} -> {duration} giây", xbmc.LOGINFO)
                        except (ValueError, TypeError):
                            duration = 0

                img_elem = div.find("img", class_="lazy")
                poster = ""
                if img_elem:
                    poster = img_elem.get("data-src")

                    if "w220_and_h330_face" in poster:
                        poster = poster.replace("w220_and_h330_face", "w600_and_h900_bestv2")

                backdrop_elem = div.find("div", class_="movie-backdrop")
                backdrop = ""
                if backdrop_elem and backdrop_elem.get("data-backdrop"):
                    backdrop = backdrop_elem.get("data-backdrop")

                    if "w300" in backdrop:
                        backdrop = backdrop.replace("w300", "w1280")
                else:
                    backdrop = poster

                #xbmc.log(f"[VietmediaF] Poster: {poster}", xbmc.LOGINFO)
                #xbmc.log(f"[VietmediaF] Backdrop: {backdrop}", xbmc.LOGINFO)
                link_elem = div.find("a")
                link = link_elem["href"] if link_elem else ""
                properties = {
                    "IsPlayable": "false",
                    "TotalTime": str(duration),
                    "ResumeTime": "0"
                }

                item = {}
                item["label"] = f"{name} [COLOR yellow]{quality}[/COLOR]"
                item["is_playable"] = False
                item["path"] = addon_url + "browse&url=" + link
                item["thumbnail"] = poster
                item["icon"] = poster
                item["label2"] = name_en
                item["info"] = {
                    'title': name,
                    'originaltitle': name_en,
                    'year': int(year) if year and year.isdigit() else 0,
                    'genre': genre,
                    'plot': description,
                    'rating': rating,
                    'duration': duration,
                    'mediatype': 'movie'
                }
                item["art"] = {
                    'thumb': poster,
                    'icon': poster,
                    'poster': poster,
                    'fanart': backdrop
                }
                item["properties"] = properties
                items.append(item)
            except Exception as e:
                xbmc.log(f"[VietmediaF] Lỗi khi xử lý phim: {str(e)}", xbmc.LOGERROR)
                continue
        if "page" in url:
            next_page =  re.search(r"/(\d+)/$", url).group(1)
            next_page = int(next_page)+1
            base_url = re.search(r"(.*\/)page",url).group(1)
        else:
            next_page = "2"
            base_url = url
        next_page_url = base_url+"page/%s/" % next_page

        try:
            response = session.head(next_page_url, verify=False, timeout=10)
            if response.status_code == 200:
                next_page_url = addon_url + "browse&url=vmf"+next_page_url
                nextpage = {
                    "label": '[COLOR yellow]Trang %s[/COLOR] ' % next_page,
                    "is_playable": False,
                    "path": next_page_url,
                    "thumbnail": 'https://i.imgur.com/yCGoDHr.png',
                    "icon": "https://i.imgur.com/yCGoDHr.png",
                    "label2": "",
                    "info": {'plot': 'Trang tiếp theo', 'mediatype': 'video'},
                    "art": {
                        'thumb': 'https://i.imgur.com/yCGoDHr.png',
                        'icon': 'https://i.imgur.com/yCGoDHr.png',
                        'poster': 'https://i.imgur.com/yCGoDHr.png'
                    }
                }
                items.append(nextpage)
        except Exception as e:
            xbmc.log(f"[VietmediaF] Lỗi khi kiểm tra trang tiếp theo: {str(e)}", xbmc.LOGINFO)

        data = {"content_type": "movies", "items": items}
        if 'page/' not in url:
            item_adv = getadv()
            items_length = len(data["items"])
            random_position = random.randint(1, min(5, items_length + 1))
            data["items"].insert(random_position, item_adv)

        return data
    cache_key = hashlib.md5(url.encode()).hexdigest() + "_movie_list"
    if cache_utils.check_cache(cache_key):
        cache_content = cache_utils.get_cache(cache_key)
        if cache_content:
            xbmc.sleep(500)
            return cache_content
    data = getlist(url)
    if data:
        cache_utils.set_cache(cache_key, data)
        xbmc.sleep(500)

    return data

def receive(url):
    if "menu" in url:
        names = ["Tìm kiếm","Phim Lẻ","Phim Bộ","Xu hướng","Thể loại","Quốc gia","Chất lượng"]
        links = [f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}timkiem/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}movies/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}tv-series/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}top/",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}theloai",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}quocgia",
                f"plugin://plugin.video.vietmediaF?action=browse&url={BASE_URL}chatluong"]
        items = []

        for name, link in zip(names,links):
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = link
            item["thumbnail"] = "https://i.imgur.com/GXyTFfi.png"
            item["icon"] = "https://i.imgur.com/GXyTFfi.png"
            item["label2"] = ""
            item["info"] = {'plot': name}
            item["art"] = {'fanart': "https://i.imgur.com/LkeOoN3.jpg"}
            items += [item]
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "tv-series" in url or "/movies/" in url or "vmf" in url:
        if "vmf" in url:
            url = url.replace("vmf","")
        match = re.search(r"url=(.*)",url)
        if match:
            url = match.group(1)
        data = listMovie(url)
        return data
    elif "/top/" in url:

        from resources import thuviencine
        data = thuviencine.get_thuviencine_top()
        return data
    elif "theloai" in url:
        links = [f'vmf{BASE_URL}adventure/', f'vmf{BASE_URL}chuong-trinh-truyen-hinh/', f'vmf{BASE_URL}kids/', f'vmf{BASE_URL}phim-bi-an/', f'vmf{BASE_URL}phim-chien-tranh/', f'vmf{BASE_URL}phim-chinh-kich/', f'vmf{BASE_URL}phim-gay-can/', f'vmf{BASE_URL}phim-gia-dinh/', f'vmf{BASE_URL}phim-gia-tuong/', f'vmf{BASE_URL}phim-hai/', f'vmf{BASE_URL}phim-hanh-dong/', f'vmf{BASE_URL}phim-hinh-su/', f'vmf{BASE_URL}phim-hoat-hinh/', f'vmf{BASE_URL}phim-khoa-hoc-vien-tuong/', f'vmf{BASE_URL}phim-kinh-di/', f'vmf{BASE_URL}phim-lang-man/', f'vmf{BASE_URL}phim-lich-su/', f'vmf{BASE_URL}phim-mien-tay/', f'vmf{BASE_URL}phim-nhac/', f'vmf{BASE_URL}phim-phieu-luu/', f'vmf{BASE_URL}phim-tai-lieu/', f'vmf{BASE_URL}reality/', f'vmf{BASE_URL}science-fiction/', f'vmf{BASE_URL}soap/', f'vmf{BASE_URL}war-politics/']
        names = ['Adventure', 'Chương Trình Truyền Hình', 'Kids', 'Phim Bí Ẩn', 'Phim Chiến Tranh', 'Phim Chính Kịch', 'Phim Gây Cấn', 'Phim Gia Đình', 'Phim Giả Tượng', 'Phim Hài', 'Phim Hành Động', 'Phim Hình Sự', 'Phim Hoạt Hình', 'Phim Khoa Học Viễn Tưởng', 'Phim Kinh Dị', 'Phim Lãng Mạn', 'Phim Lịch Sử', 'Phim Miền Tây', 'Phim Nhạc', 'Phim Phiêu Lưu', 'Phim Tài Liệu', 'Reality', 'Science Fiction', 'Soap', 'War & Politics']
        items = []
        # Ánh xạ tên thể loại với tên file ảnh tương ứng
        genre_mapping = {
            'Adventure': '_adventure_.png',
            'Chương Trình Truyền Hình': 'reality_tv_.png',
            'Kids': 'kids_.png',
            'Phim Bí Ẩn': 'mystery_.png',
            'Phim Chiến Tranh': 'war__politics.png',
            'Phim Chính Kịch': 'drama_.png',
            'Phim Gây Cấn': 'thriller_.png',
            'Phim Gia Đình': 'family_.png',
            'Phim Giả Tượng': 'fantasy_.png',
            'Phim Hài': 'comedy.png',
            'Phim Hành Động': '_action.png',
            'Phim Hình Sự': 'crime_.png',
            'Phim Hoạt Hình': 'animation_.png',
            'Phim Khoa Học Viễn Tưởng': 'sci_fi_.png',
            'Phim Kinh Dị': 'horror_.png',
            'Phim Lãng Mạn': 'romance_.png',
            'Phim Lịch Sử': 'history_.png',
            'Phim Miền Tây': 'western_.png',
            'Phim Nhạc': 'musical_.png',
            'Phim Phiêu Lưu': '_adventure_.png',
            'Phim Tài Liệu': 'documentary_.png',
            'Reality': 'reality_tv_.png',
            'Science Fiction': 'sci_fi_.png',
            'Soap': 'soap_.png',
            'War & Politics': 'war__politics.png'
        }
        for name, link in zip(names,links):
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = addon_url + "browse&url="+link

            # Lấy tên file ảnh tương ứng với thể loại
            genre_icon = genre_mapping.get(name, 'action_poster.png')  # Mặc định là action_poster.png nếu không tìm thấy
            icon_path = os.path.join(ADDON_PATH, 'resources', 'images', 'genres', genre_icon)

            item["thumbnail"] = icon_path
            item["icon"] = icon_path
            item["label2"] = ""
            item["info"] = {'plot': name}
            item["art"] = {'fanart': "https://i.imgur.com/LkeOoN3.jpg"}
            items += [item]
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "quocgia" in url:
        country_urls = {
            'Việt Nam': f'vmf{BASE_URL}country/vietnam/',
            'Anh': f'vmf{BASE_URL}country/united-kingdom/',
            'Argentina': f'vmf{BASE_URL}country/argentina/',
            'Australia': f'vmf{BASE_URL}country/australia/',
            'Austria': f'vmf{BASE_URL}country/austria/',
            'Belgium': f'vmf{BASE_URL}country/belgium/',
            'Bosnia and Herzegovina': f'vmf{BASE_URL}country/bosnia-and-herzegovina/',
            'Brazil': f'vmf{BASE_URL}country/brazil/',
            'Cambodia': f'vmf{BASE_URL}country/cambodia/',
            'Canada': f'vmf{BASE_URL}country/canada/',
            'Chile': f'vmf{BASE_URL}country/chile/',
            'China': f'vmf{BASE_URL}country/china/',
            'Colombia': f'vmf{BASE_URL}country/colombia/',
            'Czech Republic': f'vmf{BASE_URL}country/czech-republic/',
            'Denmark': f'vmf{BASE_URL}country/denmark/',
            'Dominican Republic': f'vmf{BASE_URL}country/dominican-republic/',
            'Estonia': f'vmf{BASE_URL}country/estonia/',
            'Finland': f'vmf{BASE_URL}country/finland/',
            'France': f'vmf{BASE_URL}country/france/',
            'Germany': f'vmf{BASE_URL}country/germany/',
            'Greece': f'vmf{BASE_URL}country/greece/',
            'Hong Kong': f'vmf{BASE_URL}country/hong-kong/',
            'Hungary': f'vmf{BASE_URL}country/hungary/',
            'Iceland': f'vmf{BASE_URL}country/iceland/',
            'India': f'vmf{BASE_URL}country/india/',
            'Indonesia': f'vmf{BASE_URL}country/indonesia/',
            'Ireland': f'vmf{BASE_URL}country/ireland/',
            'Israel': f'vmf{BASE_URL}country/israel/',
            'Italy': f'vmf{BASE_URL}country/italy/',
            'Japan': f'vmf{BASE_URL}country/japan/',
            'Korea': f'vmf{BASE_URL}country/korea/',
            'Latvia': f'vmf{BASE_URL}country/latvia/',
            'Lithuania': f'vmf{BASE_URL}country/lithuania/',
            'Luxembourg': f'vmf{BASE_URL}country/luxembourg/',
            'Malaysia': f'vmf{BASE_URL}country/malaysia/',
            'Mexico': f'vmf{BASE_URL}country/mexico/',
            'Mỹ': f'vmf{BASE_URL}country/usa/',
            'N/A': f'vmf{BASE_URL}country/n-a/',
            'Netherlands': f'vmf{BASE_URL}country/netherlands/',
            'New Zealand': f'vmf{BASE_URL}country/new-zealand/',
            'Nigeria': f'vmf{BASE_URL}country/nigeria/',
            'Norway': f'vmf{BASE_URL}country/norway/',
            'Peru': f'vmf{BASE_URL}country/peru/',
            'Philippines': f'vmf{BASE_URL}country/philippines/',
            'Phim bộ Mỹ': f'vmf{BASE_URL}country/phim-bo-my/',
            'Poland': f'vmf{BASE_URL}country/poland/',
            'Portugal': f'vmf{BASE_URL}country/portugal/',
            'Romania': f'vmf{BASE_URL}country/romania/',
            'Russia': f'vmf{BASE_URL}country/russia/',
            'Singapore': f'vmf{BASE_URL}country/singapore/',
            'Slovakia': f'vmf{BASE_URL}country/slovakia/',
            'South Africa': f'vmf{BASE_URL}country/south-africa/',
            'South Korea': f'vmf{BASE_URL}country/south-korea/',
            'Spain': f'vmf{BASE_URL}country/spain/',
            'Sweden': f'vmf{BASE_URL}country/sweden/',
            'Switzerland': f'vmf{BASE_URL}country/switzerland/',
            'Taiwan': f'vmf{BASE_URL}country/taiwan/',
            'Thailand': f'vmf{BASE_URL}country/thailand/',
            'Tunisia': f'vmf{BASE_URL}country/tunisia/',
            'Turkey': f'vmf{BASE_URL}country/turkey/',
            'UK': f'vmf{BASE_URL}country/uk/',
            'Ukraine': f'vmf{BASE_URL}country/ukraine/',
            'Uruguay': f'vmf{BASE_URL}country/uruguay/',
            'Venezuela': f'vmf{BASE_URL}country/venezuela/'
        }

        items = []
        for country, link in country_urls.items():
            item = {
                "label": country,
                "is_playable": False,
                "path": addon_url + "browse&url=" + link,
                "thumbnail": "",
                "icon": "",
                "label2": "",
                "info": {'plot': ''}
            }
            items.append(item)

        data = {"content_type": "episodes", "items": items}
        return data

    elif "chatluong" in url:
        links=[f'vmf{BASE_URL}quality/vietsub/', f'vmf{BASE_URL}quality/tm-pd/', f'vmf{BASE_URL}quality/tm-lt-pd/', f'vmf{BASE_URL}quality/tm/', f'vmf{BASE_URL}quality/raw/', f'vmf{BASE_URL}quality/phim-viet/', f'vmf{BASE_URL}quality/new/', f'vmf{BASE_URL}quality/lt-pd/', f'vmf{BASE_URL}quality/lt/', f'vmf{BASE_URL}quality/hd/', f'vmf{BASE_URL}quality/engsub/', f'vmf{BASE_URL}quality/cam-vietsub/', f'vmf{BASE_URL}quality/cam/', f'vmf{BASE_URL}quality/bluray-vietsub/', f'vmf{BASE_URL}quality/bluray-tm-pd/', f'vmf{BASE_URL}quality/bluray/', f'vmf{BASE_URL}quality/4k-vietsub/', f'vmf{BASE_URL}quality/4k-tm/', f'vmf{BASE_URL}quality/4k-lt/', f'vmf{BASE_URL}quality/4k/']
        names= ['Vietsub', 'TM - PĐ', 'TM - LT - PĐ', 'TM', 'Raw', 'Phim Việt', 'NEW', 'LT - PĐ', 'LT', 'HD', 'Engsub', 'CAM Vietsub', 'CAM', 'Bluray Vietsub', 'Bluray TM - PĐ', 'Bluray', '4K Vietsub', '4K TM', '4K LT', '4K']
        items = []
        for name, link in zip(names,links):
            item = {}
            item["label"] = name
            item["is_playable"] = False
            item["path"] = addon_url + "browse&url="+link
            item["thumbnail"] = ""
            item["icon"] = ""
            item["label2"] = ""
            item["info"] = {'plot': ''}
            items += [item]
        data = {"content_type": "episodes", "items": ""}
        data.update({"items": items})
        return data
    elif "/timkiem/" in url:

        def load_history():
            return tvcine_history.get_history()

        def save_history(query):
            tvcine_history.save_history(query)

        def clear_history():
            tvcine_history.delete_history()
            notify("Đã xóa lịch sử tìm kiếm")

        history = load_history()

        dialog = xbmcgui.Dialog()
        if history:
            options = ["[COLOR yellow]Nhập từ khóa mới[/COLOR]", "[COLOR yellow]Xóa lịch sử[/COLOR]"] + history
            choice = dialog.select("Chọn hoặc nhập từ khóa tìm kiếm:", options)

            if choice == -1:
                notify("Bạn đã hủy tìm kiếm")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                return None

            if choice == 0:
                keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    query = keyboard.getText()
                    query = urllib.parse.unquote(query)
                    save_history(query)
                    url = f"{BASE_URL}?s={query}"
                    data = listMovie(url)
                    return data
                else:
                    notify("Hủy tìm kiếm")
                    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                    return None
            elif choice == 1:
                confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa toàn bộ lịch sử tìm kiếm không?")
                if confirm:
                    clear_history()
                return None
            elif choice > 1:
                query = history[choice - 2]
                url = f"{BASE_URL}?s={query}"
                data = listMovie(url)
                return data
        else:

            keyboard = xbmc.Keyboard("", "Nhập tên phim tiếng Anh")
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                query = keyboard.getText()
                query = urllib.parse.unquote(query)
                save_history(query)
                url = f"{BASE_URL}?s={query}"
                data = listMovie(url)
                return data
            else:
                notify("Hủy tìm kiếm")
                xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False)
                return

    else:
        cache_key = hashlib.md5(url.encode()).hexdigest() + "_detail"
        if cache_utils.check_cache(cache_key):
            cache_content = cache_utils.get_cache(cache_key)
            if cache_content:
                return cache_content
        try:

            response = session.get(url, verify=False, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            movie_image = soup.find("div", class_="movie-image")
            movie_description = soup.find("p", class_="movie-description")
        except (ConnectionError, Timeout) as e:
            alert(f'Lỗi kết nối: {str(e)}')
            return None
        except RequestException as e:
            alert(f'Lỗi khi tải trang: {str(e)}')
            return None

        movie_title = soup.find("h1", {"itemprop": "name", "class": "entry-title"})
        english_name = None
        if movie_title:
            full_name = movie_title.text.strip()

            if "–" in full_name or "-" in full_name:
                full_name = full_name.replace("–", "-")
                full_name = re.sub(r'\s*-\s*', ' - ', full_name)
                name_parts = full_name.split(" - ")
                if len(name_parts) > 1:
                    english_name = name_parts[1].strip()

                    # Làm sạch tên tiếng Anh
                    english_name = re.sub(r'[:"\'\[\](){},!?@#$%^&*]', '', english_name)
                    english_name = re.sub(r'\s+', ' ', english_name).strip()

        if movie_description:
            description_span = movie_description.find("span", itemprop="description")
            if description_span:
                description = description_span.text.strip()
                description = re.sub(r'^Nội dung phim.*?fshare:\s*', '', description, flags=re.IGNORECASE)
                description = re.sub(r';\s*Trên đây là nội dung phim.*?$', '', description, flags=re.IGNORECASE)
                description = description.strip()
            else:
                description = "Không tìm thấy mô tả phim."
        else:
            description = "Không tìm thấy phần tử chứa mô tả phim."

        if movie_image:
            image = movie_image.find("img")["src"]
        else:
            image=""
        download_button = soup.find("li", id="download-button")
        if download_button:
            link = download_button.find("a")["href"]
            data = getlink(link, image, description, english_name)
            if data:
               cache_utils.set_cache(cache_key, data)
            return data
        else:
            alert("Không tìm thấy link. Thử lại sau")
            exit()
        return None









