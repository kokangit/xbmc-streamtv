# -*- coding: utf-8 -*-
from mocks import Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon
import streamtv
import sys
import urllib

class Navigation(object):

    def __init__(self, xbmc, xbmcplugin, xbmcgui, xbmcaddon, argv):
        self.xbmc = xbmc
        self.xbmcplugin = xbmcplugin
        self.xbmcgui = xbmcgui
        self.plugin_url = argv[0]
        self.handle = int(argv[1])
        self.params = streamtv.parameters_string_to_dict(argv[2])
        self.settings = xbmcaddon.Addon(id='plugin.video.streamtv')

    def unikeyboard(self, default, message):
        keyboard = self.xbmc.Keyboard(default, message)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return None

    def add_menu_item(self, caption, params, thumb_url=None, plot=None):
        url = self.plugin_url + '?' + urllib.urlencode(params)
        list_item = self.xbmcgui.ListItem(caption)
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        list_item.setInfo(type="Video", infoLabels={"Title": caption})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=True)

    def add_video_item(self, name, caption, url, thumb_url=None):
        list_item = self.xbmcgui.ListItem(caption)
        list_item.setProperty('IsPlayable', 'true')
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        list_item.setInfo(type="Video", infoLabels={"Title": name})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=False)

    def build_main_menu(self):
        self.add_menu_item('A-Ö', {'action': 'alpha'})
        self.add_menu_item('Sök', {'action': 'search'})
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def alpha(self):
        selections = ['0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                      'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                      'V', 'W', 'X', 'Y', 'Z', 'Å', 'Ä', 'Ö']
        for sel in selections:
            self.add_menu_item(sel, {'action': 'alphaselected',
                                     'selected': sel})
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def alpha_selected(self):
        html = streamtv.alpha_selected_html()
        for name, url in \
                streamtv.scrape_shows(html, self.params['selected']):
            params = {
                'action': 'showselected',
                'show': name,
                'url': url
                }
            self.add_menu_item(name, params)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def show_selected(self):
        show_url = self.params['url']
        html = streamtv.show_selected_html(show_url)
        seasons, thumb_url, plot = streamtv.scrape_seasons(html)
        for season in seasons:
            params = {
                'action': 'seasonselected',
                'url': show_url,
                'season': season,
                'thumb_url': thumb_url,
                'plot': plot
                }
            self.add_menu_item(season, params, thumb_url=thumb_url, plot=plot)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def season_selected(self):
        url = self.params['url']
        season = self.params['season']
        thumb_url = self.params['thumb_url']
        plot = self.params['plot']
        html = streamtv.season_selected_html(url)
        for episode, url in \
                streamtv.scrape_episodes(html, season):
            params = {
                'action': 'episodeselected',
                'url': url,
                'thumb_url': thumb_url,
                'title': episode,
                'plot': plot
                }
            self.add_menu_item(episode, params, thumb_url=thumb_url,
                               plot=plot)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def episode_selected(self):
        url = self.params['url']
        title = self.params['title']
        thumb_url = self.params['thumb_url']
        plot = self.params['plot']
        html = streamtv.episode_selected_html(url)
        for caption, url in \
                streamtv.scrape_episode(html):
            self.add_video_item(title, caption, url, thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def search_result(self, title, movie_url):
        for name, url, thumb_url in \
                streamtv.scrape_search(streamtv.get_url(movie_url)):
            params = {
                'action': 'play_video',
                'title': name,
                'movie_url': url if url else movie_url
                }
            self.add_menu_item(name, params, thumb_url=thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def play_video(self, title, movie_url):
        for caption, url, thumb_url in \
                streamtv.scrape_video(streamtv.get_url(movie_url)):
            self.add_video_item(title, caption, url, thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def search(self):
        try:
            latestSearch = self.settings.getSetting("latestSearch")
        except KeyError:
            latestSearch = ""
        text = self.unikeyboard(latestSearch, "")
        if not text or text == "": return
        self.settings.setSetting("latestSearch", text)
        for name, url, thumb_url in \
                streamtv.scrape_search(streamtv.search_html(text)):
            params = {
                'action': 'play_video',
                'title': name,
                'movie_url': url
                }
            self.add_menu_item(name, params, thumb_url=thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def dispatch(self):
        if not 'action' in self.params:
            return self.build_main_menu()
        action = self.params['action']
        if action == 'alpha':
            return self.alpha()
        elif action == 'alphaselected':
            return self.alpha_selected()
        elif action == 'showselected':
            return self.show_selected()
        elif action == 'seasonselected':
            return self.season_selected()
        elif action == 'episodeselected':
            return self.episode_selected()
        elif action == 'play_video':
            return self.play_video(self.params['title'],
                                   self.params['movie_url'])
        elif action == 'search_result':
            return self.search_result(self.params['title'],
                                      self.params['movie_url'])
        elif action == 'search':
            return self.search()

# Use of standalone Navigation for testing:
# python navigation.py <params>
if __name__ == '__main__':
    xbmc = Xbmc(level=Xbmc.LOGNOTICE)
    xbmcplugin = Xbmcplugin(xbmc)
    xbmcgui = Xbmcgui()
    xbmcaddon = Xbmcaddon()
    sys.argv = ['plugin', '10', '?' + sys.argv[1]]
    navigation = Navigation(xbmc, xbmcplugin, xbmcgui, xbmcaddon, sys.argv)
    navigation.dispatch()
