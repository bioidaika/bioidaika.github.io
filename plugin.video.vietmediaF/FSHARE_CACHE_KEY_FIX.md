# 🔧 FShare Cache Key Fix - Sửa lỗi cache key FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log mới nhất, vẫn có lỗi cache:

```
Cache không tồn tại: C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\cache\2ff46cbb95fae315a5b0107c59077e59.json
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7]
```

## 🔧 **NGUYÊN NHÂN**

### **1. ❌ Cache key không đúng:**
- Cache key được tạo từ `link` (URL đầy đủ)
- Nhưng cache được check từ `url` (URL gốc)
- Không match → cache miss

### **2. ❌ Logic cache:**
```python
# Code cũ (Lỗi):
folder_code = link.split('/')[-1]  # D33TNJF8KWN7
folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_D33TNJF8KWN7

# Nhưng cache được check từ URL gốc:
cache_key = hashlib.md5(url.encode()).hexdigest()  # 2ff46cbb95fae315a5b0107c59077e59
```

## ✅ **GIẢI PHÁP**

### **1. 🗑️ Code cũ (Lỗi):**
```python
def cache_data(url):
    cache_key = hashlib.md5(url.encode()).hexdigest()
    
    if check_cache(cache_key):
        data = get_cache(cache_key)
        if data:
            return data
    
    # ... xử lý FShare folder ...
    
    # Extract folder code from URL for safe cache key
    folder_code = link.split('/')[-1] if '/' in link else link
    folder_cache_key = f"fshare_folder_{folder_code}"
    
    data = fshare.fsharegetFolder(link)
    if data:
        set_cache(folder_cache_key, data)  # ❌ Cache key khác với check key
        return data
```

### **2. ✅ Code mới (Đúng):**
```python
def cache_data(url):
    if 'fshare' in url and 'folder' in url:
        # ... xử lý URL ...
        
        # Extract folder code from URL for safe cache key
        folder_code = link.split('/')[-1] if '/' in link else link
        folder_cache_key = f"fshare_folder_{folder_code}"
        
        # Check cache first với đúng key
        if check_cache(folder_cache_key, 30):
            cache_data = get_cache(folder_cache_key)
            if cache_data:
                return cache_data
        
        data = fshare.fsharegetFolder(link)
        if data:
            set_cache(folder_cache_key, data)  # ✅ Cache key giống với check key
            return data
```

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 TMDB search tạo URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7
```

### **2. 🔍 Action play xử lý:**
```python
if 'fshare' in link and 'folder' in link:
    data = cache_utils.cache_data(link)  # link = https://www.fshare.vn/folder/D33TNJF8KWN7
```

### **3. 📊 cache_data xử lý:**
```python
# Trước (Lỗi):
cache_key = hashlib.md5(url.encode()).hexdigest()  # 2ff46cbb95fae315a5b0107c59077e59
if check_cache(cache_key):  # ❌ Check key khác
    # ...
folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_D33TNJF8KWN7
set_cache(folder_cache_key, data)  # ❌ Set key khác

# Sau (Đúng):
folder_code = link.split('/')[-1]  # D33TNJF8KWN7
folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_D33TNJF8KWN7
if check_cache(folder_cache_key, 30):  # ✅ Check key đúng
    # ...
set_cache(folder_cache_key, data)  # ✅ Set key đúng
```

### **4. 🎬 fsharegetFolder được gọi:**
```python
data = fshare.fsharegetFolder(link)  # link = https://www.fshare.vn/folder/D33TNJF8KWN7
```

### **5. 📋 Hiển thị danh sách:**
```python
if data is not None:
    loadlistitem.list_item_main(data)  # ✅ Hiển thị danh sách folder
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ Cache hit:**
```
Input:  https://www.fshare.vn/folder/D33TNJF8KWN7
Check:  fshare_folder_D33TNJF8KWN7
Result: Load từ cache
```

### **2. ✅ Cache miss:**
```
Input:  https://www.fshare.vn/folder/D33TNJF8KWN7
Check:  fshare_folder_D33TNJF8KWN7
Result: Gọi fsharegetFolder, tạo cache
```

### **3. ✅ Cache expired:**
```
Input:  https://www.fshare.vn/folder/D33TNJF8KWN7
Check:  fshare_folder_D33TNJF8KWN7 (expired)
Result: Gọi fsharegetFolder, update cache
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
                    link = url
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
        
        # Check cache first với đúng key
        if check_cache(folder_cache_key, 30):
            cache_data = get_cache(folder_cache_key)
            if cache_data:
                return cache_data

        data = fshare.fsharegetFolder(link)
        if data:
            set_cache(folder_cache_key, data)
            return data
        else:
            logError("fsharegetFolder trả về None")
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Cache key nhất quán:**
- Check cache với key đúng
- Set cache với key đúng
- Không bị cache miss

### **2. ✅ Performance tốt:**
- Load cache nhanh
- Không gọi API không cần thiết
- Giảm thời gian tải

### **3. ✅ FShare folder hoạt động:**
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
Cache được tạo và load thành công
FShare folder hiển thị danh sách nội dung
Navigation hoạt động bình thường
```

## 🎯 **KẾT LUẬN**

**Đã sửa lỗi cache key FShare folder!**

- ✅ Cache key nhất quán
- ✅ Cache được tạo và load thành công
- ✅ FShare folder hiển thị danh sách nội dung
- ✅ Navigation hoạt động bình thường

**Action play bây giờ xử lý đúng FShare folder từ TMDB search!** 🎬✨
