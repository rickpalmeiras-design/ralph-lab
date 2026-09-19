"""Pipeline de receita mensal por região (somente biblioteca padrão)."""

import csv
import html
import math
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
VENDAS_CSV = RAIZ / "data" / "vendas.csv"
LOJAS_CSV = RAIZ / "data" / "lojas.csv"
VENDAS_LOJAS_CSV = RAIZ / "vendas_lojas.csv"
PIVOT_CSV = RAIZ / "pivot_receita.csv"
INDEX_HTML = RAIZ / "index.html"

MESES = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
NOMES_MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

# (cor, forma) por série: cores com contraste >= 3:1 sobre branco; a forma do marcador
# diferencia as séries também para quem não distingue cores.
ESTILOS_SERIES = [
    ("#1D4ED8", "circulo"),
    ("#B45309", "quadrado"),
    ("#0F766E", "triangulo"),
    ("#A21CAF", "losango"),
]

MODELO_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Receita mensal por região — {periodo}</title>
<style>
  body {{ margin: 0; padding: 16px; background: #ffffff; color: #1f2937;
         font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 4px; }}
  .subtitulo {{ margin: 0 0 16px; color: #4b5563; }}
  svg {{ display: block; width: 100%; height: auto; }}
  svg .grade {{ stroke: #e5e7eb; stroke-width: 1; }}
  svg .eixo {{ stroke: #6b7280; stroke-width: 1; }}
  svg text {{ font-family: inherit; font-size: 14px; }}
  svg .rotulo {{ fill: #374151; }}
  svg .legenda {{ fill: #111827; }}
  #conclusao {{ margin: 16px 0 0; line-height: 1.6; }}
</style>
</head>
<body>
<main>
<h1>Receita mensal por região</h1>
<p class="subtitulo">{periodo}, em reais (R$)</p>
{grafico}
<p id="conclusao">{conclusao}</p>
</main>
</body>
</html>
"""

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


def calcular_pivot(vendas_lojas_csv=VENDAS_LOJAS_CSV, meses=MESES):
    """Soma receita_brl por região e mês (YYYY-MM da coluna data), lendo o CSV do join.

    Retorna {regiao: {mes: Decimal}} com todos os meses do cabeçalho
    preenchidos (0 quando não há vendas). Falha com ValueError se alguma
    venda cair fora de `meses`, em vez de ignorá-la.
    """
    pivot = {}
    for linha in ler_csv(vendas_lojas_csv):
        mes = linha["data"][:7]
        if mes not in meses:
            raise ValueError(
                f"Venda {linha['id_venda']} tem mês {mes} (data {linha['data']}) "
                f"fora dos meses do pivot: {', '.join(meses)}"
            )
        por_mes = pivot.setdefault(linha["regiao"], dict.fromkeys(meses, Decimal("0")))
        por_mes[mes] += Decimal(linha["receita_brl"])
    return pivot


def escrever_pivot(pivot, destino=PIVOT_CSV, meses=MESES):
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["regiao", *meses])
        for regiao in sorted(pivot):
            escritor.writerow([regiao, *(f"{pivot[regiao][mes]:.2f}" for mes in meses)])


def executar_pivot():
    pivot = calcular_pivot()
    escrever_pivot(pivot)
    return pivot


def ler_pivot(pivot_csv=PIVOT_CSV):
    """Lê pivot_receita.csv e devolve (meses, {regiao: [Decimal por mês]}), na ordem do arquivo."""
    with open(pivot_csv, encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        meses = next(leitor)[1:]
        series = {linha[0]: [Decimal(v) for v in linha[1:]] for linha in leitor}
    return meses, series


def rotulo_mes(mes):
    """'2026-01' -> 'jan/26'."""
    ano, numero = mes.split("-")
    return f"{NOMES_MESES[int(numero) - 1]}/{ano[2:]}"


def passo_do_eixo(maximo, max_divisoes=6):
    """Menor passo redondo (1, 2 ou 5 × 10^n, mínimo 1000) com no máximo max_divisoes divisões."""
    potencia = 1000
    while True:
        for multiplo in (1, 2, 5):
            passo = potencia * multiplo
            if math.ceil(maximo / passo) <= max_divisoes:
                return passo
        potencia *= 10


def marcador_svg(forma, x, y, cor, titulo):
    """Marcador de ponto (forma distinta por série, para não depender só da cor)."""
    r = 4.5
    dica = f"<title>{titulo}</title>"
    if forma == "circulo":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{cor}">{dica}</circle>'
    if forma == "quadrado":
        return (
            f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r}" height="{2 * r}" '
            f'fill="{cor}">{dica}</rect>'
        )
    if forma == "triangulo":
        pontos = [(x, y - r - 1), (x + r + 1, y + r), (x - r - 1, y + r)]
    else:
        pontos = [(x, y - r - 1), (x + r + 1, y), (x, y + r + 1), (x - r - 1, y)]
    texto = " ".join(f"{px:.1f},{py:.1f}" for px, py in pontos)
    return f'<polygon points="{texto}" fill="{cor}">{dica}</polygon>'


def montar_grafico_svg(meses, series):
    """Gráfico de linhas (região × mês) como <svg> inline; todos os valores vêm do pivot."""
    largura, altura = 480, 400
    esq, dir_, topo, base = 76, 16, 16, 300
    area_l = largura - esq - dir_
    area_a = base - topo

    maximo = max(v for valores in series.values() for v in valores)
    passo = passo_do_eixo(maximo)
    limite = math.ceil(maximo / passo) * passo

    def pos_x(i):
        return esq + area_l * (i + 0.5) / len(meses)

    def pos_y(valor):
        return base - area_a * float(valor / limite)

    partes = []
    for valor in range(0, int(limite) + 1, passo):
        y = pos_y(Decimal(valor))
        rotulo = "R$ 0" if valor == 0 else f"R$ {valor // 1000} mil"
        partes.append(
            f'<line class="grade" x1="{esq}" y1="{y:.1f}" x2="{largura - dir_}" y2="{y:.1f}"/>'
            f'<text class="rotulo" x="{esq - 8}" y="{y + 4:.1f}" text-anchor="end">{rotulo}</text>'
        )
    partes.append(f'<line class="eixo" x1="{esq}" y1="{base}" x2="{largura - dir_}" y2="{base}"/>')
    partes.append(f'<line class="eixo" x1="{esq}" y1="{topo}" x2="{esq}" y2="{base}"/>')
    for i, mes in enumerate(meses):
        partes.append(
            f'<text class="rotulo" x="{pos_x(i):.1f}" y="{base + 20}" text-anchor="middle">'
            f"{rotulo_mes(mes)}</text>"
        )

    colunas_legenda = 2
    for n, (regiao, valores) in enumerate(series.items()):
        cor, forma = ESTILOS_SERIES[n % len(ESTILOS_SERIES)]
        nome = html.escape(regiao)
        pontos = " ".join(f"{pos_x(i):.1f},{pos_y(v):.1f}" for i, v in enumerate(valores))
        partes.append(
            f'<polyline points="{pontos}" fill="none" stroke="{cor}" stroke-width="2.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i, v in enumerate(valores):
            titulo = f"{nome}, {rotulo_mes(meses[i])}: {formatar_brl(v)}"
            partes.append(marcador_svg(forma, pos_x(i), pos_y(v), cor, titulo))
        lx = esq + (area_l / colunas_legenda) * (n % colunas_legenda)
        ly = base + 56 + 24 * (n // colunas_legenda)
        partes.append(
            f'<line x1="{lx:.1f}" y1="{ly}" x2="{lx + 18:.1f}" y2="{ly}" '
            f'stroke="{cor}" stroke-width="2.5"/>'
            + marcador_svg(forma, lx + 9, ly, cor, nome)
            + f'<text class="legenda" x="{lx + 26:.1f}" y="{ly + 4}">{nome}</text>'
        )

    descricao = (
        f"Gráfico de linhas da receita mensal em reais de {len(series)} regiões "
        f"({', '.join(html.escape(r) for r in series)}), de {rotulo_mes(meses[0])} "
        f"a {rotulo_mes(meses[-1])}"
    )
    return (
        f'<svg id="grafico-receita" viewBox="0 0 {largura} {altura}" role="img" '
        f'aria-label="{descricao}" xmlns="http://www.w3.org/2000/svg">'
        f"<title>{descricao}</title>" + "".join(partes) + "</svg>"
    )


def montar_conclusao(meses, series, linhas_join, orfas, lojas_sem_vendas):
    """Parágrafo de conclusão (texto puro) derivado do pivot, do join e das órfãs; sem números fixos."""
    totais = {regiao: sum(valores, Decimal("0")) for regiao, valores in series.items()}
    ranking = sorted(totais, key=lambda regiao: totais[regiao], reverse=True)
    lider, menor = ranking[0], ranking[-1]
    periodo = f"{rotulo_mes(meses[0])} a {rotulo_mes(meses[-1])}"

    frases = [
        f"No período de {periodo}, a região {lider} liderou a receita, com "
        f"{formatar_brl(totais[lider])} no total."
    ]
    if len(ranking) > 2:
        itens = [f"{r} ({formatar_brl(totais[r])})" for r in ranking[1:-1]]
        intermediarias = " e ".join([", ".join(itens[:-1]), itens[-1]] if len(itens) > 1 else itens)
        frases.append(f"Nas posições intermediárias ficaram {intermediarias}.")

    frases.append(
        f"A região de menor receita foi {menor}, com {formatar_brl(totais[menor])}, "
        f"a linha mais baixa do gráfico."
    )
    ativas = sorted({l["id_loja"] for l in linhas_join if l["regiao"] == menor})
    paradas = [l for l in lojas_sem_vendas if l["regiao"] == menor]
    if ativas and paradas:
        vendeu = " e ".join(f"a loja {id_loja}" for id_loja in ativas)
        sem_vendas = " e ".join(f"a loja {l['id_loja']} ({l['nome_loja']})" for l in paradas)
        frases.append(
            f"A causa provável é que apenas {vendeu} vendeu, enquanto {sem_vendas} "
            f"não teve vendas no período."
        )

    if orfas:
        ids = ", ".join(sorted({o["id_loja"] for o in orfas}))
        receita_orfas = sum((Decimal(o["receita_brl"]) for o in orfas), Decimal("0"))
        frases.append(
            f"Ressalva: {len(orfas)} vendas órfãs (id_loja={ids}, {formatar_brl(receita_orfas)}) "
            f"ficaram fora da análise por não terem loja cadastrada."
        )
    return " ".join(frases)


def gerar_html(pivot_csv=PIVOT_CSV, destino=INDEX_HTML):
    """Gera a página estática (autocontida, sem recursos externos) a partir do pivot."""
    meses, series = ler_pivot(pivot_csv)
    linhas_join, _, orfas, lojas_sem_vendas = juntar_vendas_lojas()
    grafico = montar_grafico_svg(meses, series)
    conclusao = html.escape(montar_conclusao(meses, series, linhas_join, orfas, lojas_sem_vendas))
    periodo = f"{rotulo_mes(meses[0])} a {rotulo_mes(meses[-1])}"
    pagina = MODELO_HTML.format(grafico=grafico, conclusao=conclusao, periodo=periodo)
    with open(destino, "w", encoding="utf-8", newline="") as f:
        f.write(pagina)


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
