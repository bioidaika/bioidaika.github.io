# 🎬 TMDB Movie Click Flow - Luồng xử lý khi click phim

## 🎯 **TỔNG QUAN**

Khi người dùng click vào 1 phim từ danh sách TMDB search, addon sẽ thực hiện một chuỗi các bước để hiển thị thông tin chi tiết và download links.

## 🔄 **LUỒNG XỬ LÝ CHI TIẾT**

### **1. 🖱️ User Click Event**
```
User clicks on movie → Kodi generates URL with action
```

**URL được tạo:**
```
plugin://plugin.video.vietmediaF?action=tmdb_movie_detail&tmdb_id=12345&media_type=movie
```

### **2. 🎯 Action Detection (default.py)**
```python
if "tmdb_movie_detail" in url:
    # Lấy tham số từ URL
    tmdb_id = args.get('tmdb_id', '')
    media_type = args.get('media_type', 'movie')
```

**Xử lý:**
- Parse URL parameters
- Extract `tmdb_id` và `media_type`
- Validate parameters

### **3. 📡 TMDB API Call**
```python
# Lấy thông tin chi tiết từ TMDB
movie_data = tmdb_search.get_movie_details(int(tmdb_id), media_type)
```

**API Call:**
- **Endpoint**: `https://api.themoviedb.org/3/movie/{tmdb_id}` hoặc `/tv/{tmdb_id}`
- **Parameters**: API key, language, timeout
- **Response**: Chi tiết phim/TV (title, plot, year, genre, etc.)

### **4. 🔗 Backend API Call**
```python
# Lấy thông tin download từ backend
download_info = tmdb_search.get_backend_download_info(int(tmdb_id), media_type)
```

**API Call:**
- **Endpoint**: `https://bioidaika.click/api/{media_type}/{tmdb_id}`
- **Method**: GET
- **Response**: Download sources với links

### **5. 🎨 Display Movie Detail**
```python
# Hiển thị thông tin chi tiết
tmdb_search.display_movie_detail(movie_data, media_type, int(tmdb_id), download_info)
```

## 🎨 **DISPLAY MOVIE DETAIL FUNCTION**

### **1. 📋 Setup Content Type**
```python
# Thiết lập content type cho Kodi
content_type = "movies" if media_type == "movie" else "tvshows"
xbmcplugin.setContent(int(sys.argv[1]), content_type)
```

### **2. 🔄 Add Sort Methods**
```python
# Thêm các phương thức sắp xếp
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
```

### **3. 🎬 Create Movie Item**
```python
# Tạo item chính từ dữ liệu TMDB
movie_item = create_movie_item(movie_data, media_type)
```

**Thông tin hiển thị:**
- **Title**: Tên phim/TV
- **Plot**: Mô tả chi tiết
- **Year**: Năm sản xuất
- **Rating**: Đánh giá TMDB
- **Genre**: Thể loại
- **Artwork**: Poster, fanart, thumbnail

### **4. 🔗 Add Download Links**
```python
# Thêm thông tin download nếu có
if download_info and download_info.get("sources"):
    sources = download_info["sources"]
    # Thêm thông tin download vào plot
    download_text = "\n\n[COLOR yellow]DOWNLOAD LINKS:[/COLOR]\n"
    for i, source in enumerate(sources, 1):
        uploader = source.get("uploader", "Unknown")
        size = source.get("size", "N/A")
        download_url = source.get("download_url", "")
        vmf_code = source.get("vmf_code", "")
        
        if download_url and download_url != "None":
            download_text += f"[COLOR lightblue]{i}. {uploader}[/COLOR] - [COLOR orange]{size}[/COLOR]\n"
            if vmf_code:
                download_text += f"   VMF Code: [COLOR yellow]{vmf_code}[/COLOR]\n"
            download_text += f"   Link: [COLOR lightgreen]{download_url}[/COLOR]\n\n"
```

### **5. 📥 Create Download Items**
```python
# Tạo các item download riêng biệt
for i, source in enumerate(sources, 1):
    if source.get("download_url") and source.get("download_url") != "None":
        download_item = {
            "label": f"[COLOR yellow]Download {i}:[/COLOR] {source.get('uploader', 'Unknown')} - {source.get('size', 'N/A')}",
            "is_playable": True,
            "path": source.get("download_url", ""),
            "thumbnail": movie_item.get("thumbnail", ""),
            "fanart": movie_item.get("fanart", ""),
            "label2": f"VMF Code: {source.get('vmf_code', 'N/A')}",
            "info": {
                "title": f"Download {i} - {source.get('uploader', 'Unknown')}",
                "plot": f"Uploader: {source.get('uploader', 'Unknown')}\nSize: {source.get('size', 'N/A')}\nVMF Code: {source.get('vmf_code', 'N/A')}\nSheet: {source.get('sheet_name', 'N/A')}",
                "mediatype": "movie" if media_type == "movie" else "tvshow"
            },
            "art": movie_item.get("art", {}),
            "properties": {
                "tmdb_id": str(tmdb_id),
                "media_type": media_type,
                "uploader": source.get("uploader", ""),
                "size": source.get("size", ""),
                "vmf_code": source.get("vmf_code", ""),
                "sheet_name": source.get("sheet_name", "")
            }
        }
        items.append(download_item)
```

## 🎯 **KẾT QUẢ HIỂN THỊ**

### **1. 📋 Movie Information:**
- **Title**: Tên phim/TV
- **Plot**: Mô tả + Download links
- **Year**: Năm sản xuất
- **Rating**: Đánh giá TMDB
- **Genre**: Thể loại
- **Artwork**: Poster, fanart, thumbnail

### **2. 📥 Download Items:**
- **Download 1**: Uploader - Size
- **Download 2**: Uploader - Size
- **Download 3**: Uploader - Size
- **...**: Các download khác

### **3. 🎨 Visual Layout:**
```
┌─────────────────────────────────────┐
│ 🎬 Movie Title (Year)               │
│ ⭐ Rating | 🎭 Genre                │
│ 📝 Plot description...              │
│                                     │
│ 📥 DOWNLOAD LINKS:                  │
│ 1. Uploader1 - Size1                │
│    VMF Code: ABC123                 │
│    Link: https://...                │
│                                     │
│ 2. Uploader2 - Size2                │
│    VMF Code: DEF456                 │
│    Link: https://...                │
└─────────────────────────────────────┘
```

## 🔧 **TECHNICAL DETAILS**

### **1. 📡 API Calls:**
- **TMDB API**: Lấy metadata phim/TV
- **Backend API**: Lấy download sources
- **Error Handling**: Try-catch cho mỗi API call

### **2. 🎨 Kodi Integration:**
- **Content Type**: movies/tvshows
- **Sort Methods**: Unsorted, Label, Date, Genre
- **List Items**: Với artwork và properties
- **Playable Items**: Download links có thể play

### **3. 🎯 User Experience:**
- **Loading**: Notify user về progress
- **Error Handling**: Alert nếu có lỗi
- **Visual**: Color coding cho download links
- **Navigation**: Dễ dàng quay lại danh sách

## ⚙️ **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ Success Case:**
- TMDB API trả về data
- Backend API trả về download sources
- Hiển thị đầy đủ thông tin + download links

### **2. ⚠️ Partial Success:**
- TMDB API trả về data
- Backend API lỗi hoặc không có sources
- Hiển thị thông tin phim nhưng không có download links

### **3. ❌ Error Case:**
- TMDB API lỗi hoặc không tìm thấy
- Hiển thị alert và quay lại danh sách

## 🎯 **KẾT QUẢ**

Khi user click vào phim từ danh sách TMDB search:

1. **📡 Gọi TMDB API** → Lấy metadata phim/TV
2. **🔗 Gọi Backend API** → Lấy download sources
3. **🎨 Hiển thị thông tin** → Movie info + Download links
4. **📥 Tạo download items** → Các link có thể click để download
5. **🎯 User có thể** → Xem thông tin chi tiết và download phim

**Addon cung cấp trải nghiệm hoàn chỉnh từ tìm kiếm đến download!** 🎬✨
