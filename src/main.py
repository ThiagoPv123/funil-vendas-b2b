import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))

from gerar_dados import gerar_leads
from processar import processar
from analisar import calcular_indicadores
from dashboard import gerar_dashboard
from relatorio import gerar_relatorio


def main() -> None:
    sep = "-" * 52
    print(f"\n{sep}")
    print("  Analise Automatizada de Funil de Vendas B2B")
    print(sep)

    print("\n[1/5] Gerando dados...")
    Path("data").mkdir(exist_ok=True)
    df_bruto = gerar_leads(300)
    df_bruto.to_csv("data/leads_brutos.csv", index=False)
    print("      300 leads gerados -> data/leads_brutos.csv")

    print("\n[2/5] Processando dados...")
    df = processar("data/leads_brutos.csv", "data/leads_processados.csv")

    print("\n[3/5] Calculando indicadores...")
    ind = calcular_indicadores(df)
    print(f"      Conversao geral : {ind['taxa_conversao_geral']}%")
    print(f"      Ticket medio    : R$ {ind['ticket_medio']:,}")
    print(f"      Gargalo         : {ind['gargalo'][0]} ({ind['gargalo'][1]}%)")
    print(f"      Pipeline ativo  : R$ {ind['pipeline_ativo']:,}")

    print("\n[4/5] Gerando dashboard...")
    Path("outputs").mkdir(exist_ok=True)
    gerar_dashboard(df, ind, "outputs/dashboard.png")

    print("\n[5/5] Gerando relatorio executivo...")
    gerar_relatorio(ind, "outputs/relatorio_executivo.md")

    print(f"\n{sep}")
    print("  Concluido. Arquivos gerados:")
    print("  - data/leads_brutos.csv")
    print("  - data/leads_processados.csv")
    print("  - outputs/dashboard.png")
    print("  - outputs/relatorio_executivo.md")
    print(sep + "\n")


if __name__ == "__main__":
    main()
