import pandas as pd
import numpy as np
import os

# ============================================================
# 1️⃣ Localização e leitura do arquivo CSV
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))

csv_files = [f for f in os.listdir(script_dir) if f.endswith(".csv")]

if not csv_files:
    print("Nenhum arquivo CSV encontrado na pasta do script.")
    exit()

file_path = os.path.join(script_dir, csv_files[0])
print(f"Arquivo encontrado: {csv_files[0]}")

df = pd.read_csv(file_path)

# ============================================================
# 2️⃣ Padronização dos nomes das colunas
# ============================================================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df = df.rename(columns={
    "datetime": "event_datetime",
    "assetid": "asset_id",
    "alarmseverityname": "alarm_severity"
})
print("Colunas após renomeação:", df.columns.tolist())

# ============================================================
# 3️⃣ Tratamento e limpeza
# ============================================================
df["event_datetime"] = pd.to_datetime(df["event_datetime"], errors="coerce")
df = df.dropna(subset=["event_datetime", "asset_id"]).drop_duplicates()

# ============================================================
# 4️⃣ Extração do grupo e chave da máquina
# ============================================================
df["machine_group"] = df["asset_id"].str.extract(r"(ACON-[A-Z]+)")
df["machine_group"] = df["machine_group"].fillna(df["asset_id"])
machine_map = {m: i+1 for i, m in enumerate(df["machine_group"].unique())}
df["MachineKey"] = df["machine_group"].map(machine_map)

# ============================================================
# 5️⃣ Ordenação e criação de colunas auxiliares
# ============================================================
df = df.sort_values(["MachineKey", "event_datetime"])
df["prev_state"] = df.groupby("MachineKey")["state"].shift(1)
df["prev_time"] = df.groupby("MachineKey")["event_datetime"].shift(1)
df["next_state"] = df.groupby("MachineKey")["state"].shift(-1)
df["next_time"] = df.groupby("MachineKey")["event_datetime"].shift(-1)

# ============================================================
# 6️⃣ Cálculo MTTR
# ============================================================
df["MTTR_Amplo"] = np.where(
    df["state"] == "A2N",
    (df["event_datetime"] - df["prev_time"]).dt.total_seconds() / 3600,
    np.nan
)
df["MTTR_Conservador"] = np.where(
    (df["state"] == "A2N") & (df["prev_state"] == "N2A"),
    df["MTTR_Amplo"],
    np.nan
)

# ============================================================
# 7️⃣ Cálculo MTBF
# ============================================================
df["MTBF_Conservador"] = np.where(
    (df["state"] == "A2N") & (df["next_state"] == "N2A"),
    (df["next_time"] - df["event_datetime"]).dt.total_seconds() / 3600,
    np.nan
)
df["MTBF_Amplo"] = np.where(
    df["state"] == "A2N",
    (df["next_time"] - df["event_datetime"]).dt.total_seconds() / 3600,
    np.nan
)

# ============================================================
# 8️⃣ Tabela de paradas (eventos de reparo)
# ============================================================
paradas = df[df["state"] == "A2N"].copy()

# ============================================================
# 9️⃣ Criação Dim_AlarmSeverity
# ============================================================
dim_alarm_severity = (
    df[["alarm_severity"]].drop_duplicates().reset_index(drop=True)
    .rename(columns={"alarm_severity": "AlarmSeverityName"})
)
dim_alarm_severity["AlarmSeverityKey"] = dim_alarm_severity.index + 1
dim_alarm_severity = dim_alarm_severity[["AlarmSeverityKey", "AlarmSeverityName"]]

df = df.merge(dim_alarm_severity, left_on="alarm_severity", right_on="AlarmSeverityName", how="left")
paradas = paradas.merge(dim_alarm_severity, left_on="alarm_severity", right_on="AlarmSeverityName", how="left")

# ============================================================
# 🔟 KPIs por máquina
# ============================================================
# Total de paradas com merge para evitar problemas de comprimento
total_paradas = paradas.groupby("MachineKey")["state"].count().reset_index()
total_paradas = total_paradas.rename(columns={"state": "Total_Paradas"})

kpi_maquina = paradas.groupby("MachineKey").agg(
    MTTR_Cons_Medio=("MTTR_Conservador", "mean"),
    MTTR_Amplo_Medio=("MTTR_Amplo", "mean"),
    MTBF_Cons_Medio=("MTBF_Conservador", "mean"),
    MTBF_Amplo_Medio=("MTBF_Amplo", "mean")
).reset_index()

kpi_maquina = kpi_maquina.merge(total_paradas, on="MachineKey", how="left")

# Disponibilidade e taxa de falha conservadora
kpi_maquina["Disponibilidade_Cons"] = kpi_maquina["MTBF_Cons_Medio"] / (
    kpi_maquina["MTBF_Cons_Medio"] + kpi_maquina["MTTR_Cons_Medio"]
)
kpi_maquina["Taxa_Falha_Cons"] = 1 / kpi_maquina["MTBF_Cons_Medio"]

# ============================================================
# 1️⃣1️⃣ KPI Global
# ============================================================
kpi_global = pd.DataFrame({
    "Total_Paradas": [paradas.shape[0]],
    "MTTR_Global_Cons": [paradas["MTTR_Conservador"].mean()],
    "MTTR_Global_Amplo": [paradas["MTTR_Amplo"].mean()],
    "MTBF_Global_Cons": [paradas["MTBF_Conservador"].mean()],
    "MTBF_Global_Amplo": [paradas["MTBF_Amplo"].mean()]
})

# ============================================================
# 1️⃣2️⃣ Criação das tabelas dimensionais restantes
# ============================================================
dim_machine = df[["MachineKey", "machine_group"]].drop_duplicates().rename(columns={"machine_group": "MachineGroup"})

dim_date = pd.DataFrame({
    "Date": pd.date_range(df["event_datetime"].min(), df["event_datetime"].max())
})
dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)
dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["Day"] = dim_date["Date"].dt.day
dim_date["Weekday"] = dim_date["Date"].dt.day_name()

# ============================================================
# 1️⃣3️⃣ Criação tabela fato Fact_Paradas
# ============================================================
paradas["DateKey"] = paradas["event_datetime"].dt.strftime("%Y%m%d").astype(int)
fact_paradas = paradas[[
    "MachineKey",
    "DateKey",
    "AlarmSeverityKey",
    "MTTR_Conservador",
    "MTTR_Amplo",
    "MTBF_Conservador",
    "MTBF_Amplo"
]].copy()

# Normalização numérica para MySQL
for col in ["MTTR_Conservador", "MTTR_Amplo", "MTBF_Conservador", "MTBF_Amplo"]:
    fact_paradas[col] = pd.to_numeric(fact_paradas[col], errors='coerce').fillna(0)

# ============================================================
# 1️⃣4️⃣ Criação tabela gold final consolidada
# ============================================================
gold_final = fact_paradas.merge(kpi_maquina, on="MachineKey", how="left")
gold_final = gold_final.merge(dim_machine, on="MachineKey", how="left")
gold_final = gold_final.merge(dim_alarm_severity, on="AlarmSeverityKey", how="left")

# Normalização da Gold Table
for col in ["MTTR_Conservador", "MTTR_Amplo", "MTBF_Conservador", "MTBF_Amplo"]:
    gold_final[col] = pd.to_numeric(gold_final[col], errors='coerce').fillna(0)

# ============================================================
# 1️⃣5️⃣ Exportação das tabelas
# ============================================================
tables_to_export = {
    "Dim_Machine": dim_machine,
    "Dim_Date": dim_date,
    "Dim_AlarmSeverity": dim_alarm_severity,
    "Fact_Paradas": fact_paradas,
    "Tabela_Paradas": paradas,
    "KPI_Por_Maquina": kpi_maquina,
    "KPI_Global": kpi_global,
    "Gold_Final_Completa": gold_final
}

for name, df_table in tables_to_export.items():
    output_file = os.path.join(script_dir, f"{name}_Normalizado.csv")
    df_table.to_csv(output_file, index=False)
    print(f"✅ {name} exportada -> {output_file}")

print("--------------------------------------------------")
print("ETL COMPLETO: todas as tabelas normalizadas exportadas com sucesso!")
print(f"Pasta de destino: {script_dir}")
print("--------------------------------------------------")