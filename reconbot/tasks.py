import sys
import traceback
import datetime
import logging

from reconbot.notificationprinters.printer import Printer
from reconbot.esi import ESI

MAX_NOTIFICATION_AGE_IN_SECONDS = 7200


logger = logging.getLogger(__name__)


def esi_notification_task(notification_options, api_queue, notifier, ping_formatter):
    try:
        sso = api_queue.get()

        esi = ESI(sso)

        logger.info(f"Retrieving notifications newer than {MAX_NOTIFICATION_AGE_IN_SECONDS} " +
                    f"seconds from {sso.character_name}.")
        notifications = esi.get_new_notifications(max_age=MAX_NOTIFICATION_AGE_IN_SECONDS)
        logger.info("Got {count} notifications.".format(count=len(notifications)))

        for notification in notifications:
            logger.debug("Notification type {type} content: {content}".format(type=notification['type'],
                                                                              content=notification['text']))

        if 'whitelist' in notification_options and type(notification_options['whitelist']) is list:
            for notification in notifications:
                print(notification['type'])
            notifications = [notification for notification in notifications
                             if notification['type'] in notification_options['whitelist']]

        logger.info("After whitelist, {count} notifications remain.".format(count=len(notifications)))

        if 'filters' in notification_options and type(notification_options['filters']) is list:
            for notification_filter in notification_options['filters']:
                notifications = [notification_filter.filter(notification) for notification in notifications]

        printer = Printer(esi, ping_formatter)

        messages = []
        for notification in notifications:
            formatted = printer.transform(notification)
            messages.append((notification, formatted))
            logger.debug("Notification type {type} formatted as {formatted}".format(type=notification['type'],
                                                                                    formatted=formatted))

        for notification, message in messages:
            notifier.notify(notification, message)

    except Exception as e:
        notify_exception("esi_notification_task", e)


def notify_exception(location, exception):
    print('[%s] Exception in %s' % (datetime.datetime.now(), location))
    print('-' * 60)
    traceback.print_exc(file=sys.stdout)
    print(exception)
    print('-' * 60)
