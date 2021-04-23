import time
import re


class CachingNotifier:
    """ Caches notifications to ensure duplicates don't pass through """

    def __init__(self, notifier, duration=3600):
        self.duration = duration
        self.notifier = notifier
        self.cache = {}
        self.blooder_cache = {}
        self.blooder_duration = duration * 4
        self.blooder_ts_re = re.compile(r'[:]blooders[:][ ]{2}`[^`]*`')

    def notify(self, text, options=None):
        if options is None:
            options = {}
        if not self._is_cached(text):
            self._cache(text)
            self.notifier.notify(text, options)

        self._cleanup()

    def _cache(self, message):
        self.cache[message] = time.time() + self.duration
        if ':blooders:' in message:
            message = self.blooder_ts_re.sub('', message)
            self.blooder_cache[message] = time.time() + self.blooder_duration

    def _is_cached(self, message):
        is_in_normal_cache = message in self.cache and self.cache[message] > time.time()
        is_in_blooder_cache = False
        if ':blooders:' in message:
            message = self.blooder_ts_re.sub('', message)
            is_in_blooder_cache = message in self.blooder_cache and self.blooder_cache[message] > time.time()
        return is_in_normal_cache or is_in_blooder_cache

    def _cleanup(self):
        current_time = time.time()

        self.cache = {message: timeout for message, timeout in self.cache.items() if timeout >= current_time}
        self.blooder_cache = {message: timeout for message, timeout in self.blooder_cache.items()
                              if timeout >= current_time}
