# -*- coding: utf-8 -*-

import requests
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

from utils         import *
from VccReqResBase import *

class VccToken(VccReqResBase):
    """
        共通 > APIトークンの取得
    """
    def __init__(self, parent, grid):
        """
            UIを設定する
        """
        super(VccToken, self).__init__(parent, grid)

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

    def communicate(self):
        """
            通信を行う
        """
        url = '%s/token/' % (confv("HOST"))
        params = {
        }
        headers = {
            'X-VCC-API-KEYSET' : 'key=%s&secret=%s' % (confv("API_KEY"), confv("API_SECRET")),
        }
        r = requests.get(url, params=params, headers=headers)

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
            save_history(rawstr, r)

            data = r.json()
            widget = self.inside('response_TreeView.view')
            self.set_response_TreeView_columnset(widget, "root", data)
