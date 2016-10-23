# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/Picon2.py
from Renderer import Renderer
from enigma import ePixmap, eServiceReference
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename

class Picon2(Renderer):
    searchPaths = ('/usr/share/enigma2/%s/', '/media/sde1/%s/', '/media/cf/%s/', '/media/sda1/%s/', '/media/usb/%s/', '/etc/%s/', '/mnt/ba/%s/', '/media/sda/%s/')

    def __init__(self):
        Renderer.__init__(self)
        self.path = 'picon'
        self.nameCache = {}
        self.pngname = ''

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                service = self.source.service
                marker = service.flags & eServiceReference.isMarker == eServiceReference.isMarker
                bouquet = service.flags & eServiceReference.flagDirectory == eServiceReference.flagDirectory
                print marker
                print bouquet
                if marker:
                    pngname = self.nameCache.get('marker', '')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'marker.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/marker.png')
                        self.nameCache['marker'] = pngname
                elif bouquet:
                    pngname = self.nameCache.get('bouquet', '')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'bouquet.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/bouquet.png')
                        self.nameCache['bouquet'] = pngname
                else:
                    sname = service.toString()
                    pos = sname.rfind(':')
                    if pos != -1:
                        sname = sname[:pos].rstrip(':').replace(':', '_')
                    pngname = self.nameCache.get(sname, '')
                    if pngname == '':
                        pngname = self.findPicon(sname)
                        if pngname != '':
                            self.nameCache[sname] = pngname
            if pngname == '':
                pngname = self.nameCache.get('default', '')
                if pngname == '':
                    pngname = self.findPicon('picon_default')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                    self.nameCache['default'] = pngname
            if self.pngname != pngname:
                self.instance.setPixmapFromFile(pngname)
                self.pngname = pngname

    def findPicon(self, serviceName):
        for path in self.searchPaths:
            pngname = path % self.path + serviceName + '.png'
            if fileExists(pngname):
                return pngname

        return ''