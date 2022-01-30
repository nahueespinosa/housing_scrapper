import asyncio

from providers import Property, Zonaprop
from typing import AsyncIterable, List
from unittest import main, TestCase
from unittest.mock import call, patch, AsyncMock


class TestZonaprop(TestCase):
    example_page: str

    @classmethod
    def setUpClass(cls) -> None:
        with open('test/examples/zonaprop.html') as file:
            cls.example_page = file.read()
        return super().setUpClass()

    @staticmethod
    async def get_prop_list(props: AsyncIterable[Property]) -> List[Property]:
        return [prop async for prop in props]

    @patch('providers.Zonaprop.request')
    def test_empty_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.zonaprop.com.ar',
            'sources': [],
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_prop_list(Zonaprop(cfg).props()))
        request_mock.assert_not_called()

    @patch('providers.Zonaprop.request')
    def test_multiple_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.zonaprop.com.ar',
            'sources': ['/departamento-venta.html', '/departamento-alquiler.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Zonaprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.zonaprop.com.ar/departamento-alquiler.html'),
            call('https://www.zonaprop.com.ar/departamento-venta.html'),
        ], any_order=True)
        self.assertEqual(0, len(result))

    @patch('providers.Zonaprop.request')
    def test_element_processing(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, '']
        cfg = {
            'base_url': 'https://www.zonaprop.com.ar',
            'sources': ['/departamento.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Zonaprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.zonaprop.com.ar/departamento.html'),
            call('https://www.zonaprop.com.ar/departamento-pagina-2.html'),
        ])
        self.assertEqual(20, len(result))
        expected_property = Property(
            url='https://www.zonaprop.com.ar/propiedades/departamento-palermo-chico-49062026.html',
            internal_id='49062026',
            title='Departamento - Palermo Chico USD 1.800',
            provider='zonaprop')
        self.assertDictEqual(expected_property.__dict__, result[0].__dict__)

    @patch('providers.Zonaprop.request')
    def test_paging_when_repeating(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, self.example_page]
        cfg = {
            'base_url': 'https://www.zonaprop.com.ar',
            'sources': ['/departamento.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Zonaprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.zonaprop.com.ar/departamento.html'),
            call('https://www.zonaprop.com.ar/departamento-pagina-2.html'),
        ])
        self.assertEqual(20, len(result))


if __name__ == '__main__':
    main()
