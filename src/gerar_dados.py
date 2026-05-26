import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

random.seed(42)
np.random.seed(42)

ETAPAS = ["Lead", "MQL", "SQL", "Proposta", "Negociação", "Fechado"]
PESO_ORIGEM = {"Site": 0.40, "LinkedIn": 0.25, "Indicação": 0.20, "Outbound": 0.15}
SEGMENTOS = ["Tech", "Indústria", "Varejo", "Serviços", "Financeiro"]

PROB_AVANCO = {
    "Lead":       0.68,
    "MQL":        0.62,
    "SQL":        0.65,
    "Proposta":   0.32,  # gargalo intencional
    "Negociação": 0.55,
}

MULT_ORIGEM = {"Site": 0.85, "LinkedIn": 1.45, "Indicação": 1.30, "Outbound": 0.65}
MULT_SEG = {"Tech": 1.4, "Financeiro": 1.6, "Indústria": 1.0, "Varejo": 0.75, "Serviços": 0.9}
WIN_RATE = 0.68


def _simular_jornada(origem: str) -> tuple:
    mult = MULT_ORIGEM[origem]
    etapa_idx = 0
    for i, etapa in enumerate(ETAPAS[:-1]):
        prob = min(PROB_AVANCO[etapa] * mult, 0.92)
        if random.random() < prob:
            etapa_idx = i + 1
        else:
            break
    etapa = ETAPAS[etapa_idx]
    if etapa == "Fechado":
        status = "Ganho" if random.random() < WIN_RATE else "Perdido"
    elif etapa_idx >= 3:
        status = "Perdido" if random.random() < 0.50 else "Em Andamento"
    else:
        status = "Em Andamento" if random.random() < 0.55 else "Perdido"
    return etapa, status


def gerar_leads(n: int = 300) -> pd.DataFrame:
    inicio = datetime(2024, 12, 1)
    fim = datetime(2025, 5, 31)
    span = (fim - inicio).days
    etapa_num = {e: i for i, e in enumerate(ETAPAS)}
    origens = list(PESO_ORIGEM.keys())
    pesos = list(PESO_ORIGEM.values())

    registros = []
    for i in range(1, n + 1):
        entrada = inicio + timedelta(days=random.randint(0, span))
        origem = random.choices(origens, weights=pesos)[0]
        segmento = random.choice(SEGMENTOS)
        etapa, status = _simular_jornada(origem)

        idx = etapa_num[etapa]
        dias_mov = min(
            idx * random.randint(7, 20) + random.randint(0, 7),
            (fim - entrada).days,
        )
        ultima_mov = entrada + timedelta(days=dias_mov)

        valor = round(np.random.lognormal(9.6, 0.65)) * MULT_SEG[segmento]
        valor = max(round(valor / 500) * 500, 3000)

        registros.append({
            "id": f"L{i:04d}",
            "data_entrada": entrada.strftime("%Y-%m-%d"),
            "origem": origem,
            "segmento": segmento,
            "etapa_atual": etapa,
            "data_ultima_movimentacao": ultima_mov.strftime("%Y-%m-%d"),
            "valor_potencial": int(valor),
            "status_final": status,
        })

    return pd.DataFrame(registros)


if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    df = gerar_leads()
    df.to_csv("data/leads_brutos.csv", index=False)
    print(f"{len(df)} leads gerados → data/leads_brutos.csv")
