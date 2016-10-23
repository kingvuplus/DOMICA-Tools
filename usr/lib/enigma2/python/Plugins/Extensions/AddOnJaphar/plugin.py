# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/AddOnJaphar/plugin.py
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from xml.dom import Node, minidom
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from enigma import *
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from twisted.web.client import downloadPage, getPage
import urllib
from Components.Label import Label
from os import *
from os import listdir, sys
from enigma import eEnv
from Components.ConfigList import ConfigListScreen
from Screens.Standby import TryQuitMainloop
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel
from skin import loadSkin
from Components.config import config, ConfigSubsection, ConfigYesNo, getConfigListEntry, ConfigInteger, ConfigText, ConfigYesNo, configfile
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import glob
import gettext

currversion = '5.3'


plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/AddOnJaphar/'
loadSkin(plugin_path + '/images/skin.xml')


class gpupdatesScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        info = ''
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        try:
            fp = urllib.urlopen('http://jam.japhar.com/download/addons/updates.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('Error in downloading updates')


class addonsupdatesScreen(Screen):
    
    def __init__(self, session):
        Screen.__init__(self, session)
        info = ''
        self['text'] = ScrollLabel(info)
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'ok': self.close,
         'cancel': self.close,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown}, -1)
        try:
            fp = urllib.urlopen('http://jam.japhar.com/download/addons/addons-updates.txt')
            count = 0
            self.labeltext = ''
            while 1:
                s = fp.readline()
                count += 1
                self.labeltext += str(s)
                if not s:
                    break

            fp.close()
            self['text'].setText(self.labeltext)
        except:
            self['text'].setText('unable to download updates')


class AboutScreen(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        info = '\n Japhar Addons/Plugin v5.3\n ---------------------------------------------------------------------- \n\n Addons/Plugin Tool connects all enigma2\n images with Server for downloading\n plugins, skins...\n\n ---------------------------------------------------------------------- \n                      www.japhar.com\n                    (c) WarLord 2015'
        self['text'] = ScrollLabel(info)
        self['key_yellow'] = Button(_('Server news'))
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
	 'yellow': self.shownews,
         'up': self['text'].pageUp,
         'down': self['text'].pageDown,
         'left': self['text'].pageUp,
         'right': self['text'].pageDown,
         'cancel': self.close}, -1)


    def shownews(self):
        self.session.open(addonsupdatesScreen)


class AddonsGroups(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Update Plugin'))
        self['key_yellow'] = Button(_('Ipk Manual'))
        self['key_blue'] = Button(_('About'))
        self.list = []
        self['list'] = MenuList([])
        self['info'] = Label()
        self['fspace'] = Label()
        self.addon = 'emu'
        self.icount = 0
        self.downloading = False
        self['info'].setText('Downloading addons groups, Please wait...')
        self.timer = eTimer()
        self.timer.callback.append(self.downloadxmlpage)
        self.timer.start(100, 1)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.okClicked,
         'blue': self.ShowAbout,
         'yellow': self.ShowIPKmnl,
         'green': self.pluginupdate,
         'red': self.close,
         'cancel': self.close}, -2)


    
    def ShowIPKmnl(self):
        self.session.open(IPKmanual)
    

    def updateable(self):
        try:
            selection = str(self.names[0])
            lwords = selection.split('_')
            lv = lwords[1]
            self.lastversion = lv
            if float(lv) == float(currversion):
                return False
            if float(lv) > float(currversion):
                return True
            return False
        except:
            return False

    def ShowAbout(self):
        self.session.open(AboutScreen)

    def pluginupdate(self):
        softupdate = self.updateable()
        if softupdate == True:
            com = 'http://jam.japhar.com/download/addons/japhar-addons-manager_' + self.lastversion + '_DM_oe16_all.ipk'
        else:
            self.session.open(MessageBox, 'Plugin is up-to-date', MessageBox.TYPE_WARNING, 2)
            return
        dom = 'Japhar Addons Manager' + self.lastversion
        self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])

    def downloadxmlpage(self):
        url = 'http://fam.japhar.com/download/addons/addons.xml'
        getPage(url).addCallback(self._gotPageLoad).addErrback(self.errorLoad)

    def errorLoad(self, error):
        print str(error)
        self['info'].setText('Addons Download Failure, No internet connection or Server down !')
        self.downloading = False

    def _gotPageLoad(self, data):
        self.xml = data
        try:
            if self.xml:
                xmlstr = minidom.parseString(self.xml)
            else:
                self.downloading = False
                self['info'].setText('Addons Download Failure, No internet connection or server down !')
                return
            self.data = []
            self.names = []
            icount = 0
            list = []
            xmlparse = xmlstr
            self.xmlparse = xmlstr
            for plugins in xmlstr.getElementsByTagName('plugins'):
                self.names.append(plugins.getAttribute('cont').encode('utf8'))

            self.list = list
            self['info'].setText('')
            self['list'].setList(self.names)
            self.downloading = True
        except:
            self.downloading = False
            self['info'].setText('Error processing server addons data.')

    def okClicked(self):
        if self.downloading == True:
            try:
                selection = str(self['list'].getCurrent())
                self.session.open(IpkgPackages, self.xmlparse, selection)
            except:
                return

        else:
            self.close




class IPKmanual(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.flist = []
        idx = 0
        ipkpth = ("/tmp")
        pkgs = listdir("/tmp")
        for fil in pkgs:
            if fil.find('.ipk') != -1:
                res = (fil, idx)
                self.flist.append(res)
                idx = idx + 1

        self['Title'] = Label(_('Install Manual Ipk'))
        self['Title2'] = Label(_('Select Package from /tmp to Install'))
        self['key_red'] = Label(_('Close'))
        self['key_green'] = Label(_('Install'))
        self['ipkglist'] = List(self.flist)
        self['actions'] = ActionMap(['OkCancelActions', 'WizardActions', 'ColorActions'],
            {
                'ok': self.ipkginst,
                'red': self.close,
                'green': self.ipkginst,
                'cancel': self.close
            }, -1)


    def ipkginst(self):
        self.sel = self['ipkglist'].getCurrent()
        if self.sel:
            self.sel = self.sel[0]
            message = _('Do you really want to install the selected Addon')+_(' :\n ') + self.sel + _(' ?')
            ybox = self.session.openWithCallback(self.ipkginst2, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('IPK Manual Installation'))

    def ipkginst2(self, answer):
        if answer is True:
            ipkpth = ("/tmp")
            dest = ipkpth + '/' + self.sel
            mydir = getcwd()
            chdir('/')
            cmd0 = 'opkg install --noaction %s > /tmp/package.info' % dest
            cmd1 = 'opkg install --force-overwrite ' + dest
            self.session.open(Console, title='IPK Manual Installation', cmdlist=[cmd0,
             cmd1,
             'sleep 5'], finishedCallback=self.msginst)
            chdir(mydir)

    def msginst(self):
        self.session.openWithCallback(self.extrstrt, MessageBox, _("Do you want restart enigma2 to reload installed addons ?"), MessageBox.TYPE_YESNO)

    def extrstrt(self, result):
        if result :
            self.session.open(TryQuitMainloop, 3)
        else :
            self.close()


class IpkgPackages(Screen):

    def __init__(self, session, xmlparse, selection):
        #self.skin = IpkgPackages.skin
        Screen.__init__(self, session)
        self.xmlparse = xmlparse
        self.selection = selection
        list = []
        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    list.append(plugin.getAttribute('name').encode('utf8'))

        list.sort()
        self['countrymenu'] = MenuList(list)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.selclicked,
         'red': self.selremoved,
         'green': self.selremoved,
         'yellow': self.seldowngrade,
         'blue': self.seldowngrade,
         'cancel': self.close}, -2)

    def selclicked(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombt(urlserver, pluginname)

    def prombt(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsg, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
        else:
            self.session.open(Console, _('downloading-installing: %s') % dom, ['opkg install -force-overwrite %s' % com])

    def callMyMsg(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console, _('downloading-installing: %s') % dom, ['ipkg install -force-overwrite %s' % com])

    def selremoved(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombtremoved(urlserver, pluginname)

    def prombtremoved(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsgRemove, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
        else:
            self.session.open(Console, _('downloading-removing: %s') % dom, ['opkg remove %s' % com])

    def callMyMsgRemove(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console, _('downloading-removing: %s') % dom, ['ipkg remove %s' % com])

    def seldowngrade(self):
        try:
            selection_country = self['countrymenu'].getCurrent()
        except:
            return

        for plugins in self.xmlparse.getElementsByTagName('plugins'):
            if str(plugins.getAttribute('cont').encode('utf8')) == self.selection:
                for plugin in plugins.getElementsByTagName('plugin'):
                    if plugin.getAttribute('name').encode('utf8') == selection_country:
                        urlserver = str(plugin.getElementsByTagName('url')[0].childNodes[0].data)
                        pluginname = plugin.getAttribute('name').encode('utf8')
                        self.prombtdowngrade(urlserver, pluginname)

    def prombtdowngrade(self, com, dom):
        self.com = com
        self.dom = dom
        if self.selection == 'Skins':
            self.session.openWithCallback(self.callMyMsgDowngrade, MessageBox, _('Do not install any skin unless you are sure it is compatible with your image.Are you sure?'), MessageBox.TYPE_YESNO)
        else:
            self.session.open(Console, _('downloading-downgrading: %s') % dom, ['opkg install -force-downgrade %s' % com])

    def callMyMsgDowngrade(self, result):
        if result:
            dom = self.dom
            com = self.com
            self.session.open(Console, _('downloading-downgrading: %s') % dom, ['ipkg install -force-downgrade %s' % com])


def main(session, **kwargs):
    session.open(AddonsGroups)


def Plugins(**kwargs):
    return PluginDescriptor(name='Japhar Addons Manager 5.3', description=_('Download your favorite plugin !'), where=[PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU], icon='images/addons.png', fnc=main)