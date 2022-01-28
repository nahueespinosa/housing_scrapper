#!/usr/bin/env python

import asyncio
import logging
import yaml

from database import Database
from notifiers import TelegramNotifier
from providers import Property, Provider
from providers import Argenprop, Inmobusqueda, Mercadolibre, Properati, Zonaprop
from typing import Iterable, List


async def process_properties(db: Database, props: Iterable[Property]) -> List[Property]:
    return [prop async for prop in props if db.insert_property(prop)]


async def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    with Database('properties.db') as db:
        tasks = []
        for provider_name, provider_cfg in cfg['providers'].items():
            provider = Provider.subclasses[provider_name](provider_cfg)
            tasks.append(process_properties(db, provider.props()))
        results = await asyncio.gather(*tasks)

    # flatten results
    new_properties = [prop for sublist in results for prop in sublist]
    notifier = TelegramNotifier(cfg['notifier'])
    notifier.notify(new_properties)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
