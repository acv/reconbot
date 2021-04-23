import sys
import traceback
import datetime

from reconbot.notificationprinters.esi.discord import Discord as ESIDiscord
from reconbot.esi import ESI

MAX_NOTIFICATION_AGE_IN_SECONDS = 6300


def esi_notification_task(notification_options, api_queue, printer, notifier):
    try:
        sso = api_queue.get()

        esi = ESI(sso)

        notifications = esi.get_new_notifications(max_age=MAX_NOTIFICATION_AGE_IN_SECONDS)

        if 'whitelist' in notification_options and type(notification_options['whitelist']) is list:
            for notification in notifications:
                print(notification['type'])
            notifications = [notification for notification in notifications
                             if notification['type'] in notification_options['whitelist']]
        
        printer = ESIDiscord(esi)        

        messages = map(lambda text: printer.transform(text), notifications)

        for message in messages:
            notifier.notify(message)

    except Exception as e:
        notify_exception("esi_notification_task", e)


def notify_exception(location, exception):
    print('[%s] Exception in %s' % (datetime.datetime.now(), location))
    print('-' * 60)
    traceback.print_exc(file=sys.stdout)
    print(exception)
    print('-' * 60)
