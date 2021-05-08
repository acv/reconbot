class PingFormatter(object):
    def __init__(self, ping_mapping, default_ping):
        self.ping_mapping = ping_mapping
        self.default_ping = default_ping

    def get_ping_string(self, notification):
        if notification['type'] in self.ping_mapping:
            return self.ping_mapping[notification['type']]
        else:
            return self.default_ping
