import cloudscraper
import logging
import yaml

from abc import ABC, abstractmethod
from dataclasses import dataclass
from requests import Response
from typing import Generator


@dataclass
class Property:
    title: str
    url: str
    internal_id: str
    provider: str


class Provider(ABC):
    subclasses = dict()

    def __init__(self, config):
        self.config = config
        self.__scraper = cloudscraper.create_scraper()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    def request(self, url) -> Response:
        logging.debug(f'Requesting {url}')
        return self.__scraper.get(url, verify=True)

    @abstractmethod
    def props_from_source(self, source) -> Generator[Property, None, None]:
        pass

    def props(self) -> Generator[Property, None, None]:
        for index, source in enumerate(self.config['sources']):
            logging.info(f'Processing source   {self.name}:{index}')
            yield from self.props_from_source(source)
