# -*- coding: utf-8 -*-

import requests
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils         import *
from VccReqResBase import *

class VccDeviceUnregist(VccReqResBase):
    """
        共通 > 登録済みデバイスの解除
    """
    def __init__(self, parent, grid):
        """
            UIを設定する
        """
        super(VccDeviceUnregist, self).__init__(parent, grid)

        ###############################################################
        (label, param) = self.set_defaultUI_request_Param()
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(param, 1, 0)

        ###############################################################
        button = self.set_defaultUI_request_Button(self.on_click)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        (label, view) = self.set_defaultUI_response_TreeView()
        self.grid.addWidget(label, 3, 0)
        self.grid.addWidget(view, 4, 0)

        ###############################################################
        (label, raw)  = self.set_defaultUI_raw_TextView()
        self.grid.addWidget(label, 5, 0)
        self.grid.addWidget(raw, 6, 0)

    def set_defaultUI_request_Param(self):
        """
            デフォルトUIのリクエストパラメータ設定
        """
        text = u"リクエスト"
        label = QtGui.QLabel(text)
        self.grid_inside['request_Param.label'] = label

        style = "QTreeWidget {background-color: rgb(220, 220, 220);}"
        param = QtGui.QTreeWidget(self)
        param.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        param.header().setStretchLastSection(False)
        param.setColumnCount(2)
        param.setHeaderLabels([u"パラメータ", u"値"])

        item = QtGui.QTreeWidgetItem(param)
        item.setText(0, "Type")
        item.setText(1, confv("Type"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(param)
        item.setText(0, "Ident")
        item.setText(1, confv("Ident"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        item = QtGui.QTreeWidgetItem(param)
        item.setText(0, "Serial")
        item.setText(1, confv("Serial"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid_inside['request_Param.param'] = param

        return (label, param)

    def communicate(self):
        """
            通信を行う
        """
        url = '%s/device/unregist/' % (confv("HOST"))
        payload = {}
        iter = QtGui.QTreeWidgetItemIterator(self.inside('request_Param.param'))
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

        return r

    def on_click(self):
        """
            クリック時
        """
        r = self.communicate()

        rawstr = dump.dump_all(r)
        self.inside('raw_TextView.raw').setPlainText(rawstr.decode('utf-8'))

        self.inside('response_TreeView.view').clear()
        if r.status_code == 200:
            data = r.json()
            widget = self.inside('response_TreeView.view')
            self.set_response_TreeView_columnset(widget, "root", data)