# 🎬 HƯỚNG DẪN LAYOUT 3 CỘT CHO TMDB SEARCH

## 📋 **TỔNG QUAN**

TMDB Search đã được tối ưu hóa để hiển thị theo layout 3 cột:
- **Cột trái**: Thông tin chi tiết (metadata)
- **Cột giữa**: Label chính (tên phim)
- **Cột phải**: Ảnh poster

## 🎯 **CẤU TRÚC LAYOUT**

### **Cột Trái - Thông Tin Chi Tiết:**
- **Title**: Tên phim chính
- **Original Title**: Tên gốc
- **Plot**: Tóm tắt phim với màu sắc
- **Year**: Năm phát hành
- **Rating**: Đánh giá với màu vàng
- **Votes**: Số lượt đánh giá với format đẹp
- **Genre**: Thể loại với màu tím
- **Country**: Quốc gia với màu xanh lá
- **Language**: Ngôn ngữ với màu xanh lá
- **Premiered**: Ngày phát hành với màu xanh dương
- **Status**: Trạng thái
- **Director**: Đạo diễn
- **Writer**: Biên kịch
- **Studio**: Hãng phim
- **MPAA**: Phân loại tuổi
- **Tagline**: Câu tagline
- **Duration**: Thời lượng
- **Episode**: Số tập (TV)
- **Season**: Mùa (TV)
- **User Rating**: Đánh giá người dùng

### **Cột Giữa - Label Chính:**
- **Label**: Tên phim với màu sắc
- **Label2**: TMDB ID
- **Plot**: Tóm tắt phim
- **Plot Outline**: Tóm tắt ngắn

### **Cột Phải - Ảnh Poster:**
- **Thumbnail**: Ảnh poster chính
- **Poster**: Ảnh poster
- **Fanart**: Background
- **Banner**: Banner
- **Landscape**: Ảnh landscape

## 🎨 **TỐI ƯU HÓA ARTWORK**

### **Artwork Properties:**
```python
"art": {
    "poster": poster_url,        # Ảnh poster chính (cột phải)
    "fanart": backdrop_url,      # Background
    "thumb": poster_url,         # Thumbnail
    "banner": poster_url,        # Banner
    "landscape": backdrop_url    # Landscape
}
```

### **Label Format Tối Ưu:**
```python
# Format cho phim: "Tên phim - Tên gốc - (Năm) | Rating | Popularity | Adult"
label = f"[COLOR white]{title}[/COLOR] - [COLOR lightgray]{original_title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"

# Format cho TV: "Tên TV - Tên gốc - (Năm) | Rating | Popularity | Adult"  
label = f"[COLOR lightblue]{title}[/COLOR] - [COLOR lightgray]{original_title}[/COLOR] - [COLOR gray]({release_year})[/COLOR] | {rating_text} {popularity_text} {adult_text}"
```

### **Properties cho Layout:**
```python
"properties": {
    "ThumbnailImage": poster_url,
    "FanartImage": backdrop_url,
    "PosterImage": poster_url,
    "BannerImage": poster_url,
    "LandscapeImage": backdrop_url,
    "Year": str(year),
    "Rating": str(rating),
    "Votes": str(votes),
    "Genre": str(genre),
    "Country": str(country),
    "Language": str(language),
    "Premiered": str(premiered),
    "Status": str(status)
}
```

**Lưu ý**: Chỉ sử dụng các artwork cơ bản mà Kodi hỗ trợ:
- ✅ **poster**: Ảnh poster chính
- ✅ **fanart**: Background
- ✅ **thumb**: Thumbnail
- ✅ **banner**: Banner
- ✅ **landscape**: Landscape
- ❌ **icon**: Không hỗ trợ
- ❌ **clearlogo**: Không hỗ trợ
- ❌ **clearart**: Không hỗ trợ
- ❌ **discart**: Không hỗ trợ
- ❌ **characterart**: Không hỗ trợ

**Lưu ý quan trọng**: Không sử dụng emoji hoặc icon vì Kodi không hiển thị được chúng.

## 🔧 **CÁCH HOẠT ĐỘNG**

### **1. Metadata Mapping:**
- **InfoTag**: Sử dụng `getVideoInfoTag()` để set metadata
- **Properties**: Sử dụng `setProperty()` để set properties
- **Artwork**: Sử dụng `setArt()` để set artwork

### **2. Layout Optimization:**
- **Thumbnail**: Được set làm `thumb` và `poster` cho cột phải
- **Fanart**: Được set làm background
- **Metadata**: Được set đầy đủ cho cột trái
- **Label**: Được format với màu sắc và emoji

### **3. Error Handling:**
- Tất cả operations đều có try-catch
- Xử lý lỗi AttributeError, ValueError, TypeError
- Safe type conversion cho tất cả dữ liệu

## 🎯 **KẾT QUẢ**

### **Layout 3 Cột:**
```
┌─────────────────┬─────────────────┬─────────────────┐
│   THÔNG TIN     │     LABEL       │     POSTER      │
│                 │                 │                 │
│ • Title         │ 🎬 Movie Name   │   [POSTER]      │
│ • Year          │ ⭐ 8.5/10       │                 │
│ • Rating        │ 🔥 Popular      │                 │
│ • Genre         │ 📅 2023         │                 │
│ • Country       │ 🌍 English      │                 │
│ • Language      │ 🎭 Action       │                 │
│ • Director      │ 📝 Plot...      │                 │
│ • Writer        │                 │                 │
│ • Studio        │                 │                 │
│ • Status        │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

## 💡 **LỢI ÍCH**

- ✅ **Layout rõ ràng**: Thông tin được phân bố hợp lý
- ✅ **Dễ đọc**: Mỗi cột có chức năng riêng biệt
- ✅ **Thông tin đầy đủ**: Metadata chi tiết từ TMDB
- ✅ **Visual appeal**: Ảnh poster chất lượng cao
- ✅ **User-friendly**: Dễ dàng quét thông tin

## 🚀 **SỬ DỤNG**

1. **Mở TMDB Search** trong VietMediaF
2. **Nhập từ khóa** tìm kiếm
3. **Xem kết quả** với layout 3 cột
4. **Chọn phim** để xem chi tiết

---

**Lưu ý**: Layout này hoạt động tốt nhất với skin Estuary mặc định của Kodi. Với các skin khác, layout có thể khác một chút nhưng vẫn giữ được cấu trúc 3 cột cơ bản.
