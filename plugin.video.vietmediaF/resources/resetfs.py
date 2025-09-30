#reset download session fshare
import re, time
import requests
import xbmcgui
import json
from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE

pDialog = None

url = "https://api.maildrop.cc/graphql"
headers = {"authority": "api.maildrop.cc","content-type": "application/json","origin": "https://maildrop.cc","referer": "https://maildrop.cc/","user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0"}
def update_progress_dialog(progress,message):
    global pDialog
    if pDialog:
        pDialog.update(int(progress),message)
def deleteMail(email,email_id):
    data = {"operationName": "DeleteMessage","variables": {"mailbox":email ,"id": email_id},"query": "mutation DeleteMessage($mailbox: String!, $id: String!) {\n  delete(mailbox: $mailbox, id: $id)\n}"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        if response_data['data']['delete'] == True:
            print("deleted")
    else:
        print("Request failed with status code:", response.status_code)
def getMessage(email,email_id):
    data = {
        "operationName": "GetMessage",
        "variables": {
            "mailbox": email,
            "id": email_id
        },
        "query": "query GetMessage($mailbox: String!, $id: String!) {\n  message(mailbox: $mailbox, id: $id) {\n    id\n    subject\n    date\n    headerfrom\n    data\n    html\n    __typename\n  }\n}"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        response_data = response.json()
        data_text = response_data['data']['message']['html']
        regex = r"href=\"(https.*dlsession.*)\"\starget"
        match = re.search(regex,data_text)
        if match:
            session_delete_link = match.group(1)
            return(session_delete_link)

def deleteAllMail(email):
    update_progress_dialog(30,'Clear box')
    data = {
            "operationName": "GetInbox",
            "variables": {"mailbox": email},
            "query": "query GetInbox($mailbox: String!) {\n  ping(message: \"Test\")\n  inbox(mailbox: $mailbox) {\n    id\n    subject\n    date\n    headerfrom\n    __typename\n  }\n  altinbox(mailbox: $mailbox)\n}"
        }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        data_list = response_data['data']['inbox']
        for item in data_list:
            id_mail = item['id']
            subject = item['subject']
            deleteMail(email,id_mail)
            
    
def getlistMail(email):
    time.sleep(15)
    timeout=240
    start_time = time.time()
    i = 1
    
    while time.time() - start_time < timeout:
        update_progress_dialog(65,f'Bắt đầu xử lý lần {i}')
        data = {
            "operationName": "GetInbox",
            "variables": {"mailbox": email},
            "query": "query GetInbox($mailbox: String!) {\n  ping(message: \"Test\")\n  inbox(mailbox: $mailbox) {\n    id\n    subject\n    date\n    headerfrom\n    __typename\n  }\n  altinbox(mailbox: $mailbox)\n}"
        }
        print("Try again: "+str(i))
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            data_list = response_data['data']['inbox']
            
            for item in data_list:
                
                id_mail = item['id']
                subject = item['subject']
                
                if "Xác nhận xóa phiên tải" in subject or "Confirm delete download history" in subject:
                    session_link = getMessage(email,id_mail)
                    print("Reset link: "+session_link)
                    deleteMail(email,id_mail)
                    return (session_link)
        else:
            print("Request failed with status code:", response.status_code)
        time.sleep(15)
        i +=1

    return("No new mail arrived")

def checkvalid(reset_code):
    global pDialog
    pDialog = xbmcgui.DialogProgress()
    
    domainfs = ADDON.getSetting('domainforfs')
    username = ADDON.getSetting('fshare_username')
    password = ADDON.getSetting('fshare_password')
    if not "@" in username:
        username = username+domainfs
    user_mail = username.strip()
    user_pass = password.strip()
    data = {'mail':user_mail , 'reset_code': reset_code}
    pDialog.create(f'Xoá phiên tải {user_mail}', 'Đang thực hiện...')
    response = requests.post('https://fshare.vip/isvalid.php', data=data)
    if response.status_code == 200:
        result = json.loads(response.text)
        if result['result'] == True:
            update_progress_dialog(10,'Thông tin tài khoản hợp lệ')
            resetdl(reset_code)
        else:
            alert("Thông tin tài khoản và mã CODE không hợp lệ")
            exit()
    else:
        alert("Lỗi xác thực thông tin tài khoản")
        exit()

def get_csrf_token(text):
    regex = r"\"csrf-token\" content=\"(.*)\""
    match = re.search(regex, text)
    if match:
        return match.group(1)
    return None
def resetdl(reset_code):
    global pDialog
    base_url = 'https://www.fshare.vn'
    domainfs = ADDON.getSetting('domainforfs')
    username = ADDON.getSetting('fshare_username')
    password = ADDON.getSetting('fshare_password')
    if not username or not password:
        alert("Bạn chưa nhập tài khoản Fshare. Nhập thông tin tài khoản")
        ADDON.openSettings()
    if not "@" in username:
        username = username+domainfs
    user_mail = username.strip()
    user_pass = password.strip()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.0.0'
    }
    try:
        with requests.Session() as session:
            deleteAllMail(reset_code)
            login_url = f"{base_url}/site/login"
            response = session.get(login_url, headers=headers)
            csrf_token = get_csrf_token(response.text)
            if not csrf_token:
                return
            data = {
                "_csrf-app": csrf_token,
                "LoginForm[email]": user_mail,
                "LoginForm[password]": user_pass,
                "LoginForm[rememberMe]": "0"
            }
            response = session.post(login_url, headers=headers, data=data)
            if response.status_code == 200:
                if 'Điều này giúp chứng minh tài khoản Fshare này thuộc về bạn' in response.text:
                    update_progress_dialog(20,'Lấy OTP code...')
                    csrf_token = get_csrf_token(response.text)
                    pattern = r'<input\s+type="text"\s+name="code_token"\s+class="mdc-textfield__input hidden"\s+value="([^"]+)"\s+hidden\s+aria-required="true">'
                    matches = re.search(pattern, response.text, re.DOTALL)
                    if matches:
                        code_token_value = matches.group(1)
                    otp_code = getlistMail(reset_code)
                    pattern = r'<input\s+type="hidden"\s+name="remove_id"\s+value="([^"]+)">'
                    matches = re.search(pattern, response.text)
                    if matches:
                        remove_id_value = matches.group(1)
                    data = {
                        "_csrf-app": csrf_token,
                        "code_otp": otp_code ,
                        "code_token": code_token_value,
                        "LoginForm[email]": user_mail,
                        "LoginForm[password]": user_pass,
                        "LoginForm[rememberMe]": "0",
                        "remove_id": remove_id_value
                    }
                    response = session.post("https://www.fshare.vn/site/verify-otp-limit", data=data)
                    if response.status_code == 200:
                        update_progress_dialog(30,'Lấy OTP thành công')
                    else:
                        notify(f"Login to Fshare not successfully {response.status_code}")
                        return
                update_progress_dialog(35,'Login Fshare thành công')
                
            else:
                alert(f"Login failed with status code: {response.status_code}")
                exit()
            file_manager_url = f"{base_url}/file/manager"
            response = session.get(file_manager_url, headers=headers)
            csrf_token = get_csrf_token(response.text)
            deleteAllMail(reset_code)
            update_progress_dialog(40,'Chuẩn bị lấy link reset')
            time.sleep(5)
            manage_session_url = f"{base_url}/account/manage-download-session"
            data = {"_csrf-app": csrf_token}
            try:
                response = session.post(manage_session_url, data=data)
                if response.status_code == 200:
                    update_progress_dialog(50,'Đã gửi link xác nhận đi')
                    getTokenLink = getlistMail(reset_code)
                    update_progress_dialog(85,'Đã nhận được link reset')
                    if "delete" in getTokenLink:
                        r = session.get(getTokenLink)
                        if r.status_code == 200:
                            #notify("Thành công")
                            update_progress_dialog(90,'Đã làm xong')
                            #return True
                        else:
                            alert(f"Lỗi reset link:{r.status_code}")
                    else:
                        alert("Không lấy được link reset")
                else:
                    alert(f"Lỗi lấy reset link:{response.status_code}")
            except Exception as e:
                notify(f"An error occurred: {str(e)}")
            logout_url = f"{base_url}/site/logout"
            response = session.get(logout_url, headers=headers)
            if response.status_code == 200:
                update_progress_dialog(100,"Logout Fshare")
                
    finally:
        if pDialog:
            pDialog.close()
            pDialog = None
    
        