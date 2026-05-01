import random


class ModeloTriagem:

    def prever(self, sinais):

        idade = sinais.get("idade")
        frequencia_cardiaca = sinais.get("frequencia_cardiaca")
        pressao_sistolica = sinais.get("pressao_sistolica")
        pressao_diastolica = sinais.get("pressao_diastolica")
        saturacao_o2 = sinais.get("saturacao_o2")
        temperatura = sinais.get("temperatura")
        frequencia_respiratoria = sinais.get("frequencia_respiratoria")
        dor = sinais.get("dor")

        print(f"Idade: {idade}")
        print(f"FC: {frequencia_cardiaca}")
        print(f"PA Sistólica: {pressao_sistolica}")
        print(f"PA Diastólica: {pressao_diastolica}")
        print(f"Saturação O2: {saturacao_o2}")
        print(f"Temperatura: {temperatura}")
        print(f"FR: {frequencia_respiratoria}")
        print(f"Dor: {dor}")

        cores = ["VERMELHO", "LARANJA", "AMARELO", "VERDE", "AZUL"]

        return {
            "corPrevista": random.choice(cores),
            "confianca": round(random.uniform(0.60, 0.99), 2),
        }
