# -*- coding: utf-8 -*-
import cookielib
from HTMLParser import HTMLParser
import os
import re
import urllib
import urllib2
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys

__settings__ = xbmcaddon.Addon(id='plugin.video.streamtv')
__language__ = __settings__.getLocalizedString

#SAVE_FILE = False
SAVE_FILE = True
MODE_START = 'start'
MODE_ALPHABETIC = 'alphabetic'
MODE_VIDEO = 'video'
MODE_PLAY = 'play'
MODE_SEARCH = 'search'
BASE_URL = 'http://stream-tv.me'
USERAGENT = ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

class MyHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        xbmc.log('----- redirecting')
        xbmc.log(str(headers))
        xbmc.log('-----')
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp,
                                                          code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def unikeyboard(default, message):
    keyboard = xbmc.Keyboard(default, message)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return keyboard.getText()
    else:
        return None

def parameters_string_to_dict(str):
    params = {}
    if str:
        pairs = str[1:].split("&")
        for pair in pairs:
            split = pair.split('=')
            if (len(split)) == 2:
                params[split[0]] = split[1]
    return params

def get_url(url, filename=None, referer=None, data=None):
    xbmc.log('get_url' + ((' (' + filename + ')') if filename else '') + ': ' +
             str(url))
    req = urllib2.Request(url)
    req.add_header('User-Agent', USERAGENT)
    if referer:
        req.add_header('Referer', referer)
    response = urllib2.urlopen(req, data)
    url = response.geturl()
    html = response.read()
    response.close()

    if filename and SAVE_FILE:
        filename = xbmc.translatePath('special://temp/' + filename)
        file = open(filename, 'w')
        file.write(html)
        file.close()
    return (url, html)

def addItems(name, image, plot, url, mode, isFolder, handle, totalItems):
    for i in range(len(name)):
        li = xbmcgui.ListItem(name[i])
        if image:
            li.setThumbnailImage(image[i])
        infoLabels = {'Title': name[i]}
        if plot:
            infoLabels['Plot'] = plot[i]
        li.setInfo(type='Video', infoLabels=infoLabels)
        if mode == MODE_PLAY:
            li.setProperty('IsPlayable', 'true')
        params = { 'mode': mode }
        if url:
            params['url'] = url[i]
        if mode == MODE_PLAY:
            url2 = url[i]
        else:
            url2 = sys.argv[0] + '?' + urllib.urlencode(params)
        xbmcplugin.addDirectoryItem(handle=handle, url=url2,
                                    listitem=li, isFolder=isFolder,
                                    totalItems=totalItems)

def addCookies2Url(url):
    c = ''
    for cookie in cookiejar:
        if cookie.domain_specified and cookie.domain in url:
            c += cookie.name + '=' + cookie.value + ';'
    if len(c) > 0:
        url += '|Cookie=' + urllib.quote(c)
    return url

def parse(handle, url, fromMode, toMode, partP, nameP, urlP, imgP, nameFlag=0,
          urlFlag=0, imgFlag=0):
    (url, html) = get_url(url, 'parse.html')
    # check for more pages
    pagination = re.findall(
        '<div class="pagination".*<a href="(.+?)">n&auml;sta', html)
    html = re.findall(partP, html, re.DOTALL)
    if not html:
        return
    html = html[0].replace('</tr><tr>', '</tr>\n<tr>')
    name = re.findall(nameP, html, nameFlag)
    url = re.findall(urlP, html, urlFlag)
    if len(url) != len(name):
        raise Exception('found ' + str(len(url)) +
                        ' urls but ' + str(len(name)) + ' names!')
    img = None
    if imgP:
        img = re.findall(imgP, html, imgFlag)
        if len(img) != len(name):
            raise Exception('found ' + str(len(img)) +
                            ' images but ' + str(len(name)) + ' names!')
    # TODO plot
    addItems(name, img, None, url, toMode, True, handle, len(name))
    if pagination and not 'disabled' in pagination[0]:
        url = BASE_URL + '/' + pagination[0]
        addItems(['Nästa...'], None, None, [url], fromMode, True, handle, 1)

def start(handle):
    totalItems = 2
    # TODO strings from resources
    addItems(['A-Ö'], None, None, None, MODE_ALPHABETIC, True, handle, totalItems)
    addItems(['Sök'], None, None, None, MODE_SEARCH, True, handle, totalItems)

def alpha(handle, selected):
    selections = ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                  'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W',
                  'X', 'Y', 'Z', 'Å', 'Ä', 'Ö']
    if not selected:
        addItems(selections, None, None, selections, MODE_ALPHABETIC, True,
                 handle, len(selections))
    else:
        parse(handle, BASE_URL, MODE_ALPHABETIC, MODE_SEARCH,
              partP='<p><a name="' + selected + '"></a></p>(.+?)</ul>',
              nameP='<li><strong><a href=".+?">(.+?)</a>',
              urlP='<li><strong><a href="(.+?)"',
              imgP=None)

def search(handle, url):
    if not url:
        try:
            latestSearch = __settings__.getSetting("latestSearch")
        except KeyError:
            latestSearch = ""
        searchString = unikeyboard(latestSearch, "")
        if searchString == "": return
        __settings__.setSetting("latestSearch", searchString)
        url = BASE_URL + '/?' + \
            urllib.urlencode({ 's': searchString, 'op.x': 0, 'op.y': 0 })
    parse(handle, url, MODE_SEARCH, MODE_VIDEO,
          partP='<div class="entry">(.+?)</div>',
          nameP='<li><a .+?">(.+?)</a>',
          urlP='<li><a href="(.+?)"',
          imgP = None)

def video(handle, url):
    (url, html) = get_url(url, 'video.html')
    url = re.findall('<IFRAME SRC="(.+?)"', html)[0]
    # TODO image
    parse(handle, url, MODE_VIDEO, MODE_PLAY,
          partP='<script type=\'text/javascript\'>.+?"playlist"(.+?)</script>',
          nameP='"label".+?:.+?"(.+?)"',
          urlP='"file".+?:.+?"(.+?)"',
          imgP = None)    

cookiejarfile = xbmc.translatePath(
    'special://temp/streamtv_cookies.dat').decode('utf-8')
cookiejar = cookielib.LWPCookieJar(cookiejarfile)
if os.path.exists(cookiejarfile):
    cookiejar.load()
    xbmc.log('cookies before:' + str(cookiejar))

cookieprocessor = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(MyHTTPRedirectHandler, cookieprocessor)
urllib2.install_opener(opener)

params = parameters_string_to_dict(sys.argv[2]) if len(sys.argv) > 2 else {}
mode = params.get('mode', None)
url = params.get("url",  None)
if url: url = urllib.unquote_plus(url)
handle = int(sys.argv[1])

xbmc.log('params=' + str(params))
xbmc.log('mode=' + str(mode))
xbmc.log('url=' + str(url))

if not mode:
    start(handle)
elif mode == MODE_ALPHABETIC:
    alpha(handle, url)
elif mode == MODE_SEARCH:
    search(handle, url)
elif mode == MODE_VIDEO:
    video(handle, url)
xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=True)

cookiejar.save()
xbmc.log('cookies after:' + str(cookiejar))
