import sys,re
import os, time, json
import remove_accents
import xbmcplugin, xbmcaddon, xbmcgui, xbmc, xbmcvfs
from resources.addon import alert, notify, TextBoxes, ADDON, ADDON_ID, ADDON_PROFILE, LOG, PROFILE
from config import VIETMEDIA_HOST
from resources import fshare
import urllib.parse


ADDON_NAME = ADDON.getAddonInfo("name")
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)
VIEWXXX = ADDON.getSetting('view_xxx')
VIEWMODE = ADDON.getSetting('view_mode')
HANDLE = int(sys.argv[1])
CACHE_TIMEOUT = 300

def debug(text):
    
    filename = os.path.join(PROFILE_PATH, 'list.dat')
    if not os.path.exists(filename):
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(text)
    else:
        with open(filename, "wb") as f:
            f.write(text.encode("UTF-8"))
            

def apply_info_to_listitem(list_item, info_dict):
    """Apply video metadata using InfoTagVideo (Kodi v20+). Fallback to setInfo on error.
    Also mirrors key fields via setInfo so skins (e.g., Estuary) render duration/premiered in plugin directories.
    """
    try:
        tag = list_item.getVideoInfoTag()
        media_type = info_dict.get('mediatype')
        if media_type:
            tag.setMediaType(media_type)
        title = info_dict.get('title')
        if title:
            tag.setTitle(title)
        original_title = info_dict.get('originaltitle')
        if original_title:
            tag.setOriginalTitle(original_title)
        year = info_dict.get('year')
        if year:
            try:
                tag.setYear(int(year))
            except Exception:
                pass
        plot = info_dict.get('plot')
        if plot:
            tag.setPlot(plot)
        duration = info_dict.get('duration')
        if duration:
            try:
                tag.setDuration(int(duration))
            except Exception:
                pass
        rating = info_dict.get('rating')
        if rating is not None:
            try:
                tag.setRating(float(rating))
            except Exception:
                pass
        votes = info_dict.get('votes')
        if votes:
            try:
                tag.setVotes(int(votes))
            except Exception:
                pass
        tvshowtitle = info_dict.get('tvshowtitle')
        if tvshowtitle:
            tag.setTvShowTitle(tvshowtitle)
        # Mirror minimal keys for skin display in directory views
        minimal = {}
        if duration:
            try:
                minimal['duration'] = int(duration)
            except Exception:
                pass
        premiered = info_dict.get('premiered')
        if premiered:
            minimal['premiered'] = premiered
        if year:
            minimal['year'] = int(year) if isinstance(year, int) or (isinstance(year, str) and year.isdigit()) else year
        if minimal:
            list_item.setInfo('video', minimal)
    except Exception as e:
        xbmc.log(f"[VietmediaF] InfoTagVideo apply failed, fallback to setInfo: {e}", xbmc.LOGINFO)
        list_item.setInfo("video", info_dict)


def check_lock(item_path):

    filename = os.path.join(PROFILE_PATH, 'lock_dir.dat')
    if not os.path.exists(filename):
        return False
    with open(filename, "r") as f:
        lines = f.readlines()
    return (item_path + "\n") in lines
def list_item_main(data):
    debug(str(data))
    if data.get("content_type") and len(data["content_type"]) > 0:
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.setContent(HANDLE, data["content_type"])
    listitems = list(range(len(data["items"])))
    for i, item in enumerate(data["items"]):
        lock_url = item["path"].replace("plugin://%s" % ADDON_ID, VIETMEDIA_HOST)
        lock_url = re.sub('\?', '/?', lock_url)
        path = item["path"]
        label = item["label"]
        filterStr = ["xxx", "sex", "jav", "cap 3", "18+", "20+"]
        if check_lock(lock_url):label = "*" + label
        listItem = xbmcgui.ListItem(label=label, label2=item["label2"])
        if VIEWXXX == 'false':
            label_ = label.lower()
            if '18+' in label_ or 'xxx' in label_ or 'XXX' in label_ or 'cấp 3' in label or 'jav' in label_ or 'JAV' in label_ or '+' in label_ or 'sex' in label_ or 'SEX' in label_ or 'fuck' in label_ or '20+' in label_:
                # listItem = xbmcgui.ListItem(label='[I]Nội dung cần thiết lập để xem[/I]', label2='', iconImage='', thumbnailImage='')
                listItem = xbmcgui.ListItem(label='[I]Nội dung cần thiết lập để xem[/I]',label2=item["label2"])
                path = 'plugin://plugin.video.vietmediaF?action=browse&node_id=75'
                
            else:
                # listItem = xbmcgui.ListItem(label=label, label2=item["label2"], iconimage=item["icon"], thumbnailImage=item["thumbnail"]) 
                listItem = xbmcgui.ListItem(label=label, label2=item["label2"]) 
        if VIEWXXX == 'true':
            listItem = xbmcgui.ListItem(label=label, label2=item["label2"])

        if item.get("info"):
            apply_info_to_listitem(listItem, item["info"]) 
        
        if item.get("art"):
            listItem.setArt(item["art"])
        
        listItem.setArt({'thumb': item["thumbnail"], 'icon': item["thumbnail"], 'poster': item["icon"]})
        # context_menu
        menu_context = []
        title = item["label"]
        title = re.sub('\[.*?]', '', title)
        title = re.sub('\s', '-', title)
        title = re.sub('--', '-', title)
        title = re.sub('--', '-', title)
        title = re.sub('[\\/*?:"<>|#]', "", title)
        title = remove_accents.remove_accents(title)
        if item.get("context_menu"):
            listItem.addContextMenuItems(item["context_menu"])
        elif "_phimle_" in path:
            command = 'RunPlugin(%s&d=select_source_phimle)' % item["path"]
            menu_context.append(('Thay đổi nguồn phim', command,))
        elif "_phimbo_" in path:
            command = 'RunPlugin(%s&d=select_source_phimbo)' % item["path"]
            menu_context.append(('Thay đổi nguồn phim', command,))
        elif "fshare.vn" in path:
            command = 'RunPlugin(%s&d=__addtofav__&file_name=%s)' % (item["path"], title)
            menu_context.append(('[COLOR yellow]Thêm vào Yêu Thích Fshare[/COLOR]', command,))
            command = 'RunPlugin(%s&d=__removeFromfav__&file_name=%s)' % (item["path"], title)
            menu_context.append(('[COLOR yellow]Xoá khỏi Yêu Thích Fshare[/COLOR]', command,))
            command = 'RunPlugin(%s&d=__qrlink__)' % item["path"]
            menu_context.append(('[COLOR yellow]Play on Mobile[/COLOR]', command,))
            if "file" in path:
                command = 'RunPlugin(%s&d=__download__)' % item["path"]
                menu_context.append(('[COLOR yellow]Download[/COLOR]', command,))
        command = 'RunPlugin(%s&d=__lock__)' % item["path"]
        menu_context.append(('Khoá mục này', command,))
        command = 'RunPlugin(%s&d=__unlock__)' % item["path"]
        menu_context.append(('Mở khoá mục này', command,))
        command = 'RunPlugin(%s&d=__settings__)' % item["path"]
        menu_context.append(('[COLOR yellow]Addon Setting[/COLOR]', command,))
        
        listItem.addContextMenuItems(menu_context)
        listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
        if item.get("properties"):
            for k, v in item["properties"].items():
                listItem.setProperty(k, v)
        listitems[i] = (path, listItem, not item["is_playable"])
        # listitems[i] = (path, listItem)
    if xbmc.getSkinDir() == "skin.arctic.zephyr.2.resurrection.mod":
        if data.get("content_type") and data["content_type"] == "movies":
            xbmc.log(f"[VietmediaF] Using viewmode 528 for movies", xbmc.LOGINFO)
            xbmc.executebuiltin("Container.SetViewMode(528)")
        else:
            xbmc.log(f"[VietmediaF] Using viewmode {VIEWMODE}", xbmc.LOGINFO)
    xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

def list_item_main_cache(data):
    #data = json.loads(data)  # Chuyển đổi chuỗi JSON thành danh sách Python
    
    items = data["items"]
    for item in items:
        list_item = xbmcgui.ListItem(label=item["label"])
        apply_info_to_listitem(list_item, item["info"]) 
        list_item.setArt({'thumb': item["thumbnail"], 'icon': item["icon"]})
        list_item.setProperty('IsPlayable', 'true' if item["is_playable"] else 'false')
        xbmcplugin.addDirectoryItem(handle=HANDLE, url=item["path"], listitem=list_item, isFolder=not item["is_playable"])
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_item(data):
    
    if data.get("content_type") and len(data["content_type"]) > 0:
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.setContent(HANDLE, data["content_type"])

    listitems = list(range(len(data["items"])))
    
    for i, item in enumerate(data["items"]):
        lock_url = item["path"]
        lock_url = re.sub('\?', '/?', lock_url)
        path = item["path"]
        label = item["label"]
        
        if "@" in label:label = label.replace("@", "")
        
        if check_lock(lock_url):
            label = "*" + label
        listItem = xbmcgui.ListItem(
            label=label, label2=item["label2"]) 
        if item.get("info"):
            apply_info_to_listitem(listItem, item["info"]) 
        if item.get("stream_info"):
            for type_, values in item["stream_info"].items():
                listItem.addStreamInfo(type_, values)
        if item.get("art"):
            listItem.setArt(item["art"])
            
        listItem.setArt({'thumb': item["thumbnail"], 'icon': item["thumbnail"], 'poster': item["icon"]})
        menu_context = []
        if item.get("context_menu"):
            listItem.addContextMenuItems(item["context_menu"]) 
        if "fshare" in path:
            command = 'RunPlugin(%s&d=__addtofav__)' % (item["path"]) 
            menu_context.append(('Thêm vào Yêu Thích Fshare', command,))
            command = 'RunPlugin(%s&d=__removeFromfav__)' % (item["path"]) 
            menu_context.append(('Xoá Yêu Thích Fshare', command,))
            command = 'RunPlugin(%s&d=__lock__)' % item["path"]
            menu_context.append(('Khoá mục này', command,))
            command = 'RunPlugin(%s&d=__unlock__)' % item["path"]
            menu_context.append(('Mở khoá mục này', command,))
            command = 'RunPlugin(%s&d=__qrlink__)' % item["path"]
            menu_context.append(('[COLOR yellow]QR Link[/COLOR]', command,))
            command = 'RunPlugin(%s&d=__removeHistory__)' % (item["path"]) 
            menu_context.append(('Xoá lịch sử dòng này', command,))
            command = 'RunPlugin(%s&d=__removeAllHistory__)' % (item["path"]) 
            menu_context.append(('Xoá tất cả lịch sử', command,))
        else:
            command = 'RunPlugin(%s&d=__removeHistory__)' % (item["path"]) 
            menu_context.append(('Xoá lịch sử dòng này', command,))
            command = 'RunPlugin(%s&d=__removeAllHistory__)' % (item["path"]) 
            menu_context.append(('Xoá tất cả lịch sử', command,))
            command = 'RunPlugin(%s&d=__lock__)' % item["path"]
            menu_context.append(('Khoá mục này', command,))
            command = 'RunPlugin(%s&d=__unlock__)' % item["path"]
            menu_context.append(('Mở khoá mục này', command,))
            
        
        listItem.addContextMenuItems(menu_context)
        listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
        if item.get("properties"):
            for k, v in item["properties"].items():
                listItem.setProperty(k, v)
        listitems[i] = (path, listItem, not item["is_playable"]) 
    
    xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

def list_item_watched_history(data):
    if data.get("content_type") and len(data["content_type"]) > 0:
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.setContent(HANDLE, data["content_type"])

    listitems = list(range(len(data["items"])))
    
    for i, item in enumerate(data["items"]):
        lock_url = item["path"]
        lock_url = re.sub('\?', '/?', lock_url)
        path = item["path"]
        label = item["label"]
        
        if "@" in label:label = label.replace("@", "")
        
        if check_lock(lock_url):
            label = "*" + label
        listItem = xbmcgui.ListItem(
            #label=label, label2=item["label2"], iconImage=item["icon"], thumbnailImage=item["thumbnail"]) 
            label=label, label2=item["label2"]) 
        if item.get("info"):
            apply_info_to_listitem(listItem, item["info"]) 
        if item.get("stream_info"):
            for type_, values in item["stream_info"].items():
                listItem.addStreamInfo(type_, values)
        if item.get("art"):
            listItem.setArt(item["art"])
            
        listItem.setArt({'thumb': item["thumbnail"], 'icon': item["thumbnail"], 'poster': item["icon"]})
        menu_context = []
        if item.get("context_menu"):
            listItem.addContextMenuItems(item["context_menu"]) 
        command = 'RunPlugin(%s&d=__removeAllWatchedHistory__)' % (item["path"]) 
        menu_context.append(('[COLOR yellow]Xoá lịch sử xem phim[/COLOR]', command,))
        if "fshare" in path:
            command = 'RunPlugin(%s&d=__addtofav__)' % (item["path"]) 
            menu_context.append(('Thêm vào Yêu Thích Fshare', command,))
            command = 'RunPlugin(%s&d=__removeFromfav__)' % (item["path"]) 
            menu_context.append(('Xoá Yêu Thích Fshare', command,))
        
        command = 'RunPlugin(%s&d=__lock__)' % item["path"]
        menu_context.append(('Khoá mục này', command,))
        command = 'RunPlugin(%s&d=__unlock__)' % item["path"]
        menu_context.append(('Mở khoá mục này', command,))
        command = 'RunPlugin(%s&d=__qrlink__)' % item["path"]
        menu_context.append(('[COLOR yellow]QR Link[/COLOR]', command,))
        
        
        listItem.addContextMenuItems(menu_context)
        listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
        if item.get("properties"):
            for k, v in item["properties"].items():
                listItem.setProperty(k, v)
        listitems[i] = (path, listItem, not item["is_playable"]) 
    
    xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)

def list_item_search_history(data):
    if data.get("content_type") and len(data["content_type"]) > 0:
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_DATE)
        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.setContent(HANDLE, data["content_type"])

    listitems = list(range(len(data["items"])))
    
    for i, item in enumerate(data["items"]):
        lock_url = item["path"]
        lock_url = re.sub('\?', '/?', lock_url)
        path = item["path"]
        label = item["label"]
        
        if "@" in label:label = label.replace("@", "")
        
        if check_lock(lock_url):
            label = "*" + label
        listItem = xbmcgui.ListItem(
            #label=label, label2=item["label2"], iconImage=item["icon"], thumbnailImage=item["thumbnail"]) 
            label=label, label2=item["label2"]) 
        if item.get("info"):
            apply_info_to_listitem(listItem, item["info"]) 
        if item.get("stream_info"):
            for type_, values in item["stream_info"].items():
                listItem.addStreamInfo(type_, values)
        if item.get("art"):
            listItem.setArt(item["art"])
            
        listItem.setArt({'thumb': item["thumbnail"], 'icon': item["thumbnail"], 'poster': item["icon"]})
        listItem.setProperty("isPlayable", item["is_playable"] and "true" or "false")
        if item.get("properties"):
            for k, v in item["properties"].items():
                listItem.setProperty(k, v)
        listitems[i] = (path, listItem, not item["is_playable"]) 
    
    xbmcplugin.addDirectoryItems(HANDLE, listitems, totalItems=len(listitems))
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True, updateListing=False, cacheToDisc=True)