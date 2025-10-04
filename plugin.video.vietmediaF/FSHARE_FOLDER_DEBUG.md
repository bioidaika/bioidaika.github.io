# 🔧 FShare Folder Debug - Debug xử lý FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log mới nhất, vẫn có lỗi:

```
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7]
```

**Không có log "Cache không tồn tại" nữa** → Cache đã hoạt động
**Nhưng vẫn có "Playlist Player: skipping unplayable item"** → `loadlistitem.list_item_main(data)` không được gọi hoặc không hoạt động đúng

## 🔧 **NGUYÊN NHÂN**

### **1. ❌ Có 2 chỗ xử lý FShare folder:**
```python
# Chỗ 1 (dòng 1222-1228):
def play(data):
    link = data["url"]
    
    # Xử lý FShare folder URL
    if 'fshare' in link and 'folder' in link:
        data = cache_utils.cache_data(link)
        if data is not None:
            loadlistitem.list_item_main(data)
        else:
            notify('Không thể tải danh sách folder')
        return  # ❌ Return ở đây

# Chỗ 2 (dòng 2395-2399):
elif 'fshare' in url and 'folder' in url:
    data = cache_utils.cache_data(url)
    if data is not None:
        loadlistitem.list_item_main(data)
    return
```

### **2. ❌ Chỗ 1 được gọi trước:**
- Chỗ 1 được gọi trước và có `return`
- Nếu FShare folder được xử lý ở chỗ 1, nó sẽ `return` và không đến được chỗ 2
- Chỗ 1 không có log để debug

## ✅ **GIẢI PHÁP**

### **1. ✅ Thêm log debug vào chỗ 1:**
```python
# Xử lý FShare folder URL
if 'fshare' in link and 'folder' in link:
    xbmc.log(f"[VietmediaF] Processing FShare folder URL: {link}", xbmc.LOGINFO)
    data = cache_utils.cache_data(link)
    if data is not None:
        xbmc.log(f"[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main", xbmc.LOGINFO)
        loadlistitem.list_item_main(data)
    else:
        xbmc.log(f"[VietmediaF] FShare folder data is None, showing error", xbmc.LOGERROR)
        notify('Không thể tải danh sách folder')
    return
```

### **2. ✅ Log debug sẽ cho biết:**
- FShare folder URL có được xử lý không
- Cache data có được load thành công không
- `loadlistitem.list_item_main(data)` có được gọi không

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 TMDB search tạo URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7
```

### **2. 🔍 Action play xử lý:**
```python
def play(data):
    link = data["url"]  # link = https://www.fshare.vn/folder/D33TNJF8KWN7
    
    # Xử lý FShare folder URL
    if 'fshare' in link and 'folder' in link:  # ✅ True
        xbmc.log(f"[VietmediaF] Processing FShare folder URL: {link}", xbmc.LOGINFO)
        data = cache_utils.cache_data(link)
        if data is not None:
            xbmc.log(f"[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main", xbmc.LOGINFO)
            loadlistitem.list_item_main(data)  # ✅ Gọi loadlistitem
        else:
            xbmc.log(f"[VietmediaF] FShare folder data is None, showing error", xbmc.LOGERROR)
            notify('Không thể tải danh sách folder')
        return  # ✅ Return ở đây
```

### **3. 📊 cache_data xử lý:**
```python
def cache_data(url):
    if 'fshare' in url and 'folder' in url:
        # ... xử lý FShare folder ...
        folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_D33TNJF8KWN7
        
        # Check cache với đúng key
        if check_cache(folder_cache_key, 30):
            cache_data = get_cache(folder_cache_key)
            if cache_data:
                return cache_data  # ✅ Return cache data
        
        data = fshare.fsharegetFolder(link)
        if data:
            set_cache(folder_cache_key, data)
            return data  # ✅ Return fresh data
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

## 🎯 **CÁC TRƯỜNG HỢP DEBUG**

### **1. ✅ Cache hit:**
```
[VietmediaF] Processing FShare folder URL: https://www.fshare.vn/folder/D33TNJF8KWN7
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
```

### **2. ❌ Cache miss:**
```
[VietmediaF] Processing FShare folder URL: https://www.fshare.vn/folder/D33TNJF8KWN7
[VietmediaF] FShare folder data is None, showing error
```

### **3. ❌ Không xử lý FShare folder:**
```
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7]
```

## 🔧 **CODE CHI TIẾT**

### **File: default.py**
```python
def play(data):
    link = data["url"]

    if link is None or len(link) == 0:
        notify('Không lấy được link')
        return

    if 'text' in link or 'Text' in link:
        content = str(link).replace("text", "")
        TextBoxes(ADDON_NAME, content)
        return

    # Xử lý FShare folder URL
    if 'fshare' in link and 'folder' in link:
        xbmc.log(f"[VietmediaF] Processing FShare folder URL: {link}", xbmc.LOGINFO)
        data = cache_utils.cache_data(link)
        if data is not None:
            xbmc.log(f"[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main", xbmc.LOGINFO)
            loadlistitem.list_item_main(data)
        else:
            xbmc.log(f"[VietmediaF] FShare folder data is None, showing error", xbmc.LOGERROR)
            notify('Không thể tải danh sách folder')
        return

    # ... rest of the function
```

## 🎯 **KẾT QUẢ MONG ĐỢI**

### **Trước (Không có log):**
```
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7]
```

### **Sau (Có log debug):**
```
[VietmediaF] Processing FShare folder URL: https://www.fshare.vn/folder/D33TNJF8KWN7
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Debug rõ ràng:**
- Biết FShare folder URL có được xử lý không
- Biết cache data có được load thành công không
- Biết `loadlistitem.list_item_main(data)` có được gọi không

### **2. ✅ Troubleshooting:**
- Nếu không có log → FShare folder không được xử lý
- Nếu có log nhưng data is None → Cache hoặc fsharegetFolder lỗi
- Nếu có log và data không None → loadlistitem.list_item_main lỗi

### **3. ✅ Performance:**
- Không ảnh hưởng đến performance
- Chỉ thêm log debug
- Không thay đổi logic

**Bây giờ có thể debug FShare folder xử lý!** 🔧✨
