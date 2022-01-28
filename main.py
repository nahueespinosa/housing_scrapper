#!/usr/bin/env python

import asyncio
import logging
import yaml

from notifiers.notifier import TelegramNotifier

from database.database import Database

from providers.argenprop import Argenprop
from providers.inmobusqueda import Inmobusqueda
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.provider import Property, Provider
from providers.zonaprop import Zonaprop

from typing import Iterable


async def process_properties(db: Database, props: Iterable[Property]):
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
