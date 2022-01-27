import re

from bs4 import BeautifulSoup
from providers.provider import Provider
from typing import Dict, Generator


class Mercadolibre(Provider):
    name: str = "mercadolibre"

    def props_from_source(self, source: str) -> Generator[Dict[str, str], None, None]:
        page_link = self.config['base_url'] + source + '_NoIndex_True'
        from_ = 1
        regex = r"(MLA-\d*)"

        while(True):
            page_response = self.request(page_link)
            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('li', class_='ui-search-layout__item')

            if not properties:
                break

            for prop in properties:
                section = prop.find('a', class_='ui-search-result__link')
                if section is None:
                    section = prop.find('a', class_='ui-search-result__content')
                href = section['href']
                matches = re.search(regex, href)
                internal_id = matches.group(1).replace('-', '')
                price_section = section.find('span', class_='price-tag')
                title_section = section.find('div', class_='ui-search-item__group--title')
                title = title_section.find('h2').get_text().strip()
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()

                yield {
                    'title': title,
                    'url': href,
                    'internal_id': internal_id,
                    'provider': self.name
                }

            from_ += 50
            page_link = self.config['base_url'] + source + f"_Desde_{from_}_NoIndex_True"
