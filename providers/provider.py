from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from aiocfscrape import CloudflareScraper
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Type


@dataclass
class Property:
    title: str
    url: str
    internal_id: str
    provider: str


class Provider(ABC):
    name: str
    subclasses: Dict[str, Type[Provider]] = dict()

    def __init__(self, config):
        logging.info(f"[{self.name}] Setting up provider")
        self.config = config

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.name] = cls

    async def request(self, url) -> str:
        logging.info(f'[{self.name}] Requesting {url}')
        # some sites return '403 Forbidden' if the request doesn't have a user-agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)',
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://www.google.com/",
        }
        async with CloudflareScraper() as session:
            async with session.get(url, headers=headers) as response:
                if not response.ok:
                    logging.warning(f'[{self.name}] Request failed with status {response.status}')
                    return ''

                return await response.text()

    @abstractmethod
    async def props_from_source(self, source) -> AsyncGenerator[Property, None]:
        raise NotImplementedError

    async def props(self) -> AsyncGenerator[Property, None]:
        for index, source in enumerate(self.config['sources']):
            logging.info(f'[{self.name}] Processing source {index}')
            async for prop in self.props_from_source(source):  # type: ignore
                logging.info(f"[{self.name}] Processing property {prop.internal_id}")
                yield prop
