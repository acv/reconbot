import configparser

from reconbot.notificationprinters.embedformat import EmbedFormat
from reconbot.notificationprinters.notificationformat import NotificationFormat


class ConfigurationException(Exception):
    pass


class Config(object):
    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        self.notifications_whitelist = []
        self.discord_config = {'ping': {}}
        self.esi_config = {}
        self.webhooks = {}
        self.notification_webhook = {}
        self.notification_formats = {}
        self.parse_config(config_file_name)

    # noinspection PyTypeChecker
    def parse_config(self, config_file_name):
        c = configparser.ConfigParser(allow_no_value=True)
        c.optionxform = lambda option: option
        c.read(config_file_name)

        self.check_if_section_present(c, 'NotificationsMonitored')

        for notification in c['NotificationsMonitored']:
            self.notifications_whitelist.append(notification)

        if len(self.notifications_whitelist) < 1:
            raise ConfigurationException("No notifications white listed.")

        self.check_if_section_present(c, 'DiscordDefaults')

        self.discord_config['default_ping'] = self.get_key(c, 'DiscordDefaults', 'default_ping')

        self.check_if_section_present(c, 'DiscordNotificationSpecificPing')

        for ping in c['DiscordNotificationSpecificPing']:
            self.discord_config['ping'][ping] = c['DiscordNotificationSpecificPing'][ping]

        notification_formats = [section for section in c.sections() if section.startswith('NotificationFormat ')]
        for n_format in notification_formats:
            self.parse_notification_format_section(c, n_format)

        self.check_if_section_present(c, "EveApplicationInfo")
        self.esi_config['ApplicationClientID'] = self.get_key(c, "EveApplicationInfo", 'ApplicationClientID')
        self.esi_config['ApplicationSecretKey'] = self.get_key(c, "EveApplicationInfo", 'ApplicationSecretKey')

        self.check_if_section_present(c, "EveCharacters")
        self.esi_config['characters'] = self.get_characters(c)

        self.check_if_section_present(c, "DiscordWebHooks")
        for hook_name in c.options("DiscordWebHooks"):
            self.webhooks[hook_name] = self.get_key(c, "DiscordWebHooks", hook_name)

        self.check_if_section_present(c, "NotificationsSpecificWebHooks")
        for notification_name in c.options("NotificationsSpecificWebHooks"):
            hook_name = self.get_key(c, "NotificationsSpecificWebHooks", notification_name)
            if hook_name not in self.webhooks:
                raise ConfigurationException("Unknown Webhook [{0}]".format(hook_name))
            self.notification_webhook[notification_name] = hook_name

        self.discord_config['default_webhook'] = self.get_key(c, 'DiscordDefaults', 'default_webhook')
        if self.discord_config['default_webhook'] not in self.webhooks:
            raise ConfigurationException("Default webhook name unknown.")

    def get_characters(self, c):
        chars = []
        char_bits = {}

        for key in c.options('EveCharacters'):
            s = key.split('.')
            if not key[0] == 'char' or not len(s) == 3 or s[2] not in ('username', 'char_id', 'refresh_token'):
                raise ConfigurationException("Unexpected character option name")
            index = int(s[1])
            if index not in char_bits:
                char_bits[index] = {}
            char_bits[index][s[2]] = self.get_key(c, 'EveCharacters', key)

        for index in sorted(char_bits.keys()):
            if len(char_bits[index]) != 3:
                raise ConfigurationException("Missing required key")
            chars.append({
                'username': char_bits[index]['username'],
                'char_id': char_bits[index]['char_id'],
                'refresh_token': char_bits[index]['refresh_token'],
            })
        return chars

    @staticmethod
    def check_if_section_present(c, section):
        if not c.has_section(section):
            raise ConfigurationException("Need a [{0}] section in config.".format(section))

    @staticmethod
    def get_key(c, section, key):
        if c.has_option(section, key):
            return c[section][key]
        else:
            raise ConfigurationException("Key {0}:{1} missing.".format(section, key))

    def parse_notification_format_section(self, c, n_format_section_name):
        notification_type = n_format_section_name.split(' ')[1]  # Per self.parse_config() should never IndexError.
        if len(notification_type) < 1:
            raise ConfigurationException(f"NotificationFormat section [{n_format_section_name}] is invalid.")
        content = None
        if c.has_option(n_format_section_name, 'content'):
            content = c.get(n_format_section_name, 'content')
        embed_prefixes = sorted(set([".".join(option.split('.')[:2]) for option in c.options(n_format_section_name)
                                     if option.startswith('embed.')]))
        embeds = []
        for prefix in embed_prefixes:
            if not c.has_option(n_format_section_name, prefix + '.formatter'):
                raise ConfigurationException(f"Missing formatter for an embed in {n_format_section_name}")
            formatter = c.get(n_format_section_name, prefix + '.formatter')
            title = None
            if c.has_option(n_format_section_name, prefix + '.title'):
                title = c.get(n_format_section_name, prefix + '.title')
            argument = None
            if c.has_option(n_format_section_name, prefix + '.argument'):
                argument = c.get(n_format_section_name, prefix + '.argument')
            embeds.append(EmbedFormat(formatter=formatter, title=title, argument=argument))
        self.notification_formats[notification_type] = NotificationFormat(content=content, embeds=embeds)
