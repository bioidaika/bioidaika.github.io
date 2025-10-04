# 🔧 Backend API Error Handling - TMDB Search

## 📋 **TỔNG QUAN**

TMDB Search đã được cải thiện để xử lý lỗi Backend API một cách thông minh và báo cáo chi tiết cho người dùng.

## 🎯 **CÁC LOẠI LỖI ĐƯỢC XỬ LÝ**

### ✅ **1. Timeout Error:**
- **Nguyên nhân**: Backend API phản hồi chậm hơn timeout setting
- **Xử lý**: Hiển thị cảnh báo nhưng vẫn hiển thị kết quả
- **Thông báo**: "Backend API timeout sau X giây"

### ✅ **2. Connection Error:**
- **Nguyên nhân**: Không thể kết nối đến Backend API
- **Xử lý**: Hiển thị cảnh báo nhưng vẫn hiển thị kết quả
- **Thông báo**: "Không thể kết nối đến Backend API: URL"

### ✅ **3. HTTP Error:**
- **Nguyên nhân**: Backend API trả về status code lỗi (4xx, 5xx)
- **Xử lý**: Hiển thị cảnh báo nhưng vẫn hiển thị kết quả
- **Thông báo**: "Backend API lỗi: STATUS_CODE"

### ✅ **4. JSON Parse Error:**
- **Nguyên nhân**: Backend API trả về response không hợp lệ
- **Xử lý**: Hiển thị cảnh báo nhưng vẫn hiển thị kết quả
- **Thông báo**: "Lỗi Backend API: ERROR_DETAILS"

## 🔄 **FLOW XỬ LÝ LỖI**

### **📊 Tìm kiếm thông thường:**
```
1. Gọi TMDB API → Lấy kết quả
2. Gọi Backend API → Kiểm tra cache từng item
3. Nếu có lỗi → Thu thập danh sách lỗi
4. Hiển thị cảnh báo nếu có lỗi
5. Hiển thị kết quả đã lọc (ẩn cache miss)
```

### **🎬 Tìm kiếm TMDB ID:**
```
1. Gọi TMDB API → Lấy thông tin chi tiết
2. Gọi Backend API → Kiểm tra cache
3. Nếu cache miss → Không hiển thị
4. Nếu có lỗi → Hiển thị cảnh báo + hiển thị kết quả
5. Nếu cache hit → Hiển thị bình thường
```

## 🚨 **THÔNG BÁO LỖI**

### **📱 Alert Dialog:**
- **Format**: "⚠️ Backend API có lỗi:\n[Chi tiết lỗi]\n\nKết quả vẫn được hiển thị nhưng có thể không chính xác."
- **Hiển thị**: Tối đa 3 lỗi đầu tiên
- **Nếu nhiều hơn**: "... và X lỗi khác"

### **📝 Log Messages:**
- **Level**: ERROR cho lỗi nghiêm trọng
- **Format**: "[VietmediaF] [ERROR_TYPE] for TMDB ID [ID]: [DETAILS]"
- **Ví dụ**: "[VietmediaF] Backend API timeout for TMDB ID 12345"

## ⚙️ **CẤU HÌNH XỬ LÝ LỖI**

### **1. Timeout Settings:**
- **Default**: 3 giây
- **Có thể điều chỉnh**: Settings → Backend API → Timeout
- **Khuyến nghị**: 3-5 giây cho mạng ổn định

### **2. Error Tolerance:**
- **Lỗi nhỏ**: Vẫn hiển thị kết quả với cảnh báo
- **Lỗi nghiêm trọng**: Có thể ẩn kết quả
- **Fallback**: Luôn có kết quả dự phòng

### **3. Logging Level:**
- **INFO**: Cache hit/miss bình thường
- **WARNING**: Timeout, connection error
- **ERROR**: HTTP error, parse error

## 🎯 **VÍ DỤ XỬ LÝ LỖI**

### **Tìm kiếm "avatar" với Backend API lỗi:**
```
1. TMDB trả về 20 kết quả
2. Backend API timeout cho 5 phim đầu
3. Backend API connection error cho 3 phim tiếp theo
4. 12 phim còn lại cache hit
5. Hiển thị: "⚠️ Backend API có lỗi:
   Phim ID 123: Backend API timeout sau 3 giây
   Phim ID 456: Không thể kết nối đến Backend API
   Phim ID 789: Backend API timeout sau 3 giây
   ... và 2 lỗi khác
   
   Kết quả vẫn được hiển thị nhưng có thể không chính xác."
6. Hiển thị 20 phim (không ẩn do lỗi)
```

### **Tìm kiếm "1132" với cache miss:**
```
1. TMDB ID 32 (phim)
2. Backend API trả về sources rỗng
3. Hiển thị: "Phim/TV với ID 32 không có trong cache backend."
4. Không hiển thị kết quả
```

## 🔧 **TROUBLESHOOTING**

### **1. Backend API không phản hồi:**
- **Kiểm tra**: URL Backend API có đúng không
- **Kiểm tra**: Mạng có kết nối không
- **Kiểm tra**: Backend server có chạy không

### **2. Timeout quá thường xuyên:**
- **Tăng timeout**: Settings → Backend API → Timeout
- **Kiểm tra mạng**: Tốc độ kết nối
- **Kiểm tra server**: Backend có chậm không

### **3. Kết quả không chính xác:**
- **Kiểm tra cache**: Backend có cập nhật cache không
- **Kiểm tra API**: Backend API có hoạt động đúng không
- **Kiểm tra logs**: Xem log để debug

## 🚀 **LỢI ÍCH**

- ✅ **Không mất kết quả**: Lỗi không làm ẩn kết quả
- ⚠️ **Cảnh báo rõ ràng**: Người dùng biết có lỗi
- 🔧 **Dễ debug**: Log chi tiết cho developer
- 📊 **Thống kê**: Biết tỷ lệ cache hit/miss
- 🛡️ **An toàn**: Luôn có fallback

---

**Backend API Error Handling đảm bảo TMDB Search hoạt động ổn định ngay cả khi có lỗi!** 🎬✨
