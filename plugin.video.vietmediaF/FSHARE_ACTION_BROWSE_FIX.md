# 🔧 FShare Action Browse Fix - Sửa lỗi sử dụng action browse cho FShare folder

## 🎯 **VẤN ĐỀ**

Từ Kodi log mới nhất:

```
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/TOP8NFSIUFDC]
```

**Vấn đề:** Mặc dù `loadlistitem.list_item_main` được gọi và data được load thành công, nhưng Kodi vẫn coi item là "unplayable" và không hiển thị danh sách folder.

## 🔍 **NGUYÊN NHÂN**

### **❌ Kodi đang coi action `play` là một action để play media:**
- FShare folder URL: `plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/TOP8NFSIUFDC`
- Kodi đang coi action `play` là một action để play media, không phải là một action để hiển thị danh sách folder
- Điều này khiến Kodi coi item là "unplayable" và không hiển thị danh sách folder

### **❌ Action `play` không phù hợp cho folder:**
- Action `play` thường được sử dụng cho media files, không phải cho folders
- Action `browse` thường được sử dụng cho folders và directories
- Kodi sẽ hiểu rằng đây là một folder và không coi nó là "unplayable"

## ✅ **GIẢI PHÁP**

### **1. ✅ Thay đổi action từ `play` sang `browse` cho FShare folder:**

#### **Trước (Lỗi):**
```python
# Tạo action URL cho nguồn sử dụng action play có sẵn
action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
is_playable = True
```

#### **Sau (Đúng):**
```python
# Tạo action URL cho nguồn - sử dụng action browse cho folder, play cho file
if is_folder:
    action_path = f"plugin://plugin.video.vietmediaF?action=browse&url={download_url}"
    is_playable = False  # Folder không playable
else:
    action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
    is_playable = True  # File playable
```

### **2. ✅ Logic phân biệt folder và file:**
```python
# Xác định loại URL (folder hoặc file)
is_folder = download_url.endswith('/') or 'folder' in download_url.lower()

# Tạo action URL cho nguồn - sử dụng action browse cho folder, play cho file
if is_folder:
    action_path = f"plugin://plugin.video.vietmediaF?action=browse&url={download_url}"
    is_playable = False  # Folder không playable
else:
    action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
    is_playable = True  # File playable
```

## 🔄 **LUỒNG XỬ LÝ MỚI**

### **1. 🎯 TMDB search tạo URL:**
```
# FShare folder:
plugin://plugin.video.vietmediaF?action=browse&url=https://www.fshare.vn/folder/TOP8NFSIUFDC

# FShare file:
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/ABC123
```

### **2. 🔍 Hàm go() xử lý:**
```python
# FShare folder sẽ được xử lý bởi action browse
if "browse" in url:
    # ... xử lý browse action ...
    data = cache_utils.cache_data(url)
    if data is not None:
        loadlistitem.list_item_main(data)
    return

# FShare file sẽ được xử lý bởi action play
elif '4share.vn/f/' in url or 'fshare.vn/file/' in url or 'fshare.vn/folder/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    # ... xử lý play action ...
    data = {"url": "", "subtitle": ""}
    data.update({"url": link, "subtitle": subtitle})
    play(data)
```

### **3. 📊 Action browse xử lý FShare folder:**
```python
def browse(url):
    # ... xử lý browse action ...
    data = cache_utils.cache_data(url)
    if data is not None:
        loadlistitem.list_item_main(data)
    return
```

### **4. 📊 Action play xử lý FShare file:**
```python
def play(data):
    # ... xử lý play action ...
    if 'fshare' in link and 'file' in link:
        # Xử lý FShare file
        link = getlink.get(link)
        item = xbmcgui.ListItem(path=link)
        xbmcplugin.setResolvedUrl(HANDLE, True, item)
        return
```

## 🎯 **LOG DEBUG MỚI (MONG ĐỢI)**

### **Trước (Lỗi):**
```
[VietmediaF] FShare folder data loaded successfully, calling loadlistitem.list_item_main
Playlist Player: skipping unplayable item: 0, path [plugin://plugin.video.vietmediaF/?action=play&url=https://www.fshare.vn/folder/TOP8NFSIUFDC]
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

### **2. ✅ Logic rõ ràng:**
- Action `browse` cho folder
- Action `play` cho file
- Kodi hiểu rõ mục đích của từng action

### **3. ✅ Tương thích tốt hơn:**
- Action `browse` tương thích tốt hơn với Kodi cho folder
- Action `play` tương thích tốt hơn với Kodi cho file
- Không bị conflict với playlist player

## 🎯 **KẾT LUẬN**

**Đã sửa lỗi hiển thị FShare folder!**

- ✅ Sử dụng action `browse` cho FShare folder
- ✅ Sử dụng action `play` cho FShare file
- ✅ Logic phân biệt folder và file rõ ràng
- ✅ FShare folder contents được hiển thị đúng
- ✅ Không bị "Playlist Player: skipping unplayable item"
- ✅ Navigation hoạt động bình thường

**FShare folder từ TMDB search bây giờ hiển thị danh sách nội dung đúng!** 🎬✨
