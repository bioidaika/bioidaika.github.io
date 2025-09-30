#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcaddon
import xbmcvfs

# Addon information
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
ADDON_PATH = ADDON.getAddonInfo("path")
ADDON_PROFILE = ADDON.getAddonInfo("profile")
PROFILE_PATH = xbmcvfs.translatePath(ADDON_PROFILE)

# User settings
USER_PIN_CODE = ADDON.getSetting('user_pin_code')
USER_VIP_CODE = ADDON.getSetting('user_vip_code')
LOCK_PIN = ADDON.getSetting('lock_pin')
VIEWMODE = ADDON.getSetting('view_mode')
VIEWXXX = ADDON.getSetting('view_xxx')
DOWNLOAD_PATH = ADDON.getSetting("download_path")
DOWNLOAD_SUB = ADDON.getSetting("download_sub")

# Fshare settings
FSHARE_USERNAME = ADDON.getSetting('fshare_username')
FSHARE_PASSWORD = ADDON.getSetting('fshare_password')
FSHARE_TOKEN = ADDON.getSetting('tokenfshare')
FSHARE_SESSION = ADDON.getSetting('sessionfshare')

# Paths
CACHE_PATH = os.path.join(xbmcvfs.translatePath(ADDON_PROFILE), 'cache')
LOG_PATH = xbmcvfs.translatePath('special://logpath/')
HOME_PATH = xbmcvfs.translatePath('special://home/')
USERDATA_PATH = os.path.join(xbmcvfs.translatePath('special://home/'), 'userdata')
ADDON_DATA_PATH = os.path.join(USERDATA_PATH, 'addon_data', ADDON_ID)

# Đảm bảo thư mục cache tồn tại
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)

# Icons
ADDON_ICON = ADDON.getAddonInfo('icon')
ADDON_FANART = ADDON.getAddonInfo('fanart')
SEARCH_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'search.png')
PLAYCODE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'playcode.png')
HISTORY_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'history.png')
SETTINGS_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'settings.png')
UTILITY_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'utility.png')
ACCINFO_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'account_info.png')
FAVORITE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'favorite.png')
FILES_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'files.png')
UPGRADE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'upgrade.png')
SPEEDTEST_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'speedtest.png')
CLEANCACHE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'cleancache.png')
FOLDER_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'folder.png')
ERROR_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'error.png')
FSFILE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'fsfile.png')
FSFOLDER_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'fsfolder.png')
FSHARE_ICON = os.path.join(ADDON_PATH, 'resources', 'images', 'fshareicon.png')

# API endpoints
FSHARE_LOGIN_API = 'https://api.fshare.vn/api/user/login'
FSHARE_PROFILE_API = 'https://api.fshare.vn/api/user/get'
FSHARE_DOWNLOAD_API = 'https://api.fshare.vn/api/session/download'
FSHARE_FOLDER_API = 'https://api.fshare.vn/api/fileops/getFolderList'
FSHARE_SEARCH_API = 'https://api.fshare.vn/api/fileops/searchInFolder'
FSHARE_FAVOURITE_API = 'https://api.fshare.vn/api/fileops/getFavourite'

# Other constants
USER_AGENT = 'kodivietmediaf-K58W6U'
MAX_SEARCH_RESULTS = 100
DEBUG_MODE = False  # Mặc định tắt chế độ debug
DELETE_INTERVAL = 10

# Error messages
ERROR_MESSAGES = {
    'no_results': 'Không tìm thấy kết quả nào',
    'login_failed': 'Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản và mật khẩu',
    'network_error': 'Lỗi kết nối mạng. Vui lòng thử lại sau',
    'invalid_url': 'URL không hợp lệ',
    'no_direct_link': 'Không thể lấy được link phát',
    'playback_error': 'Lỗi khi phát media'
}
