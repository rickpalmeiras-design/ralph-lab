"""Pipeline de receita mensal por região (somente biblioteca padrão)."""

import csv
import sys
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENDAS_CSV = RAIZ / "data" / "vendas.csv"
LOJAS_CSV = RAIZ / "data" / "lojas.csv"
VENDAS_LOJAS_CSV = RAIZ / "vendas_lojas.csv"

CAMPOS_LOJA = ["nome_loja", "regiao", "uf", "gerente"]
CABECALHO_JOIN = [
    "id_venda",
    "data",
    "id_loja",
    "categoria",
    "unidades",
    "receita_brl",
    *CAMPOS_LOJA,
]


def formatar_brl(valor):
    """Formata um Decimal no padrão pt-BR, ex.: R$ 8.120,00."""
    inteiro, centavos = f"{valor:.2f}".split(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {inteiro},{centavos}"


def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def juntar_vendas_lojas(vendas_csv=VENDAS_CSV, lojas_csv=LOJAS_CSV):
    """Join interno de vendas com lojas por id_loja (comparado como string).

    Retorna (linhas_join, vendas_lidas, orfas, lojas_sem_vendas), onde as
    linhas do join mantêm a ordem original das vendas e receita_brl é Decimal.
    """
    vendas = ler_csv(vendas_csv)
    lojas = {loja["id_loja"]: loja for loja in ler_csv(lojas_csv)}

    linhas, orfas, lojas_com_vendas = [], [], set()
    for venda in vendas:
        loja = lojas.get(venda["id_loja"])
        if loja is None:
            orfas.append(venda)
            continue
        lojas_com_vendas.add(venda["id_loja"])
        linha = dict(venda)
        linha["receita_brl"] = Decimal(venda["receita_brl"])
        for campo in CAMPOS_LOJA:
            linha[campo] = loja[campo]
        linhas.append(linha)

    lojas_sem_vendas = [l for id_loja, l in lojas.items() if id_loja not in lojas_com_vendas]
    return linhas, len(vendas), orfas, lojas_sem_vendas


def escrever_vendas_lojas(linhas, destino=VENDAS_LOJAS_CSV):
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(CABECALHO_JOIN)
        for linha in linhas:
            saida = dict(linha)
            saida["receita_brl"] = f"{linha['receita_brl']:.2f}"
            escritor.writerow([saida[campo] for campo in CABECALHO_JOIN])


def executar_join():
    linhas, lidas, orfas, lojas_sem_vendas = juntar_vendas_lojas()
    escrever_vendas_lojas(linhas)

    receita_orfas = sum((Decimal(o["receita_brl"]) for o in orfas), Decimal("0"))
    sem_vendas = ", ".join(f"{l['id_loja']} - {l['nome_loja']}" for l in lojas_sem_vendas)
    print(f"Linhas lidas: {lidas}")
    print(f"Linhas no join: {len(linhas)}")
    print(f"Órfãs descartadas: {len(orfas)} vendas, {formatar_brl(receita_orfas)}")
    print(f"Lojas sem vendas: {sem_vendas or 'nenhuma'}")
    return linhas


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    executar_join()
