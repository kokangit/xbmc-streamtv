# -*- coding: utf-8 -*-
import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
from navigation import Navigation

navigation = Navigation(xbmc, xbmcplugin, xbmcgui, xbmcaddon, sys.argv)
navigation.dispatch()
