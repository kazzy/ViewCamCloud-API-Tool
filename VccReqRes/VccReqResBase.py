# -*- coding: utf-8 -*-

import requests
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit

class VccReqResBase(QtGui.QWidget):
    """
        リクエスト・レスポンスのベースクラス
    """
    def __init__(self, parent, grid):
        super(VccReqResBase, self).__init__(parent)
        self.grid = grid
        self.grid_inside = {}

    def inside(self, key):
        """
            グリッドビューに格納されたオブェクトを取得
        """
        return self.grid_inside.get(key, None)

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
        param.setColumnCount(1)
        param.setHeaderLabels([u"パラメータ"])
        param.setStyleSheet(style)
        self.grid_inside['request_Param.param'] = param

        return (label, param)

    def set_defaultUI_request_Button(self, method):
        """
            デフォルトUIのリクエストボタン
        """
        label = u"↓"
        style = "QPushButton {background-color: rgb(67, 135, 233)}"
        button = QtGui.QPushButton(label)
        button.setStyleSheet(style)
        button.clicked.connect(method)
        self.grid_inside['request_Button.button'] = button

        return button

    def set_defaultUI_response_TreeView(self):
        """
            デフォルトUIのレスポンスツリービュー
        """
        text = u"レスポンス"
        label = QtGui.QLabel(text)
        self.grid_inside['response_TreeView.label'] = label

        style = "QTreeWidget{ background-color: rgb(220, 220, 220);}"
        view = QtGui.QTreeWidget(self)
        view.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        view.header().setStretchLastSection(False)
        view.setColumnCount(3)
        view.setHeaderLabels(["key", "value", "type"])
        view.setStyleSheet(style);
        self.grid_inside['response_TreeView.view'] = view

        return (label, view)

    def set_defaultUI_raw_TextView(self):
        """
            デフォルトUIのrawビュー
        """
        text = "Raw"
        label = QtGui.QLabel(text)
        self.grid_inside['raw_TextView.label'] = label

        style = "QPlainTextEdit { background-color: rgb(220, 220, 220); font-size: 8pt; font-family: Courier; }"
        raw = QtGui.QPlainTextEdit(self)
        raw.setStyleSheet(style);
        self.grid_inside['raw_TextView.raw'] = raw

        return (label, raw)

    def set_response_TreeView_columnset(self, widget, data):
        """
            デフォルトUIのレスポンスツリービューにカラムセットを設定
        """
        for k,v in data.items():
            print "%s" % k
            item = QtGui.QTreeWidgetItem(widget)
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)

            if isinstance(v, bool):
                item.setText(0, k)
                item.setText(1, str(v))
                item.setText(2, u"ブール") # bool is int's subclass
            elif isinstance(v, str):
                item.setText(0, k)
                item.setText(1, str(v))
                item.setText(2, u"文字列")
            elif isinstance(v, unicode):
                item.setText(0, k)
                item.setText(1, str(v))
                item.setText(2, u"文字列")
            elif isinstance(v, int):
                item.setText(0, k)
                item.setText(1, str(v))
                item.setText(2, u"数値")
            elif isinstance(v, list):
                item.setText(0, k)
                if len(v) >= 1:
                    item.setText(1, "[0...%s]" % (len(v)-1) )
                else:
                    item.setText(1, "[0]")
                item.setText(2, u"リスト")
                self.set_response_TreeView_columnset(item, v)
            elif isinstance(v, dict):
                item.setText(0, k)
                item.setText(1, "[%s]" % index)
                item.setText(2, u"オブジェクト")
                self.set_response_TreeView_columnset(item, v)
            else:
                item.setText(0, k)
                item.setText(2, u"Unknown")
