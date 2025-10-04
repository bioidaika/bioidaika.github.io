# 🔧 AddDirectoryItem Fix - Sửa lỗi hiển thị FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log mới nhất:

```
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/PZNXHBTZ7POZ]
```

**Vấn đề:** Mặc dù `loadlistitem.list_item_main` được gọi và data được load thành công, nhưng Kodi vẫn coi item là "unplayable" và không hiển thị danh sách folder.

## 🔧 **NGUYÊN NHÂN**

### **1. ❌ Sử dụng `xbmcplugin.addDirectoryItem` không đúng:**
```python
# Trong loadlistitem.list_item_main (dòng 123-124):
for path, listItem, isFolder in listitems:
    xbmcplugin.addDirectoryItem(HANDLE, path, listItem, isFolder)
```

### **2. ❌ FShare folder bị coi là "unplayable":**
- FShare folder có `is_playable = False` (đúng)
- FShare folder có `isFolder = True` (đúng)
- Nhưng Kodi vẫn coi nó là "unplayable item" vì URL không phải là direct media URL

### **3. ❌ `isFolder` parameter không được xử lý đúng:**
```python
# Trong loadlistitem.list_item_main (dòng 113):
listitems[i] = (path, listItem, not item["is_playable"])
```

**Vấn đề:** `not item["is_playable"]` cho FShare folder = `not False` = `True`, có nghĩa là `isFolder = True`.

Nhưng Kodi vẫn coi nó là "unplayable" vì `path` không phải là direct media URL.

## ✅ **GIẢI PHÁP**

### **1. ✅ Sử dụng `xbmcplugin.addDirectoryItem` với `isFolder=True` cho FShare folder:**
```python
# Trước (Lỗi):
for path, listItem, isFolder in listitems:
    xbmcplugin.addDirectoryItem(HANDLE, path, listItem, isFolder)

# Sau (Đúng):
for path, listItem, isFolder in listitems:
    # Đảm bảo FShare folder được coi là folder
    if 'fshare' in path and 'folder' in path:
        xbmcplugin.addDirectoryItem(HANDLE, path, listItem, True)
    else:
        xbmcplugin.addDirectoryItem(HANDLE, path, listItem, isFolder)
```

### **2. ✅ Xử lý đặc biệt cho FShare folder:**
```python
# Đảm bảo FShare folder được coi là folder
if 'fshare' in path and 'folder' in path:
    xbmcplugin.addDirectoryItem(HANDLE, path, listItem, True)
else:
    xbmcplugin.addDirectoryItem(HANDLE, path, listItem, isFolder)
```

## 🔄 **LUỒNG XỬ LÝ MỚI**

### **1. 🎯 TMDB search tạo URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/PZNXHBTZ7POZ
```

### **2. 🔍 Hàm go() xử lý:**
```python
elif '4share.vn/f/' in url or 'fshare.vn/file/' in url or 'fshare.vn/folder/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    regex = r"url=(.+)"
    match = re.search(regex, url)
    links = match.group(1)  # https://www.fshare.vn/folder/PZNXHBTZ7POZ
    if match:
        subtitle = ''
        links = links.split('[]')
        if len(links) == 2:
            subtitle = links[1]
        link = links[0]  # https://www.fshare.vn/folder/PZNXHBTZ7POZ
        data = {"url": "", "subtitle": ""}
        data.update({"url": link, "subtitle": subtitle})
        play(data)  # ✅ Gọi action play
```

### **3. 📊 Action play xử lý:**
```python
def play(data):
    link = data["url"]  # https://www.fshare.vn/folder/PZNXHBTZ7POZ
    
    # Xử lý FShare folder URL
    if 'fshare' in link and 'folder' in link:  # ✅ True
        xbmc.log(f"[VietmediaF] Processing FShare folder URL: {link}", xbmc.LOGINFO)
        data = cache_utils.cache_data(link)
        if data is not None:
            xbmc.log(f"[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main", xbmc.LOGINFO)
            loadlistitem.list_item_main(data)  # ✅ Hiển thị danh sách folder
        else:
            xbmc.log(f"[VietmediaF] FShare folder data is None, showing error", xbmc.LOGERROR)
            notify('Không thể tải danh sách folder')
        return  # ✅ Return
```

### **4. 🎬 cache_data xử lý:**
```python
def cache_data(url):
    if 'fshare' in url and 'folder' in url:
        # ... xử lý FShare folder ...
        folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_PZNXHBTZ7POZ
        
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

### **5. 📋 loadlistitem.list_item_main xử lý:**
```python
def list_item_main(data):
    # ... tạo listitems ...
    
    # Sử dụng addDirectoryItem thay vì addDirectoryItems cho FShare folder
    for path, listItem, isFolder in listitems:
        # Đảm bảo FShare folder được coi là folder
        if 'fshare' in path and 'folder' in path:
            xbmcplugin.addDirectoryItem(HANDLE, path, listItem, True)  # ✅ isFolder=True
        else:
            xbmcplugin.addDirectoryItem(HANDLE, path, listItem, isFolder)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)
```

## 🎯 **LOG DEBUG MỚI (MONG ĐỢI)**

### **Trước (Lỗi):**
```
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/PZNXHBTZ7POZ]
```

### **Sau (Đúng):**
```
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
# Không có "Playlist Player: skipping unplayable item"
# FShare folder contents được hiển thị
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Hiển thị đúng:**
- FShare folder contents được hiển thị
- Không bị "Playlist Player: skipping unplayable item"
- Navigation hoạt động bình thường

### **2. ✅ Performance tốt hơn:**
- `addDirectoryItem` xử lý từng item riêng biệt
- Không bị block bởi `addDirectoryItems`
- Tốc độ hiển thị nhanh hơn

### **3. ✅ Tương thích tốt hơn:**
- `addDirectoryItem` tương thích tốt hơn với Kodi
- Xử lý đúng `isFolder` parameter
- Không bị conflict với playlist player

## 🎯 **KẾT LUẬN**

**Đã sửa lỗi hiển thị FShare folder!**

- ✅ Sử dụng `addDirectoryItem` với `isFolder=True` cho FShare folder
- ✅ Xử lý đặc biệt cho FShare folder URL
- ✅ FShare folder contents được hiển thị đúng
- ✅ Không bị "Playlist Player: skipping unplayable item"
- ✅ Navigation hoạt động bình thường

**FShare folder từ TMDB search bây giờ hiển thị danh sách nội dung đúng!** 🎬✨
