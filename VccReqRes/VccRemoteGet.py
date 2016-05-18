# -*- coding: utf-8 -*-

import os
import requests
import json
from requests_toolbelt.utils import dump
from PySide import QtCore, QtGui, QtWebKit, phonon
import tempfile

from utils         import *
from VccReqResBase import *

class VccRemoteGet(VccReqResBase):
    """
        VCSリモート > [GET] データの取得
    """
    def __init__(self, parent, grid):
        """
            UIを設定する
        """
        super(VccRemoteGet, self).__init__(parent, grid)

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
        self.grid_inside['response_GetView.label'] = label

        widget = QtGui.QWidget()
        width  = int(parent.frameGeometry().width()  * 0.75)
        height = int(parent.frameGeometry().height() * 0.3)
        widget.setFixedSize(width, height)
        self.grid_inside['response_GetView.widget'] = widget

        self.grid.addWidget(label, 3, 0)
        self.grid.addWidget(widget, 4, 0)

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
        item.setExpanded(True)

        self.grid_inside['request_Param.param'] = param

        return (label, param)

    def communicate(self):
        """
            通信を行う
        """
        url = '%s/remote/' % (confv("HOST"))
        params = {}
        items = treeitem_dict(self.inside('request_Param.param'))
        params.update(items)

        headers = {
            'X-VCC-API-TOKEN' : confv("API_TOKEN")
        }
        r = requests.get(url, params=params, headers=headers)

        return r

    def set_json_view(self, rawstr, r):
        """
            JSONビュー
        """
        path = save_history(rawstr, r)

        (_, view) = self.set_defaultUI_response_TreeView()
        self.grid.addWidget(view, 4, 0)

        data = r.json()
        self.set_response_TreeView_columnset(view, "root", data)

    def set_image_view(self, rawstr, r):
        """
            JPEGビュー
        """
        path = save_history(rawstr, r)

        view = QtGui.QGraphicsView(self)
        scene = QtGui.QGraphicsScene(view)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(r.content)
        item = QtGui.QGraphicsPixmapItem(pixmap)

        items = treeitem_dict(self.inside('request_Param.param'))

        width  = self.grid_inside['response_GetView.widget'].width() - 2
        height = self.grid_inside['response_GetView.widget'].height() - 2

        # Resize
        boundingRect = item.boundingRect()
  
        itemAspectRatio  = boundingRect.width() / boundingRect.height()
        sceneAspectRatio = width / height
  
        if itemAspectRatio >= sceneAspectRatio:
            # 横幅に合わせる
            scaleRatio = width / boundingRect.width()
        else:
            # 縦の高さに合わせる
            scaleRatio = height / boundingRect.height()

        trans = QtGui.QTransform()
        trans.scale( scaleRatio, scaleRatio )
        item.setTransform(trans)

        scene.addItem(item)
        view.setScene(scene)

        self.grid.addWidget(view, 4, 0)

    def set_video_view(self, rawstr, r):
        """
            VIDEOビュー
        """
        path = save_history(rawstr, r)

        media = phonon.Phonon.MediaObject(self)
        view  = phonon.Phonon.VideoWidget(self)

        phonon.Phonon.createPath(media, view)

        width  = self.grid_inside['response_GetView.widget'].width() - 2
        height = self.grid_inside['response_GetView.widget'].height() - 2

        view.resize(width, height)

        self.grid.addWidget(view, 4, 0)

        media.setCurrentSource(path)
        media.play()

    def content_view(self, rawstr, content_type, r):
        """
            Content-Typeに応じたView
        """
        content_method = {
            'application/json' : self.set_json_view,
            'image/jpeg'       : self.set_image_view,
            'video/x-msvideo'  : self.set_video_view,
        }
        method = content_method.get(content_type, None)
        if method:
            method(rawstr, r)

    def on_click(self):
        """
            クリック時
        """
        r = self.communicate()

        rawstr = dump.dump_all(r)
        print r.headers['Content-Type']
        try:
            self.inside('raw_TextView.raw').setPlainText(rawstr.decode('utf-8'))
        except Exception as e:
            print str(e)

        #self.inside('response_GetView.widget').deleteLater()
        if r.status_code == 200:
            print "content-length : %s" % len(r.content)
            self.content_view(rawstr, r.headers['Content-Type'], r)
