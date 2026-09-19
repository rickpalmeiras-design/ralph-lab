# PRD: Receita Mensal por Região (join, pivot e página estática)

## Introdução / Visão Geral

O repositório contém duas tabelas em `data/`: `vendas.csv` (423 vendas, jan–jun/2026) e `lojas.csv` (8 lojas com região). Hoje não existe visão consolidada de receita por região.

Este projeto cria um pipeline pequeno e reproduzível em três etapas:

1. **Join interno** de vendas com lojas por `id_loja`, gerando `vendas_lojas.csv`.
2. **Pivot** da receita mensal por região, gerando `pivot_receita.csv`.
3. **Página estática** `index.html` com gráfico da receita mensal por região e um parágrafo de conclusão.

Uma suíte de testes automatizados em `tests/` valida cada etapa contra valores de conferência já verificados nos dados reais.

### Fatos dos dados (verificados em 2026-09-19)

| Item | Valor |
|---|---|
| Linhas em `vendas.csv` | 423 (60 vendas para cada loja 101–107 + 3 vendas com `id_loja=999`) |
| Vendas órfãs (`id_loja=999`) | 3 vendas: V00421, V00422, V00423. Receita somada R$ 8.120,00 |
| Loja sem vendas | 108 – Batel (Sul/PR) |
| Linhas após join interno | **420** |
| Receita total após join interno | **R$ 931.274,06** (bruto com órfãs seria R$ 939.394,06) |
| Receita por região (após join) | Sudeste 265.077,49 · Nordeste 261.862,76 · Centro-Oeste 258.323,97 · Sul 146.009,84 |
| Região líder | **Sudeste, R$ 265.077,49** |
| Meses presentes | 2026-01 a 2026-06 (6 meses) |
| Regiões | Centro-Oeste, Nordeste, Sudeste, Sul (4 regiões) |

Colunas de `vendas.csv`: `id_venda,data,id_loja,categoria,unidades,receita_brl`.
Colunas de `lojas.csv`: `id_loja,nome_loja,regiao,uf,gerente`.

## Objetivos

- Produzir `vendas_lojas.csv` com exatamente 420 linhas de dados, sem perder nem duplicar vendas válidas.
- Produzir `pivot_receita.csv` com o formato exato exigido (cabeçalho, 4 linhas de dados, 7 colunas, números limpos).
- Publicar `index.html` autocontida (abre com duplo clique, sem servidor e sem internet) com gráfico e conclusão.
- Garantir, por testes automatizados, os valores de conferência: 420 linhas, R$ 931.274,06 e Sudeste líder com R$ 265.077,49.
- Executar tudo com um único comando, usando somente a biblioteca padrão do Python.

## Histórias de Usuário

### US-001: Join interno de vendas com lojas
**Descrição:** Como analista, quero cruzar `data/vendas.csv` com `data/lojas.csv` por `id_loja` para ter cada venda enriquecida com nome da loja, região, UF e gerente.

**Critérios de Aceitação:**
- [ ] Existe um módulo Python (ex.: `pipeline.py`) com função que lê os dois CSVs em UTF-8 e faz o join interno por `id_loja`
- [ ] `vendas_lojas.csv` é gerado na raiz do projeto, em UTF-8, com cabeçalho `id_venda,data,id_loja,categoria,unidades,receita_brl,nome_loja,regiao,uf,gerente`
- [ ] `vendas_lojas.csv` tem exatamente 420 linhas de dados (421 contando o cabeçalho)
- [ ] As 3 vendas com `id_loja=999` (V00421, V00422, V00423) NÃO aparecem no arquivo de saída
- [ ] Nenhuma venda aparece duplicada (`id_venda` único no resultado)
- [ ] `receita_brl` é lida com `decimal.Decimal` (nunca `float`) e escrita com 2 casas decimais
- [ ] A execução imprime no stdout um resumo: linhas lidas, linhas no join, quantidade e receita das órfãs descartadas (3 vendas, R$ 8.120,00) e lojas sem vendas (108 – Batel)
- [ ] Teste automatizado: número de linhas do join = 420
- [ ] Teste automatizado: soma de `receita_brl` de `vendas_lojas.csv` = 931274.06
- [ ] Os testes passam (`python -m unittest discover tests`)

### US-002: Pivot de receita mensal por região
**Descrição:** Como analista, quero uma tabela região × mês com a receita para comparar regiões rapidamente.

**Critérios de Aceitação:**
- [ ] A função de pivot lê `vendas_lojas.csv` (não os CSVs originais) e agrupa por `regiao` e mês (`YYYY-MM` extraído de `data`)
- [ ] `pivot_receita.csv` é gerado na raiz, em UTF-8
- [ ] Cabeçalho exato, na primeira linha: `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`
- [ ] Exatamente 4 linhas de dados, uma por região, em ordem alfabética: Centro-Oeste, Nordeste, Sudeste, Sul (5 linhas contando o cabeçalho)
- [ ] Toda linha tem exatamente 7 colunas
- [ ] Todo valor numérico usa ponto decimal e exatamente 2 casas (ex.: `44144.42`, e `0.00` para célula sem vendas)
- [ ] Nenhum valor contém `R$`, espaço, vírgula decimal ou separador de milhar
- [ ] Soma de todas as células do pivot = 931274.06
- [ ] Soma da linha Sudeste = 265077.49, e Sudeste é a região com maior soma
- [ ] Teste automatizado: formato do pivot (cabeçalho exato, 4 linhas, 7 colunas, regex `^\d+\.\d{2}$` em cada valor)
- [ ] Teste automatizado: região líder é Sudeste com 265077.49
- [ ] Os testes passam

### US-003: Página estática com gráfico da receita mensal por região
**Descrição:** Como gestor, quero abrir uma página e ver a evolução mensal da receita de cada região.

**Critérios de Aceitação:**
- [ ] `index.html` é gerada na raiz a partir de `pivot_receita.csv` por um script Python
- [ ] A página é autocontida: sem CDN, sem fontes ou scripts externos. O gráfico é um `<svg>` inline (ou `<canvas>` desenhado por JS inline)
- [ ] O gráfico mostra as 4 regiões (uma série por região) ao longo dos 6 meses (2026-01 a 2026-06), com eixos, rótulos de mês e legenda identificando cada região
- [ ] O eixo de valores é legível em reais (formato pt-BR permitido apenas na página, por exemplo `R$ 40 mil`)
- [ ] O gráfico tem elemento identificável para teste, com `id="grafico-receita"`, e texto alternativo (`<title>`/`aria-label`)
- [ ] `<html lang="pt-BR">`, `<meta charset="utf-8">`, `<title>` descritivo e layout responsivo (sem rolagem horizontal em 375 px de largura)
- [ ] Cores das séries distinguíveis entre si e com contraste suficiente sobre o fundo
- [ ] Teste automatizado: `index.html` contém o elemento do gráfico (`id="grafico-receita"` dentro de um `<svg` ou `<canvas`)
- [ ] Os testes passam
- [ ] Verificar no navegador usando a skill dev-browser

### US-004: Parágrafo de conclusão
**Descrição:** Como gestor, quero um texto curto que interprete o gráfico, para não precisar analisar os números sozinho.

**Critérios de Aceitação:**
- [ ] `index.html` tem um único `<p id="conclusao">` logo abaixo do gráfico
- [ ] O texto do parágrafo (sem tags HTML) tem no mínimo 300 caracteres
- [ ] O texto é gerado a partir dos dados do pivot, sem números escritos à mão
- [ ] O texto cita a região líder (Sudeste) e sua receita no período (R$ 265.077,49, formato pt-BR)
- [ ] O texto cita a região de menor receita (Sul, R$ 146.009,84) e explica a causa provável: apenas a loja 107 vendeu; a loja 108 (Batel) não teve vendas
- [ ] O texto informa a ressalva de que 3 vendas órfãs (`id_loja=999`, R$ 8.120,00) ficaram fora da análise
- [ ] Teste automatizado: o parágrafo `#conclusao` existe e tem ≥ 300 caracteres
- [ ] Os testes passam
- [ ] Verificar no navegador usando a skill dev-browser

### US-005: Ponto de entrada único e execução ponta a ponta
**Descrição:** Como desenvolvedor, quero um único comando que regenere todos os artefatos, para reproduzir o resultado sem passos manuais.

**Critérios de Aceitação:**
- [ ] `python build.py` executa join → pivot → HTML nessa ordem e gera `vendas_lojas.csv`, `pivot_receita.csv` e `index.html`
- [ ] Rodar o comando duas vezes seguidas produz arquivos idênticos (idempotente, sem timestamps na saída)
- [ ] Os testes rodam com `python -m unittest discover tests` a partir da raiz, sem instalar dependências
- [ ] A suíte tem no mínimo 4 testes e todos passam: linhas do join, receita total, formato do pivot, gráfico na página
- [ ] `README.md` curto explica como gerar os arquivos, rodar os testes e abrir `index.html`
- [ ] Os artefatos gerados são commitados junto com o código

## Requisitos Funcionais

- **FR-1:** O sistema deve ler `data/vendas.csv` e `data/lojas.csv` em UTF-8.
- **FR-2:** O sistema deve fazer o join interno por `id_loja`, comparando os ids como texto (string) nos dois lados.
- **FR-3:** Vendas cujo `id_loja` não existe em `lojas.csv` (hoje, `999`) devem ser excluídas do resultado e reportadas no stdout (contagem e receita somada). O programa não deve falhar por causa delas.
- **FR-4:** Lojas sem nenhuma venda (hoje, 108 – Batel) não aparecem em `vendas_lojas.csv` e devem ser listadas no stdout como informação.
- **FR-5:** `vendas_lojas.csv` deve conter todas as colunas de `vendas.csv` seguidas de `nome_loja,regiao,uf,gerente`, preservando a ordem original das vendas.
- **FR-6:** Todos os cálculos monetários devem usar `Decimal`. Soma com `float` é proibida.
- **FR-7:** `pivot_receita.csv` deve ter o cabeçalho exato `regiao,2026-01,2026-02,2026-03,2026-04,2026-05,2026-06`, 4 linhas de dados e 7 colunas por linha.
- **FR-8:** Os valores do pivot devem ter ponto decimal, exatamente 2 casas, sem símbolo de moeda e sem separador de milhar. Combinação região × mês sem vendas deve valer `0.00`.
- **FR-9:** Os meses do cabeçalho do pivot devem ser os 6 meses fixos pedidos. Uma venda fora desses meses faz o programa falhar com mensagem clara, em vez de ser ignorada em silêncio.
- **FR-10:** `index.html` deve ser gerada por script a partir dos dados do pivot e conter o gráfico e o parágrafo de conclusão.
- **FR-11:** O gráfico deve mostrar a receita mensal de cada região, com legenda, eixos e rótulos.
- **FR-12:** O parágrafo de conclusão deve ter ≥ 300 caracteres e ser derivado dos dados (líder, menor região, ressalvas).
- **FR-13:** `tests/` deve conter no mínimo 4 testes automatizados cobrindo: linhas do join (420), receita total (931274.06), formato do pivot, presença do gráfico em `index.html`.
- **FR-14:** Os testes devem rodar sobre os arquivos gerados a partir dos dados reais e usar os valores de conferência deste PRD.

## Fora de Escopo (Non-Goals)

- Sem dependências externas (pandas, matplotlib, Chart.js via CDN etc.) nem servidor web.
- Sem interatividade avançada (filtros, dropdowns, download), apenas tooltips simples se for barato.
- Sem correção ou imputação das vendas órfãs (não tentar adivinhar a loja de `id_loja=999`).
- Sem loja 108 (Batel) como linha zerada no join. Ela só é citada como informação.
- Sem análise por categoria, loja, gerente ou UF, apenas região × mês.
- Sem deploy, CI ou hospedagem.
- Sem novos dados de entrada nem alteração em `data/*.csv`.

## Considerações de Design

- Idioma da página: português do Brasil. Formato monetário pt-BR (`R$ 265.077,49`) só no HTML. Nos CSVs, apenas números puros.
- Gráfico de linhas com 4 séries (tendência mensal por região) ou barras agrupadas. O importante é a legibilidade dos 24 pontos. Preferir rótulos diretos ou legenda clara, e não depender só de cor.
- Se for construir o gráfico, seguir a skill `dataviz` para paleta, eixos e modo claro/escuro.
- Página simples: título, gráfico, parágrafo de conclusão e rodapé com a fonte dos dados.

## Considerações Técnicas

- **Stack:** Python 3 (3.14 disponível no ambiente) só com biblioteca padrão: `csv`, `decimal`, `pathlib`, `unittest`, `html`.
- **Estrutura sugerida:**
  ```
  data/vendas.csv, data/lojas.csv    (entrada, não alterar)
  pipeline.py                        (join, pivot, geração do HTML)
  build.py                           (ponto de entrada)
  vendas_lojas.csv                   (saída 1)
  pivot_receita.csv                  (saída 2)
  index.html                         (saída 3)
  tests/test_join.py, test_pivot.py, test_pagina.py
  README.md
  ```
- **Windows:** ao escrever CSV, usar `newline=""` e `encoding="utf-8"` para evitar linhas em branco e terminador `\r\n` inconsistente. Fixar `lineterminator="\n"` para saída idêntica entre plataformas.
- **Arredondamento:** os valores já têm 2 casas. Formatar com `f"{valor:.2f}"` sobre `Decimal`. Nunca passar por `float`.
- **Ordem determinística:** regiões em ordem alfabética e vendas na ordem original, para saída idempotente.

## Métricas de Sucesso

- `python -m unittest discover tests` passa com ≥ 4 testes e 0 falhas.
- `vendas_lojas.csv`: 420 linhas de dados. Receita total = 931274.06.
- `pivot_receita.csv`: cabeçalho exato, 4 linhas, 7 colunas, região líder Sudeste = 265077.49.
- `index.html` abre offline, mostra o gráfico com as 4 regiões e 6 meses, e a conclusão tem ≥ 300 caracteres.
- `python build.py` roda duas vezes com saída idêntica (diff vazio).

## Questões em Aberto

Premissas adotadas por padrão. Podem ser ajustadas antes da implementação:

1. **Stack:** assumido Python sem dependências. Se preferir pandas ou Node, a estrutura muda.
2. **Tipo de gráfico:** assumido gráfico de linhas em SVG inline. Alternativa: barras agrupadas ou Chart.js via CDN (exigiria internet).
3. **Vendas órfãs:** assumido descarte com relatório no stdout. Alternativa: gravar também um `vendas_orfas.csv` para auditoria.
4. **Ordem das regiões no pivot:** assumida alfabética. Alternativa: por receita total decrescente (Sudeste, Nordeste, Centro-Oeste, Sul).
5. **Local dos artefatos:** assumidos na raiz do projeto, conforme os nomes dados no pedido.
