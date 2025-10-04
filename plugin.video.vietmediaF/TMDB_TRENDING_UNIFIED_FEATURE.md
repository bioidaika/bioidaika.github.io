# TMDB Trending Unified Feature

## 🎯 **Cải tiến mới:**

1. **Thêm setting cho time_window (day/week)**
2. **Gộp 2 action thành 1 action chung với parameter**

## ✨ **Tính năng mới:**

### **1. Setting mới:**
- `tmdb_trending_time_window` - "Khoảng thời gian trending" (day|week)

### **2. Action thống nhất:**
- `tmdb_trending` - Action chung cho cả Movies và TV
- Parameter `type` - "movies" hoặc "tv"
- Parameter `time_window` - "day" hoặc "week" (tùy chọn, mặc định dùng setting)

### **3. Functions mới:**
- `get_tmdb_trending_time_window()` - Lấy time_window từ setting
- `show_trending_unified()` - Function thống nhất
- `display_trending_unified_results()` - Display thống nhất

## 🔧 **Code Implementation:**

### **1. Setting mới (settings.xml):**

```xml
<setting id="tmdb_trending_time_window" type="select" label="Khoảng thời gian trending" values="day|week" default="day"/>
```

### **2. Function mới (tmdb_search.py):**

```python
def get_tmdb_trending_time_window():
    """Lấy khoảng thời gian trending từ settings"""
    time_window = ADDON.getSetting('tmdb_trending_time_window')
    if not time_window or time_window not in ['day', 'week']:
        time_window = 'day'
    return time_window

def show_trending_unified(media_type="movies", time_window=None, page=1):
    """Hiển thị danh sách trending thống nhất (Movies hoặc TV)"""
    if time_window is None:
        time_window = get_tmdb_trending_time_window()
    
    if media_type == "movies":
        data = get_trending_movies_multiple_pages(time_window)
    else:
        data = get_trending_tv_multiple_pages(time_window)
    
    # ... display logic
```

### **3. Action Handler mới (default.py):**

```python
if "tmdb_trending" in url:
    media_type = args.get('type', ['movies'])[0] if args.get('type') else 'movies'
    time_window = args.get('time_window', [None])[0] if args.get('time_window') else None
    page = int(args.get('page', ['1'])[0]) if args.get('page') else 1
    tmdb_search.show_trending_unified(media_type, time_window, page)
```

### **4. Menu Items cập nhật (default.py):**

```python
{
    "label": "[COLOR yellow]Phim Trending TMDB[/COLOR]",
    "path": "plugin://plugin.video.vietmediaF?action=tmdb_trending&type=movies",
    "plot": "Phim trending từ TMDB API (theo setting)"
},
{
    "label": "[COLOR yellow]TV Trending TMDB[/COLOR]",
    "path": "plugin://plugin.video.vietmediaF?action=tmdb_trending&type=tv",
    "plot": "TV series trending từ TMDB API (theo setting)"
}
```

## 📊 **So sánh trước và sau:**

| Tính năng | Trước | Sau |
|-----------|-------|-----|
| **Actions** | `tmdb_trending_movies`, `tmdb_trending_tv` | `tmdb_trending` (chung) |
| **Time Window** | Hardcode trong URL | Setting + URL parameter |
| **Functions** | Riêng biệt | Thống nhất |
| **Settings** | 1 setting | 2 settings |
| **URL** | 2 URL khác nhau | 1 URL với parameter |

## 🎮 **Cách sử dụng:**

### **1. Cấu hình Settings:**
- Vào **Settings → Bioidaika**
- **"Số lượng phim trending"**: 20|40|60|80|100
- **"Khoảng thời gian trending"**: day|week

### **2. Sử dụng Menu:**
- **"Phim Trending TMDB"** → Movies trending theo setting
- **"TV Trending TMDB"** → TV trending theo setting

### **3. URL Parameters:**

#### **Movies Trending:**
```
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=movies
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=movies&time_window=week
```

#### **TV Trending:**
```
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=tv
plugin://plugin.video.vietmediaF?action=tmdb_trending&type=tv&time_window=week
```

## 🔄 **Backward Compatibility:**

- ✅ Các action cũ vẫn hoạt động
- ✅ Menu items cũ vẫn hiển thị
- ✅ Không ảnh hưởng đến functionality hiện tại

## 📁 **Files được sửa:**

- `resources/settings.xml` - Thêm setting mới
- `resources/tmdb_search.py` - Thêm 3 functions mới
- `default.py` - Thêm action handler mới, cập nhật menu

## 🎯 **Kết quả:**

- ✅ **Gọn gàng hơn:** 1 action thay vì 2
- ✅ **Linh hoạt hơn:** Có thể override time_window qua URL
- ✅ **Dễ cấu hình:** Time window trong settings
- ✅ **Tương thích ngược:** Không ảnh hưởng code cũ

Tính năng Trending Unified đã hoàn thành! 🎉
