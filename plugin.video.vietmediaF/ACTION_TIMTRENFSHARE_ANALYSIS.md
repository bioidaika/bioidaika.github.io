# Phân Tích Action `_timtrenfshare_`

## 📋 **THÔNG TIN ACTION:**

### **🔗 URL Action:**
```
plugin://plugin.video.vietmediaF?action=_timtrenfshare_
```

### **📍 Vị trí code:**
- **File:** `default.py`
- **Dòng:** 1983-1986

## 🔍 **PHÂN TÍCH LUỒNG XỬ LÝ:**

### **1. 🎯 Entry Point (default.py:1983-1986):**
```python
if "_timtrenfshare_" in url:
    search_content('fshare')
    exit()
```

### **2. 🔄 Hàm `search_content` (default.py:425-465):**
```python
def search_content(search_type, query=None):
    if search_type == 'fshare':
        if query:
            data = search.searchvmf(query)
            save_search_history(query)
            loadlistitem.list_item_main(data)
        else:
            FshareSearchQuery()
            return
```

**Khi không có query → Gọi `FshareSearchQuery()`**

### **3. 🔍 Hàm `FshareSearchQuery` (default.py:774-825):**

#### **3.1. Lấy lịch sử tìm kiếm:**
```python
history = get_search_history()
```

#### **3.2. Xử lý input người dùng:**
- **Nếu không có lịch sử:** Hiển thị keyboard để nhập từ khóa
- **Nếu có lịch sử:** Hiển thị dialog với các tùy chọn:
  - `[Nhập từ khóa mới]`
  - `[Xóa lịch sử tìm kiếm]`
  - Các từ khóa đã tìm kiếm trước đó

#### **3.3. Lưu từ khóa và tìm kiếm:**
```python
save_search_history(query)
data = search.searchvmf(query)
loadlistitem.list_item_search_history(data)
```

### **4. 🌐 Hàm `search.searchvmf` (search.py:35-120):**

#### **4.1. Chuẩn bị query:**
```python
query = query.replace("\n", "").replace(".", " ")
query = urllib.parse.unquote(query)
```

#### **4.2. Gọi API FShare:**
```python
url = "https://fshare.vip/s.php?keyword=" + query
r = urlquick.get(url, headers=headers, max_age = 60*60, timeout=20)
```

#### **4.3. Xử lý kết quả:**
- **Nếu có dữ liệu:** Tạo danh sách items từ API response
- **Nếu không có dữ liệu:** Gọi `timfshare(query)` làm fallback

#### **4.4. Tạo action cho mỗi item:**
```python
link = f'plugin://plugin.video.vietmediaF?action=play&url={furl}'
playable = type_f != 0  # 0 = folder, 1 = file
```

#### **4.5. Thêm item "More on timfshare.com":**
```python
item_timfshare = {
    'label': '[COLOR yellow][I]More on timfshare.com[/I][/COLOR]',
    'is_playable': False,
    'path': 'plugin://plugin.video.vietmediaF?action=__TIMFSHARE__&ref=ref&keyword='+query,
    'thumbnail': 'https://i.imgur.com/F5582QW.png',
    'icon': 'https://i.imgur.com/F5582QW.png',
    'label2': '',
    'info': {'plot': 'Tìm kiếm thêm trên timfshare.com', 'size': ''},
    'art': {"fanart": ""}
}
```

### **5. 🔄 Action `__TIMFSHARE__` (default.py:2000-2054):**

#### **5.1. Xử lý query:**
- **Nếu có keyword trong URL:** Sử dụng keyword đó
- **Nếu không có:** Hiển thị dialog chọn từ lịch sử hoặc nhập mới

#### **5.2. Gọi `search.timfshare`:**
```python
data = search.timfshare(query)
loadlistitem.list_item_main(data)
```

### **6. 🌐 Hàm `search.timfshare` (search.py:131-180):**

#### **6.1. Gọi API timfshare.com:**
```python
api_timfshare = 'https://api.timfshare.com/v1/string-query-search?query='
headers = {
    'user-agent': "Mozilla/5.0...",
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
}
response = requests.post(api_timfshare + query, headers=headers, timeout=10)
```

#### **6.2. Tạo action cho mỗi item:**
```python
link = f'plugin://plugin.video.vietmediaF?action=play&url={furl}'
playable = type_f != '0'  # '0' = folder, khác = file
```

## 🎯 **CÁC ACTION ĐƯỢC GỌI:**

### **1. 🔄 Action `play`:**
- **Mục đích:** Phát file hoặc hiển thị folder FShare
- **URL:** `plugin://plugin.video.vietmediaF?action=play&url={furl}`
- **Được gọi từ:** `searchvmf()` và `timfshare()`

### **2. 🔄 Action `__TIMFSHARE__`:**
- **Mục đích:** Tìm kiếm thêm trên timfshare.com
- **URL:** `plugin://plugin.video.vietmediaF?action=__TIMFSHARE__&ref=ref&keyword={query}`
- **Được gọi từ:** `searchvmf()` (item "More on timfshare.com")

## 📊 **TÓM TẮT LUỒNG HOẠT ĐỘNG:**

```
_timtrenfshare_ 
    ↓
search_content('fshare')
    ↓
FshareSearchQuery() [nếu không có query]
    ↓
search.searchvmf(query)
    ↓
API: https://fshare.vip/s.php?keyword={query}
    ↓
Tạo danh sách items với action=play
    ↓
Thêm item "More on timfshare.com" với action=__TIMFSHARE__
    ↓
loadlistitem.list_item_search_history(data)
```

**Nếu không có kết quả từ FShare API:**
```
searchvmf() 
    ↓
timfshare(query) [fallback]
    ↓
API: https://api.timfshare.com/v1/string-query-search?query={query}
    ↓
Tạo danh sách items với action=play
```

## 🎉 **KẾT LUẬN:**

**Action `_timtrenfshare_` là chức năng tìm kiếm FShare chính của addon, bao gồm:**

1. ✅ **Giao diện tìm kiếm** với lịch sử
2. ✅ **API FShare chính** (fshare.vip)
3. ✅ **API fallback** (timfshare.com)
4. ✅ **Tích hợp action `play`** cho file/folder
5. ✅ **Tích hợp action `__TIMFSHARE__`** cho tìm kiếm mở rộng

**Đây là một hệ thống tìm kiếm FShare hoàn chỉnh và linh hoạt!** 🚀✨
