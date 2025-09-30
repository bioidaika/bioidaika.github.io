import xbmcgui, xbmc
import xbmcaddon
import xbmcvfs
import loadlistitem
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket, time
import threading, os
import urllib.parse
from resources import fshare
from addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE

def play_url(url):
    token, session_id = fshare.check_session()
    url = fshare.get_download_link(token, session_id, url)
    # Cho phép phát tất cả các định dạng file mà Kodi hỗ trợ
    # Không kiểm tra phần mở rộng của file
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    listitem = xbmcgui.ListItem(path=url)
    playlist.add(url, listitem)
    xbmc.Player().play(playlist)

class AddonInputHandler(BaseHTTPRequestHandler):
    input_form_completed = False
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with xbmcvfs.File(xbmcvfs.translatePath('special://home/addons/plugin.video.vietmediaF/sendurl.html'), 'r') as file:
            content = file.read()
        content = content.replace('localhost', get_ip_address())
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')
        post_data = post_data.split('&')
        form_data = {}
        for item in post_data:
            key, value = item.split('=')
            form_data[key] = urllib.parse.unquote(value.strip())

        url = form_data.get('url')
        url = url.strip()
        if not url.startswith("https://"):
            url = url.replace('http','https')
            url = f"https://{url}"
        if not url:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1 style="font-size: 100%; color: red;">URL is not provided.</h1>'.encode('utf-8'))
            return
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<h1 style="font-size: 100%; color: red;">Done.</h1>'.encode('utf-8'))
        self.wfile.close()
        xbmc.executebuiltin('Dialog.Close(all, true)')
        if "fshare.vn/folder/" in url:
            alert("Phiên bản này chưa hỗ trợ folder")
        if "fshare.vn/file/" in url:
            OnOffHistoryWatching = xbmcaddon.Addon().getSettingBool("OnOffHistoryWatching")
            if OnOffHistoryWatching:
                watchingHistory(url)
            play_url(url)
        global httpd
        httpd.shutdown()



def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def start_server():
    server_address = ('', 7777)
    global httpd
    httpd = HTTPServer(server_address, AddonInputHandler)
    httpd.serve_forever()


def display_and_close_dialog(waiting_time,url):
    progress = xbmcgui.DialogProgress()
    progress.create('Chuẩn bị nhập liệu', "Nhập liệu")
    start_time = time.time()
    while time.time() - start_time < waiting_time:
        progress.update(int((time.time() - start_time) / waiting_time * 100), f'[COLOR yellow]CHÚ Ý: ĐIỆN THOẠI VÀ KODI PHẢI CÙNG SỬ DỤNG HỆ THỐNG MẠNG.[/COLOR]\nVui lòng dùng camera điện thoại quét QR CODE hoặc mở địa chỉ: [COLOR yellow]{url}[/COLOR]. \n{int(waiting_time - (time.time() - start_time))} giây...')
        time.sleep(0.1)
    progress.close()

def show_input_form():
    back_pressed = False
    try:
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()

        ip_address = get_ip_address()
        url = f'http://{ip_address}:7777/'
        image_url = f"https://api.qrserver.com/v1/create-qr-code/?color=000000&bgcolor=FFFFFF&data={url}&qzone=1&margin=1&size=400x400&ecc=L"

        userdata_path = xbmcvfs.translatePath('special://userdata')
        filename = 'qr_code.png'
        image_path = os.path.join(userdata_path, filename)

        try:
            urllib.request.urlretrieve(image_url, image_path)
        except Exception as e:
            notify("Lỗi khi tải xuống hình ảnh:", str(e))
            exit()

        waiting_time = 7
        display_and_close_dialog(waiting_time, url)
        xbmc.executebuiltin('ShowPicture(%s)' % (image_path))

    except Exception as e:
        notify("Lỗi khi hiển thị form:", str(e))
        exit()
