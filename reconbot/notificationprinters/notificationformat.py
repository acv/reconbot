from typing import Optional, List

from reconbot.notificationprinters.embedformat import EmbedFormat


class NotificationFormat(object):
    def __init__(self, content: Optional[str], embeds: Optional[List[EmbedFormat]] = None):
        self.content = content
        if embeds is None:
            self.embeds = []
        else:
            self.embeds = embeds
