import re
import logging

from bs4 import BeautifulSoup

from .provider import Property, Provider


class Argenprop(Provider):
    name: str = 'argenprop'

    async def props_from_source(self, source: str):
        page_link = self.config['base_url'] + source
        page = 1
        regex = r'.*--(\d+)'

        processed_ids = set()

        while True:
            content = BeautifulSoup(await self.request(page_link), 'lxml')
            properties = content.find_all('div', class_='listing__item')

            if not properties:
                return

            for prop in properties:
                title = prop.find('h2', class_='card__title').get_text().strip()
                price_section = prop.find('p', class_='card__price')
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()
                href = prop.find('a', class_='card')['href']
                matches = re.search(regex, href)
                assert matches is not None
                internal_id = matches.group(1)

                if internal_id in processed_ids:
                    return  # if internal id was already processed we exit

                processed_ids.add(internal_id)

                yield Property(title=title,
                               url=self.config['base_url'] + href,
                               internal_id=internal_id,
                               provider=self.name)

            page += 1
            page_link = self.config['base_url'] + source + f'?pagina-{page}'
