import time
import yaml


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
        if not self._is_cached(notification):
            self._cache(notification)
            self.notifier.notify(notification, discord_message, options)

        self._cleanup()

    @staticmethod
    def _get_fob_string(notification):
        yaml_text = yaml.load(notification['text'], Loader=yaml.FullLoader)
        return str(yaml_text['structureID'])

    def _cache(self, notification):
        self.cache[notification['text']] = time.time() + self.duration
        if notification['type'] in ('StructureUnderAttackByBloodRaiders', 'StructureUnderAttackByGuristas'):
            self.fob_cache[self._get_fob_string(notification)] = time.time() + self.duration

    def _is_cached(self, notification):
        is_in_normal_cache = notification['text'] in self.cache and self.cache[notification['text']] > time.time()
        is_in_fob_cache = False
        if notification['type'] in ('StructureUnderAttackByBloodRaiders', 'StructureUnderAttackByGuristas'):
            is_in_fob_cache = self._get_fob_string(notification) in self.fob_cache and \
                              self.fob_cache[self._get_fob_string(notification)] > time.time()
        return is_in_normal_cache or is_in_fob_cache

    def _cleanup(self):
        current_time = time.time()

        self.cache = {content: timeout for content, timeout in self.cache.items() if timeout >= current_time}
        self.fob_cache = {content: timeout for content, timeout in self.fob_cache.items()
                          if timeout >= current_time}
