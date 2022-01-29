import asyncio
import logging
import yaml

from providers import Provider
from providers import Argenprop, Inmobusqueda, Mercadolibre, Properati, Zonaprop


async def main() -> None:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    for name, config in cfg['providers'].items():
        provider = Provider.subclasses[name](config)
        [print(prop) async for prop in provider.props()]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
