"""
prepare_dataset.py
──────────────────
Lê as tabelas brutas do MIMIC-IV-ED 2.2, realiza a limpeza e o
pré-processamento e salva o dataset pronto para treinamento em
data/dataset_processado.csv.

O target é o acuity ESI original (1–5), sem qualquer conversão
para Manchester nesta etapa. A conversão é responsabilidade da
camada de adaptação em modelo-ia/modelo.py.

Versão 2: inclui chiefcomplaint categorizado como features adicionais.
"""

from pathlib import Path
import numpy as np
import pandas as pd

# ── Caminhos ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "mimic-iv-ed-2.2" / "ed"
OUTPUT_PATH = BASE_DIR / "data" / "dataset_processado.csv"

# ── 1. Carregamento ───────────────────────────────────────────────────────────
print("Carregando dados...")

triage  = pd.read_csv(DATA_DIR / "triage.csv.gz",  compression="gzip")
edstays = pd.read_csv(DATA_DIR / "edstays.csv.gz", compression="gzip")

print(f"  triage  : {len(triage):,} registros")
print(f"  edstays : {len(edstays):,} registros")

# ── 2. Merge ──────────────────────────────────────────────────────────────────
triage_cols  = ["stay_id", "temperature", "heartrate", "resprate",
                "o2sat", "sbp", "dbp", "pain", "chiefcomplaint", "acuity"]
edstays_cols = ["stay_id", "arrival_transport", "gender"]

df = triage[triage_cols].merge(
    edstays[edstays_cols],
    on="stay_id",
    how="left",
    validate="one_to_one",
)

print(f"\nApós merge: {len(df):,} registros")

# ── 3. Remover registros sem target ───────────────────────────────────────────
antes = len(df)
df = df.dropna(subset=["acuity"]).copy()
df["acuity"] = df["acuity"].astype(int)
print(f"Removidos sem acuity: {antes - len(df):,} → {len(df):,} restantes")

# ── 4. Tratamento do campo pain ───────────────────────────────────────────────
# Estratégia de mapeamento:
#   Numérico 0–10           → valor direto
#   Faixa "X-Y"             → média aritmética  (ex: "6-7" → 6.5)
#   "critical" / "crit"     → 10
#   "mild"                  → 3
#   "moderate"              → 5
#   "bad" / "alot"          → 7
#   Incapacidade de avaliar → NaN
#   Demais textuais         → NaN
#   Numérico fora de 0–10  → NaN

pain_raw = df["pain"].astype(str).str.strip().str.lower()

pain_num = pd.to_numeric(df["pain"], errors="coerce")
df["pain_clean"] = pain_num

range_mask   = pain_raw.str.match(r"^\d+\.?\d*-\d+\.?\d*$")
range_values = pain_raw[range_mask].str.split("-").apply(
    lambda x: (float(x[0]) + float(x[1])) / 2
)
df.loc[range_mask, "pain_clean"] = range_values

df.loc[pain_raw.isin(["critical", "crit"]), "pain_clean"] = 10.0
df.loc[pain_raw.isin(["mild"]),              "pain_clean"] = 3.0
df.loc[pain_raw.isin(["moderate"]),          "pain_clean"] = 5.0
df.loc[pain_raw.isin(["bad", "alot"]),       "pain_clean"] = 7.0

unable_pattern = (
    r"^unable$|^uta$|^ua$|^u/a$|^u$|^ut$"
    r"|^non-verbal$|^sleeping$|^unknown$|^refused$"
    r"|^prehosp$|^pre-hosp$|^denies$|^not bad$"
)
unable_mask = pain_raw.str.match(unable_pattern, na=False)
df.loc[unable_mask,                          "pain_clean"] = np.nan
df.loc[pain_raw.isin(["yes"]),               "pain_clean"] = np.nan
df.loc[~df["pain_clean"].between(0, 10),     "pain_clean"] = np.nan

print(f"\nPain — válidos após tratamento: {df['pain_clean'].notna().sum():,}")
print(f"Pain — nulos após tratamento  : {df['pain_clean'].isna().sum():,}")

df = df.drop(columns=["pain"]).rename(columns={"pain_clean": "pain"})

# ── 5. Categorização do chiefcomplaint ────────────────────────────────────────
# Categorização por keyword matching com ordem de prioridade clínica.
# Queixas com maior gravidade potencial têm prioridade sobre as demais.
# Cobertura: ~78.7% dos registros; os demais recebem categoria "outro".
#
# As categorias são transformadas em features binárias (one-hot) para
# uso pelo modelo, evitando impor ordenação artificial entre categorias.

print("\nCategorizando chiefcomplaint...")

GRUPOS = [
    ("cardiovascular", [
        "chest pain", r"\bcp\b", "palpitation", "cardiac",
        "tachycardia", "bradycardia", "svt", "afib", "heart",
    ]),
    ("respiratorio", [
        "dyspnea", r"\bsob\b", "shortness of breath",
        "respiratory", "asthma", "copd", "wheezing", "stridor",
    ]),
    ("neurologico", [
        "altered mental", "seizure", "stroke", r"\btia\b",
        "confusion", "letharg", "unresponsive", "headache",
        "syncope", r"\bweakness\b", "numbness", "facial droop",
    ]),
    ("psiquiatrico", [
        r"\bsi\b", "suicide", "psych", "psychiatric", "anxiety",
        "overdose", r"\betoh\b", "alcohol", "detox", "depression",
    ]),
    ("trauma", [
        r"\bfall\b", "s/p fall", r"\bmvc\b", r"\bmva\b", "trauma",
        "laceration", "fracture", "injury", "wound", "assault", "burn",
    ]),
    ("infeccioso", [
        "fever", "sepsis", r"\bili\b", "influenza", "cellulitis",
        r"\buti\b", "pneumonia", "abscess", "infection",
    ]),
    ("abdominal", [
        r"\babd\b", "abdominal", "nausea", r"\bn/v\b", "vomit",
        "diarrhea", "rlq", "llq", "ruq", "flank pain",
        "rectal", "gi bleed", "brbpr",
    ]),
    ("dor_outros", ["pain", "ache"]),
]

cc_norm = df["chiefcomplaint"].fillna("").str.lower().str.strip()

# Inicializa com "outro" e aplica grupos em ordem de prioridade inversa
# (mais prioritário aplicado por último, sobrescreve os anteriores)
categoria = pd.Series("outro", index=df.index)

for grupo, keywords in reversed(GRUPOS):
    pattern = "|".join(keywords)
    mask = cc_norm.str.contains(pattern, na=False, regex=True)
    categoria[mask] = grupo

df["categoria_queixa"] = categoria

dist_cat = df["categoria_queixa"].value_counts()
print("  Distribuição:")
for cat, count in dist_cat.items():
    print(f"    {cat:<20} {count:>7,}  ({count/len(df)*100:.1f}%)")

# One-hot encoding — descarta "outro" como referência
categorias_dummies = pd.get_dummies(
    df["categoria_queixa"],
    prefix="queixa",
    drop_first=False,
    dtype=int,
)
# Remove a categoria "outro" (referência implícita — ausência de todas = outro)
if "queixa_outro" in categorias_dummies.columns:
    categorias_dummies = categorias_dummies.drop(columns=["queixa_outro"])

df = pd.concat([df, categorias_dummies], axis=1)
df = df.drop(columns=["chiefcomplaint", "categoria_queixa"])

# ── 6. Limpeza das variáveis numéricas ────────────────────────────────────────
limites = {
    "temperature": (85.0, 110.0),
    "heartrate":   (20.0, 250.0),
    "resprate":    (4.0,  80.0),
    "o2sat":       (50.0, 100.0),
    "sbp":         (40.0, 300.0),
    "dbp":         (20.0, 200.0),
}

vitais = list(limites.keys())

for col in vitais:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    lo, hi = limites[col]
    n_out = ((df[col] < lo) | (df[col] > hi)).sum()
    df.loc[(df[col] < lo) | (df[col] > hi), col] = np.nan
    if n_out > 0:
        print(f"  {col}: {n_out:,} valores fora de [{lo}, {hi}] → NaN")

# ── 7. Imputação por mediana por acuity ──────────────────────────────────────
print("\nImputando valores ausentes por mediana do grupo acuity...")

all_features = vitais + ["pain"]

for col in all_features:
    antes_nulos = df[col].isna().sum()
    df[col] = df.groupby("acuity")[col].transform(
        lambda x: x.fillna(x.median())
    )
    df[col] = df[col].fillna(df[col].median())
    depois_nulos = df[col].isna().sum()
    if antes_nulos > 0:
        print(f"  {col}: {antes_nulos:,} → {depois_nulos:,} nulos")

# ── 8. Codificação de variáveis categóricas ───────────────────────────────────
df["chegada_critica"] = df["arrival_transport"].isin(
    ["AMBULANCE", "HELICOPTER"]
).astype(int)

df["sexo_masculino"] = (df["gender"] == "M").astype(int)

df = df.drop(columns=["arrival_transport", "gender"])

# ── 9. Seleção final de colunas ───────────────────────────────────────────────
features_base = [
    "temperature", "heartrate", "resprate", "o2sat",
    "sbp", "dbp", "pain", "chegada_critica", "sexo_masculino",
]
features_queixa = [c for c in df.columns if c.startswith("queixa_")]
features = features_base + sorted(features_queixa)
target = "acuity"

df_final = df[features + [target]].copy()

# ── 10. Distribuição final ────────────────────────────────────────────────────
print("\n=== Distribuição final por acuity (ESI) ===")
dist = df_final[target].value_counts().sort_index()
manchester = {1: "VERMELHO", 2: "LARANJA", 3: "AMARELO", 4: "VERDE", 5: "AZUL"}
for acuity, count in dist.items():
    pct = count / len(df_final) * 100
    print(f"  ESI {acuity} ({manchester[acuity]}): {count:>7,}  ({pct:.2f}%)")

print(f"\nTotal de registros : {len(df_final):,}")
print(f"Total de features  : {len(features)}")
print(f"  Sinais vitais    : {len(features_base)}")
print(f"  Queixa (one-hot) : {len(features_queixa)}")

# ── 11. Salvar ────────────────────────────────────────────────────────────────
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df_final.to_csv(OUTPUT_PATH, index=False)
print(f"\nDataset salvo em: {OUTPUT_PATH}")