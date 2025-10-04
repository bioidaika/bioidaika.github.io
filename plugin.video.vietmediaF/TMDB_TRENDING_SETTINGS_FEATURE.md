# TMDB Trending Settings Feature

## 🎯 **Tính năng mới:**

Thêm setting để người dùng chọn số lượng phim trending muốn lấy từ TMDB API.

## ⚙️ **Cấu hình Settings:**

### **Dropdown Menu:**
- **20 phim** (mặc định) - 1 trang API
- **40 phim** - 2 trang API  
- **60 phim** - 3 trang API
- **80 phim** - 4 trang API
- **100 phim** - 5 trang API

### **Vị trí Setting:**
```
Settings → Bioidaika → TMDB API Configuration → Số lượng phim trending
```

## 🔧 **Thay đổi Code:**

### **1. Settings XML:**
```xml
<setting id="tmdb_trending_count" type="select" label="Số lượng phim trending" values="20|40|60|80|100" default="20"/>
```

### **2. Helper Function:**
```python
def get_tmdb_trending_count():
    """Lấy số lượng phim trending từ settings"""
    try:
        return int(ADDON.getSetting('tmdb_trending_count') or "20")
    except (ValueError, TypeError):
        return 20
```

### **3. Multiple Pages Function:**
```python
def get_trending_movies_multiple_pages(time_window="day"):
    """
    Lấy danh sách phim trending từ TMDB API (nhiều trang theo setting)
    """
    # Lấy số lượng phim muốn lấy từ settings
    target_count = get_tmdb_trending_count()
    
    # Tính số trang cần gọi (mỗi trang 20 phim)
    pages_needed = (target_count + 19) // 20  # Làm tròn lên
    
    all_movies = []
    for page in range(1, pages_needed + 1):
        page_data = get_trending_movies(time_window, page)
        if page_data:
            movies = page_data.get('results', [])
            all_movies.extend(movies)
            
            # Dừng khi đủ số lượng
            if len(all_movies) >= target_count:
                all_movies = all_movies[:target_count]
                break
    
    return {
        'page': 1,
        'results': all_movies,
        'total_pages': total_pages,
        'total_results': total_results
    }
```

### **4. Updated Show Function:**
```python
def show_trending_movies(time_window="day", page=1):
    """
    Hiển thị danh sách phim trending (sử dụng setting để lấy nhiều trang)
    """
    # Lấy số lượng phim từ setting
    target_count = get_tmdb_trending_count()
    notify(f"Đang tải {target_count} phim trending ({time_window})...")
    
    # Lấy dữ liệu trending movies (nhiều trang)
    movies_data = get_trending_movies_multiple_pages(time_window)
    
    # Hiển thị kết quả
    display_trending_results_simple(filtered_movies, time_window)
```

## 📊 **Logic Hoạt Động:**

### **Tính toán số trang:**
- **20 phim** → 1 trang (20 ÷ 20 = 1)
- **40 phim** → 2 trang (40 ÷ 20 = 2)  
- **60 phim** → 3 trang (60 ÷ 20 = 3)
- **80 phim** → 4 trang (80 ÷ 20 = 4)
- **100 phim** → 5 trang (100 ÷ 20 = 5)

### **Gọi API tuần tự:**
1. Gọi trang 1 → lấy 20 phim
2. Gọi trang 2 → lấy 20 phim (nếu cần)
3. Gọi trang 3 → lấy 20 phim (nếu cần)
4. ... tiếp tục cho đến khi đủ số lượng

### **Tối ưu hóa:**
- Dừng sớm khi đủ số lượng phim
- Kiểm tra tổng số trang có sẵn
- Cắt bớt nếu lấy thừa phim

## 🎮 **Cách sử dụng:**

1. **Mở Settings:**
   - Vào addon VietmediaF
   - Chọn "Settings" hoặc "Cài đặt"

2. **Cấu hình số lượng:**
   - Vào "Bioidaika" → "TMDB API Configuration"
   - Chọn "Số lượng phim trending"
   - Chọn 20/40/60/80/100 phim

3. **Sử dụng:**
   - Vào "Tìm kiếm" → "Phim Trending TMDB"
   - Addon sẽ tự động lấy đúng số lượng phim đã cấu hình

## 📁 **Files được sửa:**

- `resources/settings.xml` - Thêm setting dropdown
- `resources/tmdb_search.py` - Thêm logic gọi nhiều trang API

## ✨ **Lợi ích:**

- ✅ **Linh hoạt:** Người dùng chọn số lượng phim phù hợp
- ✅ **Hiệu quả:** Chỉ gọi API khi cần thiết
- ✅ **Tối ưu:** Dừng sớm khi đủ phim
- ✅ **Dễ sử dụng:** Dropdown menu trực quan
- ✅ **Tương thích:** Không ảnh hưởng code cũ

Tính năng đã hoàn thành! 🎉
