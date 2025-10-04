# ⚙️ TMDB API Settings Guide - Configuration

## 🎯 **THAY ĐỔI CHÍNH**

TMDB API key giờ đây được cấu hình thông qua settings thay vì hardcode trong code.

### **Trước (Hardcode):**
```python
TMDB_API_KEY = "91ffa0b976634f68d550969e0209de76"
```

### **Sau (Settings):**
```python
def get_tmdb_api_key():
    return ADDON.getSetting('tmdb_api_key') or "YOUR_TMDB_API_KEY_HERE"
```

## 📱 **CÁCH CẤU HÌNH TMDB API**

### **1. Mở Settings Addon:**
1. Vào **Add-ons** → **Video add-ons** → **VietMediaF**
2. Click chuột phải → **Add-on settings**
3. Hoặc vào **Settings** → **Add-ons** → **Manage** → **VietMediaF** → **Configure**

### **2. Tìm section "[COLOR yellow]TMDB API[/COLOR]":**
- **TMDB API Key**: Nhập API key từ https://www.themoviedb.org/settings/api
- **Ngôn ngữ TMDB**: Chọn ngôn ngữ (mặc định: vi-VN)
- **Timeout TMDB (giây)**: Thời gian chờ (mặc định: 10)

### **3. Lấy TMDB API Key:**
1. Truy cập https://www.themoviedb.org/settings/api
2. Đăng nhập tài khoản TMDB
3. Tạo API key mới
4. Copy API key và paste vào settings

## 🔧 **CÁC SETTINGS MỚI**

### **1. TMDB API Key:**
- **ID**: `tmdb_api_key`
- **Type**: Text
- **Default**: `YOUR_TMDB_API_KEY_HERE`
- **Description**: API key từ TMDB để tìm kiếm phim/TV

### **2. Ngôn ngữ TMDB:**
- **ID**: `tmdb_language`
- **Type**: Text
- **Default**: `vi-VN`
- **Description**: Ngôn ngữ hiển thị kết quả tìm kiếm

### **3. Timeout TMDB:**
- **ID**: `tmdb_timeout`
- **Type**: Number
- **Default**: `10`
- **Description**: Thời gian chờ API response (giây)

## 🚀 **LỢI ÍCH**

### **1. 🔐 Bảo mật:**
- API key không còn hardcode trong code
- Người dùng có thể thay đổi API key dễ dàng
- Không cần sửa code để cập nhật API key

### **2. ⚙️ Linh hoạt:**
- Có thể thay đổi ngôn ngữ tìm kiếm
- Có thể điều chỉnh timeout
- Dễ dàng cấu hình cho từng người dùng

### **3. 🛠️ Dễ bảo trì:**
- Không cần sửa code khi API key hết hạn
- Có thể cập nhật settings mà không cần restart addon
- Debug dễ dàng hơn

## 📊 **HOẠT ĐỘNG**

### **Khi tìm kiếm:**
1. **Lấy API key**: `get_tmdb_api_key()` từ settings
2. **Lấy ngôn ngữ**: `get_tmdb_language()` từ settings
3. **Lấy timeout**: `get_tmdb_timeout()` từ settings
4. **Gọi TMDB API**: Sử dụng các giá trị từ settings

### **Logs mới:**
```
[VietmediaF] Using TMDB API key from settings
[VietmediaF] TMDB Language: vi-VN
[VietmediaF] TMDB Timeout: 10s
```

## 🔧 **CÁC HÀM MỚI**

### **1. `get_tmdb_api_key()`:**
```python
def get_tmdb_api_key():
    return ADDON.getSetting('tmdb_api_key') or "YOUR_TMDB_API_KEY_HERE"
```

### **2. `get_tmdb_language()`:**
```python
def get_tmdb_language():
    return ADDON.getSetting('tmdb_language') or "vi-VN"
```

### **3. `get_tmdb_timeout()`:**
```python
def get_tmdb_timeout():
    return int(ADDON.getSetting('tmdb_timeout') or "10")
```

## ⚠️ **LƯU Ý**

### **1. API Key mặc định:**
- Mặc định là `YOUR_TMDB_API_KEY_HERE`
- Cần thay đổi thành API key thực tế
- Nếu không thay đổi, sẽ hiển thị lỗi

### **2. Ngôn ngữ:**
- Mặc định là `vi-VN` (Tiếng Việt)
- Có thể thay đổi thành `en-US`, `ja-JP`, etc.
- Ảnh hưởng đến ngôn ngữ hiển thị kết quả

### **3. Timeout:**
- Mặc định là 10 giây
- Có thể tăng nếu mạng chậm
- Có thể giảm nếu muốn nhanh hơn

## 🎯 **VÍ DỤ CẤU HÌNH**

### **Settings mẫu:**
```
TMDB API Key: 91ffa0b976634f68d550969e0209de76
Ngôn ngữ TMDB: vi-VN
Timeout TMDB (giây): 10
```

### **Kết quả:**
- Tìm kiếm phim bằng tiếng Việt
- Timeout 10 giây
- Sử dụng API key thực tế

---

**TMDB API giờ đây được cấu hình linh hoạt qua settings!** 🎬✨
