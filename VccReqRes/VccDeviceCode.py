# -*- coding: utf-8 -*-

import requests
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils         import *
from VccReqResBase import *

class VccDeviceCode(QtGui.QWidget):
    def __init__(self, parent, grid):
        super(VccDeviceCode, self).__init__(parent)
        self.grid = grid

        ###############################################################
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 0, 0)

        self.param = QtGui.QTreeWidget(self)
        self.param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.param.header().setStretchLastSection(False)
        self.param.setColumnCount(1)
        self.param.setHeaderLabels([u"パラメータ"])
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
        text = "Raw"
        label = QtGui.QLabel(text)
        self.grid.addWidget(label, 5, 0)

        self.raw = QtGui.QPlainTextEdit(self)
        self.raw.setStyleSheet("QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }");

        self.grid.addWidget(self.raw, 6, 0)

    def run_request(self):
        url = '%s/device/code/' % (confv("HOST"))
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
