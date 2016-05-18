# -*- coding: utf-8 -*-

import sys
sys.dont_write_bytecode = True

import os
import json
import glob
import inspect
import requests
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils     import *
from VccReqRes import *

VERSION = "1.0.0"
URL = {
    "github"    : "https://github.com/plusseed/ViewCamCloud-API-Tool",
    "reference" : "https://api-v3.nexts.tv/doc/",
    "manual"    : "https://github.com/plusseed/ViewCamCloud-API-Tool",
}

class UiMain(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(UiMain, self).__init__(parent)
        try:
            self.initUI()
        except Exception as e:
            print e

    def resizeEvent(self, event):
        width  = event.size().width()
        height = event.size().height()

        self.UiApiTree.resize(int(width * 0.25), int(height * 0.6))
        self.UiHistory.move(0, int(height * 0.6)+20+1)
        self.UiHistory.resize(int(width * 0.25), int(height * 0.4)-20-1)
        self.UiReqRes.move(int(width * 0.25)+1, 20)
        self.UiReqRes.resize(int(width * 0.75)-1, int(height)-20)

    def initUI(self):
        self.setWindowTitle(u'ViewCamCloud API Tool')
        self.setWindowIcon(QtGui.QIcon('favicon.png'))
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        #self.setFixedSize(800, 600)

        self.initMenubar()

        self.UiApiTree = self.initApiTree()
        self.UiHistory = self.initHistory()
        self.UiReqRes  = UiReqRes(self)

    def initMenubar(self):
        '''
            メニューバー
        '''
        Lmenubar = self.menuBar()

        ###############################################################
        p = Lmenubar.addMenu(u'プロファイル')
        p1 = p.addAction(u'設定')
        p1.triggered.connect(self.open_ProfileSetting)
        #p.addAction('読み込み')
        p.addSeparator()
        files = glob.glob('cache/*.profile')
        for filename in files:
            unique, ext = os.path.splitext(os.path.basename(filename))
            p.addAction(unique)
        p.addSeparator()
        p.addAction(u'終了')

        ###############################################################
        t = Lmenubar.addMenu(u'ツール')
        #t.addAction(u'マクロの読み込み')
        #t.addAction(u'マクロの記録')
        #t.addAction(u'マクロの再生')

        ###############################################################
        Rmenubar = QtGui.QMenuBar(Lmenubar)
        Lmenubar.setCornerWidget(Rmenubar, QtCore.Qt.TopRightCorner)

        h = Rmenubar.addMenu(u'ヘルプ')
        h1 = h.addAction(u'APIリファレンス')
        h1.triggered.connect(self.open_ApiReference)
        h2 = h.addAction(u'使い方')
        h2.triggered.connect(self.open_Manual)
        h3 = h.addAction(u'バージョン')
        h3.triggered.connect(self.open_Version)

        self.setMenuBar(Lmenubar)

    def initApiTree(self):
        '''
            APIツリー
        '''
        width  = self.frameGeometry().width()
        height = self.frameGeometry().height()

        ApiTree = QtGui.QTreeWidget(self)
        ApiTree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        ApiTree.header().setStretchLastSection(False)
        ApiTree.move(0, 20)

        ApiTree.setColumnCount(1)
        ApiTree.setHeaderLabels([u"API一覧"])

        apis = json.load(open("api.json"))
        for key in apis.keys():
            item = QtGui.QTreeWidgetItem(ApiTree)
            item.setText(0, key)
            for child in apis[key]["list"]:
                item2 = QtGui.QTreeWidgetItem([child["title"]])
                item2.setData(0, QtCore.Qt.UserRole, child)
                item.addChild(item2)

        ApiTree.resize(int(width * 0.25), int(height * 0.6))
        ApiTree.itemClicked.connect(self.on_click_ApiTree)

        return ApiTree

    def on_click_ApiTree(self, item, column):
        '''
            API一覧クリック時
        '''
        child = item.data(column, QtCore.Qt.UserRole)
        grid = self.UiReqRes.grid
        if child:
            # show right widget
            class_obj = globals()[child['class']]
            if not inspect.isclass(class_obj):
                print "%s class is not found" % class_obj
                return
            class_obj(self, grid)
        else:
            #clear right widget
            for i in reversed(range(grid.count())): 
                grid.itemAt(i).widget().deleteLater()

    def initHistory(self):
        '''
            履歴
        '''
        width  = self.frameGeometry().width()
        height = self.frameGeometry().height()

        History = QtGui.QTreeWidget(self)
        History.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        History.header().setStretchLastSection(False)
        History.move(0, int(height * 0.6)+20+1)

        History.setColumnCount(1)
        History.setHeaderLabels([u"履歴"])

        for i in range(50):
            item = QtGui.QTreeWidgetItem(History)
            item.setText(0, str(i))

        History.resize(int(width * 0.25), int(height * 0.4)-20-1)

        return History

    def open_ProfileSetting(self):
        '''
            プロファイル > 設定
        '''
        self.UiProfileSetting = UiProfileSetting(self)
        self.UiProfileSetting.show()

    def open_ApiReference(self):
        '''
            ヘルプ > APIリファレンス
        '''
        self.UiApiReference = UiApiReference()
        self.UiApiReference.show()

    def open_Manual(self):
        '''
            ヘルプ > 使い方
        '''
        self.UiManual = UiManual()
        self.UiManual.show()

    def open_Version(self):
        '''
            ヘルプ > バージョン
        '''
        self.UiVersion = UiVersion(self)
        self.UiVersion.show()

class UiReqRes(QtGui.QWidget):
    '''
        リクエスト・レスポンス用レイアウト
    '''
    def __init__(self, parent=None):
        super(UiReqRes, self).__init__(parent)

        width  = parent.frameGeometry().width()
        height = parent.frameGeometry().height()

        self.move(int(width * 0.25)+1, 20)
        self.resize(int(width * 0.75)-1, int(height)-20)

        self.grid = QtGui.QGridLayout()

        self.setLayout(self.grid)

class UiProfileSetting(QtGui.QDialog):
    '''
        プロファイル > 設定ダイアログ
    '''
    def __init__(self, parent=None):
        super(UiProfileSetting, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle(u"プロファイル設定")
        self.setFixedSize(640, 480)
        self.setModal(True)

        layout = QtGui.QGridLayout()
 
        ###############################################################
        self.ConfTree = QtGui.QTreeWidget(self)
        self.ConfTree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.ConfTree.header().setStretchLastSection(False)
        self.ConfTree.move(0, 20)

        self.ConfTree.setColumnCount(2)
        self.ConfTree.setHeaderLabels(["key", "value"])

        config = json.load(open("default.json"))
        for k, v in config.items():
            item = QtGui.QTreeWidgetItem(self.ConfTree)
            item.setText(0, k)
            item.setText(1, v)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        layout.addWidget(self.ConfTree, 0, 0, 10, 10)

        # OK
        button = QtGui.QPushButton("OK")
        button.clicked.connect(self.on_click_save)
        layout.addWidget(button, 11, 9)

        self.setLayout(layout)

    def on_click_save(self):
        '''
            ボタンを押したときにdefault.jsonを出力する
        '''
        data = {}
        iter = QtGui.QTreeWidgetItemIterator(self.ConfTree)
        while iter.value():
            item = iter.value()
            key   = item.text(0)
            value = item.text(1)
            data[key] = value
            iter += 1

        with open('default.json', 'w') as fp:
            jsonstr = json.dump(data, fp, indent=4)

        self.close()

class UiApiReference(QtWebKit.QWebView):
    '''
        APIリファレンス用ウインドウ
    '''
    def __init__(self, parent=None):
        super(UiApiReference, self).__init__(parent)
        self.setWindowTitle("Reference")
        self.show()
        self.load(QtCore.QUrl(URL["reference"]))

class UiManual(QtWebKit.QWebView):
    '''
        使い方用ウインドウ
    '''
    def __init__(self, parent=None):
        super(UiManual, self).__init__(parent)
        self.setWindowTitle("Manual")
        self.load(QtCore.QUrl(URL["manual"]))

class UiVersion(QtGui.QDialog):
    '''
        バージョン表示用ダイアログ
    '''
    def __init__(self, parent=None):
        super(UiVersion, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowTitle("Version")
        self.setModal(True)

        ###############################################################
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(60)

        text = "ViewCamCloud API Tool %s" % VERSION
        label = QtGui.QLabel(text)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        text = URL["github"]
        button = QtGui.QPushButton(text)
        button.setStyleSheet('QPushButton {color: blue; text-decoration: underline;}')
        button.setFlat(True)
        button.clicked.connect(self.open_GitHubUrl)
        layout.addWidget(button)

        self.setLayout(layout)

    def open_GitHubUrl(self):
        '''
            ボタンを押したときに規定のブラウザで開く
        '''
        url = QtCore.QUrl(URL["github"])
        QtGui.QDesktopServices.openUrl(url)

def main():
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForCStrings( QtCore.QTextCodec.codecForLocale() )
    ui = UiMain()
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

