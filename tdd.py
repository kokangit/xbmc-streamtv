# -*- coding: utf-8 -*-
from copy import deepcopy
from mocks import Xbmc, Xbmcplugin, Xbmcgui, Xbmcaddon
import streamtv
import unittest
from navigation import Navigation

class FirstTests(unittest.TestCase):
    def setUp(self):
        self.xbmc = Xbmc(Xbmc.LOGERROR)
        self.xbmcplugin = Xbmcplugin(self.xbmc)
        self.xbmcgui = Xbmcgui()
        self.xbmcaddon = Xbmcaddon()

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
        nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                         self.xbmcaddon, argv)
        self.assertEquals(nav.plugin_url, 'plugin')
        self.assertEquals(nav.handle, 1)
        self.assertEquals(nav.params, {})

        # call with no parameters
        nav.dispatch()
        self.assertTrue(len(self.xbmcplugin.dir_items) > 0)
        self.assertEquals(self.xbmcplugin.dir_items[0][2].caption, 'Alla')

        # select first item in list
        params = self.xbmcplugin.dir_items[0][1].split('?')[1]
        argv = ['plugin', '1', '?' + params]
        self.xbmcplugin.reset()
        nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                         self.xbmcaddon, argv)
        nav.dispatch()
        self.assertTrue(len(self.xbmcplugin.dir_items) > 0)

    def test_nav_params(self):
        argv = ['default.py', '10', '?mode=search']
        nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                         self.xbmcaddon, argv)
        self.assertEquals(nav.params, {'mode': 'search'})

    def test_traverse_all(self):
        argv = ['plugin', '1', '']
        nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                         self.xbmcaddon, argv)
        self.assertEquals(nav.plugin_url, 'plugin')
        self.assertEquals(nav.handle, 1)
        self.assertEquals(nav.params, {})

        # call with no parameters
        nav.dispatch()
        self.traverse_video = False
        self.traverse(self.xbmcplugin.dir_items, [])

    def traverse(self, dir_items, stack):
        print '***** stack: ' + str(stack)
        i = 0
        for (handle, url, listitem, isFolder) in dir_items:
            i += 1
            params = url.split('?')[1]
            if isFolder or (self.traverse_video and url.find('plugin') == 0):
                stack.append(i)
                print '***** selecting %d: %s' % (i, listitem.caption)
                argv = ['plugin', '1', '?' + params]
                self.xbmcplugin.reset()
                nav = Navigation(self.xbmc, self.xbmcplugin, self.xbmcgui,
                                 self.xbmcaddon, argv)
                nav.dispatch()
                new_list = deepcopy(self.xbmcplugin.dir_items)
                self.traverse(new_list, stack)
            else:
                pass
        if len(stack) > 0:
            stack.pop()
        return

if __name__ == '__main__':
    unittest.main()
