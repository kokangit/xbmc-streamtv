# -*- coding: utf-8 -*-
import streamtv
import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmc
from navigation import Navigation

streamtv = streamtv.Streamtv(xbmc, xbmcplugin, xbmcgui, xbmcaddon)
navigation = Navigation(xbmc, xbmcplugin, xbmcgui, xbmcaddon, streamtv, sys.argv)
navigation.dispatch()
