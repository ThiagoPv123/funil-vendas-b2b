import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Any

ETAPAS_ORDEM = ["Lead", "MQL", "SQL", "Proposta", "Negociação", "Fechado"]

BG_FIGURA = "#0D1117"
BG_PAINEL = "#161B22"
COR_AZUL = "#58A6FF"
COR_VERDE = "#3FB950"
COR_VERMELHO = "#F85149"
COR_AMARELO = "#D29922"
COR_ROXO = "#BC8CFF"
COR_TEXTO = "#E6EDF3"
COR_SUBTEXTO = "#8B949E"
COR_GRADE = "#21262D"


def _estilizar(ax):
    ax.set_facecolor(BG_PAINEL)
    ax.tick_params(colors=COR_SUBTEXTO, labelsize=8.5)
    for spine in ax.spines.values():
        spine.set_color(COR_GRADE)
    ax.title.set_color(COR_TEXTO)
    ax.title.set_fontsize(10.5)
    ax.title.set_fontweight("bold")
    ax.xaxis.label.set_color(COR_SUBTEXTO)
    ax.yaxis.label.set_color(COR_SUBTEXTO)
    ax.grid(axis="both", color=COR_GRADE, linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)


def gerar_dashboard(
    df: pd.DataFrame,
    ind: dict[str, Any],
    saida: str = "outputs/dashboard.png",
) -> None:
    fig = plt.figure(figsize=(22, 13))
    fig.patch.set_facecolor(BG_FIGURA)

    gs = gridspec.GridSpec(
        2, 3, figure=fig,
        hspace=0.50, wspace=0.38,
        left=0.05, right=0.97, top=0.88, bottom=0.07,
    )
    axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(3)]

    # --- 1. Funil (barras horizontais) ---
    ax = axes[0]
    _estilizar(ax)
    etapas = ETAPAS_ORDEM
    valores = [ind["leads_por_etapa"].get(e, 0) for e in etapas]
    cores = [COR_VERMELHO if e == "Proposta" else COR_AZUL for e in etapas]
    bars = ax.barh(etapas, valores, color=cores, edgecolor="none", height=0.55)
    ax.set_title("Funil de Vendas — leads por etapa")
    ax.set_xlabel("Nº de leads")
    ax.invert_yaxis()
    for bar, val in zip(bars, valores):
        ax.text(
            bar.get_width() + max(valores) * 0.02,
            bar.get_y() + bar.get_height() / 2,
            str(val), va="center", color=COR_TEXTO, fontsize=9,
        )
    ax.set_xlim(0, max(valores) * 1.25)
    ax.tick_params(axis="y", labelcolor=COR_TEXTO)

    # Anotação do gargalo
    gargalo_etapa = ind["gargalo"][0].split(" → ")[0]
    if gargalo_etapa in etapas:
        idx_g = etapas.index(gargalo_etapa)
        ax.annotate(
            f"  ← gargalo ({ind['gargalo'][1]}%)",
            xy=(valores[idx_g], idx_g),
            xytext=(valores[idx_g] + max(valores) * 0.02, idx_g),
            color=COR_VERMELHO, fontsize=8, va="center",
        )

    # --- 2. Evolução mensal ---
    ax = axes[1]
    _estilizar(ax)
    evo = ind["evolucao_mensal"]
    meses = evo["mes_entrada"].tolist()
    totais = evo["total_leads"].tolist()
    ganhos_mes = evo["ganhos"].tolist()
    x = np.arange(len(meses))
    ax.bar(x, totais, color=COR_AZUL, alpha=0.35, width=0.55, label="Total leads")
    ax.bar(x, ganhos_mes, color=COR_VERDE, alpha=0.9, width=0.55, label="Ganhos")
    ax.set_xticks(x)
    ax.set_xticklabels([m[-5:] for m in meses], rotation=30, color=COR_SUBTEXTO)
    ax.set_title("Evolução Mensal de Leads")
    ax.set_ylabel("Leads")
    leg = ax.legend(facecolor=BG_PAINEL, labelcolor=COR_TEXTO, fontsize=8, framealpha=0.8)
    leg.get_frame().set_edgecolor(COR_GRADE)

    # --- 3. Conversão por origem ---
    ax = axes[2]
    _estilizar(ax)
    origens = list(ind["conversao_origem"].keys())
    taxas = [ind["conversao_origem"][o]["taxa"] for o in origens]
    tots = [ind["conversao_origem"][o]["total"] for o in origens]
    cores_orig = [COR_VERDE if t == max(taxas) else
                  COR_VERMELHO if t == min(taxas) else COR_AZUL for t in taxas]
    bars = ax.bar(origens, taxas, color=cores_orig, edgecolor="none", width=0.5)
    ax.set_title("Taxa de Conversão por Origem (%)")
    ax.set_ylabel("Conversão (%)")
    for bar, taxa, tot in zip(bars, taxas, tots):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(taxas) * 0.03,
            f"{taxa}%\nn={tot}", ha="center", color=COR_TEXTO, fontsize=8.5,
        )
    ax.set_ylim(0, max(taxas) * 1.45)
    ax.tick_params(axis="x", labelcolor=COR_TEXTO)

    # --- 4. Tempo médio por etapa ---
    ax = axes[3]
    _estilizar(ax)
    etapas_t = [e for e in ETAPAS_ORDEM if e in ind["tempo_por_etapa"]]
    tempos = [ind["tempo_por_etapa"][e] for e in etapas_t]
    max_t = max(tempos) if tempos else 1
    cores_t = [COR_AMARELO if t == max_t else COR_AZUL for t in tempos]
    bars = ax.bar(etapas_t, tempos, color=cores_t, edgecolor="none", width=0.5)
    ax.set_title("Tempo Médio no Funil por Etapa (dias)")
    ax.set_ylabel("Dias")
    ax.set_xticks(range(len(etapas_t)))
    ax.set_xticklabels(etapas_t, rotation=20, color=COR_TEXTO)
    for bar, t in zip(bars, tempos):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max_t * 0.02,
            f"{t:.0f}d", ha="center", color=COR_TEXTO, fontsize=9,
        )

    # --- 5. Distribuição de ticket ---
    ax = axes[4]
    _estilizar(ax)
    tickets = df[df["status_final"] == "Ganho"]["valor_potencial"]
    if len(tickets) > 0:
        n, bins, patches = ax.hist(
            tickets / 1000, bins=14, color=COR_ROXO, edgecolor=BG_FIGURA, alpha=0.85,
        )
        media = tickets.mean() / 1000
        ax.axvline(media, color=COR_AMARELO, linestyle="--", linewidth=1.5,
                   label=f"Média: R$ {media:.0f}k")
        leg2 = ax.legend(facecolor=BG_PAINEL, labelcolor=COR_TEXTO, fontsize=8)
        leg2.get_frame().set_edgecolor(COR_GRADE)
    ax.set_title("Distribuição de Ticket — vendas ganhas")
    ax.set_xlabel("Valor (R$ mil)")
    ax.set_ylabel("Frequência")

    # --- 6. Status final (pizza) ---
    ax = axes[5]
    ax.set_facecolor(BG_PAINEL)
    ax.title.set_color(COR_TEXTO)
    ax.title.set_fontsize(10.5)
    ax.title.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_color(COR_GRADE)

    status = ind["status_dist"]
    labels = list(status.keys())
    sizes = list(status.values())
    cores_s = {"Ganho": COR_VERDE, "Perdido": COR_VERMELHO, "Em Andamento": COR_AMARELO}
    cores_pizza = [cores_s.get(l, COR_AZUL) for l in labels]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=cores_pizza,
        autopct="%1.1f%%", startangle=90,
        textprops={"color": COR_TEXTO, "fontsize": 9},
        wedgeprops={"edgecolor": BG_FIGURA, "linewidth": 1.8},
    )
    for at in autotexts:
        at.set_color(BG_FIGURA)
        at.set_fontweight("bold")
    ax.set_title("Distribuição por Status Final")

    # Título geral
    gargalo_label = ind["gargalo"][0]
    gargalo_taxa = ind["gargalo"][1]
    fig.suptitle(
        f"Dashboard — Funil de Vendas B2B  │  {ind['total_leads']} leads  "
        f"│  Conversão geral: {ind['taxa_conversao_geral']}%  "
        f"│  Ticket médio: R$ {ind['ticket_medio']:,}  "
        f"│  Gargalo: {gargalo_label} ({gargalo_taxa}%)",
        color=COR_TEXTO, fontsize=12, fontweight="bold", y=0.96,
        backgroundcolor=BG_FIGURA,
    )

    Path(saida).parent.mkdir(exist_ok=True)
    fig.savefig(saida, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Dashboard salvo → {saida}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from processar import processar
    from analisar import calcular_indicadores
    df = processar()
    gerar_dashboard(df, calcular_indicadores(df))
