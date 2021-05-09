import configparser

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

        if 'NotificationsMonitored' not in c:
            raise ConfigurationException("Need a [NotificationsMonitored] section in config.")

        for notification in c['NotificationsMonitored']:
            self.notifications_whitelist.append(notification)

        if len(self.notifications_whitelist) < 1:
            raise ConfigurationException("No notifications white listed.")

        if 'DiscordDefaults' not in c:
            raise ConfigurationException("No [DiscordDefaults] section in config.")

        if 'default_ping' in c['DiscordDefaults']:
            self.discord_config['default_ping'] = c['DiscordDefaults']['default_ping']
        else:
            raise ConfigurationException("DiscordDefaults:default_ping missing.")

        if 'DiscordNotificationSpecificPing' not in c:
            raise ConfigurationException("No [DiscordNotificationSpecificPing] section in config.")

        for ping in c['DiscordNotificationSpecificPing']:
            self.discord_config['ping'][ping] = c['DiscordNotificationSpecificPing'][ping]

        notification_formats = [section for section in c.sections() if section.startswith('NotificationFormat ')]
        for n_format in notification_formats:
            self.parse_notification_format_section(n_format, c[n_format])

    def parse_notification_format_section(self, n_format_section_name, n_format_section):
        notification_type = n_format_section.split(' ')[1]  # Per self.parse_config() should never IndexError.
        if len(notification_type) < 1:
            raise ConfigurationException(f"NotificationFormat section [{n_format_section_name}] is invalid.")
        if 'content' not in n_format_section:
            raise ConfigurationException(f"content key not found in section [{n_format_section_name}].")
        self.notification_formats[notification_type] = NotificationFormat(content=n_format_section['content'])
