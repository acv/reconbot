class StdOutNotifier:
    def __init__(self):
        pass

    # noinspection PyUnusedLocal
    @staticmethod
    def notify(notification, text, options=None):
        print('StdOutNotifier:', text)
