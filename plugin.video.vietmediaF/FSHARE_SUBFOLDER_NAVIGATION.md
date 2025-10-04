# 📁 FShare Subfolder Navigation - Điều hướng folder con

## 🎯 **TỔNG QUAN**

FShare folder có thể chứa các folder con bên trong. Addon đã được thiết kế để xử lý việc điều hướng này một cách tự động.

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 User click vào FShare folder:**
```
https://www.fshare.vn/folder/D33TNJF8KWN7
```

### **2. 📁 Hàm fsharegetFolder() xử lý:**
```python
def fsharegetFolder(url):
    # Gọi FShare API để lấy danh sách items
    payload = {
        "token": token,
        "url": url,
        "dirOnly": 0,  # Lấy cả folder và file
        "pageIndex": page_index,
        "limit": 100
    }
    
    # Xử lý response
    for f_item in f_items:
        if f_item["type"] == "0":  # Folder con
            link = f'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/{linkcode}'
            playable = False
        else:  # File
            link = f'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/{linkcode}'
            playable = True
```

### **3. 🎬 User click vào folder con:**
```
https://www.fshare.vn/folder/ABC123XYZ
```

### **4. 🔄 Hàm play() xử lý folder con:**
```python
def play(data):
    link = data["url"]
    
    # Xử lý FShare folder URL (bao gồm folder con)
    if 'fshare' in link and 'folder' in link:
        data = cache_utils.cache_data(link)
        if data is not None:
            loadlistitem.list_item_main(data)  # Hiển thị nội dung folder con
        else:
            notify('Không thể tải danh sách folder')
        return
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. ✅ Folder gốc chứa folder con:**
```
Input:  https://www.fshare.vn/folder/D33TNJF8KWN7
Output: Danh sách items (folder con + files)
```

### **2. ✅ Click vào folder con:**
```
Input:  https://www.fshare.vn/folder/ABC123XYZ
Output: Danh sách items trong folder con
```

### **3. ✅ Click vào file:**
```
Input:  https://www.fshare.vn/file/XYZ789ABC
Output: Phát file trực tiếp
```

### **4. ✅ Folder con chứa folder con khác:**
```
Input:  https://www.fshare.vn/folder/ABC123XYZ
Output: Danh sách items (folder con cấp 2 + files)
```

## 🔧 **CODE CHI TIẾT**

### **File: resources/fshare.py**
```python
def fsharegetFolder(url):
    # ... (setup code) ...
    
    # Gọi FShare API
    payload = json.dumps({
        "token": token,
        "url": url,
        "dirOnly": 0,  # Lấy cả folder và file
        "pageIndex": page_index,
        "limit": 100
    })
    
    r = session.post("https://api.fshare.vn/api/fileops/getFolderList", 
                    headers=headers, data=payload, verify=False)
    
    f_items = json.loads(r.content)
    items = []
    
    for f_item in f_items:
        name = f_item["name"]
        linkcode = f_item["linkcode"]
        size = str(f_item["size"])
        
        # Xác định loại item
        if f_item["type"] == "0":  # Folder con
            link = f'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/folder/{linkcode}'
            playable = False
        else:  # File
            link = f'plugin://plugin.video.vietmediaF?action=play&url=https://www.fshare.vn/file/{linkcode}'
            playable = True
        
        item = {
            "label": name,
            "is_playable": playable,
            "path": link,
            "thumbnail": f_icon,
            "icon": f_icon,
            "label2": name,
            "info": {'plot': name, 'size': size}
        }
        items.append(item)
    
    return {"content_type": "tvshows", "items": items}
```

### **File: default.py**
```python
def play(data):
    link = data["url"]
    
    # Xử lý FShare folder URL (bao gồm folder con)
    if 'fshare' in link and 'folder' in link:
        data = cache_utils.cache_data(link)
        if data is not None:
            loadlistitem.list_item_main(data)
        else:
            notify('Không thể tải danh sách folder')
        return
    
    # Xử lý các loại URL khác...
```

## 🎯 **TÍNH NĂNG**

### **1. 📁 Điều hướng đa cấp:**
- Folder gốc → Folder con → Folder con cấp 2 → ...
- Không giới hạn độ sâu
- Mỗi cấp được cache riêng biệt

### **2. 🔄 Pagination:**
- Mỗi folder hiển thị tối đa 100 items
- Có nút "Trang tiếp" nếu có nhiều hơn 100 items
- Cache theo từng trang

### **3. 💾 Cache thông minh:**
- Cache key: `fshare_folder_{folder_code}_page{page_index}`
- Thời gian cache: 30 phút
- Tự động refresh khi cần

### **4. 🎬 Playable detection:**
- Folder: `playable = False` → Hiển thị danh sách
- File: `playable = True` → Phát trực tiếp

## 🎯 **VÍ DỤ THỰC TẾ**

### **Cấu trúc folder:**
```
📁 Movies/
├── 📁 Action/
│   ├── 📁 2023/
│   │   ├── 🎬 movie1.mp4
│   │   └── 🎬 movie2.mp4
│   └── 🎬 old_movie.mp4
├── 📁 Comedy/
│   └── 🎬 comedy1.mp4
└── 🎬 random_movie.mp4
```

### **Luồng điều hướng:**
1. **Click Movies** → Hiển thị: Action/, Comedy/, random_movie.mp4
2. **Click Action/** → Hiển thị: 2023/, old_movie.mp4
3. **Click 2023/** → Hiển thị: movie1.mp4, movie2.mp4
4. **Click movie1.mp4** → Phát file

## 🎯 **LỢI ÍCH**

### **1. 🔄 Navigation mượt mà:**
- Không cần reload trang
- Cache nhanh chóng
- UI nhất quán

### **2. 📁 Hỗ trợ cấu trúc phức tạp:**
- Folder lồng nhau không giới hạn
- Phân loại tự động (folder vs file)
- Pagination cho folder lớn

### **3. ⚡ Performance tốt:**
- Cache thông minh
- Lazy loading
- Error handling robust

### **4. 🎬 User Experience:**
- Intuitive navigation
- Clear visual distinction
- Consistent behavior

## 🎯 **KẾT LUẬN**

FShare subfolder navigation đã được xử lý hoàn chỉnh:

1. **📁 Folder con được nhận diện** → `type == "0"`
2. **🔄 URL được tạo đúng** → `action=play&url=folder_url`
3. **🎬 Hàm play() xử lý** → Hiển thị nội dung folder con
4. **💾 Cache hoạt động** → Performance tốt
5. **🎯 Navigation vô hạn** → Không giới hạn độ sâu

**Folder con FShare hoạt động hoàn hảo!** 🎬✨
