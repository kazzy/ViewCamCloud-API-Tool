# -*- coding: utf-8 -*-

import requests
import json
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils         import *
from VccReqResBase import *

class VccBlobPostBlobServiceLocation(VccReqResBase):
    """
        BLOB > [POST] ロケーション一覧
    """
    def __init__(self, parent, grid):
        """
            UIを設定する
        """
        super(VccBlobPostBlobServiceLocation, self).__init__(parent, grid)

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
        item.setText(0, "Target")
        item.setExpanded(True)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "Type")
        item2.setText(1, confv("Type"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        item2.setExpanded(True)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "Ident")
        item2.setText(1, confv("Ident"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        item2.setExpanded(True)

        item2 = QtGui.QTreeWidgetItem(item)
        item2.setText(0, "Serial")
        item2.setText(1, confv("Serial"))
        item2.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
        item2.setExpanded(True)

        item = QtGui.QTreeWidgetItem(param)
        item.setText(0, "Parameter")
        item.setExpanded(True)

        self.grid_inside['request_Param.param'] = param

        return (label, param)

    def communicate(self):
        """
            通信を行う
        """
        url = '%s/blob/' % (confv("HOST"))
        payload = {
            "Request": "BlobServiceLocation"
        }
        items = treeitem_dict(self.inside('request_Param.param'))
        payload.update(items)

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.post(url, data=json.dumps(payload, indent=4), headers=headers)

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
            path = save_history(rawstr, r)
            data = r.json()
            widget = self.inside('response_TreeView.view')
            self.set_response_TreeView_columnset(widget, "root", data)
