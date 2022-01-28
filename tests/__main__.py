import asyncio
import logging
import yaml

from providers.zonaprop import Zonaprop
from providers.argenprop import Argenprop
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.provider import Provider
from providers.inmobusqueda import Inmobusqueda


async def main() -> None:
    # logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    for name, config in cfg['providers'].items():
        provider = Provider.subclasses[name](config)
        [print(prop) async for prop in provider.props()]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
