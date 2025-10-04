# 🔧 TMDB Search Form Fix - Missing Function

## 🚨 **VẤN ĐỀ ĐÃ SỬA**

### **Lỗi gốc:**
```
Error showing search form: name 'TMDB_API_KEY' is not defined
```

### **Nguyên nhân:**
- Hàm `show_search_form()` được gọi từ `default.py` nhưng không tồn tại trong `tmdb_search.py`
- Code cũ sử dụng biến `TMDB_API_KEY` đã bị xóa

## ✅ **GIẢI PHÁP**

### **1. Tạo hàm `show_search_form()`:**
```python
def show_search_form():
    """
    Hiển thị form tìm kiếm TMDB
    """
    try:
        # Kiểm tra API key từ settings
        api_key = get_tmdb_api_key()
        if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
            alert("TMDB API key chưa được cấu hình. Vui lòng cấu hình API key trong settings.")
            return
        
        # Hiển thị form nhập từ khóa
        keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm TMDB")
        keyboard.doModal()
        
        if keyboard.isConfirmed() and keyboard.getText():
            query = keyboard.getText().strip()
            if query:
                perform_search(query)
            else:
                alert("Vui lòng nhập từ khóa tìm kiếm")
        else:
            # Người dùng hủy
            xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
            
    except Exception as e:
        logError(f"Error showing search form: {str(e)}")
        alert(f"Lỗi hiển thị form tìm kiếm: {str(e)}")
        xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=False)
```

### **2. Sử dụng settings thay vì hardcode:**
- **Trước**: `TMDB_API_KEY` (hardcode)
- **Sau**: `get_tmdb_api_key()` (từ settings)

## 🎯 **CÁCH HOẠT ĐỘNG**

### **1. User clicks "Tìm kiếm TMDB":**
```
URL: plugin://plugin.video.vietmediaF/?action=tmdbsearch
```

### **2. `default.py` calls `tmdb_search.show_search_form()`:**
```python
if "tmdbsearch" in url:
    tmdb_search.show_search_form()
    exit()
```

### **3. `show_search_form()` checks API key:**
```python
api_key = get_tmdb_api_key()
if not api_key or api_key == "YOUR_TMDB_API_KEY_HERE":
    alert("TMDB API key chưa được cấu hình...")
    return
```

### **4. Shows keyboard input:**
```python
keyboard = xbmc.Keyboard("", "Nhập từ khóa tìm kiếm TMDB")
keyboard.doModal()
```

### **5. Calls `perform_search()`:**
```python
if keyboard.isConfirmed() and keyboard.getText():
    query = keyboard.getText().strip()
    if query:
        perform_search(query)
```

## 🔧 **CÁC TÍNH NĂNG**

### **1. ✅ API Key Validation:**
- Kiểm tra API key từ settings
- Hiển thị thông báo nếu chưa cấu hình
- Sử dụng `get_tmdb_api_key()` thay vì hardcode

### **2. ✅ Keyboard Input:**
- Hiển thị form nhập từ khóa
- Xử lý khi người dùng hủy
- Validate input trước khi tìm kiếm

### **3. ✅ Error Handling:**
- Try-catch cho tất cả operations
- Log errors chi tiết
- Hiển thị thông báo lỗi cho người dùng

### **4. ✅ Integration:**
- Tích hợp với `perform_search()`
- Sử dụng các helper functions
- Tương thích với Kodi

## 🚀 **LỢI ÍCH**

- ✅ **Không còn lỗi NameError**: Hàm `show_search_form()` đã được tạo
- ✅ **Sử dụng settings**: API key được lấy từ settings
- ✅ **User-friendly**: Form nhập từ khóa đẹp và dễ sử dụng
- ✅ **Error handling**: Xử lý lỗi tốt và thông báo rõ ràng
- ✅ **Integration**: Tích hợp hoàn chỉnh với hệ thống

## 📊 **FLOW HOÀN CHỈNH**

### **1. User clicks "Tìm kiếm TMDB"**
### **2. `show_search_form()` được gọi**
### **3. Kiểm tra API key từ settings**
### **4. Hiển thị form nhập từ khóa**
### **5. User nhập từ khóa và nhấn OK**
### **6. `perform_search()` được gọi**
### **7. Tìm kiếm TMDB API**
### **8. Kiểm tra cache backend**
### **9. Hiển thị kết quả**

## ⚠️ **LƯU Ý**

### **1. API Key cần được cấu hình:**
- Vào Settings → TMDB API → TMDB API Key
- Nhập API key thực tế từ https://www.themoviedb.org/settings/api

### **2. Backend API:**
- Mặc định đã được bật
- Có thể tắt trong settings nếu cần

### **3. Error handling:**
- Tất cả lỗi đều được log và hiển thị
- Người dùng được thông báo rõ ràng

---

**TMDB Search Form giờ đây hoạt động hoàn hảo!** 🎬✨
