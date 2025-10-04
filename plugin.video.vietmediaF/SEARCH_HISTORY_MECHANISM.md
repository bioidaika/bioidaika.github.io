# Cơ Chế Tạo Và Xóa Lịch Sử Tìm Kiếm

## 📋 **TỔNG QUAN:**

Addon VietmediaF có hệ thống quản lý lịch sử tìm kiếm hoàn chỉnh với 5 loại lịch sử khác nhau, sử dụng class `HistoryManager` để quản lý.

## 🏗️ **KIẾN TRÚC HỆ THỐNG:**

### **1. 📁 Class `HistoryManager` (history_utils.py:18-62):**

```python
class HistoryManager:
    def __init__(self, history_file):
        self.history_file = os.path.join(PROFILE_PATH, history_file)
        self.max_history_size = 50  # Tối đa 50 mục lịch sử
```

### **2. 📊 Các loại lịch sử được quản lý:**

| Loại lịch sử | File lưu trữ | Mục đích |
|--------------|--------------|----------|
| `search_history` | `lstk.dat` | Tìm kiếm FShare chung |
| `fshare_history` | `lstk4s.dat` | Tìm kiếm 4Share |
| `hdvn_history` | `hdvnsearch.dat` | Tìm kiếm HDVietnam |
| `tvcine_history` | `search_history.json` | Tìm kiếm TVCine |
| `watched_history` | `watched.dat` | Lịch sử xem phim |

## 🔧 **CÁC PHƯƠNG THỨC CHÍNH:**

### **1. ✅ Kiểm tra lịch sử (`check_history`):**
```python
def check_history(self):
    """Kiểm tra xem file lịch sử có tồn tại và có dữ liệu không"""
    if not os.path.exists(self.history_file):
        return False
    return os.path.exists(self.history_file) and os.path.getsize(self.history_file) > 0
```

### **2. 📖 Lấy lịch sử (`get_history`):**
```python
def get_history(self):
    """Lấy lịch sử tìm kiếm từ file"""
    try:
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []
```

### **3. 💾 Lưu lịch sử (`save_history`):**
```python
def save_history(self, query):
    """Lưu một query mới vào lịch sử"""
    try:
        history = self.get_history()
        if query not in history:  # Tránh trùng lặp
            history.insert(0, query)  # Thêm vào đầu danh sách
            history = history[:self.max_history_size]  # Giới hạn 50 mục
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(history))
    except Exception as e:
        notify(f"Lỗi khi lưu lịch sử: {str(e)}")
```

### **4. 🗑️ Xóa lịch sử (`delete_history`):**
```python
def delete_history(self):
    """Xóa toàn bộ lịch sử"""
    try:
        if os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write('')
            notify("Đã xoá lịch sử tìm kiếm")
    except Exception as e:
        notify(f"Lỗi khi xóa lịch sử: {str(e)}")
```

## 🎯 **CÁC HÀM WRAPPER (default.py):**

### **1. 🔍 Lịch sử tìm kiếm FShare:**
```python
def check_history():
    return search_history.check_history()

def get_search_history():
    return search_history.get_history()

def save_search_history(query):
    search_history.save_history(query)

def delete_search_history():
    search_history.delete_history()
```

### **2. 🔍 Lịch sử tìm kiếm 4Share:**
```python
def check_fshare_history():
    return fshare_history.check_history()

def get_fshare_history():
    return fshare_history.get_history()

def save_fshare_history(query):
    fshare_history.save_history(query)

def delete_fshare_history():
    fshare_history.delete_history()
```

### **3. 🔍 Lịch sử tìm kiếm HDVietnam:**
```python
def check_hdvn_history():
    return hdvn_history.check_history()

def get_hdvn_history():
    return hdvn_history.get_history()

def save_hdvn_history(query):
    hdvn_history.save_history(query)

def delete_hdvn_history():
    hdvn_history.delete_history()
```

### **4. 🔍 Lịch sử tìm kiếm TVCine:**
```python
def check_tvcine_history():
    return tvcine_history.check_history()

def get_tvcine_history():
    return tvcine_history.get_history()

def save_tvcine_history(query):
    tvcine_history.save_history(query)

def delete_tvcine_history():
    tvcine_history.delete_history()
```

### **5. 👁️ Lịch sử xem phim:**
```python
def check_watched_history():
    return watched_history.check_history()

def get_watched_history():
    return watched_history.get_history()

def save_watched_history(name, link, size):
    entry = f"{name},{link},{size}"
    watched_history.save_history(entry)

def delete_watched_history():
    watched_history.delete_history()
```

## 🔄 **LUỒNG HOẠT ĐỘNG:**

### **1. 💾 Tạo lịch sử tìm kiếm:**

#### **A. Trong `FshareSearchQuery` (default.py:817):**
```python
save_search_history(query)
```

#### **B. Trong `search_content` (default.py:432):**
```python
if query:
    data = search.searchvmf(query)
    save_search_history(query)
    loadlistitem.list_item_main(data)
```

### **2. 🗑️ Xóa lịch sử tìm kiếm:**

#### **A. Từ dialog tìm kiếm (default.py:808-812):**
```python
elif selected == 1:
    confirm = dialog.yesno("Xác nhận", "Bạn có chắc chắn muốn xóa lịch sử tìm kiếm không?")
    if confirm:
        delete_search_history()
        xbmc.executebuiltin("Container.Refresh")
    return
```

#### **B. Từ action `__removeAllSearchHistory__` (default.py:2135-2138):**
```python
if '__removeAllSearchHistory__' in url:
    delete_search_history()
    xbmc.executebuiltin("Container.Refresh")
    exit()
```

#### **C. Từ action `__removeAllSearchHistory4share__` (default.py:2139-2142):**
```python
if "__removeAllSearchHistory4share__" in url:
    delete_fshare_history()
    xbmc.executebuiltin("Container.Refresh")
    exit()
```

## 📁 **CẤU TRÚC FILE LỊCH SỬ:**

### **1. 📄 File text đơn giản:**
```
query1
query2
query3
...
```

### **2. 📄 File JSON (TVCine):**
```json
["query1", "query2", "query3"]
```

### **3. 📄 File CSV (Watched History):**
```
name1,link1,size1
name2,link2,size2
name3,link3,size3
```

## ⚙️ **TÍNH NĂNG ĐẶC BIỆT:**

### **1. ✅ Tránh trùng lặp:**
```python
if query not in history:
    history.insert(0, query)
```

### **2. ✅ Giới hạn kích thước:**
```python
history = history[:self.max_history_size]  # Tối đa 50 mục
```

### **3. ✅ Thứ tự ưu tiên:**
```python
history.insert(0, query)  # Mới nhất ở đầu danh sách
```

### **4. ✅ Xử lý lỗi:**
```python
try:
    # Thao tác với file
except Exception as e:
    notify(f"Lỗi khi lưu lịch sử: {str(e)}")
```

## 🎯 **CÁC ACTION XÓA LỊCH SỬ:**

### **1. 🔄 Action `__removeAllSearchHistory__`:**
- **Mục đích:** Xóa lịch sử tìm kiếm FShare
- **URL:** `plugin://plugin.video.vietmediaF?action=__removeAllSearchHistory__`

### **2. 🔄 Action `__removeAllSearchHistory4share__`:**
- **Mục đích:** Xóa lịch sử tìm kiếm 4Share
- **URL:** `plugin://plugin.video.vietmediaF?action=__removeAllSearchHistory4share__`

## 🎉 **KẾT LUẬN:**

**Hệ thống lịch sử tìm kiếm của addon VietmediaF bao gồm:**

1. ✅ **5 loại lịch sử** khác nhau
2. ✅ **Class `HistoryManager`** quản lý tập trung
3. ✅ **Tránh trùng lặp** và giới hạn kích thước
4. ✅ **Xử lý lỗi** robust
5. ✅ **Giao diện người dùng** thân thiện
6. ✅ **Action xóa** linh hoạt

**Đây là một hệ thống quản lý lịch sử hoàn chỉnh và hiệu quả!** 🚀✨
