# -*- coding: utf-8 -*-
import os
import re
import urllib
import urllib2

SAVE_FILE = True
BASE_URL = 'http://stream-tv.co'
USERAGENT = ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

class Streamtv:

    def __init__(self, xbmc, xbmcplugin, xbmcgui, xbmcaddon):
        self.xbmc = xbmc
        self.xbmcplugin = xbmcplugin
        self.xbmcgui = xbmcgui
        self.xbmcaddon = xbmcaddon
        temp = self.xbmc.translatePath(
            os.path.join(self.xbmcaddon.Addon().getAddonInfo('profile').\
                             decode('utf-8'), 'temp'))
        if not os.path.exists(temp):
            os.makedirs(temp)

    def convert(self, val):
        if isinstance(val, unicode):
            val = val.encode('utf8')
        elif isinstance(val, str):
            try:
                val.decode('utf8')
            except:
                pass
        return val

    def parameters_string_to_dict(self, str):
        params = {}
        if str:
            pairs = str[1:].split("&")
            for pair in pairs:
                split = pair.split('=')
                if (len(split)) == 2:
                    key = self.convert(urllib.unquote_plus(split[0]))
                    value = self.convert(urllib.unquote_plus(split[1]))
                    params[key] = value
        return params

    def get_url(self, url, filename=None, referer=None, data=None):
        """Send http request to url.
        Send the request and return the html response.
        Sends cookies, receives cookies and saves them.
        Resonse html can be saved in file for debugging.
        """
        self.xbmc.log('get_url' + ((' (' + filename + ')')
                              if filename else '') + ': ' +
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
            filename = self.xbmc.translatePath('special://temp/' + filename)
            file = open(filename, 'w')
            file.write(html)
            file.close()
        return html

    def parse(self, html, part_pattern, name_pattern, url_pattern):
        if part_pattern:
            html = re.findall(part_pattern, html, re.DOTALL)
        else:
            html = [html]
        if not html:
            return []
        html = html[0].replace('</tr><tr>', '</tr>\n<tr>')
        name = re.findall(name_pattern, html)
        if url_pattern:
            url = re.findall(url_pattern, html)
            if len(url) != len(name):
                raise Exception('found ' + str(len(url)) +
                                ' urls but ' + str(len(name)) + ' names!')
            ret = zip(name, url)
        else:
            ret = name
        return ret

    def scrape_top_menu(self, html):
        return self.parse(html,
                     part_pattern='<p><a name=(.+?)<hr',
                     name_pattern='<strong.*>(.+?)<.*/strong>.*?</p>',
                     url_pattern=None)

    def scrape_all(self, html):
        return self.parse(html,
                     part_pattern='<strong>Select.+?</p>(.+?)</html>',
                     name_pattern='<li><strong><a href=".+?">(.+?)</a>',
                     url_pattern='<li><strong><a href="(.+?)"')

    def scrape_shows(self, html, selected):
        return self.parse(html,
                     part_pattern='<strong.*?>%s[ ]*?<.*?/strong>.*?</p>(.+?)</ul>' % selected,
                     name_pattern='<li><a href=".+?">(.+?)</a>',
                     url_pattern='<li><a href="(.+?)"')

    def scrape_seasons(self, html):
        plot = re.findall('<p>(.+).+?<a href', html)[0]
        part_pattern='<div class="entry">(.+?)</div>'
        names = self.parse(html,
                      part_pattern=part_pattern,
                      name_pattern='<strong>.*?(Season [0-9]+).*?</strong>',
                      url_pattern=None)
        html = re.findall(part_pattern, html, re.DOTALL)[0]
        img_url = re.findall('<img class=.+?src="(.+?)"', html)[0]
        return names, img_url, plot

    def scrape_episodes(self, html, season):
        season = urllib.unquote_plus(season)
        return self.parse(html,
                     part_pattern='<strong>.*?%s.*?</strong>.+?<ul>(.+?)<[/]*ul>'\
                         % season,
                     name_pattern='<li><a .+?">(.+?)<(?:/a>|/a<|br/>)',
                     url_pattern='<li><a href="(.+?)"')

    def scrape_episode(self, html):
        url = re.findall('<IFRAME SRC="(.+?)"', html)[0]
        html = self.get_url(url, 'episode.html')
        if html.find('id="content">File was deleted') > -1:
            return None
        return self.parse(html,
                     part_pattern='<script type=\'text/javascript\'>.+?"playlist"(.+?)</script>',
                     name_pattern='"label".+?:.+?"(.+?)"',
                     url_pattern='"file".+?:.+?"(.+?)"')

    def scrape_search(self, html):
        return self.parse(html,
                     part_pattern='<div class="entry">(.+?)</div>',
                     name_pattern='<li><a .+?">(.+?)</a>',
                     url_pattern=None,
                     img_pattern='<img class=.+?src="(.+?)"')

    def top_menu_html(self, ):
        return self.get_url(BASE_URL, 'base.html')

    def all_selected_html(self, ):
        return self.get_url(BASE_URL, 'base.html')

    def alpha_selected_html(self, ):
        return self.get_url(BASE_URL, 'base.html')

    def show_selected_html(self, url):
        return self.get_url(url, 'selected.html')

    def season_selected_html(self, url):
        return self.get_url(url, 'season.html')

    def episode_selected_html(self, url):
        return self.get_url(url, 'episode.html')

    def search_html(self, text):
        url = BASE_URL + '/?' + urllib.urlencode({'s': text, 'op.x': 0, 'op.y': 0})
        return self.get_url(url, 'search.html')

    def get_season_number(self, season):
        s = re.findall('season.+?([0-9]+)', season, re.IGNORECASE)
        if s:
            return s[0]
        else:
            return None

    def get_episode_number(self, episode):
        e = re.findall('episode.+?([0-9]+)', episode, re.IGNORECASE)
        if e:
            return e[0]
        else:
            return None
