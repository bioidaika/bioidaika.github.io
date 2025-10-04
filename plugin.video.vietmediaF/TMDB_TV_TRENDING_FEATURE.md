# TMDB TV Trending Feature

## 🎯 **Tính năng mới:**

Thêm action trending cho TV series tương tự như movies trending.

## ✨ **Các tính năng:**

### **1. API Functions:**
- `get_trending_tv(time_window, page)` - Lấy 1 trang TV trending
- `get_trending_tv_multiple_pages(time_window)` - Lấy nhiều trang theo setting
- `show_trending_tv(time_window, page)` - Hiển thị TV trending
- `display_trending_tv_results_simple(tv_data, time_window)` - Display đơn giản

### **2. Action Handler:**
- `tmdb_trending_tv` - Xử lý action TV trending
- Hỗ trợ `time_window` (day/week) và `page` parameters

### **3. Menu Item:**
- "TV Trending TMDB" trong menu tìm kiếm
- URL: `plugin://plugin.video.vietmediaF?action=tmdb_trending_tv&time_window=day`

## 🔧 **Code Implementation:**

### **1. API Functions (tmdb_search.py):**

```python
def get_trending_tv(time_window="day", page=1):
    """Lấy danh sách TV trending từ TMDB API (1 trang)"""
    url = f"{TMDB_BASE_URL}/trending/tv/{time_window}"
    # ... API call logic

def get_trending_tv_multiple_pages(time_window="day"):
    """Lấy danh sách TV trending từ TMDB API (nhiều trang theo setting)"""
    target_count = get_tmdb_trending_count()
    pages_needed = (target_count + 19) // 20
    # ... multiple pages logic

def show_trending_tv(time_window="day", page=1):
    """Hiển thị danh sách TV trending (sử dụng setting để lấy nhiều trang)"""
    tv_data = get_trending_tv_multiple_pages(time_window)
    # ... display logic

def display_trending_tv_results_simple(tv_data, time_window):
    """Hiển thị kết quả trending TV đơn giản (không phân trang)"""
    display_search_results(None, tv_data, f"Trending TV Shows ({time_window}) - {count_info}")
```

### **2. Action Handler (default.py):**

```python
if "tmdb_trending_tv" in url:
    xbmc.log(f"[VietmediaF] Calling tmdb_search.show_trending_tv()", xbmc.LOGINFO)
    try:
        time_window = args.get('time_window', ['day'])[0] if args.get('time_window') else 'day'
        page = int(args.get('page', ['1'])[0]) if args.get('page') else 1
        tmdb_search.show_trending_tv(time_window, page)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Error calling show_trending_tv: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi gọi show_trending_tv: {str(e)}")
    exit()
```

### **3. Menu Item (default.py):**

```python
{
    "label": "[COLOR yellow]TV Trending TMDB[/COLOR]",
    "path": "plugin://plugin.video.vietmediaF?action=tmdb_trending_tv&time_window=day",
    "icon": search_icon,
    "plot": "TV series trending theo ngày từ TMDB API"
}
```

## 📊 **Tính năng tương tự Movies:**

| Tính năng | Movies | TV Shows |
|-----------|--------|----------|
| **API Endpoint** | `/trending/movie/{time_window}` | `/trending/tv/{time_window}` |
| **Settings** | Sử dụng `tmdb_trending_count` | Sử dụng `tmdb_trending_count` |
| **Multiple Pages** | ✅ | ✅ |
| **Backend Cache** | ✅ | ✅ |
| **Debug Logs** | ✅ | ✅ |
| **Error Handling** | ✅ | ✅ |

## 🎮 **Cách sử dụng:**

1. **Mở Menu Tìm kiếm:**
   - Vào addon VietmediaF
   - Chọn "Tìm kiếm"

2. **Chọn TV Trending:**
   - Chọn "TV Trending TMDB"
   - Addon sẽ hiển thị TV series trending theo setting

3. **Cấu hình số lượng:**
   - Vào Settings → Bioidaika → "Số lượng phim trending"
   - Setting này áp dụng cho cả Movies và TV Shows

## 🔄 **URL Parameters:**

- `action=tmdb_trending_tv` - Action chính
- `time_window=day` - Khoảng thời gian (day/week)
- `page=1` - Trang (không sử dụng, chỉ để tương thích)

## 📁 **Files được sửa:**

- `resources/tmdb_search.py` - Thêm 4 functions mới
- `default.py` - Thêm action handler và menu item

## 🎯 **Kết quả:**

- ✅ TV Trending TMDB xuất hiện trong menu
- ✅ Hiển thị TV series trending theo setting (20-100)
- ✅ Hỗ trợ backend cache filtering
- ✅ Debug logs đầy đủ
- ✅ Error handling hoàn chỉnh

Tính năng TV Trending đã hoàn thành! 🎉
