import time
import re


class CachingNotifier:
    """ Caches notifications to ensure duplicates don't pass through """

    def __init__(self, notifier, duration=3600):
        self.duration = duration
        self.notifier = notifier
        self.cache = {}
        self.fob_cache = {}
        self.fob_duration = duration * 4

    # noinspection PyUnusedLocal
    def notify(self, notification, discord_message, options=None):
        if options is None:
            options = {}
        if not self._is_cached(notification['text']):
            self._cache(notification['text'])
            self.notifier.notify(notification, discord_message, options)

        self._cleanup()

    def _cache(self, notification_content):
        self.cache[notification_content] = time.time() + self.duration
        if notification_content['type'] in ('StructureUnderAttackByBloodRaiders', 'StructureUnderAttackByGuristas'):
            self.fob_cache[notification_content] = time.time() + self.duration

    def _is_cached(self, notification_content):
        is_in_normal_cache = notification_content in self.cache and self.cache[notification_content] > time.time()
        is_in_fob_cache = False
        if notification_content['type'] in ('StructureUnderAttackByBloodRaiders', 'StructureUnderAttackByGuristas'):
            is_in_fob_cache = notification_content in self.fob_cache and \
                              self.fob_cache[notification_content] > time.time()
        return is_in_normal_cache or is_in_fob_cache

    def _cleanup(self):
        current_time = time.time()

        self.cache = {content: timeout for content, timeout in self.cache.items() if timeout >= current_time}
        self.fob_cache = {content: timeout for content, timeout in self.fob_cache.items()
                          if timeout >= current_time}
