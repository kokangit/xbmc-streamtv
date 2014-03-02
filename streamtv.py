# -*- coding: utf-8 -*-
import re
import urllib
import urllib2

BASE_URL = 'http://stream-tv.me'
USERAGENT = ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def convert(val):
    if isinstance(val, unicode):
        val = val.encode('utf8')
    elif isinstance(val, str):
        try:
            val.decode('utf8')
        except:
            pass
    return val

def parameters_string_to_dict(str):
    params = {}
    if str:
        pairs = str[1:].split("&")
        for pair in pairs:
            split = pair.split('=')
            if (len(split)) == 2:
                key = convert(urllib.unquote_plus(split[0]))
                value = convert(urllib.unquote_plus(split[1]))
                params[key] = value
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

def parse(html, part_pattern, name_pattern, url_pattern):
    html = re.findall(part_pattern, html, re.DOTALL)
    if not html:
        return []
    html = html[0].replace('</tr><tr>', '</tr>\n<tr>')
    name = re.findall(name_pattern, html)
    if url_pattern:
        url = re.findall(url_pattern, html)
        if len(url) != len(name):
            raise Exception('found ' + str(len(url)) +
                            ' urls but ' + str(len(name)) + ' names!')
    else:
        url = None
    if url:
        ret = zip(name, url)
    else:
        ret = name
    return ret

def scrape_shows(html, selected):
    return parse(html,
                 part_pattern='<p><a name="%s"></a></p>(.+?)</ul>' % selected,
                 name_pattern='<li><strong><a href=".+?">(.+?)</a>',
                 url_pattern='<li><strong><a href="(.+?)"')

def scrape_seasons(html):
    plot = re.findall('<p>(.+).+?<a href', html)[0]
    part_pattern='<div class="entry">(.+?)</div>'
    names = parse(html,
                  part_pattern=part_pattern,
                  name_pattern='<strong>.*?(Season [0-9]+).*?</strong>',
                  url_pattern=None)
    html = re.findall(part_pattern, html, re.DOTALL)[0]
    img_url = re.findall('<img class=.+?src="(.+?)"', html)[0]
    return names, img_url, plot

def scrape_episodes(html, season):
    season = urllib.unquote_plus(season)
    return parse(html,
                 part_pattern='<strong>.*?%s.*?</strong>(.+?)</ul>' % season,
                 name_pattern='<li><a .+?">(.+?)</a>',
                 url_pattern='<a href="(.+?)"')

def scrape_episode(html):
    url = re.findall('<IFRAME SRC="(.+?)"', html)[0]
    html = get_url(url)
    return parse(html,
                 part_pattern='<script type=\'text/javascript\'>.+?"playlist"(.+?)</script>',
                 name_pattern='"label".+?:.+?"(.+?)"',
                 url_pattern='"file".+?:.+?"(.+?)"')

def scrape_search(html):
    return parse(html,
                 part_pattern='<div class="entry">(.+?)</div>',
                 name_pattern='<li><a .+?">(.+?)</a>',
                 url_pattern=None,
                 img_pattern='<img class=.+?src="(.+?)"')

def alpha_selected_html():
    return get_url(BASE_URL)

def show_selected_html(url):
    return get_url(url)

def season_selected_html(url):
    return get_url(url)

def episode_selected_html(url):
    return get_url(url)

def search_html(text):
    url = BASE_URL + '/?' + urllib.urlencode({'s': text, 'op.x': 0, 'op.y': 0})
    return get_url(url)
