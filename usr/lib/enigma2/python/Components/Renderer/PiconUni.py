from Renderer import Renderer
from enigma import ePixmap
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS, resolveFilename

class PiconUni(Renderer):
    __module__ = __name__

    def __init__(self):
        Renderer.__init__(self)
        self.path = 'piconUni'
        self.scale = '0'
        self.nameCache = {}
        self.pngname = ''

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            elif attrib == 'noscale':
                self.scale = value
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = ''
            if what[0] is not self.CHANGED_CLEAR:
                sname = self.source.text
                sname = sname.upper().replace('.', '').replace('\xc2\xb0', '')
                if sname.startswith('4097'):
                    sname = sname.replace('4097', '1', 1)
                if ':' in sname:
                    sname = '_'.join(sname.split(':')[:10])
                pngname = self.nameCache.get(sname, '')
                if pngname is '':
                    pngname = self.findPicon(sname)
                    if pngname is not '':
                        self.nameCache[sname] = pngname
            if pngname is '':
                pngname = self.nameCache.get('default', '')
                if pngname is '':
                    pngname = self.findPicon('picon_default')
                    if pngname is '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                    self.nameCache['default'] = pngname
            if self.pngname is not pngname:
                if self.scale is '0':
                    if pngname:
                        self.instance.setScale(1)
                        self.instance.setPixmapFromFile(pngname)
                        self.instance.show()
                    else:
                        self.instance.hide()
                elif pngname:
                    self.instance.setPixmapFromFile(pngname)
                self.pngname = pngname

    def findPicon(self, serviceName):
        searchPaths = []
        if fileExists('/proc/mounts'):
            for line in open('/proc/mounts'):
                if '/dev/sd' in line:
                    searchPaths.append(line.split()[1].replace('\\040', ' ') + '/%s/')

        searchPaths.append(resolveFilename(SCOPE_CURRENT_SKIN, '%s/'))
        searchPaths.append(resolveFilename(SCOPE_PLUGINS, '%s/'))
        pathtmp = self.path.split(',')
        for path in searchPaths:
            for i in pathtmp:
                pngname = path % i + serviceName + '.png'
                if fileExists(pngname):
                    return pngname

        return ''