import cookielib
import os, sys
import requests, urllib
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

ADDON = xbmcaddon.Addon('plugin.video.psvue')
ADDON_PATH_PROFILE = xbmc.translatePath(ADDON.getAddonInfo('profile'))
UA_ANDROID_TV = 'Mozilla/5.0 (Linux; Android 6.0.1; Hub Build/MHC19J; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.98 Safari/537.36'
VERIFY = False


def epg_play_stream(url):
    headers = {
        'Accept': '*/*',
        'Content-type': 'application/x-www-form-urlencoded',
        'Origin': 'https://vue.playstation.com',
        'Accept-Language': 'en-US,en;q=0.8',
        'Referer': 'https://vue.playstation.com/watch/live',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': UA_ANDROID_TV,
        'Connection': 'Keep-Alive',
        'Host': 'media-framework.totsuko.tv',
        'reqPayload': ADDON.getSetting(id='EPGreqPayload'),
        'X-Requested-With': 'com.snei.vue.android'
    }

    r = requests.get(url, headers=headers, cookies=load_cookies(), verify=VERIFY)
    json_source = r.json()
    stream_url = json_source['body']['video']
    headers = '|User-Agent='
    headers += 'Adobe Primetime/1.4 Dalvik/2.1.0 (Linux; U; Android 6.0.1 Build/MOB31H)'
    headers += '&Cookie=reqPayload=' + urllib.quote('"' + ADDON.getSetting(id='EPGreqPayload') + '"')
    listitem = xbmcgui.ListItem()
    listitem.setMimeType("application/x-mpegURL")
    # Checks to see if VideoPlayer info is already saved. If not then info is loaded from stream link
    """
    if xbmc.getCondVisibility('String.IsEmpty(ListItem.Title)'):
        # listitem = xbmcgui.ListItem(title, plot, thumbnailImage=icon)
        # listitem.setInfo(type="Video", infoLabels={'title': title, 'plot': plot})
        listitem.setMimeType("application/x-mpegURL")
    else:
        listitem = xbmcgui.ListItem()
        listitem.setMimeType("application/x-mpegURL")
    """

    inputstreamCOND = str(json_source['body']['dai_method']) # Checks whether stream method is "mlbam" or "freewheel" or "none"

    if inputstreamCOND != 'freewheel' and xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)'):#Inputstream doesn't seem to work when dai method is "freewheel"
        stream_url = json_source['body']['video_alt'] # Uses alternate Sony stream to prevent Inputstream adaptive from crashing
        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        listitem.setProperty('inputstream.adaptive.stream_headers', headers)
        listitem.setProperty('inputstream.adaptive.license_key', headers)
    else:
        stream_url += headers

    listitem.setPath(stream_url)

    # window_id = xbmcgui.getCurrentWindowId()
    # xbmc.executebuiltin('PlayMedia('+stream_url+',True,0)')
    xbmc.Player().play(item=stream_url+headers, listitem=listitem)


def load_cookies():
    cookie_file = os.path.join(ADDON_PATH_PROFILE, 'cookies.lwp')
    cj = cookielib.LWPCookieJar()
    try:
        cj.load(cookie_file, ignore_discard=True)
    except:
        pass

    return cj


url = sys.argv[1].split("=")[1]

if url is not None:
    epg_play_stream(url)
