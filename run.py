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


discord = {
    'webhook': {
        'url': webhook_url
    },
    'mining_webhook': {
        'url': mining_webhook_url
    }
}

sso_app = {
    'client_id': sso_app_client_id,
    'secret_key': sso_app_secret_key
}

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
        'characters': {
            character_one_name: {
                'character_name': character_one_name,
                'character_id': character_one_id,
                'refresh_token': character_one_token
            },
            character_two_name: {
                'character_name': character_two_name,
                'character_id': character_two_id,
                'refresh_token': character_two_token
            },
            character_three_name: {
                'character_name': character_three_name,
                'character_id': character_three_id,
                'refresh_token': character_three_token
            },
            character_four_name: {
                'character_name': character_four_name,
                'character_id': character_four_id,
                'refresh_token': character_four_token
            },
            character_five_name: {
                'character_name': character_five_name,
                'character_id': character_five_id,
                'refresh_token': character_five_token
            },
            character_six_name: {
                'character_name': character_six_name,
                'character_id': character_six_id,
                'refresh_token': character_six_token
            },
        },
    }
}

notifiers = CachingNotifier(
    SplitterNotifier([
        RoutingNotifier(
            notifiers={
                'MoonminingAutomaticFracture': DiscordWebhookNotifier(discord['mining_webhook']['url']),
                'MoonminingExtractionFinished': DiscordWebhookNotifier(discord['mining_webhook']['url']),
                'MoonminingLaserFired': DiscordWebhookNotifier(discord['mining_webhook']['url'])
            },
            default_notifier=DiscordWebhookNotifier(discord['webhook']['url'])
        ),
        StdOutNotifier(),
    ]),
    duration=7200
)


def api_to_sso(api):
    return SSO(
        sso_app['client_id'],
        sso_app['secret_key'],
        api['refresh_token'],
        api['character_id'],
        api['character_name']
    )


api_queue_logistics = ApiQueue(list(map(api_to_sso, eve_apis['logistics-team']['characters'].values())))


def notifications_job_logistics():
    esi_notification_task(
        eve_apis['logistics-team']['notifications'],
        api_queue_logistics,
        notifiers
    )


def run_and_schedule(characters, notifications_job):
    notifications_job()

    schedule.every(math.ceil(notification_caching_timer/len(characters))).minutes.do(notifications_job)


run_and_schedule(eve_apis['logistics-team']['characters'], notifications_job_logistics)


while True:
    schedule.run_pending()
    time.sleep(1)
