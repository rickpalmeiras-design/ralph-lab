import contextlib
import io
import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pipeline  # noqa: E402


class TestPagina(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.executar_join()
        pipeline.executar_pivot()
        pipeline.gerar_html()
        cls.html = pipeline.INDEX_HTML.read_text(encoding="utf-8")

    def test_grafico_svg(self):
        self.assertRegex(self.html, r'<svg[^>]*\bid="grafico-receita"')

    def test_estrutura_e_autocontida(self):
        self.assertIn('<html lang="pt-BR">', self.html)
        self.assertIn('<meta charset="utf-8">', self.html)
        self.assertIn('<meta name="viewport"', self.html)
        self.assertRegex(self.html, r"<title>[^<]+</title>")
        self.assertNotRegex(self.html, r"(?i)(src|href)=[\"']?https?:")
        self.assertNotIn("<script", self.html)

    def test_series_e_legenda(self):
        for regiao in ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"]:
            self.assertRegex(self.html, rf'class="legenda"[^>]*>{regiao}</text>')
        self.assertEqual(self.html.count("<polyline"), 4)
        self.assertRegex(self.html, r"R\$ \d+ mil")


if __name__ == "__main__":
    unittest.main()
