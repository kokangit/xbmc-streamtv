# -*- coding: utf-8 -*-
import re
import urllib
import urllib2

BASE_URL = 'http://stream-tv.me'
USERAGENT = ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def parameters_string_to_dict(str):
    params = {}
    if str:
        pairs = str[1:].split("&")
        for pair in pairs:
            split = pair.split('=')
            if (len(split)) == 2:
                params[urllib.unquote(split[0])] = urllib.unquote(split[1]) \
                    .decode('utf-8')
    return params

def get_url(url, filename=None, referer=None, data=None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', USERAGENT)
    if referer:
        req.add_header('Referer', referer)
    response = urllib2.urlopen(req, data)
    url = response.geturl()
    html = response.read()
    response.close()
    return html

def parse(html, part_pattern, name_pattern, url_pattern, img_pattern,
          nameFlag=0, urlFlag=0, imgFlag=0):
    # TODO plot
    html = re.findall(part_pattern, html, re.DOTALL)
    if not html:
        return
    html = html[0].replace('</tr><tr>', '</tr>\n<tr>')
    name = re.findall(name_pattern, html, nameFlag)
    url = re.findall(url_pattern, html, urlFlag)
    if len(url) != len(name):
        raise Exception('found ' + str(len(url)) +
                        ' urls but ' + str(len(name)) + ' names!')
    if img_pattern:
        img = re.findall(img_pattern, html, imgFlag)
        if len(img) != len(name):
            raise Exception('found ' + str(len(img)) +
                            ' images but ' + str(len(name)) + ' names!')
    else:
        img = [None]*len(name)
    return zip(name, url, img)

def scrap_alpha(html, selected):
    return parse(html,
                 part_pattern='<p><a name="%s"></a></p>(.+?)</ul>' % selected,
                 name_pattern='<li><strong><a href=".+?">(.+?)</a>',
                 url_pattern='<li><strong><a href="(.+?)"',
                 img_pattern=None)

def scrap_search(html):
    return parse(html,
                 part_pattern='<div class="entry">(.+?)</div>',
                 name_pattern='<li><a .+?">(.+?)</a>',
                 url_pattern='<li><a href="(.+?)"',
                 img_pattern=None)

def scrap_video(html):
    url = re.findall('<IFRAME SRC="(.+?)"', html)[0]
    html = get_url(url)
    return parse(html,
                 part_pattern='<script type=\'text/javascript\'>.+?"playlist"(.+?)</script>',
                 name_pattern='"label".+?:.+?"(.+?)"',
                 url_pattern='"file".+?:.+?"(.+?)"',
                 img_pattern=None)

def alpha_html():
    return get_url(BASE_URL)
