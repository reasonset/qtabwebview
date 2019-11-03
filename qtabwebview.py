#!/usr/bin/python

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

THIS_APP_UA = "QTabWebView/0.01"

class TabWidget(QTabWidget):
    def __init__(self, url, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        url = QUrl(url)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_handler)
        view = HtmlView(self)
        self.view = view

        ##### Set Curtom profile #####
        pfn = os.environ.get("qtwview_profile")
        if (pfn):
            pf = QWebEngineProfile(pfn, view)
            page = QWebEnginePage(pf, view)
            view.setPage(page)
        profile = view.page().profile()
        profile.setHttpUserAgent(view.page().profile().httpUserAgent() + " " + THIS_APP_UA)
        ##############################

        ##### Address bar #####
        addrbar = QLineEdit()
        addrbar.setSizePolicy(QSizePolicy.Expanding, addrbar.sizePolicy().verticalPolicy())
        addrbar.returnPressed.connect(self.change_location)
        self.addrbar = addrbar

        self.setCornerWidget(addrbar)
        #######################

        view.load(url)
        ix = self.addTab(view, "loading ...")

        ##### Define keyboard shortcuts #####
        QShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_PageDown), self).activated.connect(self.pagedown)
        QShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_PageUp), self).activated.connect(self.pageup)
        QShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_W), self).activated.connect(self.closetab)
        QShortcut(QtGui.QKeySequence(Qt.CTRL | Qt.Key_R), self).activated.connect(self.reloadtab)
        QShortcut(QtGui.QKeySequence(Qt.Key_F5), self).activated.connect(self.reloadtab)
        QShortcut(QtGui.QKeySequence(Qt.ALT | Qt.Key_Left), self).activated.connect(self.pageback)
        QShortcut(QtGui.QKeySequence(Qt.ALT | Qt.Key_Right), self).activated.connect(self.pagefw)
        ####################################

    def pagedown(self):
        nextnum = self.currentIndex() + 1
        tabnum = self.count()
        if (nextnum < tabnum):
            self.setCurrentIndex(nextnum)

    def pageup(self):
        nextnum = self.currentIndex() - 1
        if (nextnum >= 0):
            self.setCurrentIndex(nextnum)

    def closetab(self):
        self.removeTab(self.currentIndex())

    def reloadtab(self):
        self.widget(self.currentIndex()).reload()

    def pageback(self):
        self.widget(self.currentIndex()).back()

    def pagefw(self):
        self.widget(self.currentIndex()).forward()

    def close_handler(self, index):
        self.removeTab(index)

    def change_location(self):
        url = self.addrbar.text()
        if not re.match('^[a-z]+://', url):
            url = "http://" + url
        self.widget(self.currentIndex()).load(QUrl(url))
        
class HtmlView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        QWebEngineView.__init__(self, *args, **kwargs)
        self.tab = self.parent()
        self.loadFinished.connect(self.change_tabtitle)

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            webView = HtmlView(self.tab)
            ix = self.tab.addTab(webView, "Loading…")
            self.tab.setCurrentIndex(ix)
            return webView
        return QWebEngineView.createWindow(self, windowType)

    def change_tabtitle(self):
        pagetitle = self.page().title()
        if (len(pagetitle) > 24):
            pagetitle = pagetitle[:23] + "…"
        thisindex = self.tab.indexOf(self)
        self.tab.setTabText(thisindex, pagetitle)

if __name__ == "__main__":
    import sys
    import re
    import os
    argv = sys.argv
    argc = len(argv)

    if (argc != 2):
        url = "https://duckduckgo.com/"
    else: 
        url = argv[1]

    # For opening local file.
    if re.match('^[a-z]+://', url):
        pass # do nothing.
    elif re.match('^/', url):
        url = 'file://' + url
    else:
        url = "http://" + url

    app = QApplication(["QtabWebView"])
    # Choice application icon. I don't know smart way for choice generic web browser icon.
    for iconpath in ["Papirus/64x64/apps/redhat-web-browser.svg", "Vibrancy-Colors/apps/96/browser.png", "Papirus/64x64/apps/internet-web-browser.svg", "breeze/apps/48/plasma-browser-integration.svg", "breeze/apps/48/internet-web-browser.svg", "Adwaita/scalable/apps/web-browser-symbolic.svg", "gnome/256x256/apps/web-browser.png", "ePapirus/22x22/actions/web-browser.svg", "AwOken/clear/128x128/apps/browser.png", "andromeda/apps/48/internet-web-browser.svg"]:
        if os.path.exists("/usr/share/icons/" + iconpath):
            app.setWindowIcon(QtGui.QIcon.fromTheme("web-browser", QtGui.QIcon("/usr/share/icons/" + iconpath)))
            break
    main = TabWidget(url)

    main.show()
    sys.exit(app.exec_())