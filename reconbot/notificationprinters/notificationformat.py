from typing import Optional


class NotificationFormat(object):
    def __init__(self, content: Optional[str], embeds=None):
        self.content = content
        if embeds is None:
            self.embeds = []
        else:
            self.embeds = embeds
