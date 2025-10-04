# TMDB Trending API Validation Fix

## 🐛 **Lỗi gặp phải:**

```
TMDB API error: 400 - {"success":false,"status_code":5,"status_message":"Invalid parameters: Your request parameters are incorrect."}
```

## 🔍 **Nguyên nhân:**

TMDB API endpoint `/trending/movie/{time_window}` chỉ chấp nhận `time_window` là `day` hoặc `week`. Nếu giá trị khác được truyền vào sẽ gây lỗi 400.

## ✅ **Giải pháp:**

Thêm validation cho `time_window` parameter để đảm bảo chỉ sử dụng giá trị hợp lệ:

### **Code cũ (gây lỗi):**
```python
url = f"{TMDB_BASE_URL}/trending/movie/{time_window}"
params = {
    'api_key': api_key,
    'page': page
}
```

### **Code mới (an toàn):**
```python
# Validate time_window parameter
if time_window not in ['day', 'week']:
    time_window = 'day'
    
url = f"{TMDB_BASE_URL}/trending/movie/{time_window}"
params = {
    'api_key': api_key,
    'page': page
}
```

## 🎯 **Kết quả:**

- ✅ TMDB API trending endpoint hoạt động bình thường
- ✅ Validation `time_window` parameter
- ✅ Fallback về `day` nếu giá trị không hợp lệ
- ✅ Action `tmdb_trending_movies` hiển thị kết quả đúng

## 📁 **File được sửa:**

- `resources/tmdb_search.py` - Function `get_trending_movies()` (dòng 1755-1758)

## 🔧 **Cách test:**

1. Mở addon VietmediaF
2. Vào menu "Tìm kiếm" → "Phim Trending TMDB"
3. Kiểm tra danh sách phim trending hiển thị

Lỗi đã được sửa thành công! 🎉
