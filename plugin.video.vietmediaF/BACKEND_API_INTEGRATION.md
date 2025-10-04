# 🔗 Backend API Integration - TMDB Search

## 📋 **TỔNG QUAN**

TMDB Search đã được tích hợp với Backend API để kiểm tra cache và chỉ hiển thị những kết quả có sẵn trong hệ thống.

## 🎯 **TÍNH NĂNG**

### ✅ **Cache Filtering:**
- **Kiểm tra cache**: Gọi backend API để kiểm tra TMDB ID có trong cache không
- **Ẩn kết quả**: Tự động ẩn những phim/TV không có trong cache
- **Hiển thị thông báo**: Thông báo số lượng kết quả được lọc

### ✅ **Cấu hình linh hoạt:**
- **Bật/tắt**: Có thể bật/tắt tính năng kiểm tra cache
- **URL tùy chỉnh**: Cấu hình URL backend API
- **Timeout**: Thiết lập thời gian chờ API

## ⚙️ **CẤU HÌNH**

### 1. **Truy cập Settings:**
- Vào **Addon Settings** → **Backend API**
- Bật **"Kích hoạt kiểm tra cache backend"**
- Nhập **"URL Backend API"** (mặc định: https://bioidaika.click)
- Thiết lập **"Timeout (giây)"** (mặc định: 3)

### 2. **Backend API Endpoint:**
```
GET /api/{media_type}/{tmdb_id}
Accept: application/json

Ví dụ:
GET /api/movie/12345
GET /api/tv/67890
```

### 3. **Response Format:**
```json
{
    "tmdb_id": "12345",
    "media_type": "movie",
    "sources": [
        {
            "uploader": "Uploader Name",
            "sheet_name": "Sheet Name",
            "download_url": "https://fshare.vn/file/...",
            "size": "2.5GB",
            "vmf_code": "1112345",
            "trailer_url": "https://youtube.com/..."
        }
    ]
}
```

## 🔧 **CÁCH HOẠT ĐỘNG**

### 1. **Tìm kiếm TMDB:**
```
User nhập từ khóa → TMDB API → Kết quả
```

### 2. **Kiểm tra Cache:**
```
Kết quả TMDB → Backend API → Lọc cache
```

### 3. **Hiển thị:**
```
Chỉ hiển thị kết quả có cache = true
```

## 📊 **FLOW CHI TIẾT**

### **🔍 Tìm kiếm thông thường:**
1. **User nhập từ khóa** → "avatar"
2. **Gọi TMDB API** → Tìm kiếm phim và TV
3. **Kiểm tra cache** → Gọi backend API cho từng kết quả
4. **Lọc kết quả** → Chỉ giữ lại những item có cache = true
5. **Hiển thị** → Danh sách đã lọc

### **🎬 Tìm kiếm bằng TMDB ID:**
1. **User nhập** → "1132" (phim ID 32)
2. **Gọi TMDB API** → Lấy thông tin chi tiết phim
3. **Kiểm tra cache** → Gọi backend API
4. **Hiển thị** → Nếu có cache, hiển thị phim

## 🚀 **TÍNH NĂNG NÂNG CAO**

### ✅ **Error Handling:**
- **Timeout**: Nếu API chậm, mặc định hiển thị kết quả
- **Connection Error**: Nếu không kết nối được, hiển thị tất cả
- **API Error**: Nếu API lỗi, hiển thị tất cả

### ✅ **Performance:**
- **Timeout ngắn**: 3 giây mặc định để không làm chậm UI
- **Parallel checking**: Kiểm tra nhiều item song song
- **Caching**: Kết quả được cache trong session

### ✅ **Logging:**
- **Chi tiết**: Log từng bước kiểm tra cache
- **Thống kê**: Hiển thị số lượng item được lọc
- **Debug**: Thông tin lỗi chi tiết

## 📝 **VÍ DỤ SỬ DỤNG**

### **Tìm kiếm "avatar":**
```
1. TMDB trả về 20 kết quả
2. Kiểm tra cache: 15/20 có trong cache
3. Hiển thị: 15 kết quả (5 bị ẩn)
4. Thông báo: "Đang kiểm tra cache backend..."
```

### **Tìm kiếm "1132":**
```
1. TMDB ID 32 (phim)
2. Kiểm tra cache: có trong cache
3. Hiển thị: Thông tin phim chi tiết
```

## 🔧 **BACKEND API REQUIREMENTS**

### **Endpoint:**
```
GET /api/{media_type}/{tmdb_id}
```

### **Request:**
```
GET /api/movie/12345
GET /api/tv/67890
```

### **Response:**
```json
{
    "tmdb_id": "12345",
    "media_type": "movie",
    "sources": [
        {
            "uploader": "Uploader Name",
            "sheet_name": "Sheet Name",
            "download_url": "https://fshare.vn/file/...",
            "size": "2.5GB",
            "vmf_code": "1112345",
            "trailer_url": "https://youtube.com/..."
        }
    ]
}
```

### **Cache Logic:**
- **Cache Hit**: Có sources với download_url hợp lệ
- **Cache Miss**: Không có sources hoặc sources không có download_url
- **Error Handling**: 
  - **200**: Success với sources array
  - **404**: Not found (mặc định hiển thị)
  - **500**: Server error (mặc định hiển thị)

## ⚡ **PERFORMANCE TIPS**

### **1. Backend API:**
- Sử dụng database index cho tmdb_id
- Cache kết quả trong memory
- Sử dụng connection pooling

### **2. Addon:**
- Giảm timeout nếu backend nhanh
- Tăng timeout nếu backend chậm
- Bật/tắt tính năng khi cần

## 🎯 **LỢI ÍCH**

- 🎬 **Chỉ hiển thị phim có sẵn**: Không làm thất vọng user
- ⚡ **Tối ưu hiệu suất**: Giảm tải cho hệ thống
- 🔧 **Linh hoạt**: Có thể bật/tắt dễ dàng
- 📊 **Thống kê**: Theo dõi hiệu quả cache

---

**Backend API Integration giúp TMDB Search chỉ hiển thị những phim/TV thực sự có sẵn trong hệ thống!** 🎬✨
