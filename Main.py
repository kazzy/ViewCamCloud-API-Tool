#!E:\python27\python.exe
# -*- coding: utf-8 -*-

import sys
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

    def initUI(self):
        self.setWindowTitle(u'ViewCamCloud API Tool')
        self.setWindowIcon(QtGui.QIcon('favicon.png'))
        self.setFixedSize(800, 600)

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

        ApiTree.setFixedSize(int(width * 0.25), int(height * 0.6))
        ApiTree.itemClicked.connect(self.on_click_ApiTree)

        return ApiTree

    def on_click_ApiTree(self, item, column):
        '''
            API一覧クリック時
        '''
        child = item.data(column, QtCore.Qt.UserRole)
        print child
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

        History.setFixedSize(int(width * 0.25), int(height * 0.4)-20-1)

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
        self.setFixedSize(int(width * 0.75)-1, int(height)-20)

        self.grid = QtGui.QGridLayout()

        self.setLayout(self.grid)

class VccDeviceUnregist(QtGui.QWidget):
    def __init__(self, parent, grid):
        super(VccDeviceUnregist, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Type")
        item.setText(1, confv("Type"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Ident")
        item.setText(1, confv("Ident"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Serial")
        item.setText(1, confv("Serial"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)


        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = u"Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/device/unregist/' % (confv("HOST"))
        payload = {}
        iter = QtGui.QTreeWidgetItemIterator(self.param)
        while iter.value():
            item = iter.value()
            key   = item.text(0)
            value = item.text(1)
            payload[key] = value
            iter += 1

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.post(url, data=payload, headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code == 200:
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1))
                    else:
                        item.setText(1, "[]")
                    item.setText(2, u"リスト")
                    for k2, v2 in v:
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, k2)
                        item2.setText(1, str(v2))
                        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                        if isinstance(v2, bool):
                            item2.setText(2, u"ブール") # bool is int's subclass
                        elif isinstance(v2, str):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, unicode):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, int):
                            item2.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")

class VccDeviceList(QtGui.QWidget):
    def __init__(self, parent, grid):
        super(VccDeviceList, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels(["パラメータ"])
        self.param.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = u"Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/device/list/' % (confv("HOST"))
        params = {
        }
        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.get(url, params=params, headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code == 200:
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1) )
                    else:
                        item.setText(1, "[0]")
                    item.setText(2, u"リスト")
                    for index, device in enumerate(v):
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, "[%s]" % index)
                        item2.setText(2, u"オブジェクト") # bool is int's subclass

                        for k3, v3 in device.items():
                            item3 = QtGui.QTreeWidgetItem(item2)
                            item3.setText(0, k3)
                            item3.setText(1, str(v3))
                            item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                            if isinstance(v3, bool):
                                item3.setText(2, u"ブール") # bool is int's subclass
                            elif isinstance(v3, str):
                                item3.setText(2, u"文字列")
                            elif isinstance(v3, unicode):
                                item3.setText(2, u"文字列")
                            elif isinstance(v3, int):
                                item3.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")

class VccRemote_POST_LoginUser(QtGui.QWidget):
    """
        [POST] ログイン
    """
    def __init__(self, parent, grid):
        super(VccRemote_POST_LoginUser, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Target")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "hostname")
        item2.setText(1, confv("hostname"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Parameter")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "user")
        item2.setText(1, confv("user"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "password")
        item2.setText(1, confv("password"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = "Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/remote/' % (confv("HOST"))
        payload = {
            "Request": "LoginUser"
        }
        iter = QtGui.QTreeWidgetItemIterator(self.param)
        while iter.value():
            item = iter.value()
            key = item.text(0)
            print key
            payload[key] = {}
            for child in item.takeChildren():
                key2   = child.text(0)
                value2 = child.text(1)
                print "  + %s = %s" % (key2, value2)
                payload[key][key2] = value2
            iter += 1

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.post(url, data=json.dumps(payload, indent=4), headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code == 200:
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1))
                    else:
                        item.setText(1, "[]")
                    item.setText(2, u"リスト")
                    for k2, v2 in v:
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, k2)
                        item2.setText(1, str(v2))
                        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                        if isinstance(v2, bool):
                            item2.setText(2, u"ブール") # bool is int's subclass
                        elif isinstance(v2, str):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, unicode):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, int):
                            item2.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")

class VccRemote_POST_UserCameraPhycam(QtGui.QWidget):
    """
        [POST] カメラ一覧
    """
    def __init__(self, parent, grid):
        super(VccRemote_POST_UserCameraPhycam, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Target")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "hostname")
        item2.setText(1, confv("hostname"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Parameter")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "token")
        item2.setText(1, confv("token"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = "Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/remote/' % (confv("HOST"))
        payload = {
            "Request": "UserCameraPhycam"
        }
        iter = QtGui.QTreeWidgetItemIterator(self.param)
        while iter.value():
            item = iter.value()
            key = item.text(0)
            print key
            payload[key] = {}
            for child in item.takeChildren():
                key2   = child.text(0)
                value2 = child.text(1)
                print "  + %s = %s" % (key2, value2)
                payload[key][key2] = value2
            iter += 1

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.post(url, data=json.dumps(payload, indent=4), headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code == 200:
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1))
                    else:
                        item.setText(1, "[]")
                    item.setText(2, u"リスト")
                    for k2, v2 in v:
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, k2)
                        item2.setText(1, str(v2))
                        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                        if isinstance(v2, bool):
                            item2.setText(2, u"ブール") # bool is int's subclass
                        elif isinstance(v2, str):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, unicode):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, int):
                            item2.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")

class VccRemote_POST_UserViewSlide(QtGui.QWidget):
    """
        [POST] 画像一覧
    """
    def __init__(self, parent, grid):
        super(VccRemote_POST_UserViewSlide, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Target")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "hostname")
        item2.setText(1, confv("hostname"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "Parameter")
        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "token")
        item2.setText(1, confv("token"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "location")
        item2.setText(1, confv("location"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "dtfrom")
        item2.setText(1, confv("dtfrom"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "dtto")
        item2.setText(1, confv("dtto"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = u"Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/remote/' % (confv("HOST"))
        payload = {
            "Request": "UserViewSlide"
        }
        iter = QtGui.QTreeWidgetItemIterator(self.param)
        while iter.value():
            item = iter.value()
            key = item.text(0)
            print key
            payload[key] = {}
            for child in item.takeChildren():
                key2   = child.text(0)
                value2 = child.text(1)
                print "  + %s = %s" % (key2, value2)
                payload[key][key2] = value2
            iter += 1

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.post(url, data=json.dumps(payload, indent=4), headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code == 200:
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1))
                    else:
                        item.setText(1, "[]")
                    item.setText(2, u"リスト")
                    for k2, v2 in v:
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, k2)
                        item2.setText(1, str(v2))
                        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                        if isinstance(v2, bool):
                            item2.setText(2, u"ブール") # bool is int's subclass
                        elif isinstance(v2, str):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, unicode):
                            item2.setText(2, u"文字列")
                        elif isinstance(v2, int):
                            item2.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")

class VccRemote_HEAD(QtGui.QWidget):
    """
        [HEAD] ステータスの確認
    """
    def __init__(self, parent, grid):
        super(VccRemote_HEAD, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = "リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "MessageId")
        item.setText(1, confv("MessageId"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = u"Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/remote/' % (confv("HOST"))
        params = {
            "MessageId": confv("MessageId")
        }
        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.head(url, params=params, headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()

class VccRemote_GET(QtGui.QWidget):
    """
        [GET] データの取得
    """
    def __init__(self, parent, grid):
        super(VccRemote_GET, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ", u"値"])
        self.param.setColumnCount(2)

        item = QtGui.QTreeWidgetItem(self.param)
        item.setText(0, "MessageId")
        item.setText(1, confv("MessageId"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid.addWidget(self.param, 1, 0)

        ###############################################################
        button = QtGui.QPushButton(u"↓")
        button.setStyleSheet("QPushButton {background-color: rgb(67, 135, 233)}")
        button.clicked.connect(self.run_request)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        self.label = QtGui.QLabel(text)
        self.grid.addWidget(self.label, 3, 0)

        self.view = QtGui.QTreeWidget(self)
        self.view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)
        self.view.setColumnCount(3)
        self.view.setHeaderLabels(["key", "value", "type"])
        self.view.setStyleSheet("QTreeWidget { background-color: rgb(220, 220, 220); }");
        self.grid.addWidget(self.view, 4, 0)

        ###############################################################
        text = u"Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/remote/' % (confv("HOST"))
        params = {
            "MessageId": confv("MessageId")
        }
        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.get(url, params=params, headers=headers)
        rawstr = dump.dump_all(r)
        self.raw.setPlainText(rawstr.decode('utf-8'))

        self.view.clear()
        if r.status_code != 200:
            return

        print r.headers['Content-Type']
        if r.headers['Content-Type'] == 'application/json':
            # QTreeWidget (以下は仮)
            data = r.json()
            for k,v in data.items():
                item = QtGui.QTreeWidgetItem(self.view)
                item.setText(0, k)
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                if isinstance(v, bool):
                    item.setText(1, str(v))
                    item.setText(2, u"ブール") # bool is int's subclass
                elif isinstance(v, str):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, unicode):
                    item.setText(1, str(v))
                    item.setText(2, u"文字列")
                elif isinstance(v, int):
                    item.setText(1, str(v))
                    item.setText(2, u"数値")
                elif isinstance(v, list):
                    if len(v) >= 1:
                        item.setText(1, "[0...%s]" % (len(v)-1) )
                    else:
                        item.setText(1, "[0]")
                    item.setText(2, u"リスト")
                    for index, device in enumerate(v):
                        item2 = QtGui.QTreeWidgetItem(item)
                        item2.setText(0, "[%s]" % index)
                        item2.setText(2, u"オブジェクト") # bool is int's subclass

                        for k3, v3 in device.items():
                            item3 = QtGui.QTreeWidgetItem(item2)
                            item3.setText(0, k3)
                            item3.setText(1, str(v3))
                            item3.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                            if isinstance(v3, bool):
                                item3.setText(2, u"ブール") # bool is int's subclass
                            elif isinstance(v3, str):
                                item3.setText(2, u"文字列")
                            elif isinstance(v3, unicode):
                                item3.setText(2, u"文字列")
                            elif isinstance(v3, int):
                                item3.setText(2, u"数値")
                else:
                    item.setText(2, u"Unknown")
        elif r.headers['Content-Type'] == 'image/jpeg':
            # QGraphicsView
            pass
        elif r.headers['Content-Type'] == 'video':
            # Q
            pass
        else:
            #
            pass

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

