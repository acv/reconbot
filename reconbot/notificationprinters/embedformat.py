from typing import Optional


class EmbedFormat(object):
    def __init__(self, formatter: str, title: Optional[str], argument: Optional[str]):
        self.formatter = formatter
        self.title = title
        self.argument = argument
