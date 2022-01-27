import logging
import yaml

from providers.zonaprop import Zonaprop
from providers.argenprop import Argenprop
from providers.mercadolibre import Mercadolibre
from providers.properati import Properati
from providers.provider import Provider
from providers.inmobusqueda import Inmobusqueda


if __name__ == '__main__':
    # logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('configuration.yml', 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    for name, config in cfg['providers'].items():
        provider = Provider.subclasses[name](config)
        [print(prop) for prop in provider.props()]
