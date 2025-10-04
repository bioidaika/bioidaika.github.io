# 🔑 HƯỚNG DẪN CẤU HÌNH TMDB API KEY

## 📋 Bước 1: Đăng ký tài khoản TMDB

1. Truy cập: https://www.themoviedb.org/
2. Nhấn **"Sign Up"** để đăng ký tài khoản mới
3. Điền thông tin và xác nhận email

## 🔑 Bước 2: Lấy API Key

1. Đăng nhập vào tài khoản TMDB
2. Truy cập: https://www.themoviedb.org/settings/api
3. Nhấn **"Request an API Key"**
4. Chọn **"Developer"** (miễn phí)
5. Điền thông tin:
   - **Application Name**: VietMediaF
   - **Application Summary**: Kodi addon for Vietnamese media
   - **Application URL**: https://github.com/your-repo
6. Nhấn **"Submit"**
7. Copy **API Key (v3 auth)** được cung cấp

## ⚙️ Bước 3: Cập nhật API Key trong addon

1. Mở file: `resources/tmdb_search.py`
2. Tìm dòng:
   ```python
   TMDB_API_KEY = "GmQsv0mEPdT2pWWAiuAIrvxDKHeskoHKfnw7h5GEOY84ajvdXrrkyzcqfmbxPrrg"
   ```
3. Thay thế bằng API key thực tế:
   ```python
   TMDB_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
   ```
4. Lưu file

## ✅ Bước 4: Kiểm tra

1. Khởi động lại Kodi
2. Mở addon VietMediaF
3. Chọn **"Tìm kiếm"** → **"Tìm kiếm TMDB"**
4. Nhập từ khóa tìm kiếm
5. Nếu hiển thị kết quả phim/TV series thì cấu hình thành công!

## 🚨 Lưu ý quan trọng

- **API Key miễn phí** có giới hạn 1000 requests/ngày
- **Không chia sẻ** API key với người khác
- **Bảo mật** API key trong file cấu hình
- Nếu gặp lỗi 401, kiểm tra lại API key

## 🔧 Xử lý sự cố

### Lỗi 401 - Invalid API Key
- Kiểm tra API key có đúng không
- Đảm bảo đã copy đầy đủ API key
- Kiểm tra không có khoảng trắng thừa

### Lỗi 429 - Too Many Requests
- Đã vượt quá giới hạn 1000 requests/ngày
- Chờ đến ngày hôm sau hoặc nâng cấp tài khoản

### Không hiển thị kết quả
- Kiểm tra kết nối internet
- Thử từ khóa tìm kiếm khác
- Kiểm tra log Kodi để xem lỗi chi tiết

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log Kodi
2. Chụp ảnh màn hình lỗi
3. Liên hệ qua GitHub Issues

---
**VietMediaF Team** - Tìm kiếm phim Việt Nam dễ dàng hơn! 🎬
