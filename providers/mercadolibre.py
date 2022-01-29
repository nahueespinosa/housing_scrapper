import re

from bs4 import BeautifulSoup
from typing import Generator

from .provider import Property, Provider


class Mercadolibre(Provider):
    name: str = 'mercadolibre'

    async def props_from_source(self, source: str) -> Generator[Property, None, None]:
        page_link = self.config['base_url'] + source + '_NoIndex_True'
        from_ = 1
        regex = r'(MLA-\d*)'

        while True:
            content = BeautifulSoup(await self.request(page_link), 'lxml')
            properties = content.find_all('li', class_='ui-search-layout__item')

            if not properties:
                break

            for prop in properties:
                section = prop.find('a', class_='ui-search-result__link')
                if section is None:
                    section = prop.find('a', class_='ui-search-result__content')
                href = section['href']
                matches = re.search(regex, href)
                internal_id = matches.group(1).replace('-', '')
                title_section = section.find('div', class_='ui-search-item__group--title')
                title = title_section.find('h2').get_text().strip()

                yield Property(title=title,
                               url=href,
                               internal_id=internal_id,
                               provider=self.name)

            from_ += 48
            filter_index = source.find('_')
            page_link = self.config['base_url'] + \
                        source[:filter_index] + f'_Desde_{from_}' + source[filter_index:] + \
                        '_NoIndex_True'
