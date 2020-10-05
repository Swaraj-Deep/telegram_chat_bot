import requests
import json
import configparser as cfg


class telegram_chatbot:
    def __init__(self, config):
        self.token = self.read_token_from_config_file(config)
        self.base_url = f'https://api.telegram.org/bot{self.token}/'

    def get_update(self, offset=None):
        url = self.base_url + 'getUpdates?timeout=100'
        if offset:
            url = url + f'&offset={offset + 1}'
        r = requests.get(url)
        return json.loads(r.content)

    def send_message(self, msg, chat_id):
        url = self.base_url + f'sendMessage?chat_id={chat_id}&text={msg}'
        if msg is not None:
            requests.get(url)

    def read_token_from_config_file(self, config):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', 'token')
