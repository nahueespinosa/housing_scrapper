import logging

from abc import ABC, abstractmethod
from aiocfscrape import CloudflareScraper
from dataclasses import dataclass
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
        logging.info(f"[{self.name}] Setting up provider")
        self.config = config

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    async def request(self, url) -> str:
        logging.info(f'[{self.name}] Requesting {url}')
        # some sites return '403 Forbidden' if the request doesn't have a user-agent
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'}
        async with CloudflareScraper() as session:
            async with session.get(url, headers=headers) as response:
                return await response.text() if response.ok else ''

    @abstractmethod
    async def props_from_source(self, source) -> Generator[Property, None, None]:
        pass

    async def props(self) -> Generator[Property, None, None]:
        for index, source in enumerate(self.config['sources']):
            logging.info(f'[{self.name}] Processing source {index}')
            async for prop in self.props_from_source(source):
                logging.info(f"[{self.name}] Processing property {prop.internal_id}")
                yield prop
