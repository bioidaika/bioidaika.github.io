# TMDB Trending Pagination Feature

## 🎯 **Tính năng mới:**

Thêm hỗ trợ phân trang cho action `tmdb_trending_movies` để người dùng có thể xem tất cả kết quả thay vì chỉ 20 phim đầu tiên.

## ✨ **Các tính năng đã thêm:**

### **1. Phân trang cơ bản:**
- Hiển thị thông tin trang hiện tại: "Trang 1/50 (20/1000 phim)"
- Nút "← Trang Trước" (nếu không phải trang đầu)
- Nút "Trang Tiếp (2) →" (nếu không phải trang cuối)

### **2. Chuyển đến trang cụ thể:**
- Nút "Chuyển đến trang..." (nếu có nhiều hơn 2 trang)
- Dialog nhập số trang với validation
- Kiểm tra phạm vi trang hợp lệ (1 đến total_pages)

### **3. URL Parameters:**
- `time_window`: day hoặc week
- `page`: số trang (mặc định là 1)

## 🔧 **Các function đã thêm/sửa:**

### **1. `show_trending_movies(time_window, page)`**
- Thêm parameter `page`
- Gọi `get_trending_movies(time_window, page)`
- Sử dụng `display_trending_results_with_pagination()`

### **2. `display_trending_results_with_pagination(movies_data, time_window, current_page)`**
- Hiển thị thông tin phân trang
- Gọi `display_search_results()` cho kết quả phim
- Thêm các nút phân trang

### **3. `add_pagination_items(time_window, current_page, total_pages)`**
- Tạo nút "Trang Trước"
- Tạo nút "Trang Tiếp"
- Tạo nút "Chuyển đến trang..."

### **4. Action Handler mới: `tmdb_trending_goto_page`**
- Xử lý chuyển đến trang cụ thể
- Dialog nhập số trang
- Validation và chuyển hướng

## 📁 **Files được sửa:**

- `resources/tmdb_search.py`:
  - Cập nhật `show_trending_movies()`
  - Thêm `display_trending_results_with_pagination()`
  - Thêm `add_pagination_items()`

- `default.py`:
  - Cập nhật action handler `tmdb_trending_movies`
  - Thêm action handler `tmdb_trending_goto_page`

## 🎮 **Cách sử dụng:**

1. Mở addon VietmediaF
2. Vào "Tìm kiếm" → "Phim Trending TMDB"
3. Xem danh sách phim trang 1
4. Sử dụng các nút phân trang:
   - **← Trang Trước**: Quay lại trang trước
   - **Trang Tiếp →**: Chuyển đến trang tiếp theo
   - **Chuyển đến trang...**: Nhập số trang cụ thể

## 🔍 **Ví dụ URL:**

```
# Trang 1 (mặc định)
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=day

# Trang 2
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=day&page=2

# Trending theo tuần, trang 5
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=week&page=5
```

## ✅ **Kết quả:**

- ✅ Người dùng có thể xem tất cả phim trending
- ✅ Phân trang mượt mà và trực quan
- ✅ Hỗ trợ chuyển đến trang bất kỳ
- ✅ Thông tin phân trang rõ ràng
- ✅ Validation đầu vào an toàn

Tính năng phân trang đã được thêm thành công! 🎉
