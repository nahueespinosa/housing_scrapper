#!/usr/bin/env python

import logging
import yaml

from notifiers.notifier import TelegramNotifier

from database.database import create_database, store_properties

from providers.argenprop import Argenprop
from providers.inmobusqueda import Inmobusqueda
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.provider import Provider
from providers.zonaprop import Zonaprop


def main() -> None:
    # logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    create_database()

    # configuration
    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    notifier = TelegramNotifier(cfg['notifier'])

    new_properties = []
    for name, config in cfg['providers'].items():
        try:
            logging.info(f'Processing provider {name}')
            provider = Provider.subclasses[name](config)
            new_properties += store_properties(provider.props())
        except Exception as error:
            logging.exception(f'Error processing provider {name}')

    notifier.notify(new_properties)


if __name__ == '__main__':
    main()
