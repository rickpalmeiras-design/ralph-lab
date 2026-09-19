"""Ponto de entrada único: gera vendas_lojas.csv, pivot_receita.csv e index.html."""
import sys

import pipeline


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    pipeline.executar_join()
    pipeline.executar_pivot()
    pipeline.gerar_html()


if __name__ == "__main__":
    main()
