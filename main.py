#!/usr/bin/env python3

import asyncio
import logging
import yaml

from argparse import ArgumentParser
from database import Database
from notifiers import TelegramNotifier
from providers import Property, Provider
from providers import Argenprop, Inmobusqueda, Mercadolibre, Properati, Zonaprop
from typing import AsyncIterable


async def main(argv=None) -> None:
    parser = ArgumentParser(description='Housing scrapper tool')
    parser.add_argument('-c', '--config', default='configuration.yml',
                        help='path to configuration file. It defaults to `configuration.yml`')
    parser.add_argument('-d', '--database', default='properties.db',
                        help='path to database file. It defaults to `properties.db`')
    parser.add_argument('--notify', dest='notify', action='store_true',
                        help='notify results through a telegram bot [default]')
    parser.add_argument('--no-notify', dest='notify', action='store_false',
                        help='avoid notifying results')
    parser.set_defaults(notify=True)
    args = parser.parse_args(argv)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open(args.config, 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    with Database(args.database) as db:
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

    if args.notify:
        notifier = TelegramNotifier(cfg['notifier'])
        notifier.notify(new_properties)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
