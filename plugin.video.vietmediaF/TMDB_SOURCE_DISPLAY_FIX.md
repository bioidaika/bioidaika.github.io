# 🔧 TMDB Source Display Fix - Sửa lỗi hiển thị nguồn

## 🎯 **VẤN ĐỀ**

Khi người dùng click vào 1 phim trong danh sách TMDB search, addon hiển thị danh sách nguồn nhưng tất cả các nguồn đều hiển thị tên phim thay vì thông tin uploader.

### **Lỗi:**
```
Hiển thị: Avatar (2009)
Thay vì: Uploader | Sheet Name | Size: 137.55 GB
```

## 🔧 **NGUYÊN NHÂN**

Trong `info` dictionary của `source_item`, `title` đang được set là tên phim:

```python
"info": {
    "title": movie_data.get("title", movie_data.get("name", "Unknown")),  # ❌ Tên phim
    # ... (các fields khác)
}
```

## ✅ **GIẢI PHÁP**

### **1. 🗑️ Code cũ (Lỗi):**
```python
"info": {
    "title": movie_data.get("title", movie_data.get("name", "Unknown")),  # ❌ Tên phim
    "plot": movie_data.get("overview", ""),
    # ... (các fields khác)
}
```

### **2. ✅ Code mới (Đúng):**
```python
"info": {
    "title": f"{uploader} | {sheet_name} | Size: {size}",  # ✅ Thông tin nguồn
    "plot": movie_data.get("overview", ""),
    # ... (các fields khác)
}
```

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 User click vào phim:**
```
Avatar (2009) → Click
```

### **2. 📊 Backend API trả về nguồn:**
```json
{
  "sources": [
    {
      "uploader": "PhongBlack",
      "sheet_name": "Phim Lẻ 4K",
      "size": "137.55 GB",
      "download_url": "https://www.fshare.vn/folder/ABC123"
    }
  ]
}
```

### **3. 🎬 Tạo source_item:**
```python
source_item = {
    "label": f"[COLOR yellow]Nguồn {i}:[/COLOR] {uploader}",  # Label chính
    "label2": f"{uploader} | {sheet_name} | Size: {size}",    # Label2
    "info": {
        "title": f"{uploader} | {sheet_name} | Size: {size}",  # ✅ Title đúng
        "plot": movie_data.get("overview", ""),                # Plot phim
        # ... (các fields khác)
    }
}
```

### **4. 🎭 Kết quả hiển thị:**
```
Label:  [COLOR yellow]Nguồn 1:[/COLOR] PhongBlack
Title:  PhongBlack | Phim Lẻ 4K | Size: 137.55 GB
Plot:   Avatar follows the story of Jake Sully...
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ FShare Folder:**
```
Input:  https://www.fshare.vn/folder/ABC123
Display: PhongBlack | Phim Lẻ 4K | Size: 137.55 GB
```

### **2. ✅ FShare File:**
```
Input:  https://www.fshare.vn/file/XYZ789
Display: Uploader | Sheet Name | Size: 2.5 GB
```

### **3. ✅ Multiple Sources:**
```
Nguồn 1: PhongBlack | Phim Lẻ 4K | Size: 137.55 GB
Nguồn 2: HDViet | Phim HD | Size: 89.2 GB
Nguồn 3: Thuviencine | Phim Bộ | Size: 45.8 GB
```

## 🔧 **CODE CHI TIẾT**

### **File: resources/tmdb_search.py**
```python
# Tạo item nguồn với thông tin phim ở bên trái
source_item = {
    "label": f"[COLOR yellow]Nguồn {i}:[/COLOR] {uploader}",
    "is_playable": is_playable,
    "path": action_path,
    "thumbnail": movie_data.get("poster_path", ""),
    "fanart": movie_data.get("backdrop_path", ""),
    "label2": source_label2,  # Uploader | Sheet | Size
    "info": {
        "title": f"{uploader} | {sheet_name} | Size: {size}",  # ✅ Title đúng
        "plot": movie_data.get("overview", ""),                # Plot phim
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
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Hiển thị đúng thông tin:**
- Title hiển thị thông tin nguồn
- Label hiển thị tên uploader
- Label2 hiển thị chi tiết

### **2. ✅ User Experience tốt:**
- Dễ phân biệt các nguồn
- Thông tin rõ ràng
- Consistent display

### **3. ✅ Thông tin đầy đủ:**
- Uploader name
- Sheet name
- File size
- Movie plot (trong info)

## 🎯 **KẾT QUẢ**

Sau khi sửa lỗi:

### **Trước (Lỗi):**
```
Avatar (2009)
Avatar (2009)
Avatar (2009)
```

### **Sau (Đúng):**
```
[COLOR yellow]Nguồn 1:[/COLOR] PhongBlack
PhongBlack | Phim Lẻ 4K | Size: 137.55 GB

[COLOR yellow]Nguồn 2:[/COLOR] HDViet
HDViet | Phim HD | Size: 89.2 GB

[COLOR yellow]Nguồn 3:[/COLOR] Thuviencine
Thuviencine | Phim Bộ | Size: 45.8 GB
```

**Nguồn hiển thị đúng thông tin uploader!** 🎬✨
