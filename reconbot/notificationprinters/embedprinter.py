import math

from reconbot.notificationprinters.discord.discordembed import DiscordEmbed, DiscordEmbedField
from reconbot.notificationprinters.embedformat import EmbedFormat
from reconbot.notificationprinters.formatter import Formatter


class EmbedPrinter(object):
    def __init__(self, printer):
        self.printer = printer

    def format(self, embed: EmbedFormat, content) -> DiscordEmbed:
        if embed.formatter == 'FormatString':
            return self.format_string(embed, content)
        elif embed.formatter == 'MineralComposition':
            return self.get_mineral_composition(embed, content)
        else:
            e = DiscordEmbed()
            e.set_description(f"Unknown embed formatted {embed.formatter}")
            return e

    def format_string(self, embed: EmbedFormat, content) -> DiscordEmbed:
        e = DiscordEmbed()
        if embed.title is not None:
            e.set_title(embed.title)
        e.set_description(embed.argument.format(Formatter(self.printer, content)))
        return e

    def get_mineral_composition(self, embed: EmbedFormat, content) -> DiscordEmbed:
        e = DiscordEmbed()
        if embed.title is not None:
            e.set_title(embed.title)
        ores = content[embed.argument]
        for ore_id in ores:
            ore_qty = math.floor(ores[ore_id])
            e.add_field(DiscordEmbedField(self.printer.get_item(ore_id), f"{ore_qty} m3"))
        return e
