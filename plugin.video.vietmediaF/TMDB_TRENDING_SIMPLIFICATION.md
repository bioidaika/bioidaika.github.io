# TMDB Trending Simplification

## 🎯 **Cải tiến:**

Loại bỏ time_window override và setting để đơn giản hóa hệ thống.

## ✨ **Thay đổi:**

### **1. Xóa Setting:**
- ❌ `tmdb_trending_time_window` - "Khoảng thời gian trending"

### **2. Xóa Function:**
- ❌ `get_tmdb_trending_time_window()` - Lấy time_window từ setting

### **3. Cập nhật Function:**
- ✅ `show_trending_unified()` - Hardcode `time_window="day"`

### **4. Cập nhật Action Handler:**
- ✅ Xóa parameter `time_window` khỏi action handler

## 🔧 **Code Changes:**

### **1. Settings (settings.xml):**

```xml
<!-- REMOVED -->
<setting id="tmdb_trending_time_window" type="select" label="Khoảng thời gian trending" values="day|week" default="day"/>
```

### **2. Function (tmdb_search.py):**

```python
# REMOVED
def get_tmdb_trending_time_window():
    """Lấy khoảng thời gian trending từ settings"""
    # ... removed

# UPDATED
def show_trending_unified(media_type="movies", page=1):
    """Hiển thị danh sách trending thống nhất (Movies hoặc TV)"""
    try:
        # Hardcode time_window = "day"
        time_window = "day"
        # ... rest of function
```

### **3. Action Handler (default.py):**

```python
# UPDATED
if "tmdb_trending" in url:
    media_type = args.get('type', ['movies'])[0] if args.get('type') else 'movies'
    page = int(args.get('page', ['1'])[0]) if args.get('page') else 1
    tmdb_search.show_trending_unified(media_type, page)
    # time_window parameter removed
```

## 📊 **So sánh trước và sau:**

| Tính năng | Trước | Sau |
|-----------|-------|-----|
| **Settings** | 2 settings | 1 setting |
| **Functions** | 4 functions | 3 functions |
| **Parameters** | type, time_window, page | type, page |
| **Time Window** | Configurable | Hardcoded "day" |
| **Complexity** | Phức tạp | Đơn giản |

## 🎮 **Cách sử dụng:**

### **1. Settings:**
- Chỉ còn **"Số lượng phim trending"**: 20|40|60|80|100

### **2. Menu Items:**
- **"Phim Trending TMDB"** → Movies trending (day)
- **"TV Trending TMDB"** → TV trending (day)

### **3. URL Examples:**
```
# Movies trending (day)
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=movies

# TV trending (day)
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=tv
```

## 🎯 **Kết quả:**

- ✅ **Đơn giản hơn:** Ít settings, ít parameters
- ✅ **Dễ sử dụng:** Không cần cấu hình time_window
- ✅ **Ổn định hơn:** Hardcode "day" - ít lỗi
- ✅ **Gọn gàng hơn:** Code ngắn gọn hơn

## 📁 **Files được sửa:**

- `resources/settings.xml` - Xóa setting
- `resources/tmdb_search.py` - Xóa function, cập nhật function
- `default.py` - Cập nhật action handler

## 🔄 **Backward Compatibility:**

- ✅ Các action cũ vẫn hoạt động
- ✅ Menu items vẫn hiển thị
- ✅ Chỉ thay đổi internal logic

Tính năng Trending đã được đơn giản hóa! 🎉
