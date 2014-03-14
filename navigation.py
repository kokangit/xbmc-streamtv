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
        self.localize = self.settings.getLocalizedString

    def unikeyboard(self, default, message):
        keyboard = self.xbmc.Keyboard(default, message)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            return keyboard.getText()
        else:
            return None

    def quality_select_dialog(self, stream_urls):
        if not stream_urls:
            return None
        qualities = [s[0] for s in stream_urls]
        dialog = self.xbmcgui.Dialog()
        answer = 0
        if len(qualities) > 1:
            answer = dialog.select(self.localize(30000), qualities)
            if answer == -1:
                return None
        url = stream_urls[answer][1]
        return url

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

    def add_video_item(self, caption, params, thumb_url=None, plot=None):
        url = self.plugin_url + '?' + urllib.urlencode(params)
        list_item = self.xbmcgui.ListItem(caption)
        list_item.setProperty('IsPlayable', 'true')
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        season = streamtv.get_season_number(params['season'])
        episode = streamtv.get_episode_number(params['episode'])
        infoLabels = {'TVshowtitle': params['show'],
                      'Season': season,
                      'Episode': episode}
        if plot:
            infoLabels['Plot'] = plot
        list_item.setInfo(type="Video", infoLabels=infoLabels)
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=False)

    def all(self):
        html = streamtv.all_selected_html()
        for name, url in \
                streamtv.scrape_all(html):
            params = {
                'action': 'showselected',
                'show': name,
                'url': url
                }
            self.add_menu_item(name, params)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def top_menu(self):
        self.add_menu_item(self.localize(30101), {'action': 'all'})
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
            self.add_video_item(episode, params, thumb_url=thumb_url,
                               plot=plot)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def episode_selected(self):
        url = self.params['url']
        title = self.params['episode']
        thumb_url = self.params['thumb_url']
        plot = self.params['plot']
        html = streamtv.episode_selected_html(url)
        streams = streamtv.scrape_episode(html)
        url = self.quality_select_dialog(streams)
        if not url:
            self.xbmcplugin.setResolvedUrl(self.handle, succeeded=False,
                                           listitem=self.xbmcgui.ListItem(''))
            return self.xbmcplugin.endOfDirectory(self.handle, succeeded=False,
                                                  cacheToDisc=True)
        list_item = self.xbmcgui.ListItem(title)
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        season = streamtv.get_season_number(self.params['season'])
        episode = streamtv.get_episode_number(self.params['episode'])
        infoLabels = {'TVshowtitle': self.params['show'],
                      'Season': season,
                      'Episode': episode}
        if plot:
            infoLabels['Plot'] = plot
        list_item.setInfo(type="Video", infoLabels=infoLabels)
        list_item.setPath(url)
        self.xbmcplugin.setResolvedUrl(self.handle, url!=None, list_item)
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
        if action == 'all':
            return self.all()
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
