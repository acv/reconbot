import math

import schedule
import time
import os
import logging
import argparse

from logging.handlers import TimedRotatingFileHandler

from reconbot.config import Config
from reconbot.filters.differentiate_fob_attacks import DifferentiateFobAttacks
from reconbot.tasks import esi_notification_task
from reconbot.notifiers.caching import CachingNotifier
from reconbot.notifiers.discordwebhook import DiscordWebhookNotifier
from reconbot.notifiers.splitter import SplitterNotifier
from reconbot.notifiers.stdout import StdOutNotifier
from reconbot.notifiers.routing import RoutingNotifier
from reconbot.apiqueue import ApiQueue
from reconbot.sso import SSO
from reconbot.db.char_db import CharDB
from dotenv import load_dotenv

load_dotenv()

log_handler = TimedRotatingFileHandler('reconbot.log', when="d", interval=7, backupCount=4)
log_handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)


notification_caching_timer = 5
webhook_url = os.getenv("WEBHOOK_URL")
mining_webhook_url = os.getenv("MINING_WEBHOOK_URL")
sso_app_client_id = os.getenv("SSO_APP_CLIENT_ID")
sso_app_secret_key = os.getenv("SSO_APP_SECRET_KEY")
character_one_name = os.getenv("CHARACTER_ONE_NAME")
character_one_id = int(os.getenv("CHARACTER_ONE_ID"))
character_one_token = os.getenv("CHARACTER_ONE_TOKEN")
character_two_name = os.getenv("CHARACTER_TWO_NAME")
character_two_id = int(os.getenv("CHARACTER_TWO_ID"))
character_two_token = os.getenv("CHARACTER_TWO_TOKEN")
character_three_name = os.getenv("CHARACTER_THREE_NAME")
character_three_id = int(os.getenv("CHARACTER_THREE_ID"))
character_three_token = os.getenv("CHARACTER_THREE_TOKEN")
character_four_name = os.getenv("CHARACTER_FOUR_NAME")
character_four_id = int(os.getenv("CHARACTER_FOUR_ID"))
character_four_token = os.getenv("CHARACTER_FOUR_TOKEN")
character_five_name = os.getenv("CHARACTER_FIVE_NAME")
character_five_id = int(os.getenv("CHARACTER_FIVE_ID"))
character_five_token = os.getenv("CHARACTER_FIVE_TOKEN")
character_six_name = os.getenv("CHARACTER_SIX_NAME")
character_six_id = int(os.getenv("CHARACTER_SIX_ID"))
character_six_token = os.getenv("CHARACTER_SIX_TOKEN")


p = argparse.ArgumentParser()
p.add_argument("-c", "--config", metavar="CONFIG", default="reconbot.ini",
               help="Path to config file (default: ./reconbot.ini)")
args = p.parse_args()


config = Config(config_file_name=args.config)


eve_apis = {
    'logistics-team': {
        'notifications': {
            'whitelist': config.notifications_whitelist,
            'filters': [
                DifferentiateFobAttacks(),
            ],
            'notification_formats': config.notification_formats,
            'ping': config.discord_config['ping'],
            'default_ping': config.discord_config['default_ping']
        },
        'characters': CharDB(config),
    }
}


custom_notifiers = {}
for notification in config.notification_webhook.keys():
    custom_notifiers[notification] = DiscordWebhookNotifier(config.webhooks[config.notification_webhook[notification]])


notifiers = CachingNotifier(
    SplitterNotifier([
        RoutingNotifier(
            notifiers=custom_notifiers,
            default_notifier=DiscordWebhookNotifier(config.webhooks[config.discord_config['default_webhook']])
        ),
        StdOutNotifier(),
    ]),
    duration=7200
)


api_queue_logistics = ApiQueue(config, [SSO(config.esi_config['ApplicationClientID'],
                                            config.esi_config['ApplicationSecretKey'],
                                            c) for c in config.esi_config['characters']])


def notifications_job_logistics():
    esi_notification_task(
        eve_apis['logistics-team']['notifications'],
        api_queue_logistics,
        notifiers
    )


def run_and_schedule(characters, notifications_job):
    notifications_job()

    schedule.every(math.ceil(notification_caching_timer/len(characters))).minutes.do(notifications_job)


run_and_schedule(config.esi_config['characters'], notifications_job_logistics)


while True:
    schedule.run_pending()
    time.sleep(1)
