from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "mimic-iv-ed-2.2" / "ed"

TRIAGE_PATH = DATA_DIR / "triage.csv.gz"

print("Caminho da base:")
print(TRIAGE_PATH)

print("\nArquivo existe?")
print(TRIAGE_PATH.exists())

triage = pd.read_csv(TRIAGE_PATH, compression="gzip")

print("\nQuantidade de registros:")
print(len(triage))

print("\nPrimeiras linhas:")
print(triage.head())

print("\nColunas:")
print(triage.columns.tolist())

print("\nInformações da tabela:")
triage.info()

print("\nValores nulos:")
print(triage.isnull().sum())

print("\nDistribuição de acuity:")
print(
    triage["acuity"]
    .value_counts(dropna=False)
    .sort_index()
)
print("\n" + "=" * 60)
print("ANÁLISE INICIAL DAS VARIÁVEIS")
print("=" * 60)

# Quantidade de pacientes e atendimentos
print("\nPacientes únicos:")
print(triage["subject_id"].nunique())

print("\nAtendimentos únicos:")
print(triage["stay_id"].nunique())

# Estatísticas das variáveis numéricas
features_numericas = [
    "temperature",
    "heartrate",
    "resprate",
    "o2sat",
    "sbp",
    "dbp"
]

print("\nEstatísticas das variáveis numéricas:")
print(triage[features_numericas].describe().T)

# Investigar a coluna pain
print("\nValores mais frequentes em 'pain':")
print(triage["pain"].value_counts(dropna=False).head(30))

print("\nQuantidade de valores diferentes em 'pain':")
print(triage["pain"].nunique(dropna=False))

print("\n" + "=" * 60)
print("INVESTIGAÇÃO DE VALORES EXTREMOS")
print("=" * 60)

for col in features_numericas:
    print(f"\n--- {col.upper()} ---")

    print("5 menores valores:")
    print(triage[col].nsmallest(5).tolist())

    print("5 maiores valores:")
    print(triage[col].nlargest(5).tolist())

pain_numerico = pd.to_numeric(triage["pain"], errors="coerce")

print("\n" + "=" * 60)
print("ANÁLISE DA COLUNA PAIN")
print("=" * 60)

print("\nValores que puderam ser convertidos para número:")
print(pain_numerico.notna().sum())

print("\nValores não nulos que NÃO puderam ser convertidos:")
print(
    triage["pain"].notna().sum()
    - pain_numerico.notna().sum()
)

print("\nMenor valor numérico:")
print(pain_numerico.min())

print("\nMaior valor numérico:")
print(pain_numerico.max())

print("\n" + "=" * 60)
print("DISTRIBUIÇÃO POR FAIXAS")
print("=" * 60)

faixas = {
    "temperature": [90, 110],
    "heartrate": [20, 250],
    "resprate": [5, 80],
    "o2sat": [50, 100],
    "sbp": [40, 300],
    "dbp": [20, 200]
}

for col, (minimo, maximo) in faixas.items():

    validos = triage[col].notna().sum()

    fora_faixa = (
        (triage[col] < minimo) |
        (triage[col] > maximo)
    ).sum()

    percentual = (fora_faixa / validos) * 100

    print(f"\n{col}")
    print(f"Preenchidos: {validos}")
    print(f"Fora da faixa investigada: {fora_faixa}")
    print(f"Percentual: {percentual:.2f}%")

pain_convertido = pd.to_numeric(triage["pain"], errors="coerce")

pain_fora_faixa = (
    (pain_convertido < 0) |
    (pain_convertido > 10)
).sum()

print("\npain")
print(f"Numéricos: {pain_convertido.notna().sum()}")
print(f"Numéricos fora de 0-10: {pain_fora_faixa}")
print(
    f"Percentual: "
    f"{(pain_fora_faixa / pain_convertido.notna().sum()) * 100:.2f}%"
)

print("\n" + "=" * 60)
print("SINAIS VITAIS POR ACUITY")
print("=" * 60)

medianas_por_acuity = (
    triage
    .groupby("acuity")[features_numericas]
    .median()
    .round(2)
)

print(medianas_por_acuity)

triage_exploracao = triage.copy()

triage_exploracao["pain_numeric"] = pd.to_numeric(
    triage_exploracao["pain"],
    errors="coerce"
)

triage_exploracao.loc[
    ~triage_exploracao["pain_numeric"].between(0, 10),
    "pain_numeric"
] = pd.NA

print("\nMediana de dor por acuity:")

print(
    triage_exploracao
    .groupby("acuity")["pain_numeric"]
    .median()
)

## Exploração da tabela edstays

EDSTAYS_PATH = DATA_DIR / "edstays.csv.gz"

print("\n" + "=" * 60)
print("EXPLORAÇÃO DA TABELA EDSTAYS")
print("=" * 60)

edstays = pd.read_csv(
    EDSTAYS_PATH,
    compression="gzip"
)

print("\nQuantidade de registros:")
print(len(edstays))

print("\nPrimeiras linhas:")
print(edstays.head())

print("\nColunas:")
print(edstays.columns.tolist())

print("\nInformações:")
edstays.info()

print("\nValores nulos:")
print(edstays.isnull().sum())

print("\nPacientes únicos:")
print(edstays["subject_id"].nunique())

print("\nAtendimentos únicos:")
print(edstays["stay_id"].nunique())

print("\n" + "=" * 60)
print("VARIÁVEIS CATEGÓRICAS DA EDSTAYS")
print("=" * 60)

categoricas = [
    "gender",
    "race",
    "arrival_transport",
    "disposition"
]

for col in categoricas:

    print(f"\n--- {col.upper()} ---")

    print("Quantidade de categorias:")
    print(edstays[col].nunique())

    print("\nDistribuição:")
    print(edstays[col].value_counts())

    print()

exploracao_transporte = triage[
    ["stay_id", "acuity"]
].merge(
    edstays[
        ["stay_id", "arrival_transport"]
    ],
    on="stay_id",
    how="inner"
)

print("\n" + "=" * 60)
print("ACUITY POR FORMA DE CHEGADA")
print("=" * 60)

tabela_transporte = pd.crosstab(
    exploracao_transporte["arrival_transport"],
    exploracao_transporte["acuity"],
    normalize="index"
) * 100

print(tabela_transporte.round(2))

print("\n" + "=" * 60)


""" print("MAPEAMENTO DAS DEMAIS TABELAS")
print("=" * 60)

arquivos = [
    "vitalsign.csv.gz",
    "diagnosis.csv.gz",
    "medrecon.csv.gz",
    "pyxis.csv.gz"
]

for arquivo in arquivos:
    caminho = DATA_DIR / arquivo

    print("\n" + "-" * 60)
    print(arquivo.upper())
    print("-" * 60)

    df_temp = pd.read_csv(
        caminho,
        compression="gzip"
    )

    print(f"Registros: {len(df_temp)}")
    print(f"Colunas: {df_temp.columns.tolist()}")

    print("\nPrimeiras 3 linhas:")
    print(df_temp.head(3))

    print("\nTipos:")
    print(df_temp.dtypes) """