import pandas as pd
from typing import Any

ETAPAS_ORDEM = ["Lead", "MQL", "SQL", "Proposta", "Negociação", "Fechado"]


def calcular_indicadores(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    ganhos = df[df["status_final"] == "Ganho"]

    # Leads que ATINGIRAM cada etapa (estão nela ou passaram por ela)
    acumulado = {
        e: int((df["etapa_num"] >= i).sum())
        for i, e in enumerate(ETAPAS_ORDEM)
    }

    # 1. Taxa de conversão por etapa (lead flow)
    conversao_etapa: dict[str, float] = {}
    for i in range(len(ETAPAS_ORDEM) - 1):
        atual = ETAPAS_ORDEM[i]
        prox = ETAPAS_ORDEM[i + 1]
        n_atual = acumulado[atual]
        n_prox = acumulado[prox]
        conversao_etapa[f"{atual} → {prox}"] = (
            round(n_prox / n_atual * 100, 1) if n_atual else 0.0
        )

    # 2. Taxa de conversão geral
    taxa_geral = round(len(ganhos) / total * 100, 1)

    # 3. Tempo médio de ciclo (leads ganhos)
    tempo_ciclo = round(ganhos["tempo_ciclo"].mean(), 1) if len(ganhos) else 0.0

    # 4. Ticket médio
    ticket_medio = round(ganhos["valor_potencial"].mean()) if len(ganhos) else 0

    # 5. Conversão por origem
    conversao_origem: dict[str, dict] = {}
    for origem, grp in df.groupby("origem"):
        g = int((grp["status_final"] == "Ganho").sum())
        conversao_origem[str(origem)] = {
            "taxa": round(g / len(grp) * 100, 1),
            "total": len(grp),
            "ganhos": g,
        }
    conversao_origem = dict(
        sorted(conversao_origem.items(), key=lambda x: x[1]["taxa"], reverse=True)
    )

    # 6. Gargalo
    gargalo = min(conversao_etapa.items(), key=lambda x: x[1])

    # 7. Evolução mensal
    evolucao = (
        df.groupby("mes_entrada")
        .agg(total_leads=("id", "count"), ganhos=("status_final", lambda x: (x == "Ganho").sum()))
        .reset_index()
    )
    evolucao["taxa_conversao"] = round(evolucao["ganhos"] / evolucao["total_leads"] * 100, 1)

    # Extras para dashboard e relatório
    tempo_por_etapa = df.groupby("etapa_atual")["dias_no_funil"].mean().round(1).to_dict()
    status_dist = df["status_final"].value_counts().to_dict()
    leads_por_etapa = {e: int((df["etapa_atual"] == e).sum()) for e in ETAPAS_ORDEM}
    pipeline_ativo = int(df[df["status_final"] == "Em Andamento"]["valor_potencial"].sum())

    return {
        "total_leads": total,
        "ganhos": len(ganhos),
        "leads_por_etapa": leads_por_etapa,
        "acumulado_por_etapa": acumulado,
        "conversao_etapa": conversao_etapa,
        "taxa_conversao_geral": taxa_geral,
        "tempo_medio_ciclo": tempo_ciclo,
        "ticket_medio": ticket_medio,
        "conversao_origem": conversao_origem,
        "gargalo": gargalo,
        "evolucao_mensal": evolucao,
        "tempo_por_etapa": tempo_por_etapa,
        "status_dist": status_dist,
        "pipeline_ativo": pipeline_ativo,
    }


if __name__ == "__main__":
    from processar import processar
    ind = calcular_indicadores(processar())
    print(f"Conversão geral : {ind['taxa_conversao_geral']}%")
    print(f"Gargalo         : {ind['gargalo'][0]} ({ind['gargalo'][1]}%)")
    print(f"Ticket médio    : R$ {ind['ticket_medio']:,}")
