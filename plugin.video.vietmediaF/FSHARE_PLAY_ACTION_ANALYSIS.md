# 🎬 FShare Play Action Analysis - Phân tích action play xử lý FShare

## 🎯 **TỔNG QUAN**

Action `play` xử lý URL FShare theo hai luồng chính: **FShare Folder** và **FShare File**. Mỗi loại có cách xử lý riêng biệt.

## 🔄 **LUỒNG XỬ LÝ CHÍNH**

### **1. 🎯 Input URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/ABC123XYZ
```

### **2. 🔍 URL Detection & Routing:**
```python
def play(data):
    link = data["url"]
    
    # 1. Kiểm tra FShare folder
    if 'fshare' in link and 'folder' in link:
        # Xử lý folder
        data = cache_utils.cache_data(link)
        if data is not None:
            loadlistitem.list_item_main(data)
        else:
            notify('Không thể tải danh sách folder')
        return
    
    # 2. Xử lý FShare file
    if "fshare.vn" in link:
        # Xử lý file
        # ... (xem chi tiết bên dưới)
```

## 📁 **XỬ LÝ FSHARE FOLDER**

### **1. 🎯 Detection:**
```python
if 'fshare' in link and 'folder' in link:
    # Đây là FShare folder URL
```

### **2. 📊 Cache & Display:**
```python
data = cache_utils.cache_data(link)
if data is not None:
    loadlistitem.list_item_main(data)  # Hiển thị danh sách files
else:
    notify('Không thể tải danh sách folder')
```

### **3. 🔄 Luồng xử lý:**
```
FShare Folder URL → cache_utils.cache_data() → fshare.fsharegetFolder() → 
FShare API → Parse Response → Create Items → loadlistitem.list_item_main()
```

## 🎬 **XỬ LÝ FSHARE FILE**

### **1. 🎯 Detection:**
```python
if "fshare.vn" in link:
    # Đây là FShare file URL
```

### **2. 📊 History Management:**
```python
from_history = False
if "fshare.vn" in link and check_watched_history():
    history = get_watched_history()
    for entry in history:
        parts = entry.strip().split(",")
        if len(parts) >= 2 and link in parts[1]:
            from_history = True
            break
```

### **3. 📝 File Info Retrieval:**
```python
if from_history:
    # Lấy thông tin từ history
    for entry in history:
        parts = entry.strip().split(",")
        if len(parts) >= 2 and link in parts[1]:
            name = parts[0]
            size = parts[2] if len(parts) > 2 else 0
            break
else:
    # Lấy thông tin từ FShare API
    name, file_type, size = fshare.get_fshare_file_info(link)
```

### **4. 🔗 Download Link Generation:**
```python
link = getlink.get(link)  # Gọi getlink.get()
if not link:
    alert("Không lấy được link. Thử lại sau.")
    return
```

### **5. 🎬 Link Resolution Process:**
```python
# getlink.py
def get(url):
    if 'fshare.vn' in url:
        return get_fshare(url)  # Gọi get_fshare()

def get_fshare(url):
    token, session_id = fshare.check_session()
    link = fshare.get_download_link(token, session_id, url)
    return link
```

### **6. 🎭 Subtitle Handling:**
```python
subtitle = ''
links = link.split('[]')

if len(links) == 2:
    subtitle = links[1]  # Subtitle URL
elif data.get('subtitle'):
    subtitle = data.get('subtitle')

if "qc" in subtitle:
    subtitle = ''  # Bỏ qua subtitle có "qc"
```

### **7. 🎬 Video Playback:**
```python
def resolve_and_notify(link, subtitle_url=None):
    # External player check
    use_external_player = ADDON.getSetting("external_player_enabled") == "true"
    
    if use_external_player:
        # Sử dụng external player
        dummy_item = xbmcgui.ListItem(path="special://home/addons/plugin.video.vietmediaF/resources/dummy.mp4")
        xbmcplugin.setResolvedUrl(HANDLE, True, dummy_item)
        success = advanced_settings_menu.launch_external_player(link, name)
    else:
        # Sử dụng Kodi player
        item = xbmcgui.ListItem(path=link)
        if "fshare.vn" in link:
            item.setMimeType('video/mp4')
            item.setContentLookup(False)
            info = {
                'title': name,
                'size': size,
                'mediatype': 'video'
            }
            item.setInfo('video', info)
        
        xbmcplugin.setResolvedUrl(HANDLE, True, item)
        
        # Xử lý subtitle
        if subtitle_url:
            download_and_set_subtitle(subtitle_url)
        elif "fshare.vn" in link:
            found_subtitle, subtitle_link = check_and_get_subtitle(name)
            if found_subtitle:
                token, session_id = fshare.check_session()
                subtitle_link = fshare.get_download_link(token, session_id, subtitle_link)
                download_and_set_subtitle(subtitle_link)
```

## 🔧 **CODE CHI TIẾT**

### **File: default.py - Hàm play()**
```python
def play(data):
    link = data["url"]
    
    # 1. FShare Folder Handling
    if 'fshare' in link and 'folder' in link:
        data = cache_utils.cache_data(link)
        if data is not None:
            loadlistitem.list_item_main(data)
        else:
            notify('Không thể tải danh sách folder')
        return
    
    # 2. FShare File Handling
    if "fshare.vn" in link:
        # History management
        from_history = False
        if check_watched_history():
            history = get_watched_history()
            for entry in history:
                parts = entry.strip().split(",")
                if len(parts) >= 2 and link in parts[1]:
                    from_history = True
                    break
        
        # File info retrieval
        if from_history:
            # Get from history
            for entry in history:
                parts = entry.strip().split(",")
                if len(parts) >= 2 and link in parts[1]:
                    name = parts[0]
                    size = parts[2] if len(parts) > 2 else 0
                    break
        else:
            # Get from API
            name, file_type, size = fshare.get_fshare_file_info(link)
        
        # Download link generation
        link = getlink.get(link)
        if not link:
            alert("Không lấy được link. Thử lại sau.")
            return
        
        # Subtitle handling
        subtitle = ''
        links = link.split('[]')
        if len(links) == 2:
            subtitle = links[1]
        elif data.get('subtitle'):
            subtitle = data.get('subtitle')
        
        if "qc" in subtitle:
            subtitle = ''
        
        link = links[0]
        
        # Video playback
        if "fshare.vn" in link or "4share.vn" in link:
            resolve_and_notify(link, subtitle if len(subtitle) > 0 else None)
```

### **File: getlink.py - Hàm get()**
```python
def get(url):
    if 'fshare.vn' in url:
        if 'token' in url:
            match = re.search(r"(\?.+?\d+)",url)
            _token = match.group(1)
            url = url.replace(_token,'')
        if not 'https' in url:
            url = url.replace('http','https')
        
        return get_fshare(url)

def get_fshare(url):
    token, session_id = fshare.check_session()
    link = fshare.get_download_link(token, session_id, url)
    return link
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ FShare Folder:**
```
Input:  https://www.fshare.vn/folder/D33TNJF8KWN7
Process: cache_utils.cache_data() → fshare.fsharegetFolder() → 
         FShare API → Parse → loadlistitem.list_item_main()
Result: Hiển thị danh sách files trong folder
```

### **2. ✅ FShare File:**
```
Input:  https://www.fshare.vn/file/ABC123XYZ
Process: fshare.get_fshare_file_info() → getlink.get() → 
         fshare.get_download_link() → resolve_and_notify()
Result: Phát file video
```

### **3. ✅ FShare File với Subtitle:**
```
Input:  https://www.fshare.vn/file/ABC123XYZ[]https://subtitle.url
Process: Split subtitle → Download subtitle → Set subtitle → Play video
Result: Phát file video với phụ đề
```

### **4. ✅ FShare File với External Player:**
```
Input:  https://www.fshare.vn/file/ABC123XYZ
Process: Check external player setting → Launch external player
Result: Mở file trong external player
```

## 🎯 **TÍNH NĂNG**

### **1. 🔄 Dual Processing:**
- Folder: Hiển thị danh sách files
- File: Phát video trực tiếp

### **2. 💾 Cache Integration:**
- Folder: Sử dụng cache system
- File: Real-time API calls

### **3. 📝 History Management:**
- Lưu lịch sử xem
- Lấy thông tin từ history
- Performance optimization

### **4. 🎭 Subtitle Support:**
- Tự động tải phụ đề
- Hỗ trợ multiple subtitle sources
- Error handling

### **5. 🎬 Player Options:**
- Kodi built-in player
- External player support
- MIME type setting

### **6. ⚠️ Error Handling:**
- Link generation errors
- API errors
- Player errors

## 🎯 **KẾT LUẬN**

Action `play` xử lý FShare URLs một cách thông minh:

1. **📁 Folder Detection** → Hiển thị danh sách files
2. **🎬 File Detection** → Phát video trực tiếp
3. **💾 Cache System** → Performance optimization
4. **📝 History Management** → User experience
5. **🎭 Subtitle Support** → Enhanced viewing
6. **🎬 Player Options** → Flexibility
7. **⚠️ Error Handling** → Robust operation

**FShare play action hoạt động hoàn hảo cho cả folder và file!** 🎬✨
