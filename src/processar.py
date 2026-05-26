import pandas as pd
from pathlib import Path

ETAPAS_ORDEM = ["Lead", "MQL", "SQL", "Proposta", "Negociação", "Fechado"]
ETAPA_NUM = {e: i for i, e in enumerate(ETAPAS_ORDEM)}
DATA_REF = pd.Timestamp("2025-05-31")


def processar(
    entrada: str = "data/leads_brutos.csv",
    saida: str = "data/leads_processados.csv",
) -> pd.DataFrame:
    df = pd.read_csv(entrada)
    df["data_entrada"] = pd.to_datetime(df["data_entrada"])
    df["data_ultima_movimentacao"] = pd.to_datetime(df["data_ultima_movimentacao"])

    df["etapa_num"] = df["etapa_atual"].map(ETAPA_NUM)
    df["dias_no_funil"] = (DATA_REF - df["data_entrada"]).dt.days
    df["dias_sem_movimentacao"] = (DATA_REF - df["data_ultima_movimentacao"]).dt.days
    df["mes_entrada"] = df["data_entrada"].dt.to_period("M").astype(str)
    df["tempo_ciclo"] = (
        df["data_ultima_movimentacao"] - df["data_entrada"]
    ).dt.days

    Path("data").mkdir(exist_ok=True)
    df.to_csv(saida, index=False)
    print(f"{len(df)} leads processados → {saida}")
    return df


if __name__ == "__main__":
    processar()
