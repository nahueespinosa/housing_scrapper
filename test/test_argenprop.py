import asyncio

from providers import Property, Argenprop
from typing import AsyncIterable, List
from unittest import main, TestCase
from unittest.mock import call, patch, AsyncMock


class TestArgenprop(TestCase):
    example_page: str

    @classmethod
    def setUpClass(cls) -> None:
        with open('test/examples/argenprop.html') as file:
            cls.example_page = file.read()
        return super().setUpClass()

    @staticmethod
    async def get_prop_list(props: AsyncIterable[Property]) -> List[Property]:
        return [prop async for prop in props]

    @patch('providers.Argenprop.request')
    def test_empty_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.argenprop.com',
            'sources': [],
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_prop_list(Argenprop(cfg).props()))
        request_mock.assert_not_called()

    @patch('providers.Argenprop.request')
    def test_multiple_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.argenprop.com',
            'sources': ['/departamento-venta', '/departamento-alquiler'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Argenprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.argenprop.com/departamento-alquiler'),
            call('https://www.argenprop.com/departamento-venta'),
        ], any_order=True)
        self.assertEqual(0, len(result))

    @patch('providers.Argenprop.request')
    def test_element_processing(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, '']
        cfg = {
            'base_url': 'https://www.argenprop.com',
            'sources': ['/departamento'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Argenprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.argenprop.com/departamento'),
            call('https://www.argenprop.com/departamento-pagina-1'),
        ])
        self.assertEqual(20, len(result))
        expected_property = Property(
            url='https://www.argenprop.com/departamento-en-venta-en-belgrano-c-3-ambientes--9774306',
            internal_id='9774306',
            title='IMPEC! Bcn c/vista abta T/luz y sol! T/externo! T/a nuevo! Excel '
                  'distrib! Lav! Bajas expensas! OPORT USD 145.000',
            provider='argenprop')
        self.assertDictEqual(expected_property.__dict__, result[0].__dict__)

    @patch('providers.Argenprop.request')
    def test_paging(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, self.example_page, self.example_page, '']
        cfg = {
            'base_url': 'https://www.argenprop.com',
            'sources': ['/departamento'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Argenprop(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.argenprop.com/departamento'),
            call('https://www.argenprop.com/departamento-pagina-1'),
            call('https://www.argenprop.com/departamento-pagina-2'),
            call('https://www.argenprop.com/departamento-pagina-3'),
        ])
        self.assertEqual(20 * 3, len(result))


if __name__ == '__main__':
    main()
