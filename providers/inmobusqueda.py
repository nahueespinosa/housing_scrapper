from bs4 import BeautifulSoup

from .provider import Property, Provider


class Inmobusqueda(Provider):
    name: str = 'inmobusqueda'

    async def props_from_source(self, source: str):
        page_link = self.config['base_url'] + source
        page = 1

        while True:
            page_content = BeautifulSoup(await self.request(page_link), 'lxml')
            properties = page_content.find_all('div', class_='ResultadoCaja')

            if not properties:
                return

            for prop in properties:
                link = prop.find('div', class_='resultadoTipo').find('a')
                href = link['href']

                if len(properties) == 1 and href == '#':
                    return

                title = link.get_text().strip()
                price_section = prop.find('div', class_='resultadoPrecio')
                if price_section is not None:
                    title = title + ' ' + price_section.get_text().strip()

                internal_id = prop.find('div', class_='codigo').get_text().strip()
                yield Property(title=title,
                               url=href,
                               internal_id=internal_id,
                               provider=self.name)

            page += 1
            page_link = self.config['base_url'] + source.replace('.html', f'-pagina-{page}.html')
