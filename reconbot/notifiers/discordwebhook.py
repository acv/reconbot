import requests

from reconbot.notificationprinters.discord.discordmessage import DiscordMessage


class DiscordWebhookNotifier:
    def __init__(self, url):
        self.url = url

    # noinspection PyUnusedLocal
    def notify(self, notification, text, options=None):
        return self._send_message(text)

    def _send_message(self, message: DiscordMessage):
        payload = message.as_data_struct()
        return requests.post(self.url, json=payload)
