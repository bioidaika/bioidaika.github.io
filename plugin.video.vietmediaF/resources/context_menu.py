import urllib.parse
import xbmc
import xbmcgui
import re
import remove_accents
import sys

def is_main_menu():
    """Kiểm tra xem đang hiển thị menu chính hay không"""
    current_url = sys.argv[0] + sys.argv[2]
    xbmc.log(f"[VietmediaF] Current URL: {current_url}", level=xbmc.LOGINFO)

    
    
    
    return ("?action=menu" in current_url or
            current_url.endswith("plugin.video.vietmediaF/") or
            "main_menu=true" in current_url or
            ("?" not in current_url and current_url.endswith("plugin.video.vietmediaF")) or
            current_url == "plugin://plugin.video.vietmediaF")

def get_context_menu_for_main_menu(item, index):
    """Tạo context menu cho các item trong menu chính"""
    menu_context = []

    
    permission = item.get("permission", "not_allowed")

    
    command = 'RunPlugin(%s&d=__lock__)' % item["path"]
    menu_context.append(('[COLOR yellow]Khoá/ Mở khoá mục[/COLOR]', command,))

    command = 'Addon.OpenSettings(plugin.video.vietmediaF)'
    menu_context.append(('[COLOR yellow]Addon Settings[/COLOR]', command,))

    
    command = 'RunPlugin(%s&d=__reorder_menu_item__&path=%s)' % (item["path"], urllib.parse.quote_plus(item["path"]))
    menu_context.append(('[COLOR yellow]Thay đổi thứ tự hiển thị[/COLOR]', command,))

    
    if permission == "allowed":
        command = 'RunPlugin(%s&d=__remove_menu_item__&path=%s)' % (item["path"], urllib.parse.quote_plus(item["path"]))
        menu_context.append(('[COLOR yellow]Xóa khỏi menu chính[/COLOR]', command,))

    
    if index == 0:
        command = 'RunPlugin(%s&d=__reset_main_menu__)' % item["path"]
        menu_context.append(('[COLOR red]Khôi phục menu mặc định[/COLOR]', command,))

    
    xbmc.log(f"[VietmediaF] Context menu for main menu item {item.get('label')}: {menu_context}", level=xbmc.LOGINFO)

    return menu_context

def get_context_menu_for_other_menu(item):
    """Tạo context menu cho các item không phải trong menu chính"""
    menu_context = []

    
    command = 'RunPlugin(%s&d=__add_to_main_menu__)' % item["path"]
    menu_context.append(('[COLOR yellow]Thêm vào menu chính[/COLOR]', command,))

    return menu_context

def get_context_menu_for_specific_item(item, path, title):
    """Tạo context menu cho các loại item cụ thể"""
    menu_context = []

    if "_phimle_" in path:
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

    return menu_context

def check_if_item_in_main_menu(item):
    """Kiểm tra xem một item đã tồn tại trong menu chính chưa"""
    
    from resources.menu_utils import get_main_menu

    
    current_path = item.get("path", "")
    if not current_path:
        return False

    
    xbmc.log(f"[VietmediaF] Checking if item is in main menu: {current_path}", level=xbmc.LOGINFO)

    
    current_path = current_path.split('&d=')[0] if '&d=' in current_path else current_path

    
    main_menu_items = get_main_menu()

    
    for main_item in main_menu_items:
        main_item_path = main_item.get("path", "")
        
        main_item_path = main_item_path.split('&d=')[0] if '&d=' in main_item_path else main_item_path

        xbmc.log(f"[VietmediaF] Comparing with main menu item: {main_item_path}", level=xbmc.LOGDEBUG)

        if main_item_path == current_path:
            xbmc.log(f"[VietmediaF] Item found in main menu", level=xbmc.LOGINFO)
            return True

    xbmc.log(f"[VietmediaF] Item not found in main menu", level=xbmc.LOGINFO)
    return False

def get_common_context_menu(item, is_in_main_menu):
    """Tạo context menu chung cho tất cả các item"""
    menu_context = []

    
    command = 'RunPlugin(%s&d=__lock__)' % item["path"]
    menu_context.append(('Khoá mục này', command,))
    command = 'RunPlugin(%s&d=__unlock__)' % item["path"]
    menu_context.append(('Mở khoá mục này', command,))

    
    if is_in_main_menu and not any('Addon Settings' in item[0] for item in menu_context):
        command = 'Addon.OpenSettings(plugin.video.vietmediaF)'
        menu_context.append(('[COLOR yellow]Addon Setting[/COLOR]', command,))

    return menu_context

def prepare_title(label):
    """Chuẩn bị tiêu đề cho context menu"""
    title = label
    title = re.sub('\[.*?]', '', title)
    title = re.sub('\s', '-', title)
    title = re.sub('--', '-', title)
    title = re.sub('--', '-', title)
    title = re.sub('[\\\\/*?:"<>|
    title = remove_accents.remove_accents(title)
    return title

def build_context_menu(item, index):
    """Xây dựng context menu cho một item"""
    path = item["path"]
    title = prepare_title(item["label"])
    menu_context = []

    
    permission = item.get("permission", "not_allowed")

    
    xbmc.log(f"[VietmediaF] Building context menu for item: {item.get('label')} | Path: {path}", level=xbmc.LOGINFO)
    xbmc.log(f"[VietmediaF] Item permission value: {permission}", level=xbmc.LOGINFO)

    
    is_in_main_menu = is_main_menu()
    xbmc.log(f"[VietmediaF] Is in main menu: {is_in_main_menu}", level=xbmc.LOGINFO)

    
    if is_in_main_menu:
        
        xbmc.log(f"[VietmediaF] Adding main menu context menu for item: {item.get('label')}", level=xbmc.LOGINFO)
        menu_context.extend(get_context_menu_for_main_menu(item, index))
    else:
        
        
        is_already_in_main_menu = check_if_item_in_main_menu(item)
        xbmc.log(f"[VietmediaF] Is already in main menu: {is_already_in_main_menu}", level=xbmc.LOGINFO)

        
        if not is_already_in_main_menu:
            xbmc.log(f"[VietmediaF] Adding 'Add to main menu' option", level=xbmc.LOGINFO)
            menu_context.extend(get_context_menu_for_other_menu(item))

    
    menu_context.extend(get_context_menu_for_specific_item(item, path, title))

    
    menu_context.extend(get_common_context_menu(item, is_in_main_menu))

    
    if item.get("context_menu"):
        for ctx_item in item["context_menu"]:
            menu_context.append(ctx_item)

    
    unique_menu = []
    unique_commands = set()

    for menu_item in menu_context:
        command = menu_item[1]
        if command not in unique_commands:
            unique_commands.add(command)
            unique_menu.append(menu_item)

    
    xbmc.log(f"[VietmediaF] Final context menu for item {item.get('label')}: {unique_menu}", level=xbmc.LOGINFO)

    return unique_menu
