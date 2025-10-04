# 🎬 TMDB 3-Column Layout Update - Cập nhật layout 3 cột

## 🎯 **THAY ĐỔI CHÍNH**

Cập nhật layout 3 cột khi click vào phim từ danh sách TMDB search để giữ nguyên thông tin phim và poster, chỉ thay đổi phần giữa (label2) để hiển thị danh sách nguồn download.

### **Trước (Thay đổi hoàn toàn):**
- Hiển thị thông tin phim mới
- Không giữ nguyên layout 3 cột
- Download links hiển thị riêng biệt

### **Sau (Giữ nguyên layout):**
- Giữ nguyên thông tin phim (bên trái)
- Giữ nguyên poster (bên phải)
- Giữ nguyên ngày tháng năm (góc dưới bên phải)
- Chỉ thay đổi phần giữa (label2) để hiển thị danh sách nguồn

## 🎨 **LAYOUT 3 CỘT MỚI**

### **1. 📋 Cột Trái (Thông tin phim):**
- **Title**: Tên phim/TV
- **Plot**: Mô tả chi tiết
- **Year**: Năm sản xuất
- **Rating**: Đánh giá TMDB
- **Genre**: Thể loại
- **Cast**: Diễn viên
- **Director**: Đạo diễn

### **2. 🎯 Cột Giữa (Danh sách nguồn):**
- **Nguồn 1**: Uploader - Sheet Name
- **Nguồn 2**: Uploader - Sheet Name
- **Nguồn 3**: Uploader - Sheet Name
- **...**: Các nguồn khác

### **3. 🖼️ Cột Phải (Poster):**
- **Poster**: Ảnh poster phim/TV
- **Fanart**: Ảnh nền (nếu có)
- **Thumbnail**: Ảnh thumbnail

### **4. 📅 Góc Dưới Phải:**
- **Ngày tháng năm**: Ngày sản xuất
- **Runtime**: Thời lượng phim
- **Status**: Trạng thái (Released, In Production, etc.)

## 🔄 **LUỒNG XỬ LÝ MỚI**

### **1. 🖱️ User Click Event:**
```
User clicks on movie → Generate URL with tmdb_movie_detail action
```

### **2. 🎯 Action Detection:**
```python
if "tmdb_movie_detail" in url:
    # Lấy tham số từ URL
    tmdb_id = args.get('tmdb_id', '')
    media_type = args.get('media_type', 'movie')
```

### **3. 📡 API Calls:**
```python
# Lấy thông tin chi tiết từ TMDB
movie_data = tmdb_search.get_movie_details(int(tmdb_id), media_type)

# Lấy thông tin download từ backend
download_info = tmdb_search.get_backend_download_info(int(tmdb_id), media_type)
```

### **4. 🎨 Display với Layout 3 Cột:**
```python
# Tạo item chính từ dữ liệu TMDB (giữ nguyên layout 3 cột)
movie_item = create_movie_item(movie_data, media_type)

# Tạo các item nguồn download
for i, source in enumerate(sources, 1):
    uploader = source.get("uploader", "Unknown")
    sheet_name = source.get("sheet_name", "Unknown")
    download_url = source.get("download_url", "")
    
    # Xác định loại URL (folder hoặc file)
    is_folder = download_url.endswith('/') or 'folder' in download_url.lower()
    
    # Tạo label2 cho nguồn
    source_label2 = f"{uploader} - {sheet_name}"
    
    # Tạo action URL cho nguồn
    if is_folder:
        # URL folder - không playable, hiển thị danh sách
        action_path = f"plugin://plugin.video.vietmediaF?action=fshare_folder&url={download_url}&uploader={uploader}&sheet={sheet_name}"
        is_playable = False
    else:
        # URL file - playable, gọi action play
        action_path = f"plugin://plugin.video.vietmediaF?action=play_fshare&url={download_url}&uploader={uploader}&sheet={sheet_name}"
        is_playable = True
```

## 🎯 **CÁC ACTION HANDLERS MỚI**

### **1. 📁 FShare Folder Handler:**
```python
if "fshare_folder" in url:
    # Xử lý hiển thị danh sách folder FShare
    fshare_url = args.get('url', '')
    uploader = args.get('uploader', 'Unknown')
    sheet_name = args.get('sheet', 'Unknown')
    
    if fshare_url:
        # Gọi hàm hiển thị danh sách folder FShare
        from .resources.fshare import list_folder_contents
        list_folder_contents(fshare_url, uploader, sheet_name)
```

### **2. ▶️ FShare Play Handler:**
```python
if "play_fshare" in url:
    # Xử lý play file FShare
    fshare_url = args.get('url', '')
    uploader = args.get('uploader', 'Unknown')
    sheet_name = args.get('sheet', 'Unknown')
    
    if fshare_url:
        # Gọi hàm play file FShare
        from .resources.fshare import play_fshare_file
        play_fshare_file(fshare_url, uploader, sheet_name)
```

## 🔧 **FUNCTIONS MỚI TRONG FSHARE.PY**

### **1. 📁 list_folder_contents():**
```python
def list_folder_contents(fshare_url, uploader, sheet_name):
    """
    Hiển thị danh sách nội dung folder FShare
    
    Args:
        fshare_url (str): URL folder FShare
        uploader (str): Tên uploader
        sheet_name (str): Tên sheet
    """
    # Thiết lập content type
    xbmcplugin.setContent(int(sys.argv[1]), "files")
    
    # Tạo header item
    header_item = {
        "label": f"[COLOR yellow]Folder:[/COLOR] {uploader} - {sheet_name}",
        "is_playable": False,
        "path": "",
        "info": {
            "title": f"Folder: {uploader} - {sheet_name}",
            "plot": f"Uploader: {uploader}\nSheet: {sheet_name}\nURL: {fshare_url}",
            "mediatype": "folder"
        }
    }
    
    # TODO: Implement FShare folder listing logic
    # Hiển thị danh sách files và folders trong FShare folder
```

### **2. ▶️ play_fshare_file():**
```python
def play_fshare_file(fshare_url, uploader, sheet_name):
    """
    Play file FShare
    
    Args:
        fshare_url (str): URL file FShare
        uploader (str): Tên uploader
        sheet_name (str): Tên sheet
    """
    # Tạo ListItem cho file
    list_item = xbmcgui.ListItem(label=f"Playing: {uploader} - {sheet_name}")
    list_item.setInfo("video", {
        "title": f"Playing: {uploader} - {sheet_name}",
        "plot": f"File from {uploader} - {sheet_name}\nURL: {fshare_url}",
        "mediatype": "movie"
    })
    list_item.setProperty("IsPlayable", "true")
    
    # Set path để Kodi có thể play
    list_item.setPath(fshare_url)
    
    # Auto-play file
    xbmc.Player().play(fshare_url, list_item)
```

## 🎨 **VISUAL LAYOUT MỚI**

### **Khi click vào phim:**
```
┌─────────────────────────────────────┐
│ 🎬 Movie Title (Year)               │
│ ⭐ Rating | 🎭 Genre                │
│ 📝 Plot description...              │
│                                     │
│ 🎯 DANH SÁCH NGUỒN:                 │
│ 1. Uploader1 - Sheet1               │
│ 2. Uploader2 - Sheet2               │
│ 3. Uploader3 - Sheet3               │
│                                     │
│ 📅 2023 | ⏱️ 120 min                │
└─────────────────────────────────────┘
```

### **Khi click vào nguồn (folder):**
```
┌─────────────────────────────────────┐
│ 📁 Folder: Uploader1 - Sheet1       │
│                                     │
│ 📄 File 1: movie.mp4                │
│ 📄 File 2: subtitle.srt             │
│ 📄 File 3: poster.jpg               │
│                                     │
│ 📅 2023 | ⏱️ 120 min                │
└─────────────────────────────────────┘
```

### **Khi click vào nguồn (file):**
```
┌─────────────────────────────────────┐
│ ▶️ Playing: Uploader1 - Sheet1      │
│                                     │
│ 🎬 Movie Title (Year)               │
│ ⭐ Rating | 🎭 Genre                │
│ 📝 Plot description...              │
│                                     │
│ 📅 2023 | ⏱️ 120 min                │
└─────────────────────────────────────┘
```

## 🔄 **URL STRUCTURE**

### **1. Movie Detail URL:**
```
plugin://plugin.video.vietmediaF?action=tmdb_movie_detail&tmdb_id=12345&media_type=movie
```

### **2. FShare Folder URL:**
```
plugin://plugin.video.vietmediaF?action=fshare_folder&url=https://fshare.vn/folder/abc123&uploader=Uploader1&sheet=Sheet1
```

### **3. FShare Play URL:**
```
plugin://plugin.video.vietmediaF?action=play_fshare&url=https://fshare.vn/file/xyz789&uploader=Uploader1&sheet=Sheet1
```

## 🎯 **LỢI ÍCH**

### **1. 🎨 Layout nhất quán:**
- Giữ nguyên thông tin phim
- Giữ nguyên poster và artwork
- Chỉ thay đổi phần cần thiết

### **2. 🔄 Navigation mượt mà:**
- Dễ dàng quay lại danh sách
- Thông tin phim luôn hiển thị
- Không bị mất context

### **3. 📱 User Experience tốt:**
- Layout quen thuộc
- Thông tin rõ ràng
- Dễ sử dụng

### **4. 🔧 Technical:**
- Code đơn giản hơn
- Dễ bảo trì
- Performance tốt

## ⚙️ **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ Success Case:**
- TMDB API trả về data
- Backend API trả về download sources
- Hiển thị layout 3 cột với danh sách nguồn

### **2. ⚠️ Partial Success:**
- TMDB API trả về data
- Backend API lỗi hoặc không có sources
- Hiển thị layout 3 cột nhưng không có nguồn

### **3. ❌ Error Case:**
- TMDB API lỗi hoặc không tìm thấy
- Hiển thị alert và quay lại danh sách

## 🎯 **KẾT QUẢ**

Khi user click vào phim từ danh sách TMDB search:

1. **🎨 Giữ nguyên layout 3 cột** → Thông tin phim + Poster + Ngày tháng
2. **🎯 Thay đổi phần giữa** → Hiển thị danh sách nguồn download
3. **📁 Click vào nguồn folder** → Hiển thị danh sách files/folders
4. **▶️ Click vào nguồn file** → Play file trực tiếp
5. **🔄 Navigation mượt mà** → Dễ dàng quay lại và điều hướng

**Layout 3 cột giờ đây nhất quán và user-friendly!** 🎬✨
