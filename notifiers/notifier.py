import logging
import random
import telegram

from typing import Dict, Sequence


class TelegramNotifier:
    def __init__(self, config: Dict[str, str]):
        logging.info(f"Setting up bot with token {config['token']}")
        self.config = config
        self.bot = telegram.Bot(token=self.config['token'])

    def notify(self, properties: Sequence[Dict[str, str]]) -> None:
        if properties:
            logging.info(f'Notifying about {len(properties)} properties')
            text = random.choice(self.config['messages'])
            self.bot.send_message(chat_id=self.config['chat_id'], text=text)

        for prop in properties:
            logging.info(f"Notifying about {prop['url']}")
            self.bot.send_message(chat_id=self.config['chat_id'],
                text=f"[{prop['title']}]({prop['url']})",
                parse_mode=telegram.ParseMode.MARKDOWN)

    def test(self, message: str) -> None:
        self.bot.send_message(chat_id=self.config['chat_id'], text=message)
