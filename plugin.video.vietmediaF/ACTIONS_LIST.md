# 📋 Danh sách các Action trong VietmediaF Addon

## 🎯 **TỔNG QUAN**

Addon VietmediaF có rất nhiều action để xử lý các chức năng khác nhau. Dưới đây là danh sách đầy đủ các action được sử dụng trong addon.

## 🔍 **ACTION CHÍNH**

### **1. 🏠 Menu & Navigation**
- `action=menu` - Hiển thị menu chính
- `action=browse` - Duyệt nội dung từ các nguồn khác nhau
- `action=play` - Phát nội dung (file, folder, URL)

### **2. 🔍 Tìm kiếm**
- `action=tmdbsearch` - Tìm kiếm TMDB
- `action=__search__` - Tìm kiếm chung
- `action=__searchTVHD__` - Tìm kiếm trên TVHD
- `action=__timkiem__` - Tìm kiếm nâng cao
- `action=_timtrenfshare_` - Tìm kiếm trên FShare
- `action=_timtrenfshare1_` - Tìm kiếm FShare với keyword
- `action=_timtren4share_` - Tìm kiếm trên 4Share
- `action=_timtren4share1_` - Tìm kiếm 4Share với keyword
- `action=__searchphongblack__` - Tìm kiếm PhongBlack
- `action=__searchphongblack1__` - Tìm kiếm PhongBlack với keyword

### **3. 📊 Nguồn dữ liệu**
- `action=__TIMFSHARE__` - Nguồn TimFShare
- `action=__TIMTVHD__` - Nguồn TVHD
- `action=thuviencine_top` - Top Thuviencine
- `action=__phimle__` - Phim lẻ
- `action=__phimbo__` - Phim bộ

### **4. 🎬 Phát nội dung**
- `action=play` - Phát file/folder
- `action=fetch_espisode` - Lấy tập phim
- `action=showWindow` - Hiển thị cửa sổ

### **5. ⚙️ Cài đặt & Tiện ích**
- `action=__settings__` - Mở cài đặt
- `action=tienich` - Menu tiện ích
- `action=subtitle_fonts` - Quản lý font phụ đề
- `action=install_subtitle_font` - Cài đặt font phụ đề
- `action=install_arctic_zephyr` - Cài đặt skin Arctic Zephyr
- `action=show_skin_install_guide` - Hướng dẫn cài skin

### **6. 👤 Tài khoản**
- `action=quick_account_menu` - Menu tài khoản nhanh
- `action=quick_account_code` - Tài khoản code
- `action=quick_account_qr` - Tài khoản QR
- `action=account_fshare` - Tài khoản FShare
- `action=get_user_information_fourshare` - Thông tin user 4Share

### **7. 📁 Quản lý FShare**
- `action=folderxxx` - FShare favorites
- `action=top_follow_share` - Top follow share
- `action=home_fshare` - Home FShare

### **8. 📈 Thống kê & Lịch sử**
- `action=__history__` - Lịch sử xem
- `action=__removeAllHistoryPlayCode__` - Xóa tất cả lịch sử
- `action=__removeHistory__` - Xóa lịch sử
- `action=__removeAllSearchHistory__` - Xóa lịch sử tìm kiếm
- `action=__removeAllSearchHistory4share__` - Xóa lịch sử tìm kiếm 4Share
- `action=_topsearch100_` - Top 100 tìm kiếm

### **9. 🔧 Hệ thống**
- `action=__download__` - Tải xuống
- `action=__showdownload__` - Hiển thị tải xuống
- `action=__speedtest__` - Test tốc độ
- `action=__backup__` - Backup
- `action=__restore__` - Restore
- `action=__exitKodi__` - Thoát Kodi

### **10. 🖼️ Hiển thị**
- `action=__PIC__` - Hiển thị hình ảnh
- `action=__forbiddenZone__` - Vùng cấm

### **11. 🔗 Xử lý URL**
- `action=VMF` - Xử lý VMF code
- `action=textbox` - Hiển thị textbox
- `action=addon` - Xử lý addon

## 🎯 **ACTION MỚI ĐƯỢC THÊM**

### **TMDB Integration:**
- `action=tmdbsearch` - Tìm kiếm TMDB
- `action=tmdb_movie_detail` - Chi tiết phim TMDB

## 🔄 **LUỒNG XỬ LÝ ACTION**

### **1. 🎯 URL Parsing:**
```python
def go():
    url = sys.argv[0] + sys.argv[2]
    
    # Parse URL parameters
    args = {}
    if '?' in url:
        query_string = url.split('?', 1)[1]
        args = dict(urllib_parse.parse_qsl(query_string))
```

### **2. 🔍 Action Detection:**
```python
# Kiểm tra action trong URL
if 'action=menu' in url:
    # Xử lý menu
elif 'action=play' in url:
    # Xử lý phát nội dung
elif 'action=tmdbsearch' in url:
    # Xử lý tìm kiếm TMDB
# ... các action khác
```

### **3. 🎬 Action Execution:**
```python
# Mỗi action có hàm xử lý riêng
def handle_menu():
    data = getMenu()
    loadlistitem.list_item_main(data)

def handle_play(data):
    # Xử lý phát nội dung
    pass

def handle_tmdb_search():
    # Xử lý tìm kiếm TMDB
    pass
```

## 🎯 **CÁC ACTION QUAN TRỌNG NHẤT**

### **1. 🏠 Core Actions:**
- `menu` - Menu chính
- `play` - Phát nội dung
- `browse` - Duyệt nội dung

### **2. 🔍 Search Actions:**
- `tmdbsearch` - Tìm kiếm TMDB (mới)
- `__search__` - Tìm kiếm chung
- `_timtrenfshare_` - Tìm kiếm FShare

### **3. ⚙️ System Actions:**
- `__settings__` - Cài đặt
- `__history__` - Lịch sử
- `__download__` - Tải xuống

### **4. 🎬 Media Actions:**
- `play` - Phát file/folder
- `fetch_espisode` - Lấy tập phim
- `showWindow` - Hiển thị cửa sổ

## 🎯 **KẾT LUẬN**

Addon VietmediaF có **hơn 50 action** khác nhau để xử lý:

1. **🏠 Navigation** → Menu, browse, play
2. **🔍 Search** → TMDB, FShare, 4Share, TVHD
3. **📊 Data Sources** → Google Sheets, APIs
4. **🎬 Media** → Play, fetch, display
5. **⚙️ System** → Settings, utilities, management
6. **👤 Account** → User management
7. **📈 Analytics** → History, statistics
8. **🔧 Tools** → Download, backup, restore

**Mỗi action được thiết kế để xử lý một chức năng cụ thể!** 🎬✨
