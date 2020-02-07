# -*- coding: utf-8 -*-
"""

    Copyright (C) 2014-2016 bromix (plugin.video.youtube)
    Copyright (C) 2016-2018 plugin.video.youtube

    SPDX-License-Identifier: GPL-2.0-only
    See LICENSES/GPL-2.0-only for more information.
"""

import xbmc
import xbmcgui
import xbmcplugin

from infotagger.listitem import ListItemInfoTag

from ..abstract_provider_runner import AbstractProviderRunner
from ...exceptions import KodionException
from ...items import *
from ... import AbstractProvider
from . import info_labels
from . import xbmc_items


class XbmcRunner(AbstractProviderRunner):
    def __init__(self):
        AbstractProviderRunner.__init__(self)
        self.handle = None
        self.settings = None

    def run(self, provider, context=None):

        self.handle = context.get_handle()

        try:
            results = provider.navigate(context)
        except KodionException as ex:
            if provider.handle_exception(context, ex):
                context.log_error(ex.__str__())
                xbmcgui.Dialog().ok("Exception in ContentProvider", ex.__str__())
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
            return

        self.settings = context.get_settings()

        result = results[0]
        options = {}
        options.update(results[1])

        if isinstance(result, bool) and not result:
            xbmcplugin.endOfDirectory(self.handle, succeeded=False)
        elif isinstance(result, VideoItem) or isinstance(result, AudioItem) or isinstance(result, UriItem):
            self._set_resolved_url(context, result)
        elif isinstance(result, DirectoryItem):
            self._add_directory(context, result)
        elif isinstance(result, list):
            item_count = len(result)
            for item in result:
                if isinstance(item, DirectoryItem):
                    self._add_directory(context, item, item_count)
                elif isinstance(item, VideoItem):
                    self._add_video(context, item, item_count)
                elif isinstance(item, AudioItem):
                    self._add_audio(context, item, item_count)
                elif isinstance(item, ImageItem):
                    self._add_image(context, item, item_count)

            xbmcplugin.endOfDirectory(
                self.handle, succeeded=True,
                updateListing=options.get(AbstractProvider.RESULT_UPDATE_LISTING, False),
                cacheToDisc=options.get(AbstractProvider.RESULT_CACHE_TO_DISC, True))

            # set alternative view mode
            if context.get_settings().is_override_view_enabled():
                view_mode = context.get_ui().get_view_mode()
                if view_mode is not None:
                    context.log_debug('Override view mode to "%d"' % view_mode)
                    xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode)
        else:
            # handle exception
            pass

    def _set_resolved_url(self, context, base_item, succeeded=True):
        item = xbmc_items.to_playback_item(context, base_item)
        item.setPath(base_item.get_uri())
        xbmcplugin.setResolvedUrl(self.handle, succeeded=succeeded, listitem=item)

        """
        # just to be sure :)
        if not isLiveStream:
            tries = 100
            while tries>0:
                xbmc.sleep(50)
                if xbmc.Player().isPlaying() and xbmc.getCondVisibility("Player.Paused"):
                    xbmc.Player().pause()
                    break
                tries-=1
        """

    def _add_directory(self, context, directory_item, item_count=0):
        art = {'icon': 'DefaultFolder.png',
               'thumb': directory_item.get_image()}

        item = xbmcgui.ListItem(label=directory_item.get_name(), offscreen=True)

        info_tag = ListItemInfoTag(item, tag_type='video')

        # only set fanart is enabled
        if directory_item.get_fanart() and self.settings.show_fanart():
            art['fanart'] = directory_item.get_fanart()


        item.setArt(art)

        if directory_item.get_context_menu() is not None:
            item.addContextMenuItems(directory_item.get_context_menu(),
                                     replaceItems=directory_item.replace_context_menu())

        info_tag.set_info(info_labels.create_from_item(directory_item))
        item.setPath(directory_item.get_uri())

        is_folder = True
        if directory_item.is_action():
            is_folder = False
            item.setProperty('isPlayable', 'false')

        if directory_item.next_page:
            item.setProperty('specialSort', 'bottom')

        if directory_item.get_channel_subscription_id():  # make channel_subscription_id property available for keymapping
            item.setProperty('channel_subscription_id', directory_item.get_channel_subscription_id())

        xbmcplugin.addDirectoryItem(handle=self.handle,
                                    url=directory_item.get_uri(),
                                    listitem=item,
                                    isFolder=is_folder,
                                    totalItems=item_count)

    def _add_video(self, context, video_item, item_count=0):
        item = xbmc_items.to_video_item(context, video_item)
        item.setPath(video_item.get_uri())
        xbmcplugin.addDirectoryItem(handle=self.handle,
                                    url=video_item.get_uri(),
                                    listitem=item,
                                    totalItems=item_count)

    def _add_image(self, context, image_item, item_count):
        art = {'icon': 'DefaultPicture.png',
               'thumb': image_item.get_image()}

        item = xbmcgui.ListItem(label=image_item.get_name(), offscreen=True)

        if image_item.get_fanart() and self.settings.show_fanart():
            art['fanart'] = image_item.get_fanart()

        item.setArt(art)

        if image_item.get_context_menu() is not None:
            item.addContextMenuItems(image_item.get_context_menu(), replaceItems=image_item.replace_context_menu())

        item.setInfo(type='picture', infoLabels=info_labels.create_from_item(image_item))

        item.setPath(image_item.get_uri())
        xbmcplugin.addDirectoryItem(handle=self.handle,
                                    url=image_item.get_uri(),
                                    listitem=item,
                                    totalItems=item_count)

    def _add_audio(self, context, audio_item, item_count):
        item = xbmc_items.to_audio_item(context, audio_item)
        item.setPath(audio_item.get_uri())
        xbmcplugin.addDirectoryItem(handle=self.handle,
                                    url=audio_item.get_uri(),
                                    listitem=item,
                                    totalItems=item_count)
