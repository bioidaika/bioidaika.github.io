# TMDB Trending API Fix

## 🐛 **Lỗi gặp phải:**

```
TMDB API error: 400 - {"success":false,"status_code":5,"status_message":"Invalid parameters: Your request parameters are incorrect."}
```

## 🔍 **Nguyên nhân:**

TMDB API endpoint `/trending/movie/{time_window}` không chấp nhận parameter `language` trong một số trường hợp, đặc biệt khi `language` là `en-US` (default).

## ✅ **Giải pháp:**

Chỉ thêm parameter `language` khi cần thiết (không phải default):

### **Code cũ (gây lỗi):**
```python
params = {
    'api_key': api_key,
    'page': page,
    'language': get_tmdb_language()  # ← Luôn thêm language
}
```

### **Code mới (an toàn):**
```python
params = {
    'api_key': api_key,
    'page': page
}

# Chỉ thêm language nếu không phải default
language = get_tmdb_language()
if language and language != 'en-US':
    params['language'] = language
```

## 🎯 **Kết quả:**

- ✅ TMDB API trending endpoint hoạt động bình thường
- ✅ Không gửi parameter `language` không cần thiết
- ✅ Action `tmdb_trending_movies` hiển thị kết quả đúng

## 📁 **File được sửa:**

- `resources/tmdb_search.py` - Function `get_trending_movies()` (dòng 1756-1764)

## 🔧 **Cách test:**

1. Mở addon VietmediaF
2. Vào menu "Tìm kiếm" → "Phim Trending TMDB"
3. Kiểm tra danh sách phim trending hiển thị

Lỗi đã được sửa thành công! 🎉
