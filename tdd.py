# -*- coding: utf-8 -*-
from mocks import Xbmc, Xbmcplugin, Xbmcgui
import unittest
from navigation import Navigation

class FirstTests(unittest.TestCase):
    def test_navigation(self):
        argv = ['plugin', '1', '']
        xbmc = Xbmc()
        xbmcplugin = Xbmcplugin(xbmc)
        xbmcgui = Xbmcgui()
        nav = Navigation(Xbmc, Xbmcplugin, Xbmcgui, argv)
        self.assertEquals(nav.plugin_url, 'plugin')
        self.assertEquals(nav.handle, 1)
        self.assertEquals(nav.params, {})

    def test_nav_params(self):
        xbmc = Xbmc()
        xbmcplugin = Xbmcplugin(xbmc)
        xbmcgui = Xbmcgui()
        argv = ['default.py', '10', '?mode=search']
        nav = Navigation(Xbmc, Xbmcplugin, Xbmcgui, argv)
        self.assertEquals(nav.params, {'mode': 'search'})

if __name__ == '__main__':
    unittest.main()
