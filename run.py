import math

import schedule
import time
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


log_handler = TimedRotatingFileHandler('reconbot.log', when="d", interval=7, backupCount=4)
log_handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))

logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
logger.info("Application Started")


notification_caching_timer = 5

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
        'characters': CharDB(config).chars,
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


api_queue_logistics = ApiQueue([SSO(config.esi_config['ApplicationClientID'],
                                    config.esi_config['ApplicationSecretKey'],
                                    c) for c in eve_apis['logistics-team']['characters']])


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
