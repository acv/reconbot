class RoutingNotifier:
    def __init__(self, notifiers, default_notifier):
        self.notifiers = notifiers
        self.default_notifier = default_notifier

    def notify(self, notification, text, options=None):
        if options is None:
            options = {}

        if notification['type'] in self.notifiers:
            self.notifiers[notification['type']].notify(notification, text, options)
        else:
            self.default_notifier.notify(notification, text, options)
