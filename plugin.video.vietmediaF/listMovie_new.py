def listMovie(url):

    def listMovie_(url):
        success = False
        for _ in range(3):
            try:
                response = session.get(url, verify=False, timeout=30)
                success = True
                break
            except Exception as e:
                alert('Không lấy được nội dung từ web')
                return None
        
        if not success:
            return None
            
        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article", {"id": lambda x: x and x.startswith("post-")})
        items = []
        
        def get_movie_info_from_api(article_id):
            try:
                api_url = f"https://thuvienhd.top/?feed=fsharejson&id={article_id}"
                api_response = session.get(api_url, verify=False, timeout=30)
                if api_response.status_code != 200:
                    return None
                    
                movie_data = json.loads(api_response.content)
                return movie_data
            except Exception as e:
                xbmc.log(f"[VietmediaF] Lỗi khi lấy thông tin API: {str(e)}", xbmc.LOGINFO)
                return None
        
        for article in articles:
            try:
                # Lấy article_id từ thẻ article
                article_id = article.get('id', '')
                if article_id and article_id.startswith('post-'):
                    article_id = article_id.replace('post-', '')
                else:
                    continue
                    
                # Lấy thông tin phim từ API
                movie_data = get_movie_info_from_api(article_id)
                if not movie_data:
                    continue
                    
                # Xử lý dữ liệu từ API
                title = movie_data.get('title', '')
                description = movie_data.get('description', '')
                year = movie_data.get('year', '')
                poster = movie_data.get('image', '') or movie_data.get('img', '')
                categories = movie_data.get('category', [])
                links = movie_data.get('link', [])
                
                # Tạo chuỗi thể loại
                genre = '/'.join([cat.get('name', '') for cat in categories]) if categories else 'N/A'
                
                # Tạo tên hiển thị
                display_name = title
                if year:
                    display_name = f"{title} ({year})"
                
                # Tạo item
                item = {}
                item["label"] = display_name
                item["is_playable"] = False
                
                # Tạo URL cho trang chi tiết phim
                movie_url = f"https://thuvienhd.top/?p={article_id}"
                item["path"] = addon_url + "browse&url=" + movie_url
                
                item["thumbnail"] = poster
                item["icon"] = poster
                item["label2"] = display_name
                
                # Thông tin phim
                item["info"] = {
                    'title': display_name,
                    'plot': description,
                    'genre': genre,
                    'year': int(year) if year and year.isdigit() else 0,
                    'mediatype': 'movie'
                }
                
                # Artwork
                item["art"] = {
                    "fanart": poster,
                    "poster": poster,
                    "thumb": poster,
                    "icon": poster
                }
                
                items.append(item)
            except Exception as e:
                xbmc.log(f"[VietmediaF] Lỗi xử lý phim: {str(e)}", xbmc.LOGINFO)
                continue
        
        # Xử lý phân trang
        try:
            pagination = soup.find("div", class_="pagination")
            if pagination:
                current_page_span = pagination.find("span", class_="current")
                current_page = int(current_page_span.text.strip())
                next_page = current_page + 1

                if "trending" in url:
                    next_url = "https://thuvienhd.top/trending/page/%s?get=movies" % next_page
                else:
                    if "page" in url:
                        match = re.search(r"(.*)/page",url)
                        if match:
                            next_url = match.group(1)
                    else:
                        next_url = url

                    next_url = "%s/page/%s" % (next_url,next_page)
                next_page_url = addon_url + "browse&url=vmf"+next_url
                nextpage = {
                    "label": '[COLOR yellow]Trang %s [/COLOR]' % str(next_page), 
                    "is_playable": False, 
                    "path": next_page_url, 
                    "thumbnail": 'https://i.imgur.com/yCGoDHr.png', 
                    "icon": "https://i.imgur.com/yCGoDHr.png", 
                    "label2": "", 
                    "info": {'plot': 'Trang tiếp'}
                }
                items.append(nextpage)
        except Exception as e:
            xbmc.log(f"[VietmediaF] Lỗi xử lý phân trang: {str(e)}", xbmc.LOGINFO)
        
        data = {"content_type": "movies", "items": items}
        return data

    cache_filename = hashlib.md5(url.encode()).hexdigest() + '_cache.json'
    cache_path = os.path.join(CACHE_PATH, cache_filename)
    if cache_utils.check_cache(cache_path):
        with open(cache_path, 'r') as cache_file:
            cache_content = json.load(cache_file)
        return cache_content
    else:
        data = listMovie_(url)
        if data:
            with open(cache_path, "w") as f:
                json.dump(data, f)
        return data
