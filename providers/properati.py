from bs4 import BeautifulSoup
from typing import Generator

from .provider import Property, Provider


class Properati(Provider):
    name: str = 'properati'

    async def props_from_source(self, source: str) -> Generator[Property, None, None]:
        page_link = self.config['base_url'] + source
        page = 1
        total_pages = 1

        while True:
            if page > total_pages:
                break

            page_content = BeautifulSoup(await self.request(page_link), 'lxml')
            properties = page_content.find_all('div', class_='item-description')

            if page == 1:
                nav_list = page_content.select('#page-wrapper > div.results-content > div.container.wide-listing > div.content > div.row.items-container > div.item-list.span6 > div > div.pagination.pagination-centered > ul > li')
                total_pages = len(nav_list) - 2

            if not properties:
                break

            for prop in properties:
                link = prop.find('a', class_='item-url')
                title = link['title']
                price_section = prop.find('p', class_='price')
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()
                href = link['href']
                internal_id = prop.find('a', class_='icon-fav')['data-property_id']

                yield Property(title=title,
                               url=href,
                               internal_id=internal_id,
                               provider=self.name)

            page += 1
            page_link = self.config['base_url'] + source + '/%s/' % page
