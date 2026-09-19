import contextlib
import html
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

    def test_conclusao(self):
        paragrafos = re.findall(r'<p id="conclusao">(.*?)</p>', self.html, re.DOTALL)
        self.assertEqual(len(paragrafos), 1)
        texto = html.unescape(re.sub(r"<[^>]+>", "", paragrafos[0]))
        self.assertGreaterEqual(len(texto), 300)
        # o parágrafo vem logo abaixo do gráfico
        self.assertRegex(self.html, r'</svg>\s*<p id="conclusao">')
        self.assertIn("Sudeste", texto)
        self.assertIn("R$ 265.077,49", texto)
        self.assertIn("Sul", texto)
        self.assertIn("R$ 146.009,84", texto)
        self.assertIn("apenas a loja 107", texto)
        self.assertIn("loja 108 (Batel) não teve vendas", texto)
        self.assertIn("3 vendas órfãs (id_loja=999, R$ 8.120,00)", texto)


if __name__ == "__main__":
    unittest.main()
