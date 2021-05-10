from typing import List, Optional

from reconbot.notificationprinters.discord.discordembed import DiscordEmbed


class DiscordMessage(object):
    content: Optional[str]
    embeds: List[DiscordEmbed]

    def __init__(self):
        self.content = None
        self.embeds = []

    def set_content(self, content: str):
        self.content = content

    def add_embed(self, embed: DiscordEmbed):
        self.embeds.append(embed)

    def as_data_struct(self):
        struct = {}
        if self.content is not None:
            struct['content'] = self.content
        if len(self.embeds) > 0:
            struct['embeds'] = [embed.as_data_struct() for embed in self.embeds]
        return struct

    def as_text(self) -> str:
        parts = []
        if self.content is not None:
            parts.append(self.content)
        for embed in self.embeds:
            parts.append(embed.as_text())
        return "\n\n".join(parts)
