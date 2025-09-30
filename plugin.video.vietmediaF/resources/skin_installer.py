import os
import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import zipfile
import urllib.request
import shutil
from resources.addon import notify, alert, TextBoxes, ADDON_PATH, ADDON_NAME, ADDON

def check_and_prompt_skin_installation():
    """
    Kiểm tra xem skin.arctic.zephyr.2.resurrection.mod có được cài đặt không
    và hiển thị hộp thoại hỏi người dùng có muốn cài đặt không
    """

    if ADDON.getSettingBool('skin_prompt_shown'):
        return

    skin_installed = xbmc.getCondVisibility('System.HasAddon(skin.arctic.zephyr.2.resurrection.mod)')

    if not skin_installed:
        dialog = xbmcgui.Dialog()
        response = dialog.yesno(
            "Cài đặt skin cho VietmediaF",
            "Bạn có muốn cài đặt skin cho VietmediaF không?\n\nSkin này đã được tích hợp vào repo của addon VietmediaF."
        )


        ADDON.setSettingBool('skin_prompt_shown', True)

        if response:

            repo_installed = xbmc.getCondVisibility('System.HasAddon(repository.vietmediaf)')

            if not repo_installed:
                dialog.ok(
                    "Cài đặt Repository",
                    "Bạn cần cài đặt Repository VietmediaF trước.\n\nHãy vào System > Add-ons > Install from zip file và chọn file zip của repository VietmediaF."
                )
            else:

                xbmc.executebuiltin('InstallAddon(skin.arctic.zephyr.2.resurrection.mod)')
                dialog.ok(
                    "Đang cài đặt skin",
                    "Skin đang được cài đặt. Sau khi hoàn tất, bạn có thể kích hoạt skin trong Settings > Interface > Skin."
                )
        else:
            dialog.ok(
                "Thông báo",
                "Bạn có thể cài đặt skin này trong repo VietmediaF bất cứ lúc nào."
            )
    else:

        ADDON.setSettingBool('skin_prompt_shown', True)

def install_arctic_zephyr():
    """
    Cài đặt skin Arctic Zephyr 2 Resurrection Mod và các file cấu hình
    Cho phép người dùng chọn giữa các cấu hình Home Menu khác nhau (ThuvienCine hoặc ThuVienHD)
    """
    try:
        # Kiểm tra xem skin đã được cài đặt chưa
        skin_installed = xbmc.getCondVisibility('System.HasAddon(skin.arctic.zephyr.2.resurrection.mod)')
        dialog = xbmcgui.Dialog()

        if not skin_installed:
            alert("Skin Arctic Zephyr 2 Resurrection Mod chưa được cài đặt. Vào đây để đọc hướng dẫn [COLOR yellow]https://kodi.vn/[/COLOR]")
            return
        else:
            # Hiển thị lựa chọn giữa các cấu hình Home Menu
            choices = ["ThuvienCine", "ThuVienHD"]
            selected = dialog.select("Chọn kiểu Home Menu", choices)

            if selected < 0:  # Người dùng đã hủy
                return False

            selected_theme = choices[selected].lower()

            # Tiến hành cài đặt cấu hình đã chọn
            if extract_skin_config_files(selected_theme):
                if dialog.yesno("Hoàn tất",
                                f"Các file cấu hình {choices[selected]} đã được cài đặt thành công.\n\n"
                                "Để áp dụng các thay đổi, bạn cần khởi động lại Kodi.\n\n"
                                "Bạn có muốn khởi động lại Kodi ngay bây giờ không?"):
                    xbmc.executebuiltin('RestartApp')
                return True
            else:
                alert("Không thể copy các file cấu hình. Vui lòng thử lại sau.")
                return False
    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi cài đặt skin: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi khi cài đặt skin: {str(e)}")
        return False

def extract_skin_config_files(theme='thuviencine'):
    try:

        userdata_path = xbmcvfs.translatePath('special://userdata')
        addon_data_path = os.path.join(userdata_path, 'addon_data')
        if not os.path.exists(addon_data_path):
            os.makedirs(addon_data_path)

        theme_path = os.path.join(ADDON_PATH, 'resources', 'skins', theme)
        guisettings_path = os.path.join(theme_path, 'guisettings.xml')
        skin_zip_path = os.path.join(theme_path, 'skin.arctic.zephyr.2.resurrection.mod.zip')
        shortcuts_zip_path = os.path.join(theme_path, 'script.skinshortcuts.zip')
        skinvariables_zip_path = os.path.join(theme_path, 'script.skinvariables.zip')


        files_missing = False
        missing_files = []
        if not os.path.exists(guisettings_path):
            files_missing = True
            missing_files.append("guisettings.xml")

        if not os.path.exists(skin_zip_path):
            files_missing = True
            missing_files.append("skin.arctic.zephyr.2.resurrection.mod.zip")

        if not os.path.exists(shortcuts_zip_path):
            files_missing = True
            missing_files.append("script.skinshortcuts.zip")

        if not os.path.exists(skinvariables_zip_path):
            files_missing = True
            missing_files.append("script.skinvariables.zip")

        if files_missing:
            dialog = xbmcgui.Dialog()
            if dialog.yesno("Cấu hình skin", f"Các file cấu hình skin sau không tồn tại trong thư mục {theme}: {', '.join(missing_files)}\n\nBạn có muốn tiếp tục mà không có các file này không?"):
                notify("Tiếp tục mà không có đầy đủ file cấu hình")
            else:
                return False


        if os.path.exists(guisettings_path):
            try:
                shutil.copy2(guisettings_path, userdata_path)
                xbmc.log(f"[VietmediaF] Đã copy guisettings.xml từ {theme} vào {userdata_path}", xbmc.LOGINFO)
            except Exception as e:
                xbmc.log(f"[VietmediaF] Lỗi khi copy guisettings.xml: {str(e)}", xbmc.LOGERROR)
                alert(f"Lỗi khi copy guisettings.xml: {str(e)}")


        if os.path.exists(skin_zip_path):
            with zipfile.ZipFile(skin_zip_path, 'r') as zip_ref:
                zip_ref.extractall(addon_data_path)
                xbmc.log(f"[VietmediaF] Đã giải nén skin.arctic.zephyr.2.resurrection.mod.zip vào {addon_data_path}", xbmc.LOGINFO)

        if os.path.exists(shortcuts_zip_path):
            with zipfile.ZipFile(shortcuts_zip_path, 'r') as zip_ref:
                zip_ref.extractall(addon_data_path)
                xbmc.log(f"[VietmediaF] Đã giải nén script.skinshortcuts.zip vào {addon_data_path}", xbmc.LOGINFO)

        if os.path.exists(skinvariables_zip_path):
            with zipfile.ZipFile(skinvariables_zip_path, 'r') as zip_ref:
                zip_ref.extractall(addon_data_path)
                xbmc.log(f"[VietmediaF] Đã giải nén script.skinvariables.zip vào {addon_data_path}", xbmc.LOGINFO)

        return True

    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi copy các file cấu hình: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi khi copy các file cấu hình: {str(e)}")
        return False


def display_skin_installer():
    openwizard_installed = xbmc.getCondVisibility('System.HasAddon(plugin.program.openwizard)')
    openwizard_version = ""

    if openwizard_installed:

        openwizard_addon = xbmcaddon.Addon('plugin.program.openwizard')
        openwizard_version = openwizard_addon.getAddonInfo('version')

        # Kiểm tra phiên bản bằng cách so sánh chuỗi
        try:
            from packaging import version
            if version.parse(openwizard_version) < version.parse("2.0.7.2"):
                openwizard_installed = False
        except ImportError:
            # Nếu không có thư viện packaging, sử dụng phương pháp so sánh đơn giản
            current_version = [int(x) for x in openwizard_version.split('.')]
            required_version = [2, 0, 7, 2]

            # So sánh từng phần của phiên bản
            for i in range(min(len(current_version), len(required_version))):
                if current_version[i] < required_version[i]:
                    openwizard_installed = False
                    break
                elif current_version[i] > required_version[i]:
                    break

    if not openwizard_installed:
        dialog = xbmcgui.Dialog()
        response = dialog.yesno(
            "Cài đặt OpenWizard",
            "OpenWizard (phiên bản VMF) chưa được cài đặt.\n\nBạn có muốn cài đặt OpenWizard từ repository VietmediaF Official không?"
        )

        if response:

            xbmc.executebuiltin('InstallAddon(plugin.program.openwizard)')
            dialog.ok(
                "Đang cài đặt OpenWizard",
                "OpenWizard đang được cài đặt. Vui lòng đợi trong giây lát..."
            )
        else:
            dialog.ok(
                "Thông báo",
                "Bạn cần cài đặt OpenWizard để tiếp tục."
            )
        return
    else:

        dialog = xbmcgui.Dialog()
        dialog.ok(
            "Thông báo",
            "Hãy cài đặt bản build 11.36 đi kèm skin"
        )
        xbmc.executebuiltin('ActivateWindow(Programs,plugin://plugin.program.openwizard/,return)')


def show_skin_install_guide():
    """
    Hiển thị hướng dẫn cài đặt skin thủ công
    """
    try:

        guide_path = os.path.join(ADDON_PATH, 'resources', 'skins', 'README_INSTALL.txt')


        if not os.path.exists(guide_path):
            alert("Không tìm thấy file hướng dẫn cài đặt.")
            return


        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()


        from resources.utils import TextBoxes
        TextBoxes("Hướng dẫn cài đặt skin Arctic Zephyr 2 Resurrection Mod", guide_content)

    except Exception as e:
        xbmc.log(f"[VietmediaF] Lỗi khi hiển thị hướng dẫn cài đặt: {str(e)}", xbmc.LOGERROR)
        alert(f"Lỗi khi hiển thị hướng dẫn cài đặt: {str(e)}")


