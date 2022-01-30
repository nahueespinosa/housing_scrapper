import asyncio

from providers import Property, Mercadolibre
from typing import AsyncIterable, List
from unittest import main, TestCase
from unittest.mock import call, patch, AsyncMock


class TestMercadolibre(TestCase):
    example_page: str

    @classmethod
    def setUpClass(cls) -> None:
        with open('tests/examples/mercadolibre.html') as file:
            cls.example_page = file.read()
        return super().setUpClass()

    @staticmethod
    async def get_prop_list(props: AsyncIterable[Property]) -> List[Property]:
        return [prop async for prop in props]

    @patch('providers.Mercadolibre.request')
    def test_empty_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://inmuebles.mercadolibre.com.ar',
            'sources': [],
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_prop_list(Mercadolibre(cfg).props()))
        request_mock.assert_not_called()

    @patch('providers.Mercadolibre.request')
    def test_multiple_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://inmuebles.mercadolibre.com.ar',
            'sources': ['/venta/', '/alquiler/'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Mercadolibre(cfg).props()))
        request_mock.assert_has_calls([
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_NoIndex_True'),
            call('https://inmuebles.mercadolibre.com.ar/venta/_NoIndex_True'),
        ], any_order=True)
        self.assertEqual(0, len(result))

    @patch('providers.Mercadolibre.request')
    def test_element_processing(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, '']
        cfg = {
            'base_url': 'https://inmuebles.mercadolibre.com.ar',
            'sources': ['/alquiler/'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Mercadolibre(cfg).props()))
        request_mock.assert_has_calls([
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_NoIndex_True'),
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_Desde_49_NoIndex_True'),
        ])
        self.assertEqual(48, len(result))
        expected_property = Property(
            url='https://departamento.mercadolibre.com.ar/MLA-1120363656-departamento-1-dormitorio-sin-mascotas-_JM',
            internal_id='MLA1120363656',
            title='Alquilo Departamento 1 Dormitorio Sin Expensas Sin Mascotas',
            provider='mercadolibre')
        self.assertDictEqual(expected_property.__dict__, result[0].__dict__)

    @patch('providers.Mercadolibre.request')
    def test_paging_with_filter(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, self.example_page, self.example_page, '']
        cfg = {
            'base_url': 'https://inmuebles.mercadolibre.com.ar',
            'sources': ['/alquiler/_PriceRange_0ARS-50000ARS'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Mercadolibre(cfg).props()))
        request_mock.assert_has_calls([
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_PriceRange_0ARS-50000ARS_NoIndex_True'),
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_Desde_49_PriceRange_0ARS-50000ARS_NoIndex_True'),
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_Desde_97_PriceRange_0ARS-50000ARS_NoIndex_True'),
            call('https://inmuebles.mercadolibre.com.ar/alquiler/_Desde_145_PriceRange_0ARS-50000ARS_NoIndex_True'),
        ])
        self.assertEqual(48 * 3, len(result))


if __name__ == '__main__':
    main()
