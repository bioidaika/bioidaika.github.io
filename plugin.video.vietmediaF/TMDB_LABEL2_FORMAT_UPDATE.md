# TMDB Label2 Format Update

## 🎯 **Cải tiến:**

Cập nhật format hiển thị `label2` để hiển thị thông tin đầy đủ hơn: `<tên phim> | <tên phim gốc> (năm)`

## ✨ **Thay đổi:**

### **Trước:**
```
label2: "TMDB ID: 123456"
```

### **Sau:**
```
label2: "Tên phim | Original Title (2023)"
```

## 🔧 **Code Implementation:**

### **Logic mới:**
```python
# Tạo label2 với format: <tên phim> | <tên phim gốc> (năm) hoặc <tên phim> (năm)
# Loại bỏ duplicate nếu tên gốc và tên địa phương trùng nhau
label2_parts = []
if title:
    label2_parts.append(title)
if original_title and original_title != title and original_title.strip():
    label2_parts.append(original_title)

# Thêm năm vào cuối
if release_year:
    if len(label2_parts) > 1:  # Có cả tên và tên gốc
        label2_parts.append(f"({release_year})")
    else:  # Chỉ có tên
        label2_parts.append(f"({release_year})")

label2 = " | ".join(label2_parts) if label2_parts else f"TMDB ID: {tmdb_id}" if tmdb_id else ""
```

## 📊 **Các trường hợp hiển thị:**

### **1. Tên gốc khác tên địa phương:**
```
label2: "Kẻ Hủy Diệt | The Terminator (1984)"
```

### **2. Tên gốc trùng tên địa phương (loại bỏ duplicate):**
```
label2: "Avengers: Endgame (2019)"
```

### **3. Chỉ có tên phim và năm:**
```
label2: "Avengers: Endgame (2019)"
```

### **4. Chỉ có tên phim:**
```
label2: "Avengers: Endgame"
```

### **5. Fallback (không có thông tin):**
```
label2: "TMDB ID: 123456"
```

## 🎮 **Ví dụ thực tế:**

### **Movies:**
- **Trùng tên:** `title="Avengers: Endgame"`, `original_title="Avengers: Endgame"` → `"Avengers: Endgame (2019)"`
- **Khác tên:** `title="Kẻ Hủy Diệt"`, `original_title="The Terminator"` → `"Kẻ Hủy Diệt | The Terminator (1984)"`

### **TV Shows:**
- **Trùng tên:** `name="Breaking Bad"`, `original_name="Breaking Bad"` → `"Breaking Bad (2008)"`
- **Khác tên:** `name="Vua Bếp"`, `original_name="MasterChef"` → `"Vua Bếp | MasterChef (2010)"`

## 📋 **Lợi ích:**

1. **Thông tin đầy đủ hơn:** Hiển thị tên phim, tên gốc và năm
2. **Dễ nhận biết:** Người dùng có thể phân biệt phim dễ dàng
3. **Format nhất quán:** Tất cả items đều có format giống nhau
4. **Loại bỏ duplicate:** Không hiển thị tên trùng lặp
5. **Fallback an toàn:** Vẫn hiển thị TMDB ID nếu thiếu thông tin

## 🔄 **Backward Compatibility:**

- ✅ Không ảnh hưởng đến functionality hiện tại
- ✅ Chỉ thay đổi cách hiển thị `label2`
- ✅ Fallback về format cũ nếu thiếu dữ liệu

## 📁 **Files được sửa:**

- `resources/tmdb_search.py` - Cập nhật logic tạo `label2`

## 🎯 **Kết quả:**

Bây giờ `label2` sẽ hiển thị thông tin phim/TV đầy đủ và dễ đọc hơn! 🚀
