# -*- coding: utf-8 -*-
from mocks import Xbmc, Xbmcplugin, Xbmcgui
import streamtv
import sys
import urllib

class Navigation(object):

    def __init__(self, xbmc, xbmcplugin, xbmcgui, argv):
        self.xbmc = xbmc
        self.xbmcplugin = xbmcplugin
        self.xbmcgui = xbmcgui
        self.plugin_url = argv[0]
        self.handle = int(argv[1])
        self.params = streamtv.parameters_string_to_dict(argv[2])

    def add_menu_item(self, caption, params, thumb_url=None):
        url = self.plugin_url + '?' + urllib.urlencode(params)
        list_item = self.xbmcgui.ListItem(caption)
        if thumb_url:
            list_item.setThumbnailImage(thumb_url)
        list_item.setInfo(type="Video", infoLabels={"Title": caption})
        return self.xbmcplugin.addDirectoryItem(handle=self.handle, url=url,
                                                listitem=list_item,
                                                isFolder=True)

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

    def alphaselected(self):
        html = streamtv.alpha_html()
        for name, url, thumb_url in \
                streamtv.scrap_alpha(html, self.params['selected']):
            params = {
                'action': 'play_movie',
                'title': name,
                'movie_url': url
                }
            self.add_menu_item(name, params, thumb_url)
        return self.xbmcplugin.endOfDirectory(self.handle, succeeded=True,
                                              cacheToDisc=True)

    def play_movie(self, title, movie_url):
        player_urls = streamtv.scrap_movie(streamtv.get_url(movie_url))
        if len(player_urls) > 1:
            return self.list_movie_parts(title, player_urls)

        if len(player_urls) == 0:
            dialog = self.xbmcgui.Dialog()
            return dialog.ok("Error", "No stream found")

        return self.play_stream(title, player_urls[0])

    def search(self):
        kb = self.xbmc.Keyboard('', 'Search', False)
        kb.doModal()
        if kb.isConfirmed():
            text = kb.getText()
            matches = dreamfilm.scrap_search(dreamfilm.search(text))
            for m in matches:
                self.add_movie_list_item(m[0], m[1])
            return self.xbmcplugin.endOfDirectory(self.handle)

    def dispatch(self):
        if not 'action' in self.params:
            return self.build_main_menu()
        action = self.params['action']
        if action == 'alpha':
            return self.alpha()
        elif action == 'alphaselected':
            return self.alphaselected()
        elif action == 'play_movie':
            return self.play_movie(self.params['title'],
                                   self.params['movie_url'])
        elif action == 'search':
            return self.search()

# Use of standalone Navigation for testing:
# python navigation.py <params>
if __name__ == '__main__':
    xbmc = Xbmc(level=Xbmc.LOGNOTICE)
    xbmcplugin = Xbmcplugin(xbmc)
    xbmcgui = Xbmcgui()
    sys.argv = ['plugin', '10', '?' + sys.argv[1]]
    navigation = Navigation(xbmc, xbmcplugin, xbmcgui, sys.argv)
    navigation.dispatch()
