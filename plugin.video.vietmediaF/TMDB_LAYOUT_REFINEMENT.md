# 🎬 TMDB Layout Refinement - Tinh chỉnh layout

## 🎯 **THAY ĐỔI CHÍNH**

Tinh chỉnh layout 3 cột khi click vào phim từ danh sách TMDB search để tối ưu hóa thông tin hiển thị.

### **Trước (Thông tin trùng lặp):**
- Hiển thị tên phim (không cần thiết vì đã có ở trang trước)
- Thông tin bên trái là chi tiết nguồn download
- Label2 chỉ hiển thị uploader - sheet name

### **Sau (Thông tin tối ưu):**
- Loại bỏ tên phim (không cần thiết)
- Thông tin bên trái là thông tin phim (giống danh sách trước)
- Label2 hiển thị: `Uploader | Sheet Name | Size: XXX GB`

## 🎨 **LAYOUT 3 CỘT MỚI**

### **1. 📋 Cột Trái (Thông tin phim):**
- **Title**: Tên phim/TV
- **Plot**: Mô tả chi tiết
- **Year**: Năm sản xuất
- **Rating**: Đánh giá TMDB
- **Votes**: Số lượt đánh giá
- **Genre**: Thể loại
- **Cast**: Diễn viên (nếu có)
- **Director**: Đạo diễn (nếu có)

### **2. 🎯 Cột Giữa (Danh sách nguồn):**
- **Nguồn 1**: Fshare | Phim Bộ Phụ Đề Việt | Size: 137.55 GB
- **Nguồn 2**: Uploader2 | Sheet2 | Size: 89.23 GB
- **Nguồn 3**: Uploader3 | Sheet3 | Size: 156.78 GB
- **...**: Các nguồn khác

### **3. 🖼️ Cột Phải (Poster):**
- **Poster**: Ảnh poster phim/TV
- **Fanart**: Ảnh nền (nếu có)
- **Thumbnail**: Ảnh thumbnail

### **4. 📅 Góc Dưới Phải:**
- **Ngày tháng năm**: Ngày sản xuất
- **Runtime**: Thời lượng phim
- **Status**: Trạng thái (Released, In Production, etc.)

## 🔧 **CÁC THAY ĐỔI CODE**

### **1. 🗑️ Loại bỏ item chính:**
```python
# XÓA: Tạo item chính từ dữ liệu TMDB
# movie_item = create_movie_item(movie_data, media_type)
# items.append(movie_item)
```

### **2. 🎯 Cập nhật format label2:**
```python
# Trước:
source_label2 = f"{uploader} - {sheet_name}"

# Sau:
source_label2 = f"{uploader} | {sheet_name} | Size: {size}"
```

### **3. 📋 Thông tin phim ở bên trái:**
```python
"info": {
    "title": movie_data.get("title", movie_data.get("name", "Unknown")),
    "plot": movie_data.get("overview", ""),
    "year": movie_data.get("release_date", movie_data.get("first_air_date", "")).split("-")[0] if movie_data.get("release_date") or movie_data.get("first_air_date") else "",
    "rating": movie_data.get("vote_average", 0),
    "votes": movie_data.get("vote_count", 0),
    "genre": ", ".join([genre.get("name", "") for genre in movie_data.get("genres", [])]),
    "mediatype": "movie" if media_type == "movie" else "tvshow"
}
```

### **4. 🎨 Artwork từ movie_data:**
```python
"art": {
    "poster": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get("poster_path") else "",
    "fanart": f"https://image.tmdb.org/t/p/w1280{movie_data.get('backdrop_path', '')}" if movie_data.get("backdrop_path") else "",
    "thumb": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get("poster_path") else ""
}
```

## 🎨 **VISUAL LAYOUT MỚI**

### **Khi click vào phim:**
```
┌─────────────────────────────────────┐
│ 🎬 When Life Gives You Tangerines   │
│ ⭐ 8.5 | 🎭 Drama, Romance          │
│ 📝 Plot description...              │
│                                     │
│ 🎯 DANH SÁCH NGUỒN:                 │
│ 1. Fshare | Phim Bộ Phụ Đề Việt     │
│    | Size: 137.55 GB                │
│ 2. Uploader2 | Sheet2 | Size: 89.23 GB │
│ 3. Uploader3 | Sheet3 | Size: 156.78 GB │
│                                     │
│ 📅 2023 | ⏱️ 120 min                │
└─────────────────────────────────────┘
```

### **Khi click vào nguồn (folder):**
```
┌─────────────────────────────────────┐
│ 🎬 When Life Gives You Tangerines   │
│ ⭐ 8.5 | 🎭 Drama, Romance          │
│ 📝 Plot description...              │
│                                     │
│ 📁 Folder: Fshare - Phim Bộ Phụ Đề Việt │
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
│ 🎬 When Life Gives You Tangerines   │
│ ⭐ 8.5 | 🎭 Drama, Romance          │
│ 📝 Plot description...              │
│                                     │
│ ▶️ Playing: Fshare - Phim Bộ Phụ Đề Việt │
│                                     │
│ 📅 2023 | ⏱️ 120 min                │
└─────────────────────────────────────┘
```

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
# Tạo các item nguồn download với thông tin phim
for i, source in enumerate(sources, 1):
    uploader = source.get("uploader", "Unknown")
    sheet_name = source.get("sheet_name", "Unknown")
    size = source.get("size", "N/A")
    
    # Tạo label2 với format mới
    source_label2 = f"{uploader} | {sheet_name} | Size: {size}"
    
    # Tạo item với thông tin phim ở bên trái
    source_item = {
        "label": f"[COLOR yellow]Nguồn {i}:[/COLOR] {uploader}",
        "label2": source_label2,
        "info": {
            "title": movie_data.get("title", movie_data.get("name", "Unknown")),
            "plot": movie_data.get("overview", ""),
            "year": movie_data.get("release_date", movie_data.get("first_air_date", "")).split("-")[0],
            "rating": movie_data.get("vote_average", 0),
            "votes": movie_data.get("vote_count", 0),
            "genre": ", ".join([genre.get("name", "") for genre in movie_data.get("genres", [])]),
            "mediatype": "movie" if media_type == "movie" else "tvshow"
        },
        "art": {
            "poster": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}",
            "fanart": f"https://image.tmdb.org/t/p/w1280{movie_data.get('backdrop_path', '')}",
            "thumb": f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"
        }
    }
    items.append(source_item)
```

## 🎯 **LỢI ÍCH**

### **1. 📱 Thông tin tối ưu:**
- Loại bỏ thông tin trùng lặp
- Thông tin phim luôn hiển thị
- Danh sách nguồn rõ ràng

### **2. 🎨 Layout nhất quán:**
- Giữ nguyên thông tin phim
- Giữ nguyên poster và artwork
- Chỉ thay đổi phần cần thiết

### **3. 🔄 Navigation mượt mà:**
- Dễ dàng quay lại danh sách
- Thông tin phim luôn hiển thị
- Không bị mất context

### **4. 📊 Thông tin chi tiết:**
- Label2 hiển thị đầy đủ thông tin nguồn
- Thông tin phim đầy đủ và chính xác
- Artwork chất lượng cao

## ⚙️ **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ Success Case:**
- TMDB API trả về data
- Backend API trả về download sources
- Hiển thị layout 3 cột với thông tin phim và danh sách nguồn

### **2. ⚠️ Partial Success:**
- TMDB API trả về data
- Backend API lỗi hoặc không có sources
- Hiển thị layout 3 cột với thông tin phim nhưng không có nguồn

### **3. ❌ Error Case:**
- TMDB API lỗi hoặc không tìm thấy
- Hiển thị alert và quay lại danh sách

## 🎯 **KẾT QUẢ**

Khi user click vào phim từ danh sách TMDB search:

1. **🎨 Layout 3 cột tối ưu** → Thông tin phim + Danh sách nguồn + Poster
2. **📋 Thông tin phim đầy đủ** → Title, Plot, Year, Rating, Genre
3. **🎯 Danh sách nguồn rõ ràng** → Uploader | Sheet | Size
4. **🖼️ Artwork chất lượng cao** → Poster, Fanart, Thumbnail
5. **🔄 Navigation mượt mà** → Dễ dàng quay lại và điều hướng

**Layout 3 cột giờ đây tối ưu và thông tin đầy đủ!** 🎬✨
