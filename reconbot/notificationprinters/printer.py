from typing import Dict  # Python 3.8 requires
import datetime
import math

import yaml
import requests

from reconbot.esi import ESI
from reconbot.notificationprinters.discord.discordmessage import DiscordMessage
from reconbot.notificationprinters.embedprinter import EmbedPrinter
from reconbot.notificationprinters.formatter import Formatter
from reconbot.notificationprinters.notificationformat import NotificationFormat
from reconbot.notificationprinters.pingformatter import PingFormatter


class Printer(object):
    def __init__(self, eve: ESI, notification_formats: Dict[str, NotificationFormat], ping_formatter: PingFormatter):
        self.eve = eve
        self.ping_formatter = ping_formatter
        self.notification_formats = notification_formats

    def transform(self, notification) -> DiscordMessage:
        payload = self.get_notification_payload(notification)

        return payload

    def get_notification_payload(self, notification):
        payload = DiscordMessage()
        if notification['type'] in self.notification_formats:
            yaml_text = yaml.load(notification['text'], Loader=yaml.FullLoader)
            yaml_text['notification_timestamp'] = notification['timestamp']
            payload.set_content(self.get_notification_content(notification, yaml_text))
            for embed in self.notification_formats[notification['type']].embeds:
                embed_printer = EmbedPrinter(self)
                payload.add_embed(embed_printer.format(embed, yaml_text))
        else:
            payload.set_content('Unknown notification type for printing [' + notification['type'] + ']')
        return payload

    def get_notification_content(self, notification, yaml_text):
        content_template = self.notification_formats[notification['type']].content
        ping_part = "%s `[%s]` " % (self.ping_formatter.get_ping_string(notification),
                                    self.timestamp_to_date(notification['timestamp']))
        if content_template is None:
            content_template = ''
        content_template = ping_part + content_template
        notification_content = content_template.format(Formatter(self, yaml_text))
        return notification_content

    def get_corporation_or_alliance(self, entity_id):
        try:
            return self.get_corporation(entity_id)
        except requests.RequestException:
            return self.get_alliance(entity_id)

    def get_item(self, item_id):
        item = self.eve.get_item(item_id)
        return item['name']

    def get_planet(self, planet_id):
        planet = self.eve.get_planet(planet_id)
        system = self.get_system(planet['system_id'])
        return '%s in %s' % (planet['name'], system)

    def get_moon(self, moon_id):
        moon = self.eve.get_moon(moon_id)
        return moon['name']

    @staticmethod
    def get_campaign_event_type(event_type):
        if event_type == 1:
            return 'TCU'
        elif event_type == 2:
            return 'IHUB'
        elif event_type == 3:
            return 'Station'
        else:
            return 'Unknown structure type "%d"' % event_type

    def get_structure_name(self, structure_id):
        structure = self.eve.get_structure(structure_id)
        if 'name' in structure:
            return structure['name']
        else:
            return "Unknown name"

    @staticmethod
    def timestamp_to_date(timestamp):
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def eve_timestamp_to_date(microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds/10000000 - 11644473600
        return datetime.datetime.utcfromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def eve_duration_to_date(timestamp, microseconds):
        """
        Convert microsoft epoch to unix epoch
        Based on: http://www.wiki.eve-id.net/APIv2_Char_NotificationTexts_XML
        """

        seconds = microseconds/10000000
        timedelta = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(seconds=seconds)
        return timedelta.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_percentage(value):
        if value <= 1:
            value = value * 100
        return '%.1f%%' % value

    @staticmethod
    def get_isk(isk):
        return '%.2f ISK' % isk

    @staticmethod
    def get_string(value):
        return str(value)

    @staticmethod
    def get_string_preserve_bold(value):
        return str(value).replace('<b>', '**').replace('</b>', '**')

    def get_corporation_from_link(self, show_info):
        return self.get_corporation(show_info[-1])

    def get_structure_type_from_link(self, show_info):
        return self.get_item(show_info[1])

    def get_system_from_link(self, show_info):
        return self.get_system(show_info[-1])

    def get_character_from_link(self, show_info):
        return self.get_character(show_info[-1])

    def get_pos_wants(self, wants):
        wants = map(lambda w: '%s: %d' % (self.get_item(w['typeID']), w['quantity']), wants)

        return ', '.join(wants)

    def get_citadel_services(self, modules):
        services = map(lambda item_id: self.get_item(item_id), modules)

        return ', '.join(services)

    def get_corporation(self, corporation_id):
        corporation = self.eve.get_corporation(corporation_id)
        result = '[%s](<https://zkillboard.com/corporation/%d/>)' % (corporation['name'], corporation_id)

        if 'alliance_id' in corporation:
            result = '[%s] [%s]' % (result, self.get_alliance(corporation['alliance_id']))

        return result

    def get_alliance(self, alliance_id):
        alliance = self.eve.get_alliance(alliance_id)
        return '[%s](<https://zkillboard.com/alliance/%d/>)' % (alliance['name'], alliance_id)

    def get_system(self, system_id):
        system = self.eve.get_system(system_id)
        return '**[%s](<http://evemaps.dotlan.net/system/%s>)**' % (system['name'], system['name'])

    def get_character(self, character_id):
        if not character_id:
            return 'Unknown character'

        try:
            character = self.eve.get_character(character_id)
        except requests.HTTPError as ex:
            # Patch for character being unresolvable and ESI throwing internal errors
            # Temporarily stub character to not break our behavior.
            if ex.response.status_code == 500 or ex.response.status_code == 404:
                character = {'name': 'Unknown character', 'corporation_id': 98356193}
            else:
                raise

        return '**[%s](<https://zkillboard.com/character/%d/>)** %s' % (
            character['name'],
            character_id,
            self.get_corporation(character['corporation_id'])
        )

    def get_killmail(self, killmail_id, killmail_hash):
        killmail = self.eve.get_killmail(killmail_id, killmail_hash)
        victim = self.get_character(killmail['victim']['character_id'])
        ship = self.get_item(killmail['victim']['ship_type_id'])
        system = self.get_system(killmail['solar_system_id'])

        return '%s lost a(n) %s in %s (<https://zkillboard.com/kill/%d/>)' % (
            victim,
            ship,
            system,
            killmail_id
        )

    # oreVolumeByType:
    # 45490: 1176484.4156596793
    # 45496: 1101576.78784565
    # 45502: 1734458.036109956
    # 45504: 1657730.84487711
    def get_moon_composition(self, ore_data):
        ore_strings = []
        for ore_type in ore_data:
            ore_qty = ore_data[ore_type]
            ore_strings.append(self.get_item(ore_type) + ': ' + str(math.floor(ore_qty)) + " m3")
        return '(' + ', '.join(ore_strings) + ')'

    def get_remaining_fuels(self, list_of_types_and_qty):
        fuels = []
        for fuel in list_of_types_and_qty:
            if len(fuel) != 2:
                continue
            fuel_str = ""
            fuel_str += self.get_item(fuel[1])
            fuel_str += ': '
            fuel_str += str(fuel[0])
            fuels.append(fuel_str)
        if len(fuels) > 0:
            return "(" + "; ".join(fuels) + ")"
        else:
            return ""

