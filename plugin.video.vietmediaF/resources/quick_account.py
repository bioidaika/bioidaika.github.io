import requests
import xbmcgui
import time
from resources.addon import ADDON, ADDON_PATH, notify, alert, logError

def display_quick_account_menu():
    """Hiển thị menu nhập nhanh tài khoản"""
    import sys
    import xbmcplugin
    from resources.utils import add_menu_item
    password_icon = ADDON_PATH + '/resources/images/code_number.png'
    qr_icon = ADDON_PATH + '/resources/images/scan_qr.png'
    settings_icon = ADDON_PATH + '/resources/images/setting_.png'
    handle = int(sys.argv[1])


    add_menu_item(handle, "Nhập bằng mã QR",
                 "plugin://plugin.video.vietmediaF?action=quick_account_qr",
                 False, qr_icon,
                 "Nhập tài khoản Fshare bằng mã QR")


    add_menu_item(handle, "Nhập nhanh bằng Code",
                 "plugin://plugin.video.vietmediaF?action=quick_account_code",
                 False, password_icon,
                 "Nhập nhanh tài khoản Fshare bằng Code")
    add_menu_item(handle, "Nhập từ addon settings",
                 "plugin://plugin.video.vietmediaF?action=__settings__",
                 False, settings_icon,
                 "Nhập thông tin tài khoản Fshare")

    xbmcplugin.endOfDirectory(handle)

def quick_account_code():
    dialog = xbmcgui.Dialog()

    account_code = dialog.numeric(0, "Nhập mã tài khoản Fshare")

    if not account_code:
        notify("Đã hủy nhập code")
        return

    try:
        ADDON.setSetting("account_code", account_code)

        response = requests.post(
            "https://fshare.vip/account_manager/getid.php",
            json={"account_code": account_code},
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "b7f2a9c4-5d8e-4a1f-92e7-3c6b8d9a7f0e",
                "X-Client-ID": "kodiuser"
            }
        )

        if response.status_code != 200:
            alert("Lỗi khi lấy thông tin tài khoản: %s" % response.status_code)
            return

        data = response.json()

        if data.get("status") != "success":
            alert("Lỗi: %s" % data.get('message', 'Không thể lấy thông tin tài khoản'))
            return

        account_data = data.get("data", {})
        email = account_data.get("email", "")
        encrypted_password = account_data.get("encrypted_password", "")

        if not email or not encrypted_password:
            alert("Không tìm thấy thông tin tài khoản hợp lệ")
            return

        from resources.password_crypto import PasswordDecryption
        password_decryptor = PasswordDecryption()
        password = password_decryptor.decrypt(encrypted_password)

        if not password:
            alert("Không thể giải mã mật khẩu")
            return


        ADDON.setSetting('fshare_username', email)
        ADDON.setSetting('fshare_password', password)


        from resources.fshare import updateAcc
        updateAcc()

    except Exception as e:
        alert("Lỗi khi xử lý: %s" % str(e))

def quick_account_qr():
    """Xử lý nhập tài khoản bằng mã QR"""
    import os
    import socket
    import threading
    import json
    import urllib.parse
    import xbmc
    import xbmcvfs
    from http.server import HTTPServer, BaseHTTPRequestHandler

    response = xbmcgui.Dialog().yesno(
        "Nhập tài khoản bằng mã QR",
        "Chú ý Kodi và điện thoại của bạn phải kết nối chung mạng wifi.\nBạn đã sẵn sàng chưa?"
    )
    if not response:
        return

    adv_data = None
    try:
        adv_response = requests.get('https://fshare.vip/adv/qc.json', timeout=5)
        if adv_response.status_code == 200:
            adv_data = adv_response.json()
    except Exception as e:
        xbmc.log(f"Không thể tải quảng cáo: {str(e)}", xbmc.LOGINFO)

    if not adv_data or not isinstance(adv_data, list) or len(adv_data) == 0:
        adv_data = [{
            "name": "Khuyến mãi đặc biệt",
            "expiredDate": "2029-12-31",
            "pilot": "Giảm giá khi mua tài khoản VIP!"
        }]

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    PORT = 8081
    local_ip = get_local_ip()
    server_url = f"http://{local_ip}:{PORT}"
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((local_ip, PORT))
        if result == 0:
            PORT = 8082
            server_url = f"http://{local_ip}:{PORT}"
        sock.close()
    except:
        pass


    html_path = os.path.join(xbmcvfs.translatePath(ADDON_PATH), 'resources', 'qr_form.html')


    adv_name = adv_data[0].get('name', 'Khuyến mãi đặc biệt')
    adv_pilot = adv_data[0].get('pilot', 'Giảm giá khi mua tài khoản VIP!')


    adv_name = adv_name.replace('[COLOR yellow]', '').replace('[/COLOR]', '')

    html_content = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nhập tài khoản Fshare</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333333;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }
        input[type="text"],
        input[type="password"],
        input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #dcdcdc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo img {
            max-width: 150px;
        }
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
            display: none;
        }
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
            display: none;
        }
        .adv-section {
            margin-top: 30px;
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: #ffffff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        .adv-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }
        .adv-content {
            margin-bottom: 15px;
            text-align: center;
        }
        .adv-contact {
            text-align: center;
            padding: 10px;
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            margin-top: 10px;
        }
        .adv-contact a {
            color: #ffffff;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h2>VietmediaF</h2>
        </div>
        <h1>Nhập tài khoản Fshare</h1>
        <form id="accountForm">
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Mật khẩu:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Lưu thông tin</button>
        </form>
        <div id="successMessage" class="success-message">
            Đã lưu thông tin tài khoản thành công! Bạn có thể đóng trang này.
        </div>
        <div id="errorMessage" class="error-message">
            Có lỗi xảy ra khi lưu thông tin tài khoản.
        </div>

        <div class="adv-section" id="advSection">
            <div class="adv-title">{{ADV_NAME}}</div>
            <div class="adv-content">{{ADV_PILOT}}</div>
            <div class="adv-contact">
                Liên hệ Zalo: <a href="https://zalo.me/ngocduc1977" target="_blank">0915134560</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('accountForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {
                showError('Vui lòng nhập đầy đủ thông tin');
                return;
            }

            // Gửi dữ liệu đến server
            fetch('/set_account', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Lỗi kết nối');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    showSuccess();
                } else {
                    showError(data.message || 'Có lỗi xảy ra');
                }
            })
            .catch(error => {
                showError(error.message);
            });
        });

        function showSuccess() {
            document.getElementById('successMessage').style.display = 'block';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('accountForm').style.display = 'none';
        }

        function showError(message) {
            const errorElement = document.getElementById('errorMessage');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            document.getElementById('successMessage').style.display = 'none';
        }
    </script>
</body>
</html>
'''


    os.makedirs(os.path.dirname(html_path), exist_ok=True)


    html_content = html_content.replace('{{ADV_NAME}}', adv_name)
    html_content = html_content.replace('{{ADV_PILOT}}', adv_pilot)


    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


    server_running = True
    account_info = {}


    class AccountHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                if self.path == '/' or self.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()


                    with open(html_path, 'rb') as file:
                        self.wfile.write(file.read())
                elif self.path == '/logo.png':
                    logo_path = os.path.join(xbmcvfs.translatePath(ADDON_PATH), 'icon.png')
                    if os.path.exists(logo_path):
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.end_headers()

                        with open(logo_path, 'rb') as file:
                            self.wfile.write(file.read())

                else:

                    self.send_response(302)
                    self.send_header('Location', '/')
                    self.end_headers()
            except Exception as e:

                notify(f"Lỗi khi xử lý GET: {str(e)}")

                self.send_response(500)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"Lỗi server: {str(e)}".encode('utf-8'))

        def do_POST(self):
            try:
                if self.path == '/set_account':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))


                    nonlocal account_info
                    account_info = {
                        'email': data.get('email', ''),
                        'password': data.get('password', '')
                    }

                    alert(f"Nhận được thông tin tài khoản: {account_info['email']}")
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json; charset=utf-8')
                    self.end_headers()
                    response = json.dumps({'success': True, 'message': 'Đã lưu thông tin thành công'})
                    self.wfile.write(response.encode('utf-8'))
                    nonlocal server_running
                    server_running = False
                    xbmc.executebuiltin('Dialog.Close(all,true)')
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception as e:

                alert(f"Lỗi khi xử lý POST: {str(e)}")

                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                response = json.dumps({'success': False, 'message': f"Lỗi server: {str(e)}"})
                self.wfile.write(response.encode('utf-8'))

        def log_message(self, format, *args):

            return


    server_instance = [None]


    def stop_server():
        nonlocal server_running
        server_running = False

        # Gửi request để đảm bảo server thoát khỏi vòng lặp handle_request
        try:
            import urllib.request
            urllib.request.urlopen(f"http://{local_ip}:{PORT}", timeout=1)
        except:
            pass

        # Đóng server nếu còn tồn tại
        if server_instance[0] is not None:
            try:
                server_instance[0].server_close()
                server_instance[0] = None
                notify("Server đã dừng")
            except Exception as e:
                logError(f"Lỗi khi đóng server: {str(e)}")
                pass


    def run_server():
        try:
            from http.server import HTTPServer

            # Cho phép tái sử dụng địa chỉ
            HTTPServer.allow_reuse_address = True

            try:
                server = HTTPServer((local_ip, PORT), AccountHandler)
                server_instance[0] = server

                # Đặt timeout cho server
                server.timeout = 0.5

                notify(f"Server đã khởi động tại {server_url}")

                # Vòng lặp xử lý request
                while server_running:
                    try:
                        server.handle_request()
                        xbmc.sleep(100)
                    except Exception as e:
                        logError(f"Lỗi khi xử lý request: {str(e)}")
                        if not server_running:
                            break
                        xbmc.sleep(500)  # Tránh vòng lặp vô hạn nếu có lỗi liên tục

                # Đóng server khi thoát vòng lặp
                try:
                    server.server_close()
                    server_instance[0] = None
                    logError("Server đã được đóng bởi vòng lặp chính")
                except Exception as e:
                    logError(f"Lỗi khi đóng server trong vòng lặp chính: {str(e)}")
            except Exception as e:
                alert(f"Lỗi khi tạo server: {str(e)}")
        except Exception as e:
            alert(f"Lỗi khi khởi động server: {str(e)}")


    encoded_url = urllib.parse.quote(server_url)
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?color=000000&bgcolor=FFFFFF&data={encoded_url}&qzone=1&margin=1&size=400x400&ecc=L"


    userdata_path = xbmcvfs.translatePath('special://userdata')
    filename = 'qr_code.png'
    image_path = os.path.join(userdata_path, filename)


    dialog = xbmcgui.Dialog()
    dialog.notification("VietmediaF", "Đang khởi động server local...", xbmcgui.NOTIFICATION_INFO, 3000)


    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()


    class QRWindow(xbmcgui.WindowDialog):
        def __init__(self, qr_image_path, server_url):
            super(QRWindow, self).__init__()
            screen_width = self.getWidth()
            screen_height = self.getHeight()
            window_width = int(screen_width * 0.8)
            window_height = int(screen_height * 0.8)
            x_pos = int((screen_width - window_width) / 2)
            y_pos = int((screen_height - window_height) / 2)
            self.main_background = xbmcgui.ControlImage(0, 0, screen_width, screen_height, '')
            self.main_background.setColorDiffuse('0xAA000000')
            self.addControl(self.main_background)
            self.background = xbmcgui.ControlImage(x_pos, y_pos, window_width, window_height, '')
            self.background.setColorDiffuse('0xFF333333')
            self.addControl(self.background)
            border_size = 2
            self.border_top = xbmcgui.ControlImage(x_pos, y_pos, window_width, border_size, '')
            self.border_top.setColorDiffuse('0xFF3498DB')
            self.addControl(self.border_top)
            self.border_bottom = xbmcgui.ControlImage(x_pos, y_pos + window_height - border_size, window_width, border_size, '')
            self.border_bottom.setColorDiffuse('0xFF3498DB')
            self.addControl(self.border_bottom)

            self.border_left = xbmcgui.ControlImage(x_pos, y_pos, border_size, window_height, '')
            self.border_left.setColorDiffuse('0xFF3498DB')
            self.addControl(self.border_left)

            self.border_right = xbmcgui.ControlImage(x_pos + window_width - border_size, y_pos, border_size, window_height, '')
            self.border_right.setColorDiffuse('0xFF3498DB')
            self.addControl(self.border_right)


            qr_size = int(window_height * 0.6)
            qr_x = x_pos + int(window_width * 0.05)
            qr_y = y_pos + int((window_height - qr_size) / 2)

            self.qr_image = xbmcgui.ControlImage(qr_x, qr_y, qr_size, qr_size, qr_image_path)
            self.addControl(self.qr_image)

            text_x = qr_x + qr_size + int(window_width * 0.05)
            text_y = qr_y
            text_width = window_width - qr_size - int(window_width * 0.15)
            text_height = qr_size

            instruction_bg = xbmcgui.ControlImage(text_x, text_y, text_width, text_height - 40, '')
            instruction_bg.setColorDiffuse('0xFF2C3E50')
            self.addControl(instruction_bg)

            title_label = xbmcgui.ControlLabel(text_x + 10, text_y + 10, text_width - 20, 30, "", 'font14', '0xFFFFFF00')
            self.addControl(title_label)

            instructions = ""

            self.text_label = xbmcgui.ControlTextBox(text_x + 10, text_y + 50, text_width - 20, text_height - 120)
            self.addControl(self.text_label)
            self.text_label.setText(instructions)

            url_label = xbmcgui.ControlLabel(text_x + 10, text_y + text_height - 60, text_width - 20, 30, f"Quét mã QR để truy cập: {server_url}", 'font13', '0xFFFFFF00')
            self.addControl(url_label)

            button_width = 200
            button_height = 40
            button_x = x_pos + (window_width - button_width) // 2
            button_y = y_pos + window_height - button_height - 20

            self.button_bg = xbmcgui.ControlButton(
                button_x, button_y, button_width, button_height,
                "Hủy",
                focusTexture='',
                noFocusTexture='',
                alignment=2,
                textColor='0xFFFFFFFF',
                focusedColor='0xFF3498DB',
                shadowColor='0xFF000000'
            )
            self.addControl(self.button_bg)

            hint_y = button_y - 30
            self.hint_label = xbmcgui.ControlLabel(
                x_pos, hint_y, window_width, 25,
                "Nhấn ESC, Back hoặc nút Hủy để thoát",
                'font12', '0xFFFFFFFF', alignment=2
            )
            self.addControl(self.hint_label)

            self.should_close = False

        def onControl(self, control):
            if control == self.button_bg:
                self.confirm_exit()

        def close(self):
            self.should_close = True
            super(QRWindow, self).close()

        def confirm_exit(self):
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Xác nhận", "Bạn có muốn hủy nhập tài khoản không?"):

                stop_server()
                self.close()

        def onAction(self, action):
            if action.getId() in [7, 9, 10, 92]:
                self.confirm_exit()


    try:
        import urllib.request
        urllib.request.urlretrieve(qr_image_url, image_path)
        alert(f"Quét mã QR hoặc truy cập: [COLOR yellow]{server_url}[/COLOR]")

        qr_window = QRWindow(image_path, server_url)
        def check_server_status():
            nonlocal server_running
            while server_running:
                xbmc.sleep(500)
            if qr_window and not qr_window.should_close:
                qr_window.close()

        status_thread = threading.Thread(target=check_server_status)
        status_thread.daemon = True
        status_thread.start()

        qr_window.doModal()
        if qr_window.should_close:
            server_running = False

        del qr_window
    except Exception as e:
        alert(f"Không thể tạo mã QR: {str(e)}\n\nVui lòng truy cập: {server_url}")

    wait_count = 0
    while server_running and wait_count < 6:
        xbmc.sleep(500)
        wait_count += 1


    stop_server()
    dialog = xbmcgui.Dialog()
    dialog.notification("VietmediaF", "Đã đóng server local", xbmcgui.NOTIFICATION_INFO, 3000)
    if account_info and account_info.get('email') and account_info.get('password'):
        try:
            email = account_info['email']
            password = account_info['password']

            # Lưu thông tin tài khoản vào cài đặt
            ADDON.setSetting('fshare_username', email)
            ADDON.setSetting('fshare_password', password)

            notify("Đã lưu thông tin tài khoản %s" % email)

            # Cập nhật tài khoản
            try:
                from resources.fshare import updateAcc
                success = updateAcc()
                if not success:
                    notify("Đã lưu thông tin nhưng không thể cập nhật tài khoản")
            except Exception as e:
                logError(f"Lỗi khi gọi updateAcc: {str(e)}")
                notify("Đã lưu thông tin nhưng gặp lỗi khi cập nhật tài khoản")

            return True
        except Exception as e:
            logError(f"Lỗi khi lưu thông tin tài khoản: {str(e)}")
            alert(f"Lỗi khi lưu thông tin tài khoản: {str(e)}")
            return False
    else:
        alert("Không nhận được thông tin tài khoản")
        return False
