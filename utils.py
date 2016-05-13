# -*- coding: utf-8 -*-

import json

def confv(key):
    """
        プロファイル設定値の取得
    """
    with open('default.json') as fp:
        data = json.load(fp)

    return data.get(key)

