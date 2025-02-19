import requests
import base64
import time


class SSO:

    def __init__(self, client_id, secret_key, character):
        self.client_id = client_id
        self.secret_key = secret_key
        self.character = character
        self.login_server = 'https://login.eveonline.com'
        self.access_token = None
        self.access_token_expiry = None

    def get_access_token(self):
        if self.token_expired():
            return self.fetch_access_token()

        return self.access_token

    def fetch_access_token(self):
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': self.character.refresh_token
        }
        headers = {
            'authorization': 'Basic %s' % base64.b64encode(
                str.encode('%s:%s' % (self.client_id, self.secret_key))).decode('utf-8')
        }
        r = requests.post('%s/v2/oauth/token' % self.login_server, data=payload, headers=headers)
        if r.status_code == 200:
            response = r.json()
            self.access_token = response['access_token']
            refresh_token = response['refresh_token']
            if refresh_token != self.character.refresh_token:
                self.character.refresh_token = refresh_token
                self.character.save()
            self.access_token_expiry = self.set_token_expiry(response['expires_in'])
            return self.access_token
        else:
            r.raise_for_status()

    def set_token_expiry(self, seconds):
        self.access_token_expiry = time.time() + seconds
        return self.access_token_expiry

    def token_expired(self):
        return self.access_token_expiry is None or self.access_token_expiry <= time.time()
