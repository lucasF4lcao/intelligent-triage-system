from fastapi import FastAPI
from pydantic import BaseModel

import modelo

modelo = modelo.ModeloTriagem()

app = FastAPI()


class SinaisVitaisRequest(BaseModel):
    idade: int | None = None
    frequencia_cardiaca: int | None = None
    pressao_sistolica: int | None = None
    pressao_diastolica: int | None = None
    saturacao_o2: int | None = None
    temperatura: float | None = None
    frequencia_respiratoria: int | None = None
    dor: int | None = None


class ClassificacaoResponse(BaseModel):
    corPrevista: str
    confianca: float


@app.post("/classificar", response_model=ClassificacaoResponse)
def classificar(sinais: SinaisVitaisRequest):

    resultado = modelo.prever(sinais.model_dump())

    return resultado


# uvicorn main:app --host 127.0.0.1 --port 5000 --reload
