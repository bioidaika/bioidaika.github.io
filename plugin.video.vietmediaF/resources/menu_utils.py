import os
import json
import xbmcvfs
import xbmcgui
import xbmc
from resources.addon import ADDON, PROFILE_PATH, notify, alert


CUSTOM_MENU_FILE = os.path.join(PROFILE_PATH, 'custom_menu.json')
MAIN_MENU_FILE = os.path.join(PROFILE_PATH, 'main_menu.json')
CUSTOM_ICONS_DIR = os.path.join(xbmcvfs.translatePath('special://home/addons/plugin.video.vietmediaF/resources/images/custom'))

def get_custom_menu():
    """Lấy menu tùy chỉnh từ file JSON"""
    if not os.path.exists(CUSTOM_MENU_FILE):
        return []

    try:
        with open(CUSTOM_MENU_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi đọc custom menu: {str(e)}", level=xbmc.LOGERROR)
        return []

def save_custom_menu(menu_items):
    """Lưu menu tùy chỉnh vào file JSON"""
    try:
        with open(CUSTOM_MENU_FILE, 'w', encoding='utf-8') as f:
            json.dump(menu_items, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi lưu custom menu: {str(e)}", level=xbmc.LOGERROR)
        return False

def add_to_custom_menu(item):
    """Thêm một item vào menu tùy chỉnh"""
    custom_menu = get_custom_menu()

    
    for existing_item in custom_menu:
        if existing_item.get('path') == item.get('path'):
            notify("Item đã tồn tại trong menu tùy chỉnh")
            return False

    
    item['fixed'] = ""

    
    custom_menu.append(item)

    
    return save_custom_menu(custom_menu)

def remove_from_custom_menu(path):
    """Xóa một item khỏi menu tùy chỉnh dựa trên path"""
    custom_menu = get_custom_menu()

    
    for i, item in enumerate(custom_menu):
        if item.get('path') == path:
            del custom_menu[i]
            return save_custom_menu(custom_menu)

    notify("Không tìm thấy item trong menu tùy chỉnh")
    return False

def rename_custom_menu_item(path, new_label):
    """Đổi tên một item trong menu tùy chỉnh"""
    custom_menu = get_custom_menu()

    
    for item in custom_menu:
        if item.get('path') == path:
            item['label'] = new_label
            return save_custom_menu(custom_menu)

    notify("Không tìm thấy item trong menu tùy chỉnh")
    return False

def reorder_custom_menu_item(path, new_position):
    """Thay đổi vị trí của một item trong menu tùy chỉnh"""
    custom_menu = get_custom_menu()

    
    item_to_move = None
    item_index = -1

    for i, item in enumerate(custom_menu):
        if item.get('path') == path:
            item_to_move = item
            item_index = i
            break

    if item_to_move is None:
        notify("Không tìm thấy item trong menu tùy chỉnh")
        return False

    
    del custom_menu[item_index]

    
    new_position = max(0, min(new_position, len(custom_menu)))
    custom_menu.insert(new_position, item_to_move)

    return save_custom_menu(custom_menu)

def get_default_icon(position):
    """Lấy icon mặc định dựa trên vị trí trong menu"""
    icon_path = os.path.join(CUSTOM_ICONS_DIR, f'custom_{position + 1}.png')

    
    if xbmcvfs.exists(icon_path):
        return icon_path

    
    return os.path.join(xbmcvfs.translatePath('special://home/addons/plugin.video.vietmediaF/resources/images'), 'default.png')

def reset_custom_menu():
    """Xóa toàn bộ menu tùy chỉnh"""
    if os.path.exists(CUSTOM_MENU_FILE):
        try:
            os.remove(CUSTOM_MENU_FILE)
            notify("Đã xóa menu tùy chỉnh")
            return True
        except Exception as e:
            xbmc.log(f"[VietmediaF] Lỗi khi xóa custom menu: {str(e)}", level=xbmc.LOGERROR)
            return False
    return True

def sync_with_google_sheet(google_sheet_items):
    """Cập nhật các item cố định từ Google Sheet vào menu tùy chỉnh"""
    custom_menu = get_custom_menu()
    updated = False

    
    fixed_items = [item for item in google_sheet_items if item.get("fixed") == "x"]

    
    for i, item in enumerate(custom_menu):
        
        for fixed_item in fixed_items:
            if item.get("path") == fixed_item.get("path"):
                
                if item.get("icon") != fixed_item.get("icon") or item.get("thumbnail") != fixed_item.get("thumbnail"):
                    item["icon"] = fixed_item.get("icon")
                    item["thumbnail"] = fixed_item.get("thumbnail")
                    updated = True
                
                item["fixed"] = "x"
                break

    
    if updated:
        save_custom_menu(custom_menu)
        xbmc.log("[VietmediaF] Đã cập nhật menu tùy chỉnh từ Google Sheet", level=xbmc.LOGINFO)

    return updated



def get_main_menu():
    """Lấy menu chính từ file JSON"""
    if not os.path.exists(MAIN_MENU_FILE):
        return []

    try:
        with open(MAIN_MENU_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi đọc main menu: {str(e)}", level=xbmc.LOGERROR)
        return []

def save_main_menu(menu_items):
    """Lưu menu chính vào file JSON"""
    try:
        
        if not os.path.exists(os.path.dirname(MAIN_MENU_FILE)):
            os.makedirs(os.path.dirname(MAIN_MENU_FILE))

        with open(MAIN_MENU_FILE, 'w', encoding='utf-8') as f:
            json.dump(menu_items, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi lưu main menu: {str(e)}", level=xbmc.LOGERROR)
        return False

def add_to_main_menu(item):
    """Thêm một item vào menu chính"""
    main_menu = get_main_menu()

    
    for existing_item in main_menu:
        if existing_item.get('path') == item.get('path'):
            notify("Item đã tồn tại trong menu chính")
            return False

    
    item['permission'] = "allowed"

    
    item['position'] = len(main_menu)

    
    main_menu.append(item)

    
    return save_main_menu(main_menu)

def remove_from_main_menu(path):
    """Xóa một item khỏi menu chính dựa trên path"""
    main_menu = get_main_menu()

    
    path = path.split('&d=')[0] if '&d=' in path else path

    
    for i, item in enumerate(main_menu):
        item_path = item.get('path', '')
        
        item_path = item_path.split('&d=')[0] if '&d=' in item_path else item_path

        if item_path == path:
            
            if item.get('permission') == "not_allowed":
                notify("Không thể xóa item này")
                return False

            
            del main_menu[i]

            
            for j, remaining_item in enumerate(main_menu):
                remaining_item['position'] = j

            return save_main_menu(main_menu)

    notify("Không tìm thấy item trong menu chính")
    return False

def rename_main_menu_item(path, new_label):
    """\u0110\u1ed5i t\u00ean m\u1ed9t item trong menu ch\u00ednh"""
    main_menu = get_main_menu()

    
    path = path.split('&d=')[0] if '&d=' in path else path

    
    for i, item in enumerate(main_menu):
        item_path = item.get('path', '')
        
        item_path = item_path.split('&d=')[0] if '&d=' in item_path else item_path

        if item_path == path:
            item['label'] = new_label
            return save_main_menu(main_menu)

    notify("Kh\u00f4ng t\u00ecm th\u1ea5y item trong menu ch\u00ednh")
    return False

def reorder_main_menu_item(path, new_position):
    """Thay đổi vị trí của một item trong menu chính"""
    main_menu = get_main_menu()

    
    path = path.split('&d=')[0] if '&d=' in path else path

    
    item_to_move = None
    item_index = -1

    for i, item in enumerate(main_menu):
        item_path = item.get('path', '')
        
        item_path = item_path.split('&d=')[0] if '&d=' in item_path else item_path

        if item_path == path:
            item_to_move = item
            item_index = i
            break

    if item_to_move is None:
        notify("Không tìm thấy item trong menu chính")
        return False

    
    del main_menu[item_index]

    
    new_position = max(0, min(new_position, len(main_menu)))
    main_menu.insert(new_position, item_to_move)

    
    for i, item in enumerate(main_menu):
        item['position'] = i

    return save_main_menu(main_menu)

def reset_main_menu():
    """Xóa toàn bộ menu chính"""
    if os.path.exists(MAIN_MENU_FILE):
        try:
            os.remove(MAIN_MENU_FILE)
            notify("Đã xóa menu chính")
            
            sync_menu_from_google_sheet()
            return True
        except Exception as e:
            xbmc.log(f"[VietmediaF] Lỗi khi xóa main menu: {str(e)}", level=xbmc.LOGERROR)
            return False
    return True

def sync_menu_from_google_sheet():
    """Tạo menu chính từ Google Sheet"""
    
    import urlquick
    import json

    
    url = 'https://docs.google.com/spreadsheets/d/1GjvqQgbLeMSXULB64BhLi4poxVv4V-PWCgeRBj3Zq4k/gviz/tq?gid=0&headers=1'
    response = urlquick.get(url, max_age=60 * 60)
    data = response.text

    
    start_index = data.index('{')
    end_index = data.rindex('}') + 1
    json_data = data[start_index:end_index]
    parsed_data = json.loads(json_data)

    
    items = []
    for row in parsed_data['table']['rows']:
        
        label = row['c'][0]['v']
        path = row['c'][1]['v']
        is_playable = row['c'][2]['v'] == 'true'
        thumbnail = row['c'][3].get('v', '')
        icon = row['c'][4].get('v', '')
        label2 = row['c'][5].get('v', '')
        plot = row['c'][6].get('v', '')
        visible = row['c'][7].get('v', 'On')
        permission = row['c'][8].get('v', 'not_allowed')

        if visible == "On":
            
            item = {
                'label': label,
                'path': path,
                'is_playable': is_playable,
                'thumbnail': thumbnail,
                'icon': icon,
                'label2': label2,
                'info': {'plot': plot},
                'permission': permission,
                'position': len(items)
            }

            items.append(item)

    
    save_main_menu(items)

    return items

def is_item_in_main_menu(path):
    """Kiểm tra xem một item có trong menu chính không"""
    main_menu = get_main_menu()

    
    path = path.split('&d=')[0] if '&d=' in path else path

    for item in main_menu:
        item_path = item.get('path', '')
        item_path = item_path.split('&d=')[0] if '&d=' in item_path else item_path

        if item_path == path:
            return True

    return False

def is_allowed_to_remove(path):
    """Kiểm tra xem một item có thể xóa không"""
    main_menu = get_main_menu()

    
    path = path.split('&d=')[0] if '&d=' in path else path

    for item in main_menu:
        item_path = item.get('path', '')
        item_path = item_path.split('&d=')[0] if '&d=' in item_path else item_path

        if item_path == path:
            return item.get('permission') == "allowed"

    return False

def prompt_add_to_main_menu(item):
    """Hiển thị hộp thoại để thêm item vào menu chính"""
    dialog = xbmcgui.Dialog()

    
    if dialog.yesno("Thêm vào Menu Chính", "Bạn có muốn thêm mục này vào Menu Chính không?"):
        
        default_name = item.get('label', '').replace('[COLOR yellow]', '').replace('[/COLOR]', '')
        new_name = dialog.input("Đặt tên cho mục này", defaultt=default_name)

        if not new_name:
            new_name = default_name

        
        new_item = {
            'label': new_name,
            'path': item.get('path', ''),
            'is_playable': item.get('is_playable', False),
            'thumbnail': item.get('thumbnail', ''),
            'icon': item.get('icon', ''),
            'label2': item.get('label2', ''),
            'info': item.get('info', {'plot': ''})
        }

        
        if add_to_main_menu(new_item):
            notify(f"Đã thêm '{new_name}' vào Menu Chính")
            xbmc.executebuiltin("Container.Refresh")
            return True
        else:
            notify("Không thể thêm vào Menu Chính")
            return False

    return False
