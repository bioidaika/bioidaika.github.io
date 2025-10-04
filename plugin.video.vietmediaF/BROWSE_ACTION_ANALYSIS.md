# 🔍 Browse Action Analysis - Phân tích action browse

## 🎯 **TỔNG QUAN**

Action `browse` được sử dụng để xử lý các URL từ các nguồn khác nhau, bao gồm Google Docs, Thuviencine, Thuvienhd, và Hdvietnam.

## 🔄 **LUỒNG XỬ LÝ**

### **1. 🎯 URL Input:**
```
plugin://plugin.video.vietmediaF?action=browse&url=https://docs.google.com/spreadsheets/d/1yCyQ1ZqIaeEkh5TYiXqPkTkRtrlbWkc6mL5jA2s6VqM/edit?usp=drivesdk
```

### **2. 🔍 Xử lý trong hàm go():**
```python
def go():
    url = sys.argv[0] + sys.argv[2]
    
    # Parse URL parameters
    args = {}
    if '?' in url:
        query_string = url.split('?', 1)[1]
        args = dict(urllib_parse.parse_qsl(query_string))
    
    # Xử lý các loại URL khác nhau
    if "docs.google.com" in url:
        handle_google_docs_url(url)
        return
    elif "thuviencine" in url:
        process_url(url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')
    elif "thuvienhd" in url:
        process_url(url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')
    elif "hdvietnam" in url:
        process_url(url, 'hdvietnam.xyz', hdvn.receive, 'hdvietnam.xyz')
```

### **3. 📊 Xử lý Google Docs URL:**
```python
def handle_google_docs_url(url):
    if ADDON.getSetting('gochiase') == 'false':
        # Hiển thị cảnh báo cho user
        dialog = xbmcgui.Dialog()
        confirmed = dialog.yesno("Cảnh báo", 
            "Đây là nội dung được lấy từ danh sách chia sẻ file...")
        
        if confirmed:
            ADDON.setSetting('gochiase', 'true')
            data = cache_utils.cache_data(url)
            if data is not None:
                loadlistitem.list_item_main(data)
        else:
            xbmc.executebuiltin("Action(Back)")
    else:
        # Xử lý trực tiếp
        data = cache_utils.cache_data(url)
        if data is not None:
            loadlistitem.list_item_main(data)
```

## 🎯 **CÁC LOẠI URL ĐƯỢC XỬ LÝ**

### **1. ✅ Google Docs/Sheets:**
```
Input:  https://docs.google.com/spreadsheets/d/...
Action: handle_google_docs_url()
Result: Hiển thị danh sách từ Google Sheets
```

### **2. ✅ Thuviencine:**
```
Input:  https://thuviencine.com/...
Action: process_url(url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')
Result: Hiển thị nội dung từ Thuviencine
```

### **3. ✅ Thuvienhd:**
```
Input:  https://thuvienhd.top/...
Action: process_url(url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')
Result: Hiển thị nội dung từ Thuvienhd
```

### **4. ✅ Hdvietnam:**
```
Input:  https://hdvietnam.xyz/...
Action: process_url(url, 'hdvietnam.xyz', hdvn.receive, 'hdvietnam.xyz')
Result: Hiển thị nội dung từ Hdvietnam
```

## 🔧 **CODE CHI TIẾT**

### **File: default.py - Hàm go()**
```python
def go():
    url = sys.argv[0] + sys.argv[2]
    
    # Parse URL parameters
    args = {}
    if '?' in url:
        query_string = url.split('?', 1)[1]
        args = dict(urllib_parse.parse_qsl(query_string))
    
    # Xử lý Google Docs
    if "docs.google.com" in url:
        handle_google_docs_url(url)
        return
    
    # Xử lý các nguồn khác
    if "thuviencine" in url:
        process_url(url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')
    elif "thuvienhd" in url:
        process_url(url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')
    elif "hdvietnam" in url:
        process_url(url, 'hdvietnam.xyz', hdvn.receive, 'hdvietnam.xyz')
```

### **File: default.py - Hàm handle_google_docs_url()**
```python
def handle_google_docs_url(url):
    if ADDON.getSetting('gochiase') == 'false':
        # Hiển thị cảnh báo lần đầu
        dialog = xbmcgui.Dialog()
        confirmed = dialog.yesno("Cảnh báo", 
            "Đây là nội dung được lấy từ danh sách chia sẻ file...")
        
        if confirmed:
            ADDON.setSetting('gochiase', 'true')
            data = cache_utils.cache_data(url)
            if data is not None:
                loadlistitem.list_item_main(data)
        else:
            xbmc.executebuiltin("Action(Back)")
    else:
        # Xử lý trực tiếp
        data = cache_utils.cache_data(url)
        if data is not None:
            loadlistitem.list_item_main(data)
```

### **File: default.py - Hàm process_url()**
```python
def process_url(plugin_url, source_name, receive_function, source_domain):
    def handle_url(url):
        plugin_url = f"plugin://plugin.video.vietmediaF?action=browse&url={url}"
        
        try:
            if "thuviencine" in url:
                process_url(plugin_url, 'thuviencine.com', tvcine.receive, 'thuviencine.com')
            elif "thuvienhd" in url:
                process_url(plugin_url, 'thuvienhd.top', tvhd.receive, 'thuvienhd.top')
            elif "docs.google.com" in url:
                handle_google_docs_url(plugin_url)
        except Exception as e:
            xbmcgui.Dialog().notification("Lỗi", "Có lỗi xảy ra...")
```

## 🎯 **TÍNH NĂNG**

### **1. 🔍 URL Detection:**
- Tự động nhận diện loại URL
- Xử lý theo từng loại nguồn
- Error handling robust

### **2. 💾 Cache Integration:**
- Sử dụng `cache_utils.cache_data()`
- Tự động cache kết quả
- Performance tối ưu

### **3. ⚠️ User Warning:**
- Cảnh báo cho Google Docs lần đầu
- Setting để bỏ qua cảnh báo
- User experience tốt

### **4. 🔄 Modular Design:**
- Mỗi nguồn có hàm xử lý riêng
- Dễ dàng thêm nguồn mới
- Code maintainable

## 🎯 **SO SÁNH VỚI FSHARE**

### **1. ✅ Điểm tương đồng:**
- Sử dụng `cache_utils.cache_data()`
- Hiển thị qua `loadlistitem.list_item_main()`
- Error handling tương tự

### **2. 🔄 Điểm khác biệt:**
- Browse: Xử lý nhiều nguồn khác nhau
- FShare: Chỉ xử lý FShare URLs
- Browse: Có cảnh báo user
- FShare: Xử lý trực tiếp

### **3. 💡 Có thể áp dụng:**
- Cấu trúc xử lý URL tương tự
- Cache integration
- Error handling pattern
- User experience design

## 🎯 **KẾT LUẬN**

Action `browse` cung cấp một pattern tốt để xử lý FShare URLs:

1. **🔍 URL Detection** → Nhận diện loại URL
2. **💾 Cache Integration** → Sử dụng cache system
3. **🎬 Display Logic** → Hiển thị kết quả
4. **⚠️ User Experience** → Cảnh báo và feedback
5. **🔄 Error Handling** → Xử lý lỗi robust

**Pattern này có thể được áp dụng để cải thiện xử lý FShare URLs!** 🎬✨
