# KODI Add-on Repository

Đây là một repository chứa các add-on cho KODI. Repository này được thiết kế để dễ dàng thêm và quản lý các add-on.

## Cấu trúc Repository

```
.
├── addons.xml           # File chứa thông tin về tất cả các add-on
├── addons.xml.md5       # File chứa MD5 hash của addons.xml
├── generate_addons_xml.py  # Script để tự động tạo addons.xml và addons.xml.md5
├── plugin.video.hdvn/    # Add-on HDVN
└── repo_vietmediaf_offical/  # Repository add-on
```

## Cách sử dụng

1. Thêm add-on mới:
   - Tạo một thư mục mới cho add-on của bạn (ví dụ: `plugin.video.myaddon`)
   - Tạo file `addon.xml` trong thư mục đó với thông tin về add-on
   - Thêm code Python cho add-on của bạn

2. Cập nhật repository:
   - Chạy script `generate_addons_xml.py` để tự động tạo file `addons.xml` và `addons.xml.md5`
   ```bash
   python generate_addons_xml.py
   ```

3. Cài đặt repository trong KODI:
   - Tạo file `repository.xml` với thông tin về repository của bạn
   - Nén tất cả các file thành file ZIP
   - Cài đặt file ZIP trong KODI

## Tạo Repository Add-on

Để tạo một repository add-on, tạo một thư mục mới (ví dụ: `repository.myaddons`) với cấu trúc sau:

```
repository.myaddons/
├── addon.xml
└── icon.png
```

File `addon.xml` cho repository add-on nên có dạng:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="repository.myaddons"
       name="My Add-ons Repository"
       version="1.0.0"
       provider-name="Your Name">
    <extension point="xbmc.addon.repository">
        <info compressed="false">https://your-domain.com/addons.xml</info>
        <checksum>https://your-domain.com/addons.xml.md5</checksum>
        <datadir zip="true">https://your-domain.com/</datadir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <summary>My Add-ons Repository</summary>
        <description>Repository containing my KODI add-ons</description>
        <platform>all</platform>
    </extension>
</addon>
```

## Lưu ý

- Đảm bảo rằng tất cả các URL trong repository add-on đều có thể truy cập được
- Cập nhật `addons.xml` và `addons.xml.md5` mỗi khi bạn thêm hoặc cập nhật add-on
- Kiểm tra kỹ các add-on trước khi thêm vào repository 