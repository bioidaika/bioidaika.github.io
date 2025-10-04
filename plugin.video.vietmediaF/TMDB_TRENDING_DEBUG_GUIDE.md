# TMDB Trending Settings Debug Guide

## 🐛 **Vấn đề gặp phải:**

Người dùng đã cài đặt 40 phim trending nhưng kết quả hiển thị vẫn như cũ (20 phim).

## 🔍 **Các nguyên nhân có thể:**

### **1. Cache Settings:**
- Kodi có thể cache settings cũ
- Cần restart addon hoặc Kodi

### **2. Setting chưa được lưu:**
- Setting chưa được lưu đúng cách
- File settings.xml chưa được cập nhật

### **3. Code chưa được reload:**
- Code mới chưa được load
- Cần restart addon

## 🛠️ **Cách Debug:**

### **Bước 1: Kiểm tra Logs**
1. Mở "Phim Trending TMDB"
2. Xem Kodi log để kiểm tra debug messages:
   ```
   [VietmediaF] TMDB Settings Debug:
   [VietmediaF] - Trending Count: 40
   [VietmediaF] Target trending count: 40
   [VietmediaF] Pages needed: 2 for 40 movies
   [VietmediaF] Fetched 40 trending movies from 2 pages (target: 40)
   ```

### **Bước 2: Restart Addon**
1. Vào Settings → Add-ons → Manage Dependencies
2. Tìm "plugin.video.vietmediaF"
3. Disable → Enable lại addon

### **Bước 3: Kiểm tra Settings File**
1. Mở file: `userdata/addon_data/plugin.video.vietmediaF/settings.xml`
2. Tìm dòng: `<setting id="tmdb_trending_count">40</setting>`
3. Nếu không có hoặc khác 40 → setting chưa được lưu

### **Bước 4: Clear Cache**
1. Xóa thư mục cache: `userdata/addon_data/plugin.video.vietmediaF/cache/`
2. Restart Kodi

## 🔧 **Code Debug đã thêm:**

### **1. Debug Settings:**
```python
def get_tmdb_trending_count():
    setting_value = ADDON.getSetting('tmdb_trending_count')
    count = int(setting_value or "20")
    xbmc.log(f"[VietmediaF] TMDB trending count setting: '{setting_value}' -> {count}", xbmc.LOGINFO)
    return count
```

### **2. Debug Multiple Pages:**
```python
def get_trending_movies_multiple_pages(time_window="day"):
    target_count = get_tmdb_trending_count()
    pages_needed = (target_count + 19) // 20
    xbmc.log(f"[VietmediaF] Pages needed: {pages_needed} for {target_count} movies", xbmc.LOGINFO)
    
    # ... fetch pages ...
    
    xbmc.log(f"[VietmediaF] Fetched {len(all_movies)} trending movies from {pages_needed} pages (target: {target_count})", xbmc.LOGINFO)
```

### **3. Debug Show Function:**
```python
def show_trending_movies(time_window="day", page=1):
    # Debug tất cả settings
    xbmc.log(f"[VietmediaF] TMDB Settings Debug:", xbmc.LOGINFO)
    xbmc.log(f"[VietmediaF] - Trending Count: {target_count}", xbmc.LOGINFO)
```

## 📋 **Checklist Debug:**

- [ ] Kiểm tra Kodi log có hiển thị "Trending Count: 40" không?
- [ ] Kiểm tra "Pages needed: 2 for 40 movies" không?
- [ ] Kiểm tra "Fetched 40 trending movies" không?
- [ ] Restart addon đã thử chưa?
- [ ] Clear cache đã thử chưa?
- [ ] Settings file có đúng không?

## 🎯 **Kết quả mong đợi:**

Khi setting = 40 phim:
- Log: "Target trending count: 40"
- Log: "Pages needed: 2 for 40 movies"  
- Log: "Fetched 40 trending movies from 2 pages"
- UI: Hiển thị 40 phim thay vì 20 phim

## 🚨 **Nếu vẫn không hoạt động:**

1. **Kiểm tra file settings.xml:**
   ```xml
   <setting id="tmdb_trending_count">40</setting>
   ```

2. **Force reload settings:**
   ```python
   ADDON = xbmcaddon.Addon()
   ADDON.reloadSettings()
   ```

3. **Hard reset addon:**
   - Uninstall addon
   - Reinstall addon
   - Cấu hình lại settings

Debug logs sẽ giúp xác định chính xác vấn đề! 🔍
