# -*- coding: utf-8 -*-
import sys
import xbmcplugin
import xbmcgui
import xbmc
from navigation import Navigation

navigation = Navigation(xbmc, xbmcplugin, xbmcgui, sys.argv)
navigation.dispatch()
