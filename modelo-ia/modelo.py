from pathlib import Path
import pandas as pd
import joblib

# BASE_DIR aponta para a raiz do projeto (dois níveis acima de modelo-ia/)
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "triagem_model.pkl"

model = joblib.load(MODEL_PATH)

# Ordem das features exatamente igual ao treino (train.py)
FEATURES = ["temperature", "heartrate", "resprate", "o2sat", "sbp", "dbp", "pain"]


def _celsius_para_fahrenheit(celsius):
    """O modelo foi treinado com temperatura em Fahrenheit (padrão MIMIC-IV)."""
    if celsius is None:
        return None
    return celsius * 9 / 5 + 32


def _mapear_cor_manchester(pred: int, sinais_celsius: dict) -> str:
    """
    Refina a saída binária do modelo para as 5 cores do Protocolo Manchester.

    O modelo foi treinado com a escala ESI do MIMIC-IV:
      pred=1 → acuity 1-2 → VERMELHO ou LARANJA  (alta prioridade)
      pred=0 → acuity 3-5 → AMARELO, VERDE ou AZUL (baixa prioridade)

    O refinamento usa limiares clínicos do MTS para separar as cores
    dentro de cada grupo.
    """
    o2sat     = sinais_celsius.get("o2sat")     or 100
    sbp       = sinais_celsius.get("sbp")       or 120
    heartrate = sinais_celsius.get("heartrate") or 80
    resprate  = sinais_celsius.get("resprate")  or 16
    temp_c    = sinais_celsius.get("temperature_c") or 37.0
    pain      = sinais_celsius.get("pain")      or 0

    if pred == 1:
        # Alta prioridade — distingue VERMELHO de LARANJA
        # Critérios de VERMELHO: risco imediato de vida (falência de órgão)
        critico = (
            o2sat < 90
            or sbp < 80
            or heartrate > 150 or heartrate < 40
            or resprate > 30  or resprate < 8
            or temp_c > 40.5  or temp_c < 35.0
        )
        return "VERMELHO" if critico else "LARANJA"

    else:
        # Baixa prioridade — distingue AMARELO, VERDE e AZUL
        # AMARELO: urgente (sinais limítrofes ou dor intensa)
        if (
            pain >= 7
            or o2sat < 95
            or sbp < 100
            or heartrate > 120
            or temp_c > 38.5
        ):
            return "AMARELO"

        # VERDE: pouco urgente
        if pain >= 4:
            return "VERDE"

        # AZUL: não urgente
        return "AZUL"


class ModeloTriagem:

    def prever(self, sinais: dict) -> dict:
        """
        Recebe os sinais vitais no formato da API (campos em português,
        temperatura em Celsius) e retorna corPrevista e confianca.

        Campos esperados:
          temperatura (°C), frequencia_cardiaca, frequencia_respiratoria,
          saturacao_o2, pressao_sistolica, pressao_diastolica, dor (0-10)
        """

        temp_c = sinais.get("temperatura")

        # Traduz campos da API para os nomes do treino.
        # Temperatura é convertida de Celsius → Fahrenheit (padrão MIMIC-IV).
        dados_modelo = {
            "temperature": _celsius_para_fahrenheit(temp_c),
            "heartrate":   sinais.get("frequencia_cardiaca"),
            "resprate":    sinais.get("frequencia_respiratoria"),
            "o2sat":       sinais.get("saturacao_o2"),
            "sbp":         sinais.get("pressao_sistolica"),
            "dbp":         sinais.get("pressao_diastolica"),
            "pain":        sinais.get("dor"),
        }

        df = pd.DataFrame([dados_modelo], columns=FEATURES)

        for col in FEATURES:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Preenche nulos com mediana (mesmo tratamento do treino)
        df = df.fillna(df.median())

        pred      = int(model.predict(df)[0])
        proba     = model.predict_proba(df)[0]
        confianca = round(float(proba[pred]), 4)

        # Passa sinais em Celsius + demais para o mapeamento de cor
        sinais_para_cor = {
            "temperature_c": temp_c,
            "heartrate":     sinais.get("frequencia_cardiaca"),
            "resprate":      sinais.get("frequencia_respiratoria"),
            "o2sat":         sinais.get("saturacao_o2"),
            "sbp":           sinais.get("pressao_sistolica"),
            "pain":          sinais.get("dor"),
        }

        cor = _mapear_cor_manchester(pred, sinais_para_cor)

        return {
            "corPrevista": cor,
            "confianca": confianca,
        }


# ── Teste rápido: python modelo.py ───────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        {
            "nome": "Emergência crítica (VERMELHO esperado)",
            "sinais": {
                "temperatura": 41.0, "frequencia_cardiaca": 158,
                "frequencia_respiratoria": 32, "saturacao_o2": 86,
                "pressao_sistolica": 72, "pressao_diastolica": 48, "dor": 9,
            },
        },
        {
            "nome": "Muito urgente (LARANJA esperado)",
            "sinais": {
                "temperatura": 39.2, "frequencia_cardiaca": 118,
                "frequencia_respiratoria": 24, "saturacao_o2": 93,
                "pressao_sistolica": 100, "pressao_diastolica": 65, "dor": 7,
            },
        },
        {
            "nome": "Urgente (AMARELO esperado)",
            "sinais": {
                "temperatura": 38.6, "frequencia_cardiaca": 105,
                "frequencia_respiratoria": 20, "saturacao_o2": 94,
                "pressao_sistolica": 98, "pressao_diastolica": 65, "dor": 7,
            },
        },
        {
            "nome": "Pouco urgente (VERDE esperado)",
            "sinais": {
                "temperatura": 37.5, "frequencia_cardiaca": 82,
                "frequencia_respiratoria": 16, "saturacao_o2": 98,
                "pressao_sistolica": 125, "pressao_diastolica": 80, "dor": 4,
            },
        },
        {
            "nome": "Não urgente (AZUL esperado)",
            "sinais": {
                "temperatura": 36.8, "frequencia_cardiaca": 70,
                "frequencia_respiratoria": 14, "saturacao_o2": 99,
                "pressao_sistolica": 122, "pressao_diastolica": 78, "dor": 1,
            },
        },
    ]

    m = ModeloTriagem()
    print("=" * 60)
    for caso in casos:
        resultado = m.prever(caso["sinais"])
        print(f"Caso : {caso['nome']}")
        print(f"  Cor: {resultado['corPrevista']:<10}  Confiança: {resultado['confianca']}")
        print()