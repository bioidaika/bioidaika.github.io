# Hướng Dẫn Debug Lịch Sử TMDB Search

## 🐛 **VẤN ĐỀ:**

Người dùng không thấy khung tìm kiếm có lịch sử ở lần search TMDB thứ 2.

## 🔍 **CÁC THAY ĐỔI DEBUG ĐÃ THỰC HIỆN:**

### **1. ✅ Sửa lỗi API key:**
```python
# Trước (LỖI):
if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_TMDB_API_KEY_HERE":

# Sau (ĐÚNG):
api_key = get_tmdb_api_key()
if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
```

### **2. ✅ Thêm debug logs:**
```python
def get_tmdb_search_history():
    history = tmdb_search_history.get_history()
    xbmc.log(f"[VietmediaF] Getting TMDB search history: {history}", xbmc.LOGINFO)
    return history

def save_tmdb_search_history(query):
    xbmc.log(f"[VietmediaF] Saving TMDB search history: {query}", xbmc.LOGINFO)
    tmdb_search_history.save_history(query)

# Trong show_search_form():
history = get_tmdb_search_history()
xbmc.log(f"[VietmediaF] TMDB Search History: {history}", xbmc.LOGINFO)
```

### **3. ✅ Sửa lỗi lưu lịch sử trùng lặp:**
- **Trước:** Lưu lịch sử 2 lần (trong `show_search_form` và `perform_search`)
- **Sau:** Chỉ lưu lịch sử 1 lần trong `perform_search`

## 🔧 **CÁCH KIỂM TRA:**

### **1. 📋 Kiểm tra log Kodi:**
1. Mở Kodi
2. Vào Settings → System → Logging
3. Bật "Enable debug logging"
4. Restart Kodi
5. Thực hiện tìm kiếm TMDB
6. Kiểm tra log file: `C:\Users\ostno\AppData\Roaming\Kodi\kodi.log`

### **2. 🔍 Tìm các dòng log:**
```
[VietmediaF] Getting TMDB search history: []
[VietmediaF] Saving TMDB search history: [từ khóa]
[VietmediaF] TMDB Search History: [danh sách lịch sử]
```

### **3. 📁 Kiểm tra file lịch sử:**
- **Đường dẫn:** `C:\Users\ostno\AppData\Roaming\Kodi\userdata\addon_data\plugin.video.vietmediaF\tmdb_search.dat`
- **Nội dung:** Mỗi dòng một từ khóa tìm kiếm

## 🎯 **CÁC TRƯỜNG HỢP CÓ THỂ XẢY RA:**

### **1. ✅ Lịch sử hoạt động bình thường:**
```
Lần 1: Getting TMDB search history: []
Lần 1: Saving TMDB search history: [từ khóa 1]
Lần 2: Getting TMDB search history: [từ khóa 1]
Lần 2: Hiển thị dialog chọn lịch sử
```

### **2. ❌ Lịch sử không được lưu:**
```
Lần 1: Getting TMDB search history: []
Lần 1: Saving TMDB search history: [từ khóa 1]
Lần 2: Getting TMDB search history: []
Lần 2: Vẫn hiển thị keyboard
```
**Nguyên nhân:** Lỗi lưu file hoặc quyền truy cập

### **3. ❌ Lịch sử không được đọc:**
```
Lần 1: Getting TMDB search history: []
Lần 1: Saving TMDB search history: [từ khóa 1]
Lần 2: Getting TMDB search history: [từ khóa 1]
Lần 2: Vẫn hiển thị keyboard
```
**Nguyên nhân:** Lỗi logic trong `show_search_form`

## 🔧 **CÁCH SỬA LỖI:**

### **1. ✅ Nếu lịch sử không được lưu:**
- Kiểm tra quyền ghi file
- Kiểm tra đường dẫn PROFILE_PATH
- Kiểm tra lỗi trong `HistoryManager.save_history()`

### **2. ✅ Nếu lịch sử không được đọc:**
- Kiểm tra đường dẫn file lịch sử
- Kiểm tra encoding file
- Kiểm tra lỗi trong `HistoryManager.get_history()`

### **3. ✅ Nếu logic hiển thị sai:**
- Kiểm tra điều kiện `if not history:`
- Kiểm tra dialog select
- Kiểm tra exception handling

## 📊 **TEST CASE:**

### **1. 🧪 Test cơ bản:**
1. Mở TMDB Search lần 1
2. Nhập từ khóa "avengers"
3. Kiểm tra log: `Saving TMDB search history: avengers`
4. Mở TMDB Search lần 2
5. Kiểm tra log: `Getting TMDB search history: [avengers]`
6. Kiểm tra hiển thị dialog chọn lịch sử

### **2. 🧪 Test nhiều từ khóa:**
1. Tìm kiếm "avengers" → Lưu
2. Tìm kiếm "spider man" → Lưu
3. Tìm kiếm "iron man" → Lưu
4. Mở TMDB Search lần 4
5. Kiểm tra dialog có 3 từ khóa + 2 tùy chọn

### **3. 🧪 Test xóa lịch sử:**
1. Có lịch sử → Chọn "[Xóa lịch sử tìm kiếm]"
2. Xác nhận xóa
3. Mở TMDB Search lần sau
4. Kiểm tra hiển thị keyboard đơn giản

## 🎉 **KẾT QUẢ MONG ĐỢI:**

**Sau khi sửa lỗi, TMDB Search sẽ hoạt động như sau:**

1. ✅ **Lần đầu:** Hiển thị keyboard đơn giản
2. ✅ **Lần sau:** Hiển thị dialog chọn lịch sử
3. ✅ **Lưu lịch sử:** Tự động lưu mọi từ khóa
4. ✅ **Xóa lịch sử:** Có thể xóa từ dialog
5. ✅ **Debug logs:** Hiển thị đầy đủ thông tin

**TMDB Search với lịch sử sẽ hoạt động hoàn hảo!** 🚀✨
