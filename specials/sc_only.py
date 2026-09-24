# -*- coding: utf-8 -*-
"""Use the existing StreamingCommunity channel before listing a title."""

from core.item import Item
from core import servertools
from channels import streamingcommunity
from platformcode import logger


def _stream_url(item):
    return item.url.replace('/watch/', '/iframe/')


def playable(item):
    """Resolve the same server used by the channel, without starting Kodi playback."""
    try:
        urls, available, _ = servertools.resolve_video_urls_for_playing(
            'streamingcommunityws', _stream_url(item))
        return bool(available and urls and urls[0][1])
    except Exception:
        logger.error('StreamingCommunity availability check failed: %s' % item.url)
        return False


def episodes(item):
    """Keep only episodes for which the native resolver finds a stream."""
    try:
        return [episode for episode in streamingcommunity.episodios(item)
                if playable(episode)]
    except Exception:
        logger.error('StreamingCommunity episode lookup failed: %s' % item.url)
        return []


def match(info, title, kind):
    """Return a confirmed channel item, or None; never show an unverified poster."""
    tmdb_id = info.get('tmdb_id') or info.get('id')
    if not tmdb_id or kind not in ('movie', 'tvshow'):
        return None
    try:
        results = streamingcommunity.search(
            Item(channel='streamingcommunity', contentType=kind), title)
        for result in results:
            if result.contentType != kind or str(result.infoLabels.get('tmdb_id')) != str(tmdb_id):
                continue
            available = playable(result) if kind == 'movie' else bool(episodes(result))
            if available:
                result.infoLabels = info
                result.sc_verified = True
                return result
    except Exception:
        logger.error('StreamingCommunity title lookup failed: %s' % title)
    return None

