# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

from __future__ import absolute_import, division, unicode_literals

from .storage import Storage
from ..items import from_json, to_json


class FavoriteList(Storage):
    def __init__(self, filename):
        super(FavoriteList, self).__init__(filename)

    def clear(self):
        self._clear()

    @staticmethod
    def _sort_item(_item):
        return _item[2].get_name().upper()

    def get_items(self):
        result = self._get_by_ids(process=from_json)
        return sorted(result, key=self._sort_item, reverse=False)

    def add(self, base_item):
        item_json_data = to_json(base_item)
        self._set(base_item.get_id(), item_json_data)

    def remove(self, base_item):
        self._remove(base_item.get_id())
