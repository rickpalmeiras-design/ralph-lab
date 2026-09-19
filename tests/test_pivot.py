import contextlib
import csv
import io
import re
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pipeline  # noqa: E402

CABECALHO = "regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06"


class TestPivot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.executar_join()
        pipeline.executar_pivot()
        with open(pipeline.PIVOT_CSV, encoding="utf-8", newline="") as f:
            cls.texto = f.read()
        cls.linhas = list(csv.reader(io.StringIO(cls.texto, newline="")))

    def test_formato(self):
        self.assertEqual(self.linhas[0], CABECALHO.split(","))
        dados = self.linhas[1:]
        self.assertEqual([l[0] for l in dados], ["Centro-Oeste", "Nordeste", "Sudeste", "Sul"])
        for linha in dados:
            self.assertEqual(len(linha), 7)
            for valor in linha[1:]:
                self.assertRegex(valor, r"^\d+\.\d{2}$")
        self.assertNotIn("\r", self.texto)

    def test_soma_total(self):
        total = sum((Decimal(v) for l in self.linhas[1:] for v in l[1:]), Decimal("0"))
        self.assertEqual(total, Decimal("931274.06"))

    def test_regiao_lider(self):
        somas = {
            l[0]: sum((Decimal(v) for v in l[1:]), Decimal("0")) for l in self.linhas[1:]
        }
        lider = max(somas, key=somas.get)
        self.assertEqual(lider, "Sudeste")
        self.assertEqual(somas[lider], Decimal("265077.49"))

    def test_mes_fora_do_cabecalho_falha(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = Path(tmp) / "vendas_lojas.csv"
            caminho.write_text(
                ",".join(pipeline.CABECALHO_JOIN) + "\n"
                "V99999,2026-07-01,101,Bebidas,1,10.00,Asa Norte,Centro-Oeste,DF,Marina Alves\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "V99999.*2026-07"):
                pipeline.calcular_pivot(caminho)


if __name__ == "__main__":
    unittest.main()
