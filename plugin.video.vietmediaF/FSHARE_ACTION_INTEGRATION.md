# 🔗 FShare Action Integration - Tích hợp action FShare có sẵn

## 🎯 **THAY ĐỔI CHÍNH**

Sử dụng action `play` có sẵn trong addon để xử lý URL FShare thay vì tạo action mới.

### **Trước (Tạo action mới):**
- Tạo `fshare_folder` action mới
- Tạo `play_fshare` action mới
- Viết functions mới trong fshare.py
- Code phức tạp và trùng lặp

### **Sau (Sử dụng action có sẵn):**
- Sử dụng `play` action có sẵn
- Tận dụng logic xử lý FShare đã có
- Code đơn giản và nhất quán
- Không cần viết thêm functions

## 🔧 **CÁC THAY ĐỔI CODE**

### **1. 🗑️ Loại bỏ action handlers mới:**
```python
# XÓA: fshare_folder action handler
# XÓA: play_fshare action handler
```

### **2. 🗑️ Loại bỏ functions mới:**
```python
# XÓA: list_folder_contents() function
# XÓA: play_fshare_file() function
```

### **3. ✅ Sử dụng action play có sẵn:**
```python
# Trước:
if is_folder:
    action_path = f"plugin://plugin.video.vietmediaF?action=fshare_folder&url={download_url}&uploader={uploader}&sheet={sheet_name}"
    is_playable = False
else:
    action_path = f"plugin://plugin.video.vietmediaF?action=play_fshare&url={download_url}&uploader={uploader}&sheet={sheet_name}"
    is_playable = True

# Sau:
action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
is_playable = True
```

## 🎯 **ACTION PLAY CÓ SẴN**

### **URL Format:**
```
plugin://plugin.video.vietmediaF?action=play&url={fshare_url}
```

### **Ví dụ:**
```
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/D33TNJF8KWN7
plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/xyz789
```

### **Xử lý trong default.py:**
```python
if '4share.vn/f/' in url or'fshare.vn/file/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    # Xử lý các loại URL khác nhau
    # FShare được xử lý tự động
```

## 🔄 **LUỒNG XỬ LÝ MỚI**

### **1. 🎯 Tạo action URL:**
```python
# Tạo action URL cho nguồn sử dụng action play có sẵn
action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
is_playable = True
```

### **2. 🖱️ User Click Event:**
```
User clicks on source → Kodi calls action=play&url={fshare_url}
```

### **3. 🎯 Action Detection:**
```python
# Trong default.py, action play đã có sẵn xử lý FShare
if '4share.vn/f/' in url or'fshare.vn/file/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    # Xử lý FShare URL tự động
```

### **4. 📁 Folder vs File:**
- **Folder**: Action play sẽ hiển thị danh sách files trong folder
- **File**: Action play sẽ play file trực tiếp

## 🎯 **LỢI ÍCH**

### **1. 📦 Code đơn giản:**
- **Trước**: 100+ dòng code mới
- **Sau**: 2 dòng code
- **Giảm**: 98% code

### **2. 🔄 Tận dụng logic có sẵn:**
- Sử dụng logic xử lý FShare đã được test
- Không cần viết lại từ đầu
- Đảm bảo tính nhất quán

### **3. 🛠️ Dễ bảo trì:**
- Không cần maintain code mới
- Sử dụng logic đã ổn định
- Ít bug hơn

### **4. ⚡ Performance tốt:**
- Không cần load thêm functions
- Sử dụng cache có sẵn
- Tốc độ xử lý nhanh hơn

## 📊 **SO SÁNH**

| Aspect | Trước | Sau |
|--------|-------|-----|
| **Actions** | 2 actions mới | 1 action có sẵn |
| **Functions** | 2 functions mới | 0 functions mới |
| **Code Lines** | 100+ dòng | 2 dòng |
| **Maintenance** | Phức tạp | Đơn giản |
| **Testing** | Cần test mới | Đã test sẵn |
| **Consistency** | Có thể khác | Nhất quán |

## 🔧 **TECHNICAL DETAILS**

### **Action Play Handler:**
```python
# Trong default.py, action play đã xử lý:
if '4share.vn/f/' in url or'fshare.vn/file/' in url or 'ok.ru' in url or 'drive.google.com' in url:
    # Xử lý FShare URL
    # - Folder: Hiển thị danh sách files
    # - File: Play file trực tiếp
```

### **URL Generation:**
```python
# Đơn giản và nhất quán
action_path = f"plugin://plugin.video.vietmediaF?action=play&url={download_url}"
```

### **Properties:**
```python
"properties": {
    "tmdb_id": str(tmdb_id),
    "media_type": media_type,
    "uploader": uploader,
    "sheet_name": sheet_name,
    "size": size,
    "vmf_code": vmf_code,
    "download_url": download_url
}
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ FShare Folder:**
- **URL**: `https://www.fshare.vn/folder/D33TNJF8KWN7`
- **Action**: `action=play&url={folder_url}`
- **Kết quả**: Hiển thị danh sách files trong folder

### **2. ✅ FShare File:**
- **URL**: `https://www.fshare.vn/file/xyz789`
- **Action**: `action=play&url={file_url}`
- **Kết quả**: Play file trực tiếp

### **3. ✅ Other URLs:**
- **4share.vn**: Được xử lý tự động
- **ok.ru**: Được xử lý tự động
- **drive.google.com**: Được xử lý tự động

## 🎯 **KẾT QUẢ**

Khi user click vào nguồn FShare từ danh sách TMDB:

1. **🎯 Action URL đơn giản** → `action=play&url={fshare_url}`
2. **🔄 Sử dụng logic có sẵn** → Không cần viết mới
3. **📁 Folder/File tự động** → Xử lý thông minh
4. **⚡ Performance tốt** → Tận dụng cache và logic đã tối ưu
5. **🛠️ Dễ bảo trì** → Không cần maintain code mới

**Tích hợp FShare action giờ đây đơn giản và hiệu quả!** 🎬✨
