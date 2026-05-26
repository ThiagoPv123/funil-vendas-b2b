from datetime import datetime
from pathlib import Path
from typing import Any


def gerar_relatorio(
    ind: dict[str, Any],
    saida: str = "outputs/relatorio_executivo.md",
) -> None:
    gargalo_nome = ind["gargalo"][0]
    gargalo_taxa = ind["gargalo"][1]
    origens = list(ind["conversao_origem"].items())
    melhor = origens[0]
    pior = origens[-1]

    evo = ind["evolucao_mensal"]
    meses = evo["mes_entrada"].tolist()
    totais = evo["total_leads"].tolist()
    mes_pico = meses[totais.index(max(totais))]
    tendencia = "crescente" if len(totais) >= 2 and totais[-1] > totais[-2] else "de queda" if len(totais) >= 2 and totais[-1] < totais[-2] else "estável"

    linhas = [
        "# Relatório Executivo — Funil de Vendas B2B",
        "",
        f"**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}  ",
        "**Período:** Dezembro/2024 – Maio/2025  ",
        f"**Base analisada:** {ind['total_leads']} leads",
        "",
        "---",
        "",
        "## Visão Geral",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Leads analisados | {ind['total_leads']} |",
        f"| Vendas ganhas | {ind['ganhos']} |",
        f"| Taxa de conversão geral | {ind['taxa_conversao_geral']}% |",
        f"| Ticket médio | R$ {ind['ticket_medio']:,.0f} |",
        f"| Tempo médio de ciclo (ganhos) | {ind['tempo_medio_ciclo']} dias |",
        f"| Pipeline ativo (potencial) | R$ {ind['pipeline_ativo']:,.0f} |",
        "",
        "---",
        "",
        "## Funil por Etapa",
        "",
        "| Etapa | Leads atuais | Leads que atingiram | Conversão para próxima etapa |",
        "|---|---|---|---|",
    ]

    etapas = ["Lead", "MQL", "SQL", "Proposta", "Negociação", "Fechado"]
    for etapa in etapas:
        n_atual = ind["leads_por_etapa"].get(etapa, 0)
        n_acum = ind["acumulado_por_etapa"].get(etapa, 0)
        chave = next((k for k in ind["conversao_etapa"] if k.startswith(etapa)), None)
        if chave:
            taxa = ind["conversao_etapa"][chave]
            flag = " ⚠️ **gargalo**" if chave == gargalo_nome else ""
            linhas.append(f"| {etapa} | {n_atual} | {n_acum} | {taxa}%{flag} |")
        else:
            linhas.append(f"| {etapa} | {n_atual} | {n_acum} | — |")

    linhas += [
        "",
        "---",
        "",
        "## Diagnóstico",
        "",
        "### Gargalo principal",
        "",
        f"A maior perda acontece na transição **{gargalo_nome}**, com aproveitamento de apenas "
        f"**{gargalo_taxa}%**. Isso significa que {100 - gargalo_taxa:.0f}% dos leads que chegam "
        f"a essa etapa não avançam — concentrando aqui o maior impacto negativo no resultado comercial.",
        "",
        "### Canais de aquisição",
        "",
    ]

    for origem, dados in ind["conversao_origem"].items():
        part = round(dados["total"] / ind["total_leads"] * 100, 1)
        linhas.append(
            f"- **{origem}**: {dados['taxa']}% de conversão "
            f"({dados['ganhos']} ganhos / {dados['total']} leads — {part}% do volume total)"
        )

    linhas += [
        "",
        f"**{melhor[0]}** tem a melhor conversão ({melhor[1]['taxa']}%) mas representa "
        f"{round(melhor[1]['total'] / ind['total_leads'] * 100, 1)}% dos leads. "
        f"**{pior[0]}** tem a menor ({pior[1]['taxa']}%) — baixa qualificação ou desalinhamento de perfil.",
        "",
        "### Tendência mensal",
        "",
        f"O volume de novos leads está **{tendencia}** no período. "
        f"O mês de maior entrada foi **{mes_pico}** com {max(totais)} leads.",
        "",
        "---",
        "",
        "## Recomendações",
        "",
        f"1. **Investigar o gargalo em _{gargalo_nome}_**: levantar motivos de perda declarados, "
        f"avaliar tempo de resposta após proposta, qualidade do follow-up e adequação do "
        f"valor ao perfil do lead.",
        "",
        f"2. **Priorizar {melhor[0]} como canal de crescimento**: maior ROI por lead. "
        f"Aumentar volume nesse canal melhora a conversão geral sem alterar o processo de vendas.",
        "",
        f"3. **Revisar critérios de qualificação do {pior[0]}**: conversão abaixo da média "
        f"sugere leads com perfil inadequado ou expectativas desalinhadas na entrada do funil.",
        "",
        f"4. **Agir nos {ind['leads_por_etapa'].get('Proposta', 0)} leads com proposta aberta**: "
        f"leads parados há mais tempo nessa etapa têm maior chance de resgate com contato ativo.",
        "",
        "---",
        "",
        "*Relatório gerado automaticamente por `src/main.py`. "
        "Dados fictícios para fins de demonstração técnica.*",
    ]

    Path(saida).parent.mkdir(exist_ok=True)
    Path(saida).write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório salvo → {saida}")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from processar import processar
    from analisar import calcular_indicadores
    gerar_relatorio(calcular_indicadores(processar()))
