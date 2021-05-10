from reconbot.notificationprinters.discord.discordmessage import DiscordMessage


class StdOutNotifier:
    def __init__(self):
        pass

    # noinspection PyUnusedLocal
    @staticmethod
    def notify(notification, discord_message: DiscordMessage, options=None):
        print('StdOutNotifier:', discord_message.as_data_struct())
