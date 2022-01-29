#!/usr/bin/env python3

import asyncio
import logging
import yaml

from database import Database
from notifiers import TelegramNotifier
from providers import Property, Provider
from providers import Argenprop, Inmobusqueda, Mercadolibre, Properati, Zonaprop
from typing import AsyncIterable


async def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    with Database('properties.db') as db:
        new_properties = []
        async def task(props: AsyncIterable[Property]) -> None:
            async for prop in props:
                if db.insert_property(prop):
                    new_properties.append(prop)

        tasks = []
        for provider_name, provider_cfg in cfg['providers'].items():
            provider = Provider.subclasses[provider_name](provider_cfg)
            tasks.append(task(provider.props()))
        await asyncio.gather(*tasks)

    notifier = TelegramNotifier(cfg['notifier'])
    notifier.notify(new_properties)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
