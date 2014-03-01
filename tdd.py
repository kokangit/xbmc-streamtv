# -*- coding: utf-8 -*-
from mocks import Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon
import streamtv
import unittest
from navigation import Navigation

class FirstTests(unittest.TestCase):
    def test_streamtv(self):
        params = streamtv.parameters_string_to_dict('?mode=search')
        self.assertEquals(params, {'mode': 'search'})
        params = streamtv.parameters_string_to_dict('?action=search_result&movie_url=http%3A%2F%2Fstream-tv.me%2Fwatch-arrow-online-streaming%2F&title=Arrow')
        self.assertEquals(params['action'], 'search_result')
        self.assertEquals(params['movie_url'],
                          'http://stream-tv.me/watch-arrow-online-streaming/')
        self.assertEquals(params['title'], 'Arrow')

    def test_navigation(self):
        argv = ['plugin', '1', '']
        xbmc = Xbmc()
        xbmcplugin = Xbmcplugin(xbmc)
        xbmcgui = Xbmcgui()
        xbmcaddon = Xbmcaddon()
        nav = Navigation(Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon, argv)
        self.assertEquals(nav.plugin_url, 'plugin')
        self.assertEquals(nav.handle, 1)
        self.assertEquals(nav.params, {})

    def test_nav_params(self):
        xbmc = Xbmc()
        xbmcplugin = Xbmcplugin(xbmc)
        xbmcgui = Xbmcgui()
        xbmcaddon = Xbmcaddon()
        argv = ['default.py', '10', '?mode=search']
        nav = Navigation(Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon, argv)
        self.assertEquals(nav.params, {'mode': 'search'})

if __name__ == '__main__':
    unittest.main()
