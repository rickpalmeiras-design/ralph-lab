# Receita mensal por região

Pipeline em Python (só biblioteca padrão, sem dependências) que cruza `data/vendas.csv` com
`data/lojas.csv`, gera o pivot de receita mensal por região e publica uma página estática com
gráfico e conclusão.

## Gerar os arquivos

```
python build.py
```

Gera, na raiz do projeto e nesta ordem: `vendas_lojas.csv` (join), `pivot_receita.csv` (pivot) e
`index.html` (página). A saída é determinística: rodar duas vezes produz arquivos idênticos.

## Rodar os testes

```
python -m unittest discover tests
python -m compileall -q .
```

## Abrir a página

Dê duplo clique em `index.html` (ou abra o arquivo no navegador). A página é autocontida e
funciona offline.
