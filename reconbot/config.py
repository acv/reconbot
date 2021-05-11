import configparser

from reconbot.notificationprinters.embedformat import EmbedFormat
from reconbot.notificationprinters.notificationformat import NotificationFormat


class ConfigurationException(Exception):
    pass


class Config(object):
    def __init__(self, config_file_name):
        self.notifications_whitelist = []
        self.discord_config = {'ping': {}}
        self.notification_formats = {}
        self.parse_config(config_file_name)

    # noinspection PyTypeChecker
    def parse_config(self, config_file_name):
        c = configparser.ConfigParser(allow_no_value=True)
        c.optionxform = lambda option: option
        c.read(config_file_name)

        if not c.has_section('NotificationsMonitored'):
            raise ConfigurationException("Need a [NotificationsMonitored] section in config.")

        for notification in c['NotificationsMonitored']:
            self.notifications_whitelist.append(notification)

        if len(self.notifications_whitelist) < 1:
            raise ConfigurationException("No notifications white listed.")

        if not c.has_section('DiscordDefaults'):
            raise ConfigurationException("No [DiscordDefaults] section in config.")

        if c.has_option('DiscordDefaults', 'default_ping'):
            self.discord_config['default_ping'] = c['DiscordDefaults']['default_ping']
        else:
            raise ConfigurationException("DiscordDefaults:default_ping missing.")

        if not c.has_section('DiscordNotificationSpecificPing'):
            raise ConfigurationException("No [DiscordNotificationSpecificPing] section in config.")

        for ping in c['DiscordNotificationSpecificPing']:
            self.discord_config['ping'][ping] = c['DiscordNotificationSpecificPing'][ping]

        notification_formats = [section for section in c.sections() if section.startswith('NotificationFormat ')]
        for n_format in notification_formats:
            self.parse_notification_format_section(c, n_format)

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
