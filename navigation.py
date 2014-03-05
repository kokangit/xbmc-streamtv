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
        infoLabels = {"Title": caption}
        if plot:
            infoLabels['Plot'] = plot
        list_item.setInfo(type="Video", infoLabels=infoLabels)
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=True)

    def add_video_item(self, name, show, season, episode, caption, url,
                       thumb_url=None):
        list_item = self.xbmcgui.ListItem(caption)
        list_item.setProperty('IsPlayable', 'true')
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        season = streamtv.get_season_number(season)
        episode = streamtv.get_episode_number(episode)
        list_item.setInfo(type="Video",
                          infoLabels={'TVshowtitle': show,
                                      'Season': season,
                                      'Episode': episode})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=False)

    def top_menu(self):
        html = streamtv.top_menu_html()
        selections = streamtv.scrape_top_menu(html)
        for sel in selections:
            self.add_menu_item(sel.strip(), {'action': 'alphaselected',
                                             'selected': sel.strip()})
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
        show = self.params['show']
        html = streamtv.show_selected_html(show_url)
        seasons, thumb_url, plot = streamtv.scrape_seasons(html)
        for season in seasons:
            params = {
                'action': 'seasonselected',
                'url': show_url,
                'show': show,
                'season': season,
                'thumb_url': thumb_url,
                'plot': plot
                }
            self.add_menu_item(season, params, thumb_url=thumb_url, plot=plot)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def season_selected(self):
        url = self.params['url']
        show = self.params['show']
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
                'show': show,
                'season': season,
                'episode': episode,
                'plot': plot
                }
            self.add_menu_item(episode, params, thumb_url=thumb_url,
                               plot=plot)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def episode_selected(self):
        url = self.params['url']
        title = self.params['episode']
        show = self.params['show']
        season = self.params['season']
        episode = self.params['episode']
        thumb_url = self.params['thumb_url']
        plot = self.params['plot']
        html = streamtv.episode_selected_html(url)
        for caption, url in \
                streamtv.scrape_episode(html):
            self.add_video_item(title, show, season, episode, caption, url,
                                thumb_url)
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
        html = streamtv.search_html(text)
        for name, url in \
                streamtv.scrape_search(html):
            params = {
                'action': 'showselected',
                'show': name,
                'url': url
                }
            self.add_menu_item(name, params)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def dispatch(self):
        if not 'action' in self.params:
            return self.top_menu()
        action = self.params['action']
        if action == 'alphaselected':
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
        elif action == 'search':
            return self.search()
        elif action == 'search_result':
            return self.search_result(self.params['title'],
                                      self.params['movie_url'])

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
