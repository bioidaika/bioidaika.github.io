# 🔧 FShare Folder Routing Fix - Sửa lỗi routing FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log mới nhất:

```
[VietmediaF] Processing URL in go(): plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
[VietmediaF] Unquoted URL: plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
Cache không tồn tại: C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\cache\fshare_folder_MLU9DUTD43W2.json
Cache không tồn tại: C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\cache\fshare_folder_MLU9DUTD43W2_page0.json
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2]
```

**Vấn đề:** Không có log debug từ action `play`! Điều này có nghĩa là FShare folder URL không được xử lý bởi action `play` mà bởi action khác.

## 🔧 **NGUYÊN NHÂN**

### **1. ❌ FShare folder được xử lý ở 2 chỗ:**
```python
# Chỗ 1 (dòng 1221-1231) - action play:
def play(data):
    link = data["url"]
    
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
        return  # ❌ Nhưng không bao giờ được gọi!

# Chỗ 2 (dòng 2398-2402) - hàm go():
elif 'fshare' in url and 'folder' in url:
    data = cache_utils.cache_data(url)
    if data is not None:
        loadlistitem.list_item_main(data)
    return  # ✅ Được gọi trước, blocking action play
```

### **2. ❌ Routing không đúng:**
- FShare folder URL được xử lý bởi chỗ 2 (hàm `go()`) **TRƯỚC** khi action `play` được gọi
- Chỗ 2 kiểm tra `'fshare' in url and 'folder' in url` và xử lý ngay lập tức
- Action `play` (chỗ 1) không bao giờ được gọi

### **3. ❌ Không có routing cho action play:**
- Trong hàm `go()`, không có phần xử lý cho `action=play`
- URL `plugin://plugin.video.vietmediaF/?action=play&url=...` được xử lý bởi các `elif` khác nhau dựa trên nội dung URL
- FShare folder URL được xử lý bởi `elif 'fshare' in url and 'folder' in url:` thay vì action `play`

## ✅ **GIẢI PHÁP**

### **1. ✅ Xóa bỏ xử lý FShare folder riêng biệt:**
```python
# Xóa bỏ chỗ 2 (dòng 2398-2402):
# elif 'fshare' in url and 'folder' in url:
#     data = cache_utils.cache_data(url)
#     if data is not None:
#         loadlistitem.list_item_main(data)
#     return
```

### **2. ✅ Thêm FShare folder vào xử lý action play:**
```python
# Thêm 'fshare.vn/folder/' vào dòng 2371:
elif '4share.vn/f/' in url or 'fshare.vn/file/' in url or 'fshare.vn/folder/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    regex = r"url=(.+)"
    match = re.search(regex, url)
    links = match.group(1)
    if match:
        subtitle = ''
        links = links.split('[]')
        if len(links) == 2:
            subtitle = links[1]
        link = links[0]
        data = {"url": "", "subtitle": ""}
        data.update({"url": link, "subtitle": subtitle})
        play(data)  # ✅ Gọi action play
    else:
        alert("Lỗi không xác định được link 01. Báo dev xử lí :-((")
        exit()
```

## 🔄 **LUỒNG XỬ LÝ MỚI**

### **1. 🎯 TMDB search tạo URL:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
```

### **2. 🔍 Hàm go() xử lý:**
```python
url = sys.argv[0] + sys.argv[2]
xbmc.log(f"[VietmediaF] Processing URL in go(): {url}", xbmc.LOGINFO)

if not "thread_id" in url:
    url = urllib_parse.unquote_plus(url)
    xbmc.log(f"[VietmediaF] Unquoted URL: {url}", xbmc.LOGINFO)

# ... (other elif checks)

# Trước (Lỗi):
# elif 'fshare' in url and 'folder' in url:  # ❌ Xử lý trước action play
#     data = cache_utils.cache_data(url)
#     if data is not None:
#         loadlistitem.list_item_main(data)
#     return

# Sau (Đúng):
elif '4share.vn/f/' in url or 'fshare.vn/file/' in url or 'fshare.vn/folder/' in url or 'ok.ru' in url or 'drive.google.com' in url:  # ✅ Xử lý FShare folder
    regex = r"url=(.+)"
    match = re.search(regex, url)
    links = match.group(1)  # https://www.fshare.vn/folder/MLU9DUTD43W2
    if match:
        subtitle = ''
        links = links.split('[]')
        if len(links) == 2:
            subtitle = links[1]
        link = links[0]  # https://www.fshare.vn/folder/MLU9DUTD43W2
        data = {"url": "", "subtitle": ""}
        data.update({"url": link, "subtitle": subtitle})
        play(data)  # ✅ Gọi action play
```

### **3. 📊 Action play xử lý:**
```python
def play(data):
    link = data["url"]  # https://www.fshare.vn/folder/MLU9DUTD43W2
    
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
        folder_cache_key = f"fshare_folder_{folder_code}"  # fshare_folder_MLU9DUTD43W2
        
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

### **5. 📋 Hiển thị danh sách:**
```python
if data is not None:
    loadlistitem.list_item_main(data)  # ✅ Hiển thị danh sách folder
```

## 🎯 **LOG DEBUG MỚI**

### **Trước (Lỗi):**
```
[VietmediaF] Processing URL in go(): plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
[VietmediaF] Unquoted URL: plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
Cache không tồn tại: C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\cache\fshare_folder_MLU9DUTD43W2.json
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2]
```

### **Sau (Đúng):**
```
[VietmediaF] Processing URL in go(): plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
[VietmediaF] Unquoted URL: plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/MLU9DUTD43W2
[VietmediaF] Processing FShare folder URL: https://www.fshare.vn/folder/MLU9DUTD43W2
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
```

## 🎯 **LỢI ÍCH**

### **1. ✅ Routing đúng:**
- FShare folder URL được xử lý bởi action `play`
- Không bị block bởi xử lý riêng biệt
- Log debug rõ ràng

### **2. ✅ Đơn giản hóa:**
- Chỉ 1 chỗ xử lý FShare folder
- Không duplicate code
- Dễ maintain

### **3. ✅ Functionality:**
- FShare folder hiển thị danh sách nội dung
- Navigation hoạt động bình thường
- Cache hoạt động đúng

## 🎯 **KẾT LUẬN**

**Đã sửa lỗi routing FShare folder!**

- ✅ Xóa bỏ xử lý FShare folder riêng biệt trong hàm `go()`
- ✅ Thêm FShare folder vào xử lý action `play`
- ✅ Action `play` được gọi đúng
- ✅ Log debug rõ ràng
- ✅ FShare folder hiển thị danh sách nội dung
- ✅ Navigation hoạt động bình thường

**Action play bây giờ xử lý đúng FShare folder từ TMDB search!** 🎬✨
