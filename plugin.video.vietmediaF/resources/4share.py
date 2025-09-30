import re, json, os, io
import requests,xbmcvfs
import time
import xbmcplugin, xbmcaddon, xbmcgui, xbmc, xbmcvfs
from addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)


useragent = 'kodivietmediaf-K58W6U'
domainfs = ADDON.getSetting('domainforfs')#domain mail
username = ADDON.getSetting('4share_username')
password = ADDON.getSetting('4share_password')



def debug(text):
    filename = os.path.join(PROFILE_PATH, "fshare.dat" )
    if not os.path.exists(filename):
        with open(filename,"w+") as f:
            f.write(text)
    else:
        with open(filename, "a") as f:
            f.write(text+'\n')

def login():
    if not username or not password:
        alert("Bạn chưa nhập tài khoản 4share. Nhập thông tin tài khoản")
        ADDON.openSettings()
    username = username.strip()
    password = password.strip()
    querystring = {"cmd":"get_token"}
    payload = {"username": username,"password": password}
    response = requests.post(url_get_token, data = payload,params=querystring)
    json_data = json.loads(response.content)
    token_4s = json_data['payload']
    if 'Not valid' in token_4s:
        line = "User name: [COLOR yellow]%s[/COLOR]\n" % username
        line += "Password: [COLOR yellow]%s[/COLOR]" % password
        alert(line,title="Kiểm tra lại thông tin")
        user_choice = dialog.yesno('Nhập tài khoản', 'Bạn muốn đến Addon Setting luôn không?')
        if user_choice:
            ADDON.openSettings()
        else:return
    else:
        ADDON.setSetting(id="session4s",value=token_4s)
    return token_4s
    
def logout():
    header = {'Cookie' : 'session_id=' + session_id}
    r = requests.get('https://api.fshare.vn/api/user/logout',headers=header)

def getUserInfo(token):
    headers = {"accesstoken01":token_4s}
    r = requests.get(url_get_user_information,headers=headers)
    #check_json_data = validateJSON(r.content)
    json_data = json.loads(r.content)
    
def isvalid(token):
    
def get_download_link(token,session_id,link):
    payload = json.dumps({
      "zipflag": 0,
      "url": link,
      "password": "",
      "token": token
    })
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
      'User-Agent': 'kodivietmediaf-K58W6U',
      'Authorization': 'Bearer efdf39c90189ddfbff339ae344c28db5f6c11885',
      'Cookie': 'session_id='+session_id
    }
    r = requests.post(download_api, headers=headers, data=payload)
    jstr = json.loads(r.content)
    if r.status_code == 404:
        alert("Link này không tồn tại hoặc bị xoá")
    if r.status_code == 201:
        alert("Tài khoản chưa đăng nhập")
    if r.status_code == 200:
        link_download = jstr["location"]
        return (link_download)
def homeFolder(token,session_id):
    url = "https://api.fshare.vn/api/fileops/list?pageIndex=0&dirOnly=0&limit=100&path="
    headers = {
          'useragent': 'kodivietmediaf-K58W6U',
          'Cookie': 'session_id=%s' % session_id
        }
    r = requests.get(url, headers=headers)
    jstr = json.loads(r.content)
    for i in jstr:
        name = jstr["name"]
        linkcode = jstr["linkcode"]
        ftype = jstr["type"]
        if ftype == 0:isFolder = True
        if ftype == 1:isFolder = False
        size = jstr["size"]
        
        item = xbmcgui.ListItem(label=name, path=link)
        item.setInfo(type='Video', infoLabels={'size': size})
        item.setArt({'thumb': f_icon, 'icon': f_icon})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=isFolder)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
def getListFolder(token,session_id,link):
    payload = json.dumps({
          "token": token,
          "url": link,
          "dirOnly": 0,
          "pageIndex": 0,
          "limit": 100
        })
    headers = {
          'Content-Type': 'application/json',
          'useragent': useragent,
          'Cookie': 'session_id=%s' % session_id
        }
    r = requests.post("https://api.fshare.vn/api/fileops/getFolderList", headers=headers, data=payload)
    jstr = json.loads(r.content)
    context_menu_items = []
    for i in jstr:
        name = jstr["name"]
        furl = jstr["furl"]
        link = 'plugin://plugin.video.vietmediaF?action=play&url=%s' % furl
        ftype = jstr["type"]
        if ftype == 0:isFolder = True
        if ftype == 1:isFolder = False
        size = jstr["size"]
        item = xbmcgui.ListItem(label=name, path=link)
        item.setInfo(type='Video', infoLabels={'size': size})
        item.setArt({'thumb': f_icon, 'icon': f_icon})
        context_menu_items.append(('Thêm vào yêu thích Fshare', 'RunPlugin(%s?action=play&d=__addtofav__&url=%s)' % (sys.argv[0], link)))
        item.addContextMenuItems(context_menu_items)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=item, isFolder=isFolder)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
def fileInFolder(url):
    token,session_id = check_session()
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Vietmediaf /Kodi1.1.99-092019',
        'Fshare-Session-Id': session_id
    }
    json_data = {'token': token,'url': url}
    r = requests.post('https://api.fshare.vn/api/fileops/getTotalFileInFolder',headers=headers,json=json_data)
    if (r.status_code) == 200:
        jsdata = json.loads(r.content)
        return(jsdata["total"])
    else:
        return "-"
        
def isvalid(session_id):
    useragent = 'kodivietmediaf-K58W6U'
    headers = {
          'useragent': useragent,
          'Cookie': 'session_id=%s' % session_id
        }
    r = requests.get("https://api.fshare.vn/api/user/get",headers=headers)
    
    if (r.status_code) == 200:
        return True
    return False
def getAccFshare():
    username = ADDON.getSetting('fshare_username')
    password = ADDON.getSetting('fshare_password')
    if not username or not password:
        alert("Bạn chưa nhập tài khoản Fshare. Nhập thông tin tài khoản")
        ADDON.openSettings()
        username = ADDON.getSetting('fshare_username')
        password = ADDON.getSetting('fshare_password')
    if "@" not in username:
        domainforfs = ADDON.getSetting('domainforfs')
        username = username + domainforfs
    
    return (username,password)
def getBackupAcc():
    username_backup = ADDON.getSetting('username_backup')
    password_backup = ADDON.getSetting('password_backup')
    backup_option_fshare = ADDON.getSetting('backup_option_fshare')
    if backup_option_fshare == "true":
            username_backup,password_backup = getAccFshare()
            
    else:
        if not username_backup or not password_backup:
            alert("Bạn chưa nhập [COLOR yellow]tài khoản Backup[/COLOR]. Nhập thông tin tài khoản")
            ADDON.openSettings()
            backup_option_fshare = ADDON.getSetting('backup_option_fshare')
            if backup_option_fshare == "true":
                username_backup,password_backup = getAccFshare()
                
            else:
                username_backup = ADDON.getSetting('username_backup')
                password_backup = ADDON.getSetting('password_backup')
                if "@" not in username_backup:
                    domainforbackup = ADDON.getSetting('domainforbackup')
                    username_backup = username_backup+domainforbackup
                    
    return (username_backup,password_backup)
        
def check_session():
    username = ADDON.getSetting('fshare_username')
    if not "@" in username:
        username = username+domainfs
    password = ADDON.getSetting('fshare_password')
    token = ADDON.getSetting('tokenfshare')
    session_id = ADDON.getSetting('sessionfshare')
    timelog = ADDON.getSetting('timelog')
    if not username or not password:
        alert("Bạn chưa nhập tài khoản Fshare. Nhập thông tin tài khoản")
        ADDON.openSettings()
    if not token or not session_id:
        token, session_id = login()
        ADDON.setSetting(id="tokenfshare", value=token)
        ADDON.setSetting(id="sessionfshare", value=session_id)
    elif not isvalid(session_id):
        token, session_id = login()
        ADDON.setSetting(id="tokenfshare", value=token)
        ADDON.setSetting(id="sessionfshare", value=session_id)
    return (token,session_id)
def get_fshare_file_info(url):
    if "plugin" in url:
        regex = r"url=([^&]+)"
        match = re.search(regex,url)
        if match:
            url = match.group(1)
    token,session_id = check_session()
    data   = '{"token" : "%s", "url" : "%s"}' % (token,url)
    header = {'User-Agent': useragent,'Cookie' : 'session_id=' + session_id }
    r = requests.post('https://118.69.164.19/api/fileops/get',headers=header,data=data,verify=False)
    try:
        jstr = json.loads(r.content)
        name = jstr['name']
        file_type=jstr['file_type']
        size=jstr['size']
        
        return(name,file_type,size)
    except json.JSONDecodeError:
        return ("File không tồn tại","","")
