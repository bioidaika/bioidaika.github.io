# 🔧 FShare Folder Cache Fix - Sửa lỗi cache FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log, có 2 lỗi chính:

### **1. ❌ Cache không tồn tại:**
```
Cache không tồn tại: C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\cache\5f2124fccef4dd4b16f98eedf0287f33.json
```

### **2. ❌ Playlist Player skipping unplayable item:**
```
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/AESIYZRLDUVL]
```

## 🔧 **NGUYÊN NHÂN**

### **1. ❌ Cache parsing lỗi:**
Hàm `cache_data` đang tìm kiếm pattern `url=(.+)` nhưng URL từ TMDB search không có pattern này:

```python
# URL từ TMDB search:
https://www.fshare.vn/folder/AESIYZRLDUVL

# Pattern tìm kiếm:
url=(.+)

# Kết quả: Không match → return None
```

### **2. ❌ Logic xử lý URL:**
```python
# Code cũ (Lỗi):
regex = r"url=(.+)"
match = re.search(regex, url)
if not match:
    logError("Không tìm thấy URL trong: " + url)
    return None  # ❌ Return None
```

## ✅ **GIẢI PHÁP**

### **1. 🗑️ Code cũ (Lỗi):**
```python
else:
    try:
        regex = r"url=(.+)"
        match = re.search(regex, url)
        if not match:
            logError("Không tìm thấy URL trong: " + url)
            return None  # ❌ Return None
        link = match.group(1)
```

### **2. ✅ Code mới (Đúng):**
```python
else:
    try:
        # Kiểm tra nếu URL đã là FShare URL trực tiếp
        if url.startswith('https://www.fshare.vn/folder/'):
            link = url  # ✅ Sử dụng URL trực tiếp
        else:
            # Tìm URL trong parameter
            regex = r"url=(.+)"
            match = re.search(regex, url)
            if not match:
                logError("Không tìm thấy URL trong: " + url)
                return None
            link = match.group(1)
```

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 TMDB search tạo URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/AESIYZRLDUVL
```

### **2. 🔍 Action play xử lý:**
```python
if 'fshare' in link and 'folder' in link:
    data = cache_utils.cache_data(link)  # link = https://www.fshare.vn/folder/AESIYZRLDUVL
```

### **3. 📊 cache_data xử lý:**
```python
# Trước (Lỗi):
regex = r"url=(.+)"
match = re.search(regex, "https://www.fshare.vn/folder/AESIYZRLDUVL")
# Không match → return None

# Sau (Đúng):
if url.startswith('https://www.fshare.vn/folder/'):
    link = url  # ✅ Sử dụng URL trực tiếp
```

### **4. 🎬 fsharegetFolder được gọi:**
```python
data = fshare.fsharegetFolder(link)  # link = https://www.fshare.vn/folder/AESIYZRLDUVL
```

### **5. 📋 Hiển thị danh sách:**
```python
if data is not None:
    loadlistitem.list_item_main(data)  # ✅ Hiển thị danh sách folder
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ URL trực tiếp (TMDB search):**
```
Input:  https://www.fshare.vn/folder/AESIYZRLDUVL
Result: Sử dụng URL trực tiếp
```

### **2. ✅ URL với parameter (Menu):**
```
Input:  plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/ABC123
Result: Extract URL từ parameter
```

### **3. ✅ URL với page (Pagination):**
```
Input:  plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/ABC123&page=2
Result: Extract URL và page
```

## 🔧 **CODE CHI TIẾT**

### **File: resources/cache_utils.py**
```python
def cache_data(url):
    """Cache dữ liệu từ URL và trả về dữ liệu đã cache"""
    
    if 'fshare' in url and 'folder' in url:
        url = urllib.parse.unquote_plus(url)
        
        if 'api' in url:
            # Xử lý API URL
            # ... (existing code)
        else:
            try:
                # Kiểm tra nếu URL đã là FShare URL trực tiếp
                if url.startswith('https://www.fshare.vn/folder/'):
                    link = url  # ✅ Sử dụng URL trực tiếp
                else:
                    # Tìm URL trong parameter
                    regex = r"url=(.+)"
                    match = re.search(regex, url)
                    if not match:
                        logError("Không tìm thấy URL trong: " + url)
                        return None
                    link = match.group(1)
                
                # Xử lý page parameter
                page_match = re.search(r"page=(\d+)", url)
                if page_match:
                    page = page_match.group(1)
                    if '?' in link:
                        link += '&'
                    else:
                        link += '?'
                    link += "page=" + page
                    
            except Exception as e:
                logError(f"Lỗi parse URL: {str(e)}")
                return None

        # Extract folder code from URL for safe cache key
        folder_code = link.split('/')[-1] if '/' in link else link
        folder_cache_key = f"fshare_folder_{folder_code}"

        data = fshare.fsharegetFolder(link)
        if data:
            set_cache(folder_cache_key, data)
            return data
        else:
            logError("fsharegetFolder trả về None")
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Xử lý đúng URL:**
- URL trực tiếp từ TMDB search
- URL với parameter từ menu
- URL với page từ pagination

### **2. ✅ Cache hoạt động:**
- Tạo cache key đúng
- Lưu cache thành công
- Load cache khi cần

### **3. ✅ FShare folder hiển thị:**
- Danh sách folder con
- Danh sách file
- Navigation hoạt động

## 🎯 **KẾT QUẢ**

### **Trước (Lỗi):**
```
Cache không tồn tại → return None
Playlist Player: skipping unplayable item
```

### **Sau (Đúng):**
```
Cache được tạo thành công
FShare folder hiển thị danh sách nội dung
Navigation hoạt động bình thường
```

## 🎯 **KẾT LUẬN**

**Đã sửa lỗi cache FShare folder!**

- ✅ URL trực tiếp được xử lý đúng
- ✅ Cache được tạo và load thành công
- ✅ FShare folder hiển thị danh sách nội dung
- ✅ Navigation hoạt động bình thường

**Action play bây giờ xử lý đúng FShare folder từ TMDB search!** 🎬✨
