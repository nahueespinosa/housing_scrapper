from bs4 import BeautifulSoup
from providers.provider import Provider
from typing import Dict, Generator


class Zonaprop(Provider):
    name: str = 'zonaprop'

    def props_from_source(self, source: str) -> Generator[Dict[str, str], None, None]:
        page_link = self.config['base_url'] + source
        page = 1
        processed_ids = []

        while(True):
            page_response = self.request(page_link)
            if page_response.status_code != 200:
                break

            page_content = BeautifulSoup(page_response.content, 'lxml')
            properties = page_content.find_all('div', class_='postingCard')

            for prop in properties:
                # if data-id was already processed we exit
                if prop['data-id'] in processed_ids:
                    return
                processed_ids.append(prop['data-id'])
                title = prop.find('a', class_='go-to-posting').get_text().strip()
                price_section = prop.find('span', class_='firstPrice')
                if price_section is not None:
                    title = title + ' ' + price_section['data-price']

                yield {
                    'title': title,
                    'url': self.config['base_url'] + prop['data-to-posting'],
                    'internal_id': prop['data-id'],
                    'provider': self.provider_name
                }

            page += 1
            page_link = self.config['base_url'] + source.replace(".html", f"-pagina-{page}.html")
