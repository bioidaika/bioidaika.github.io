# TMDB Search Feature - VietMediaF Addon

## Tổng quan
Tính năng tìm kiếm phim và TV series qua TMDB API đã được tích hợp vào addon VietMediaF.

## Cách sử dụng

### 1. Truy cập tính năng
- Mở addon VietMediaF
- Chọn "Tìm kiếm" từ menu chính
- Chọn "Tìm kiếm TMDB"

### 2. Thực hiện tìm kiếm
- Nhập từ khóa tìm kiếm (tên phim, diễn viên, đạo diễn, v.v.)
- Nhấn OK để bắt đầu tìm kiếm
- Kết quả sẽ hiển thị danh sách phim và TV series

### 3. Kết quả tìm kiếm
- **Phim lẻ**: Hiển thị danh sách phim với poster, năm phát hành, điểm đánh giá
- **Phim bộ**: Hiển thị danh sách TV series với thông tin tương tự
- **Thông tin chi tiết**: Mỗi phim có mô tả, điểm đánh giá, ngày phát hành

## Cấu hình

### API Key TMDB
Để sử dụng tính năng, cần có API key từ TMDB:
1. Đăng ký tài khoản tại https://www.themoviedb.org/
2. Tạo API key từ Settings > API
3. Thay thế `TMDB_API_KEY` trong file `resources/tmdb_search.py`

### Cấu hình hiện tại
```python
TMDB_API_KEY = "8f1b4a2b3c4d5e6f7g8h9i0j1k2l3m4n"  # Thay bằng API key thực tế
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
```

## Cấu trúc dữ liệu

### Response từ TMDB API
```json
{
  "page": 1,
  "results": [
    {
      "id": 123456,
      "title": "Tên phim",
      "overview": "Mô tả phim",
      "poster_path": "/path/to/poster.jpg",
      "backdrop_path": "/path/to/backdrop.jpg",
      "release_date": "2024-01-01",
      "vote_average": 8.5
    }
  ],
  "total_pages": 10,
  "total_results": 200
}
```

### Item hiển thị trên Kodi
```python
{
    "label": "Tên phim (2024)",
    "is_playable": False,
    "path": "plugin://plugin.video.vietmediaF?action=tmdb_movie_detail&tmdb_id=123456&media_type=movie",
    "thumbnail": "https://image.tmdb.org/t/p/w500/poster.jpg",
    "fanart": "https://image.tmdb.org/t/p/w500/backdrop.jpg",
    "info": {
        "plot": "Mô tả chi tiết...",
        "title": "Tên phim",
        "year": 2024,
        "rating": 8.5,
        "mediatype": "movie"
    }
}
```

## Tính năng

### 1. Tìm kiếm đa ngôn ngữ
- Hỗ trợ tìm kiếm bằng tiếng Việt
- Kết quả hiển thị bằng tiếng Việt (nếu có)

### 2. Hiển thị đầy đủ thông tin
- Poster phim chất lượng cao
- Backdrop (hình nền) cho fanart
- Điểm đánh giá TMDB
- Ngày phát hành
- Mô tả chi tiết

### 3. Phân loại kết quả
- Phim lẻ và phim bộ được phân tách rõ ràng
- Giới hạn 10 kết quả mỗi loại để tránh quá tải

### 4. Tìm kiếm lại
- Có nút "Tìm kiếm lại" để thực hiện tìm kiếm mới
- Không cần quay lại menu chính

## Lỗi thường gặp

### 1. Không tìm thấy kết quả
- Kiểm tra từ khóa tìm kiếm
- Thử từ khóa khác hoặc tiếng Anh
- Kiểm tra kết nối internet

### 2. Lỗi API
- Kiểm tra API key TMDB
- Kiểm tra kết nối internet
- Xem log để biết chi tiết lỗi

### 3. Không hiển thị poster
- Kiểm tra kết nối internet
- TMDB có thể tạm thời không khả dụng

## Tích hợp với backend

Tính năng này có thể được mở rộng để tích hợp với backend API:
- Gọi API `https://bioidaika.click:1106/api/movie/{tmdb_id}` để lấy link download
- Hiển thị thêm thông tin về nguồn download có sẵn

## Cập nhật

Để cập nhật tính năng:
1. Thay thế file `resources/tmdb_search.py`
2. Restart addon VietMediaF
3. Kiểm tra hoạt động bình thường
