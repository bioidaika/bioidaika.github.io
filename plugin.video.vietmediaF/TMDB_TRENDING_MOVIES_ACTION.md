# TMDB Trending Movies Action

## 📋 Tổng quan

Action `tmdb_trending_movies` cho phép hiển thị danh sách phim trending từ TMDB API.

## 🔧 Cách sử dụng

### **URL Action:**
```
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=day
```

### **Tham số:**
- `time_window` (optional): Khoảng thời gian trending
  - `day` (mặc định): Trending theo ngày
  - `week`: Trending theo tuần

### **Ví dụ:**
```
# Trending theo ngày
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=day

# Trending theo tuần  
plugin://plugin.video.vietmediaF?action=tmdb_trending_movies&time_window=week
```

## 🎯 Chức năng

### **1. Lấy dữ liệu từ TMDB API:**
- Endpoint: `/trending/movie/{time_window}`
- Hỗ trợ: `day` và `week`
- Ngôn ngữ: Theo setting addon
- Timeout: Theo setting addon

### **2. Lọc theo Backend Cache:**
- Kiểm tra cache backend cho từng phim
- Chỉ hiển thị phim có trong cache
- Hiển thị cảnh báo nếu backend API lỗi

### **3. Hiển thị kết quả:**
- Sử dụng layout 3 cột
- Thông tin phim đầy đủ
- Poster và fanart từ TMDB
- Click để xem chi tiết và nguồn download

## 📁 Files được sửa đổi

### **1. resources/tmdb_search.py:**
- `get_trending_movies()`: Lấy dữ liệu từ TMDB API
- `show_trending_movies()`: Hiển thị danh sách trending

### **2. default.py:**
- Action handler: `tmdb_trending_movies`
- Menu item trong `timkiemMenu()`

## 🔄 Luồng hoạt động

1. **User click** → Action `tmdb_trending_movies`
2. **Lấy tham số** → `time_window` (mặc định: day)
3. **Gọi TMDB API** → `/trending/movie/{time_window}`
4. **Lọc cache** → Kiểm tra backend cache
5. **Hiển thị** → Danh sách phim trending

## ⚙️ Cấu hình cần thiết

- **TMDB API Key**: Phải được cấu hình trong settings
- **Backend API**: Có thể bật/tắt trong settings
- **Language**: Theo setting addon

## 🎨 Giao diện

- **Menu**: "Phim Trending TMDB" trong Tìm kiếm
- **Layout**: 3 cột (thông tin | poster | label2)
- **Thông báo**: "Đang tải phim trending..."
- **Cache check**: "Đang kiểm tra cache backend..."

## ✅ Hoàn thành

Action `tmdb_trending_movies` đã được implement thành công và sẵn sàng sử dụng!
