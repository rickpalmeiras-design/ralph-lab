import contextlib
import csv
import io
import sys
import unittest
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pipeline  # noqa: E402


class TestJoin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            pipeline.executar_join()
        with open(pipeline.VENDAS_LOJAS_CSV, encoding="utf-8", newline="") as f:
            cls.linhas = list(csv.DictReader(f))

    def test_numero_de_linhas_do_join(self):
        self.assertEqual(len(self.linhas), 420)

    def test_soma_da_receita(self):
        total = sum((Decimal(l["receita_brl"]) for l in self.linhas), Decimal("0"))
        self.assertEqual(total, Decimal("931274.06"))

    def test_orfas_fora_e_ids_unicos(self):
        ids = [l["id_venda"] for l in self.linhas]
        self.assertEqual(len(ids), len(set(ids)))
        for orfa in ("V00421", "V00422", "V00423"):
            self.assertNotIn(orfa, ids)

    def test_cabecalho_exato(self):
        with open(pipeline.VENDAS_LOJAS_CSV, encoding="utf-8", newline="") as f:
            self.assertEqual(
                f.readline(),
                "id_venda,data,id_loja,categoria,unidades,receita_brl,nome_loja,regiao,uf,gerente\n",
            )


if __name__ == "__main__":
    unittest.main()
