import logging
import random
import telegram


class TelegramNotifier:
    def __init__(self, config):
        logging.info(f"Setting up bot with token {config['token']}")
        self.config = config
        self.bot = telegram.Bot(token=self.config['token'])

    def notify(self, properties):
        if properties:
            logging.info(f'Notifying about {len(properties)} properties')
            text = random.choice(self.config['messages'])
            self.bot.send_message(chat_id=self.config['chat_id'], text=text)

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            self.bot.send_message(chat_id=self.config['chat_id'],
                text=f"[{prop['title']}]({prop['url']})",
                parse_mode=telegram.ParseMode.MARKDOWN)

    def test(self, message):
        self.bot.send_message(chat_id=self.config['chat_id'], text=message)
