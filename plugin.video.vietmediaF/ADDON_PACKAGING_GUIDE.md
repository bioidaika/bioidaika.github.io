# Hướng Dẫn Đóng Gói Addon VietmediaF

## 📋 **CÁC FILE CẦN XÓA TRƯỚC KHI ĐÓNG GÓI:**

### **1. 🗑️ Thư mục `__pycache__` (BẮT BUỘC):**
```
plugin.video.vietmediaF/__pycache__/
plugin.video.vietmediaF/resources/__pycache__/
plugin.video.vietmediaF/resources/lib/__pycache__/
```
**Lý do:** Chứa các file Python bytecode (.pyc) được tạo tự động, không cần thiết cho addon

### **2. 📄 File backup và temporary (KHUYẾN NGHỊ):**
```
plugin.video.vietmediaF/loadlistitem.py.bak
```
**Lý do:** File backup không cần thiết cho người dùng cuối

### **3. 📚 File documentation (TÙY CHỌN):**
```
plugin.video.vietmediaF/*.md
```
**Bao gồm:**
- `ACTIONS_LIST.md`
- `ADD_DIRECTORY_ITEM_FIX.md`
- `BACKEND_API_DEFAULT_ENABLED.md`
- `BACKEND_API_ENABLE_GUIDE.md`
- `BACKEND_API_ERROR_HANDLING.md`
- `BACKEND_API_INTEGRATION.md`
- `BACKEND_TIMEOUT_UPDATE.md`
- `BIOIDAIKA_SETTINGS_SIMPLIFICATION.md`
- `BROWSE_ACTION_ANALYSIS.md`
- `FSHARE_ACTION_BROWSE_FIX.md`
- `FSHARE_ACTION_INTEGRATION.md`
- `FSHARE_CACHE_FIX.md`
- `FSHARE_CACHE_KEY_FINAL_FIX.md`
- `FSHARE_CACHE_KEY_FIX.md`
- `FSHARE_FOLDER_CACHE_FIX.md`
- `FSHARE_FOLDER_DEBUG.md`
- `FSHARE_FOLDER_PLAY_FIX.md`
- `FSHARE_FOLDER_ROUTING_FIX.md`
- `FSHARE_FOLDER_STILL_NOT_WORKING.md`
- `FSHARE_PLAY_ACTION_ANALYSIS.md`
- `FSHARE_SUBFOLDER_DISPLAY_FIX.md`
- `FSHARE_SUBFOLDER_NAVIGATION.md`
- `LAYOUT_3_COLUMNS_GUIDE.md`
- `LOADLISTITEM_DIRECTORY_FIX.md`
- `TMDB_3_COLUMN_LAYOUT_UPDATE.md`
- `TMDB_API_KEY_DEFAULT_UPDATE.md`
- `TMDB_API_SETTINGS_GUIDE.md`
- `TMDB_API_SETUP.md`
- `TMDB_LANGUAGE_DROPDOWN_IMPROVEMENT.md`
- `TMDB_LAYOUT_REFINEMENT.md`
- `TMDB_LIST_VIEW_SIMPLIFICATION.md`
- `TMDB_MOVIE_CLICK_FLOW.md`
- `TMDB_MOVIE_DETAIL_FIX.md`
- `TMDB_SEARCH_FORM_FIX.md`
- `TMDB_SEARCH_README.md`
- `TMDB_SOURCE_DISPLAY_FIX.md`
- `TMDB_SOURCE_DISPLAY_SIMPLIFICATION.md`
- `TMDB_VIEW_MODES_GUIDE.md`

**Lý do:** Các file documentation này chỉ dành cho developer, không cần thiết cho người dùng cuối

## 🚀 **HƯỚNG DẪN ĐÓNG GÓI:**

### **Bước 1: Xóa các file không cần thiết**
```bash
# Xóa thư mục __pycache__
rmdir /s /q __pycache__
rmdir /s /q resources\__pycache__
rmdir /s /q resources\lib\__pycache__

# Xóa file backup
del loadlistitem.py.bak

# Xóa tất cả file .md (tùy chọn)
del *.md
```

### **Bước 2: Tạo file ZIP**
1. Chọn tất cả file và thư mục trong `plugin.video.vietmediaF`
2. Tạo file ZIP với tên: `plugin.video.vietmediaF.zip`
3. Đảm bảo cấu trúc thư mục được giữ nguyên

### **Bước 3: Cài đặt trên máy khác**
1. Copy file ZIP vào máy đích
2. Giải nén vào thư mục addons của Kodi
3. Khởi động lại Kodi

## 📁 **CẤU TRÚC ADDON SAU KHI LÀM SẠCH:**

```
plugin.video.vietmediaF/
├── addon.xml
├── autorun.py
├── cfdecoder.py
├── cfscrape.py
├── config.py
├── default.py
├── fanart.png
├── fshare.png
├── getlink.py
├── htmlement.py
├── icon_play.png
├── icon.png
├── input_form.html
├── listMovie_new.py
├── loadlistitem.py
├── platform.py
├── remove_accents.py
├── resources/
│   ├── 4share.py
│   ├── addon.py
│   ├── advanced_settings_menu.py
│   ├── cache_manager.py
│   ├── cache_utils.py
│   ├── context_menu.py
│   ├── download.py
│   ├── dummy.mp4
│   ├── fonts/
│   ├── fshare.py
│   ├── gsheet.py
│   ├── hdvn.py
│   ├── hdvnsearch.py
│   ├── history_utils.py
│   ├── images/
│   ├── index.php
│   ├── iptv.py
│   ├── kodi_cleaner.py
│   ├── lib/
│   ├── maild.py
│   ├── menu_utils.py
│   ├── password_crypto.py
│   ├── preload.py
│   ├── qr_form.html
│   ├── quick_account.py
│   ├── resetfs.py
│   ├── search.py
│   ├── server_url.py
│   ├── server.py
│   ├── settings.xml
│   ├── skin_installer.py
│   ├── skins/
│   ├── source_installer.py
│   ├── sources/
│   ├── speedfs.py
│   ├── speedtest_result.xml
│   ├── subtitle_fonts.py
│   ├── thuviencine.py
│   ├── tmdb_search.py
│   ├── tvcine.py
│   ├── tvhd.py
│   ├── utils.py
│   └── vmf.py
├── unwise.py
├── urlquick.py
├── version.txt
└── vmfdecode.py
```

## ⚠️ **LƯU Ý QUAN TRỌNG:**

### **✅ BẮT BUỘC XÓA:**
- Tất cả thư mục `__pycache__`
- File `.pyc` (nếu có)

### **✅ KHUYẾN NGHỊ XÓA:**
- File backup (`.bak`)
- File documentation (`.md`)

### **❌ KHÔNG ĐƯỢC XÓA:**
- `addon.xml` (file cấu hình chính)
- `version.txt` (thông tin phiên bản)
- Tất cả file `.py` (source code)
- Thư mục `resources/` và nội dung
- File hình ảnh (`.png`, `.jpg`)

## 🎯 **KẾT QUẢ:**

**Sau khi làm sạch, addon sẽ:**
- ✅ Nhẹ hơn (không có file cache)
- ✅ Sạch sẽ (không có file development)
- ✅ Sẵn sàng cài đặt trên máy khác
- ✅ Hoạt động bình thường với tất cả tính năng

**Addon VietmediaF đã sẵn sàng để đóng gói và phân phối!** 🚀✨
