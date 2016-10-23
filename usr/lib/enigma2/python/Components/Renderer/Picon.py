# Embedded file name: /usr/lib/enigma2/python/Components/Renderer/Picon.py
import os
from Renderer import Renderer
from enigma import ePixmap
from Tools.Alternatives import GetWithAlternative
from Tools.Directories import pathExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.Harddisk import harddiskmanager
searchPaths = []
lastPiconPath = None

def initPiconPaths():
    global searchPaths
    searchPaths = []
    for mp in ('/usr/share/enigma2/', '/'):
        onMountpointAdded(mp)

    for part in harddiskmanager.getMountedPartitions():
        onMountpointAdded(part.mountpoint)


def onMountpointAdded(mountpoint):
    try:
        path = os.path.join(mountpoint, 'picon') + '/'
        if os.path.isdir(path) and path not in searchPaths:
            for fn in os.listdir(path):
                if fn.endswith('.png'):
                    print '[Picon] adding path:', path
                    searchPaths.append(path)
                    break

    except Exception as ex:
        print '[Picon] Failed to investigate %s:' % mountpoint, ex


def onMountpointRemoved(mountpoint):
    path = os.path.join(mountpoint, 'picon') + '/'
    try:
        searchPaths.remove(path)
        print '[Picon] removed path:', path
    except:
        pass


def onPartitionChange(why, part):
    if why == 'add':
        onMountpointAdded(part.mountpoint)
    elif why == 'remove':
        onMountpointRemoved(part.mountpoint)


def findPicon(serviceName):
    global lastPiconPath
    print '[Picon] Searching for: %s.png' % serviceName
    if lastPiconPath is not None:
        pngname = lastPiconPath + serviceName + '.png'
        if pathExists(pngname):
            return pngname
    for path in searchPaths:
        if pathExists(path):
            pngname = path + serviceName + '.png'
            if pathExists(pngname):
                lastPiconPath = path
                return pngname

    return ''


def getPiconName(serviceName):
    sname = '_'.join(GetWithAlternative(serviceName).split(':', 10)[:10])
    pngname = findPicon(sname)
    if not pngname:
        fields = sname.split('_', 3)
        if len(fields) > 2 and fields[2] != '2':
            fields[2] = '1'
            pngname = findPicon('_'.join(fields))
    return pngname


class Picon(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.pngname = ''
        self.lastPath = None
        pngname = findPicon('picon_default')
        self.defaultpngname = None
        if not pngname:
            tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
            if pathExists(tmp):
                pngname = tmp
            else:
                pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
        if os.path.getsize(pngname):
            self.defaultpngname = pngname
        return

    def addPath(self, value):
        if pathExists(value):
            if not value.endswith('/'):
                value += '/'
            if value not in searchPaths:
                searchPaths.append(value)

    def applySkin(self, desktop, parent):
        attribs = self.skinAttributes[:]
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.addPath(value)
                attribs.remove((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                pngname = getPiconName(self.source.text)
            if not pngname:
                service = self.source.source.service
                info = service and service.info()
                if info:
                    name = info.getName().replace('/', '_').replace('\xc2\x86', '').replace('\xc2\x87', '')
                    pngname = findPicon(name)
                    if not pngname:
                        pngname = findPicon(name.lower())
                    if not pngname:
                        pngname = findPicon(name.upper())
                    if not pngname:
                        name = name.replace(' ', '').replace('.', '')
                        pngname = findPicon(name.lower())
                    if not pngname:
                        pngname = findPicon(name.upper())
            if not pngname:
                pngname = self.defaultpngname
            if self.pngname != pngname:
                if pngname:
                    self.instance.setScale(1)
                    self.instance.setPixmapFromFile(pngname)
                    self.instance.show()
                else:
                    self.instance.hide()
                self.pngname = pngname


harddiskmanager.on_partition_list_change.append(onPartitionChange)
initPiconPaths()