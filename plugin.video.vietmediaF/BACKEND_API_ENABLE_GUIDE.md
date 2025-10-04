# 🔧 Backend API Enable Guide - TMDB Search

## 🚨 **VẤN ĐỀ**

Backend API chưa được gọi vì setting mặc định là `false`. Cần bật để kiểm tra cache.

## ✅ **CÁCH BẬT BACKEND API**

### **1. 📱 Mở Settings Addon:**
1. Vào **Add-ons** → **Video add-ons** → **VietMediaF**
2. Click chuột phải → **Add-on settings**
3. Hoặc vào **Settings** → **Add-ons** → **Manage** → **VietMediaF** → **Configure**

### **2. ⚙️ Cấu hình Backend API:**
1. Tìm section **"[COLOR yellow]Backend API[/COLOR]"**
2. Bật **"Kích hoạt kiểm tra cache backend"** = `true`
3. Kiểm tra **"URL Backend API"** = `https://bioidaika.click`
4. Kiểm tra **"Timeout (giây)"** = `3`

### **3. 🔄 Restart Addon:**
- Thoát và vào lại addon để áp dụng settings

## 📊 **DEBUG LOGS**

Sau khi bật, bạn sẽ thấy các logs sau trong Kodi log:

### **✅ Backend API Enabled:**
```
[VietmediaF] Filtering cached results - Backend API enabled: True
[VietmediaF] Filtering 20 movies
[VietmediaF] Checking cache for movie ID 123: Avatar
[VietmediaF] Calling Backend API: https://bioidaika.click/api/movie/123
[VietmediaF] Backend URL: https://bioidaika.click, Timeout: 3s
[VietmediaF] Making request to Backend API...
[VietmediaF] Backend API response: 200
[VietmediaF] Movie ID 123 CACHE HIT
```

### **❌ Backend API Disabled:**
```
[VietmediaF] Filtering cached results - Backend API enabled: False
[VietmediaF] Backend API disabled, returning all results without filtering
```

## 🎯 **CÁC TRƯỜNG HỢP XỬ LÝ**

### **1. Cache Hit (Có trong cache):**
- **Log**: `[VietmediaF] Movie ID 123 CACHE HIT`
- **Action**: Hiển thị phim trong danh sách

### **2. Cache Miss (Không có trong cache):**
- **Log**: `[VietmediaF] Movie TMDB ID 123 CACHE MISS, hiding`
- **Action**: Ẩn phim khỏi danh sách

### **3. Backend API Error:**
- **Log**: `[VietmediaF] Movie ID 123 ERROR, showing anyway`
- **Action**: Hiển thị phim + cảnh báo lỗi

### **4. Backend API Disabled:**
- **Log**: `[VietmediaF] Backend API disabled, skipping cache check`
- **Action**: Hiển thị tất cả phim (không lọc)

## 🔧 **TROUBLESHOOTING**

### **1. Không thấy logs Backend API:**
- **Kiểm tra**: Settings có bật `backend_api_enabled` không
- **Kiểm tra**: Restart addon sau khi thay đổi settings

### **2. Backend API timeout:**
- **Tăng timeout**: Settings → Timeout (giây) → 5 hoặc 10
- **Kiểm tra mạng**: Kết nối internet có ổn định không

### **3. Backend API connection error:**
- **Kiểm tra URL**: Settings → URL Backend API
- **Kiểm tra server**: Backend server có chạy không

### **4. Tất cả phim bị ẩn:**
- **Kiểm tra cache**: Backend có dữ liệu không
- **Kiểm tra API**: Backend API có trả về đúng format không

## 📈 **THỐNG KÊ**

Sau khi bật, bạn sẽ thấy thống kê:
```
[VietmediaF] Cache check completed: 15/20 items cached
```

- **15/20**: 15 phim có trong cache, 20 phim tổng cộng
- **Tỷ lệ cache hit**: 75%

## 🚀 **LỢI ÍCH SAU KHI BẬT**

- ✅ **Lọc kết quả**: Chỉ hiển thị phim có trong cache
- ✅ **Tiết kiệm thời gian**: Không phải click vào phim không có
- ✅ **Trải nghiệm tốt**: Chỉ thấy phim có thể xem được
- ✅ **Debug dễ dàng**: Logs chi tiết để theo dõi

---

**Bật Backend API để có trải nghiệm tìm kiếm tối ưu!** 🎬✨
