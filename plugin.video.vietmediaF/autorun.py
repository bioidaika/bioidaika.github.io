import xbmc, xbmcaddon
def autorunvmf():
    if xbmcaddon.Addon().getSetting('chayvmf') == 'true':
        xbmc.executebuiltin("RunAddon(plugin.video.vietmediaF)")
autorunvmf()