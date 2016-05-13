# -*- coding: utf-8 -*-

import requests
import json
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils         import *
from VccReqResBase import *

class VccRemoteHead(VccReqResBase):
    """
        VCSリモート > [HEAD] ステータスの確認
    """
    def __init__(self, parent, grid):
        """
            UIを設定する
        """
        super(VccRemoteHead, self).__init__(parent, grid)

        ###############################################################
        (label, param) = self.set_defaultUI_request_Param()
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(param, 1, 0)

        ###############################################################
        button = self.set_defaultUI_request_Button(self.on_click)
        self.grid.addWidget(button, 2, 0)

        ###############################################################
        text = u"レスポンス"
        label = QtGui.QLabel(text)
        self.grid_inside['response_HeadView.label'] = label

        text = u""
        style = "QLabel {color: rgb(220, 0, 0); padding: 60px 0px; font-size: 14pt;}"
        status = QtGui.QLabel(text)
        status.setStyleSheet(style)
        status.setAlignment(QtCore.Qt.AlignCenter)
        self.grid_inside['response_HeadView.status'] = status

        self.grid.addWidget(label, 3, 0)
        self.grid.addWidget(status, 4, 0)

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
        item.setText(0, "MessageId")
        item.setText(1, confv("MessageId"))
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

        self.grid_inside['request_Param.param'] = param

        return (label, param)

    def communicate(self):
        """
            通信を行う
        """
        url = '%s/remote/' % (confv("HOST"))
        params = {
            "MessageId": confv("MessageId")
        }
        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.head(url, params=params, headers=headers)

        return r

    def on_click(self):
        """
            クリック時
        """
        r = self.communicate()

        rawstr = dump.dump_all(r)
        self.inside('raw_TextView.raw').setPlainText(rawstr.decode('utf-8'))

        self.inside('response_HeadView.status').clear()
        if r.status_code == 200:
            self.inside('response_HeadView.status').setText(r.headers['X-Vcc-Api-Queue-Status'])
