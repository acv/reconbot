import configparser


class ConfigurationException(Exception):
    pass


class Config(object):
    def __init__(self, config_file_name):
        self.parse_config(config_file_name)
        self.notifications_whitelist = []
        self.discord_config = {'ping': {}}

    # noinspection PyTypeChecker
    def parse_config(self, config_file_name):
        c = configparser.ConfigParser(allow_no_value=True)
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
