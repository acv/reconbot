class SplitterNotifier:
    def __init__(self, notifiers=None):
        if notifiers is None:
            notifiers = []
        self.notifiers = notifiers

    def notify(self, notification, text, options=None):
        if options is None:
            options = {}
        for notifier in self.notifiers:
            notifier.notify(notification, text, options)
