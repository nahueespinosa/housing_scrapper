import asyncio

from providers import Property, Properati
from typing import AsyncIterable, List
from unittest import main, TestCase
from unittest.mock import call, patch, AsyncMock


class TestProperati(TestCase):
    example_page: str

    @classmethod
    def setUpClass(cls) -> None:
        with open('tests/examples/properati.html') as file:
            cls.example_page = file.read()
        return super().setUpClass()

    @staticmethod
    async def get_prop_list(props: AsyncIterable[Property]) -> List[Property]:
        return [prop async for prop in props]

    @patch('providers.Properati.request')
    def test_empty_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.properati.com.ar',
            'sources': [],
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_prop_list(Properati(cfg).props()))
        request_mock.assert_not_called()

    @patch('providers.Properati.request')
    def test_multiple_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.properati.com.ar',
            'sources': ['/s/capital-federal/alquiler', '/s/capital-federal/venta'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Properati(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.properati.com.ar/s/capital-federal/alquiler'),
            call('https://www.properati.com.ar/s/capital-federal/venta'),
        ], any_order=True)
        self.assertEqual(0, len(result))

    @patch('providers.Properati.request')
    def test_element_processing(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, '']
        cfg = {
            'base_url': 'https://www.properati.com.ar',
            'sources': ['/s/alquiler'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Properati(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.properati.com.ar/s/alquiler'),
            call('https://www.properati.com.ar/s/alquiler?page=2'),
        ])
        self.assertEqual(30, len(result))
        expected_property = Property(
            url='https://www.properati.com.ar/detalle/48ykj_alquiler_departamento_villa-devoto_hpjt',
            internal_id='48ykj',
            title='Departamento en Villa Devoto $ 60.000',
            provider='properati')
        self.assertDictEqual(expected_property.__dict__, result[0].__dict__)

    @patch('providers.Properati.request')
    def test_paging(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, self.example_page, self.example_page, '']
        cfg = {
            'base_url': 'https://www.properati.com.ar',
            'sources': ['/s/alquiler'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Properati(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.properati.com.ar/s/alquiler'),
            call('https://www.properati.com.ar/s/alquiler?page=2'),
            call('https://www.properati.com.ar/s/alquiler?page=3'),
            call('https://www.properati.com.ar/s/alquiler?page=4'),
        ])
        self.assertEqual(30 * 3, len(result))


if __name__ == '__main__':
    main()
