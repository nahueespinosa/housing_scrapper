from bs4 import BeautifulSoup

from .provider import Property, Provider


class Properati(Provider):
    name: str = 'properati'

    async def props_from_source(self, source: str):
        page_link = self.config['base_url'] + source
        page = 1

        while True:
            page_content = BeautifulSoup(await self.request(page_link), 'lxml')
            properties = page_content.find_all('div', class_=lambda class_: class_ and class_.startswith("StyledCardInfo"))

            if not properties:
                break

            for prop in properties:
                link = prop.find('a')
                title = link.find('h2').get_text().strip()
                price_section = prop.find('div', class_=lambda class_: class_ and class_.startswith("StyledPrice"))
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()
                href = link['href']
                internal_id = href.replace('/detalle/', '')[:5]

                yield Property(title=title,
                               url=self.config['base_url'] + href,
                               internal_id=internal_id,
                               provider=self.name)

            page += 1
            page_link = self.config['base_url'] + source + f'?page={page}'
