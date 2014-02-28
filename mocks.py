# Mocks for testing


class Xbmc(object):
    BACK = 1
    LOGERROR = ['ERROR', 1]
    LOGNOTICE = ['NOTICE', 2]

    def __init__(self, level=LOGERROR):
        self.level = level

    class Keyboard(object):
        def __init__(self, placeholder, header, hidden):
            self.placeholder = placeholder
            self.header = header
            self.hidden = hidden

        def doModal(self):
            pass

        def isConfirmed(self):
            return True

        def getText(self):
            return 'bad'

    def log(self, msg, level=LOGNOTICE):
        if level[1] <= self.level[1]:
            print msg

    class Player(object):
        def play(self, *args, **kwargs):
            print 'playing stream %s (%s)'  % (kwargs['listitem'].infoLabels['Title'], kwargs['item'])
            return Xbmc.BACK


class Xbmcplugin(object):

    def __init__(self, xbmc):
        self.xbmc = xbmc
        self.dir_items = []

    def addDirectoryItem(self, handle, url, listitem, isFolder):
        self.dir_items.append((handle, url, listitem, isFolder))
        self.xbmc.log('addDirectoryItem %s - %s' % (str(listitem.caption),
                                                    str(url)), Xbmc.LOGNOTICE)

    def endOfDirectory(self, handle, succeeded=None, updateListing=None,
                       cacheToDisc=None):
        pass


class Xbmcgui(object):
    class ListItem(object):

        def __init__(self, *args, **kwargs):
            if len(args) == 1:
                self.caption = args[0]

        def setInfo(self, type, infoLabels):
            self.type = type
            self.infoLabels = infoLabels

        def setThumbnailImage(self, thumb_url):
            pass

    class Dialog(object):
        def ok(self, title, msg):
            print '[DIALOG] %s - %s' % (title, msg)
            return Xbmc.BACK

        def select(self, title, alternatives):
            print '[DIALOG SELECT] %s' % title
            print "\n".join(alternatives)
            return 0  # Select first one"

