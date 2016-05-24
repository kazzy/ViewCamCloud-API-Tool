# -*- coding: utf-8 -*-

import os
import json
import datetime
from PySide import QtGui

def confv(key):
    """
        プロファイル設定値の取得
    """
    with open('default.json') as fp:
        data = json.load(fp)

    return data.get(key)

def treeitem_dict(treeitem):
    """
        QTreeWidgetItem内の2カラムデータをdictとして返す
    """
    def get_dict(item):
        resp = {}

        k = item.text(0)
        if item.columnCount() == 2:
            v = item.text(1)
            resp[k] = v
        else:
            resp[k] = {}
            for child in item.takeChildren():
                cresp = get_dict(child)
                resp[k].update(cresp)
        return resp

    resp = {}
    iter = QtGui.QTreeWidgetItemIterator(treeitem)

    while iter.value():
        item = iter.value()
        cresp = get_dict(item)
        resp.update(cresp)
        iter += 1

    print json.dumps(resp, indent=4)

    return resp

def save_history(raw, r):
    """
        historyディレクトリにファイルを保存する
    """
    dt = datetime.datetime.now()
    dtstr = dt.strftime('%Y%m%dT%H%M%S')

    pid = os.getpid()

    ct2ext = {
        'application/json' : 'json',
        'image/jpeg'       : 'jpg',
        'video/x-msvideo'  : 'avi',
        'video/quicktime'  : 'mov',
        'video/mp4'        : 'mp4',
    }
    ext = ct2ext.get(r.headers['Content-Type'])
    if not ext:
        return None

    raw_dir = "history"

    if(os.path.isdir(raw_dir) == False):
        os.makedirs(raw_dir)

    path = os.path.join(raw_dir, '%s@%s.' % (dtstr, pid))
    with open(path + 'raw', 'wb') as fp:
        fp.write(raw)

    with open(path + ext, 'wb') as fp:
        fp.write(r.content)

    return path + ext
