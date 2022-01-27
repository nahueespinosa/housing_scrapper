import cloudscraper
import logging
import yaml

from abc import ABC, abstractmethod
from typing import Dict, Generator


class Provider(ABC):
    subclasses = dict()

    def __init__(self, config):
        self.config = config
        self.__scraper = cloudscraper.create_scraper()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    def request(self, url):
        logging.info(f"Requesting {url}")
        return self.__scraper.get(url, verify=True)

    @abstractmethod
    def props_from_source(self, source) -> Generator[Dict[str, str], None, None]:
        pass

    def props(self):
        for source in self.config['sources']:
            logging.info(f'Processing source {source}')
            yield from self.props_from_source(source)
