import asyncio

from providers import Property, Inmobusqueda
from typing import AsyncIterable, List
from unittest import main, TestCase
from unittest.mock import call, patch, AsyncMock


class TestInmobusqueda(TestCase):
    example_page: str

    @classmethod
    def setUpClass(cls) -> None:
        with open('tests/examples/inmobusqueda.html') as file:
            cls.example_page = file.read()
        return super().setUpClass()

    @staticmethod
    async def get_prop_list(props: AsyncIterable[Property]) -> List[Property]:
        return [prop async for prop in props]

    @patch('providers.Inmobusqueda.request')
    def test_empty_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.inmobusqueda.com.ar',
            'sources': [],
        }
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_prop_list(Inmobusqueda(cfg).props()))
        request_mock.assert_not_called()

    @patch('providers.Inmobusqueda.request')
    def test_multiple_sources(self, request_mock: AsyncMock) -> None:
        request_mock.return_value = ''
        cfg = {
            'base_url': 'https://www.inmobusqueda.com.ar',
            'sources': ['/departamento-venta.html', '/departamento-alquiler.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Inmobusqueda(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.inmobusqueda.com.ar/departamento-alquiler.html'),
            call('https://www.inmobusqueda.com.ar/departamento-venta.html'),
        ], any_order=True)
        self.assertEqual(0, len(result))

    @patch('providers.Inmobusqueda.request')
    def test_element_processing(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, '']
        cfg = {
            'base_url': 'https://www.inmobusqueda.com.ar',
            'sources': ['/departamento.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Inmobusqueda(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.inmobusqueda.com.ar/departamento.html'),
            call('https://www.inmobusqueda.com.ar/departamento-pagina-2.html'),
        ])
        self.assertEqual(18, len(result))
        expected_property = Property(
            url='https://www.inmobusqueda.com.ar/ficha.verdestacado.php?'
                'id=200769&pos=1&ppv=900&lp=0&hash=c5f1a18b08316b25e4cdbfcadbf167f24f3049dd&rd=1684979823',
            internal_id='IB-200769',
            title='Departamento en Alquiler $40.000',
            provider='inmobusqueda')
        self.assertDictEqual(expected_property.__dict__, result[0].__dict__)

    @patch('providers.Inmobusqueda.request')
    def test_paging(self, request_mock: AsyncMock) -> None:
        request_mock.side_effect = [self.example_page, self.example_page, self.example_page, '']
        cfg = {
            'base_url': 'https://www.inmobusqueda.com.ar',
            'sources': ['/departamento.html'],
        }
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.get_prop_list(Inmobusqueda(cfg).props()))
        request_mock.assert_has_calls([
            call('https://www.inmobusqueda.com.ar/departamento.html'),
            call('https://www.inmobusqueda.com.ar/departamento-pagina-2.html'),
            call('https://www.inmobusqueda.com.ar/departamento-pagina-3.html'),
            call('https://www.inmobusqueda.com.ar/departamento-pagina-4.html'),
        ])
        self.assertEqual(18 * 3, len(result))


if __name__ == '__main__':
    main()
