"""
modelo.py
─────────
Carrega o modelo treinado e expõe a classe ModeloTriagem para uso
pelo main.py (FastAPI).

Fluxo:
  1. Recebe sinais vitais + queixa da API (campos em português, temperatura °C)
  2. Traduz e normaliza para o formato do treino (17 features)
  3. Modelo prediz o acuity ESI (1–5)
  4. Camada de adaptação converte ESI → cor do Protocolo de Manchester
"""

from pathlib import Path
import pandas as pd
import joblib

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "triagem_model.pkl"

model = joblib.load(MODEL_PATH)

# Ordem das features exatamente igual ao treino (prepare_dataset + train.py)
FEATURES = [
    "temperature", "heartrate", "resprate", "o2sat",
    "sbp", "dbp", "pain", "chegada_critica", "sexo_masculino",
    "queixa_abdominal", "queixa_cardiovascular", "queixa_dor_outros",
    "queixa_infeccioso", "queixa_neurologico", "queixa_psiquiatrico",
    "queixa_respiratorio", "queixa_trauma",
]

# Medianas do conjunto de treino — usadas como fallback para campos ausentes.
# Calculadas a partir do dataset_processado.csv (prepare_dataset.py).
MEDIANAS_TREINO = {
    "temperature":           98.0,
    "heartrate":             84.0,
    "resprate":              18.0,
    "o2sat":                 99.0,
    "sbp":                  133.0,
    "dbp":                   77.0,
    "pain":                   4.0,
    "chegada_critica":        0.0,
    "sexo_masculino":         0.0,
    "queixa_abdominal":       0.0,
    "queixa_cardiovascular":  0.0,
    "queixa_dor_outros":      0.0,
    "queixa_infeccioso":      0.0,
    "queixa_neurologico":     0.0,
    "queixa_psiquiatrico":    0.0,
    "queixa_respiratorio":    0.0,
    "queixa_trauma":          0.0,
}

# Categorias de queixa e seus keywords (mesma lógica do prepare_dataset.py)
# Ordem de prioridade: primeiro match (mais prioritário) ganha.
GRUPOS_QUEIXA = [
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

# Mapeamento ESI → cor base do Manchester (equivalência ordinal)
ESI_PARA_MANCHESTER = {
    1: "VERMELHO",
    2: "LARANJA",
    3: "AMARELO",
    4: "VERDE",
    5: "AZUL",
}


def _celsius_para_fahrenheit(celsius: float | None) -> float | None:
    """Converte Celsius → Fahrenheit. O modelo foi treinado com °F (MIMIC-IV)."""
    if celsius is None:
        return None
    return celsius * 9 / 5 + 32


def _categorizar_queixa(queixa: str | None) -> str:
    """
    Converte texto livre da queixa principal na categoria correspondente.
    Retorna 'outro' se nenhum grupo for identificado.
    """
    if not queixa:
        return "outro"

    texto = queixa.strip().lower()

    for grupo, keywords in GRUPOS_QUEIXA:
        pattern = "|".join(keywords)
        import re
        if re.search(pattern, texto):
            return grupo

    return "outro"


def _queixa_para_features(categoria: str) -> dict:
    """Converte a categoria da queixa em features binárias (one-hot)."""
    categorias_validas = [
        "abdominal", "cardiovascular", "dor_outros", "infeccioso",
        "neurologico", "psiquiatrico", "respiratorio", "trauma",
    ]
    return {
        f"queixa_{cat}": 1 if categoria == cat else 0
        for cat in categorias_validas
    }


def _aplicar_camada_manchester(esi: int, sinais: dict) -> str:
    """
    Converte o acuity ESI predito para a cor do Protocolo de Manchester.

    Estratégia:
      - Mapeamento base: ESI 1→VERMELHO ... ESI 5→AZUL (concordância ordinal
        confirmada na literatura, κ=0.51).
      - Override clínico apenas para VERMELHO: discriminadores com embasamento
        sólido na literatura que não foram usados para construir o target
        (sem data leakage).
    """
    cor_base = ESI_PARA_MANCHESTER.get(esi, "AMARELO")

    o2sat     = sinais.get("o2sat")         or 100
    sbp       = sinais.get("sbp")           or 120
    heartrate = sinais.get("heartrate")     or 80
    resprate  = sinais.get("resprate")      or 16
    temp_c    = sinais.get("temperature_c") or 37.0

    sinais_criticos = (
        o2sat < 90
        or sbp < 80
        or heartrate > 150 or heartrate < 40
        or resprate > 30   or resprate < 8
        or temp_c > 40.5   or temp_c < 35.0
    )

    if sinais_criticos:
        return "VERMELHO"

    return cor_base


class ModeloTriagem:

    def prever(self, sinais: dict) -> dict:
        """
        Recebe sinais vitais no formato da API (campos em português,
        temperatura em Celsius) e retorna corPrevista e confianca.

        Campos esperados (todos opcionais — ausentes recebem mediana do treino):
          temperatura (°C), frequencia_cardiaca, frequencia_respiratoria,
          saturacao_o2, pressao_sistolica, pressao_diastolica, dor (0–10),
          queixa_principal (texto livre, opcional),
          ambulancia (bool, opcional),
          sexo_masculino (bool, opcional)
        """
        import re

        temp_c = sinais.get("temperatura")

        chegada_critica = 1 if sinais.get("ambulancia") else 0
        sexo_masculino  = 1 if sinais.get("sexo_masculino") else 0

        # Categoriza a queixa e converte para one-hot
        queixa_texto    = sinais.get("queixa_principal") or ""
        categoria       = _categorizar_queixa(queixa_texto)
        queixa_features = _queixa_para_features(categoria)

        dados_modelo = {
            "temperature":    _celsius_para_fahrenheit(temp_c),
            "heartrate":      sinais.get("frequencia_cardiaca"),
            "resprate":       sinais.get("frequencia_respiratoria"),
            "o2sat":          sinais.get("saturacao_o2"),
            "sbp":            sinais.get("pressao_sistolica"),
            "dbp":            sinais.get("pressao_diastolica"),
            "pain":           sinais.get("dor"),
            "chegada_critica": chegada_critica,
            "sexo_masculino":  sexo_masculino,
            **queixa_features,
        }

        df = pd.DataFrame([dados_modelo], columns=FEATURES)

        for col in FEATURES:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Imputa ausentes com medianas do treino
        for col in FEATURES:
            if df[col].isna().any():
                df[col] = df[col].fillna(MEDIANAS_TREINO[col])

        esi       = int(model.predict(df)[0])
        proba     = model.predict_proba(df)[0]
        classes   = list(model.classes_)
        idx       = classes.index(esi)
        confianca = round(float(proba[idx]), 4)

        sinais_para_manchester = {
            "temperature_c": temp_c,
            "heartrate":     sinais.get("frequencia_cardiaca"),
            "resprate":      sinais.get("frequencia_respiratoria"),
            "o2sat":         sinais.get("saturacao_o2"),
            "sbp":           sinais.get("pressao_sistolica"),
        }

        cor = _aplicar_camada_manchester(esi, sinais_para_manchester)

        return {
            "corPrevista": cor,
            "confianca":   confianca,
        }


# ── Teste rápido: python modelo.py ───────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        {
            "nome": "Emergência crítica (VERMELHO esperado)",
            "sinais": {
                "temperatura": 41.0, "frequencia_cardiaca": 158,
                "frequencia_respiratoria": 32, "saturacao_o2": 86,
                "pressao_sistolica": 72, "pressao_diastolica": 48,
                "dor": 9, "ambulancia": True,
                "queixa_principal": "Chest pain, dyspnea",
            },
        },
        {
            "nome": "Muito urgente (LARANJA esperado)",
            "sinais": {
                "temperatura": 39.2, "frequencia_cardiaca": 118,
                "frequencia_respiratoria": 24, "saturacao_o2": 93,
                "pressao_sistolica": 100, "pressao_diastolica": 65,
                "dor": 7, "ambulancia": True,
                "queixa_principal": "Dyspnea",
            },
        },
        {
            "nome": "Urgente (AMARELO esperado)",
            "sinais": {
                "temperatura": 38.6, "frequencia_cardiaca": 105,
                "frequencia_respiratoria": 20, "saturacao_o2": 94,
                "pressao_sistolica": 98, "pressao_diastolica": 65,
                "dor": 7, "queixa_principal": "Abd pain",
            },
        },
        {
            "nome": "Pouco urgente (VERDE esperado)",
            "sinais": {
                "temperatura": 37.5, "frequencia_cardiaca": 82,
                "frequencia_respiratoria": 16, "saturacao_o2": 98,
                "pressao_sistolica": 125, "pressao_diastolica": 80,
                "dor": 4, "queixa_principal": "s/p Fall, knee pain",
            },
        },
        {
            "nome": "Não urgente (AZUL esperado)",
            "sinais": {
                "temperatura": 36.8, "frequencia_cardiaca": 70,
                "frequencia_respiratoria": 14, "saturacao_o2": 99,
                "pressao_sistolica": 122, "pressao_diastolica": 78,
                "dor": 1, "queixa_principal": "Sore throat",
            },
        },
    ]

    m = ModeloTriagem()
    print("=" * 65)
    for caso in casos:
        resultado = m.prever(caso["sinais"])
        queixa    = caso["sinais"].get("queixa_principal", "—")
        print(f"Caso  : {caso['nome']}")
        print(f"Queixa: {queixa}")
        print(f"  → {resultado['corPrevista']:<10}  Confiança: {resultado['confianca']}")
        print()