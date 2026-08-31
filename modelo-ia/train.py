"""
train.py
────────
Treina um classificador Random Forest para prever o acuity ESI (1–5)
a partir do dataset pré-processado gerado pelo prepare_dataset.py.

O modelo aprende a classificação clínica real registrada pelos
enfermeiros do MIMIC-IV-ED. A conversão para o Protocolo de Manchester
é responsabilidade da camada de adaptação em modelo-ia/modelo.py.
"""

from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import joblib

# ── Caminhos ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset_processado.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ── 1. Carregar dataset processado ────────────────────────────────────────────
print("Carregando dataset processado...")

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset não encontrado em {DATA_PATH}.\n"
        "Execute prepare_dataset.py antes de treinar."
    )

df = pd.read_csv(DATA_PATH)
print(f"  {len(df):,} registros carregados")

target = "acuity"

features = [c for c in df.columns if c != target]

X = df[features]
y = df[target]

print("\nDistribuição do target (acuity ESI):")
dist = y.value_counts().sort_index()
manchester = {1: "VERMELHO", 2: "LARANJA", 3: "AMARELO", 4: "VERDE", 5: "AZUL"}
for acuity, count in dist.items():
    print(f"  ESI {acuity} ({manchester[acuity]}): {count:>7,}  ({count/len(y)*100:.2f}%)")

# ── 2. Divisão treino / teste ─────────────────────────────────────────────────
# stratify garante que a proporção de cada classe seja mantida nos dois splits,
# essencial dado o desbalanceamento (ESI 5 = 0.26% dos dados).
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

print(f"\nTreino : {len(X_train):,} amostras")
print(f"Teste  : {len(X_test):,} amostras")

# ── 3. Treinamento ────────────────────────────────────────────────────────────
# class_weight="balanced" compensa o desbalanceamento entre as classes
# sem necessidade de oversampling — o Random Forest ajusta o peso de cada
# amostra inversamente proporcional à frequência da sua classe.
print("\nTreinando Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    n_jobs=1,        # ← era -1
)

model.fit(X_train, y_train)
print("Treinamento concluído.")

# ── 4. Avaliação no conjunto de teste ─────────────────────────────────────────
print("\n=== Avaliação no conjunto de teste ===")

pred = model.predict(X_test)

print(f"\nAcurácia geral: {accuracy_score(y_test, pred):.4f}")

print("\nRelatório por classe:")
target_names = [f"ESI {i} ({manchester[i]})" for i in sorted(y.unique())]
print(classification_report(y_test, pred, target_names=target_names))

print("Matriz de confusão:")
print(confusion_matrix(y_test, pred))

# ── 5. Validação cruzada (5-fold) ─────────────────────────────────────────────
# Confirma que o desempenho não é artefato do split específico.
print("\n=== Validação cruzada (5-fold, F1-macro) ===")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=1)

print(f"F1-macro por fold: {[round(s, 4) for s in scores]}")
print(f"Média : {scores.mean():.4f}")
print(f"Desvio: {scores.std():.4f}")

# ── 6. Importância das features ───────────────────────────────────────────────
print("\n=== Importância das features ===")
importances = sorted(
    zip(features, model.feature_importances_),
    key=lambda x: x[1],
    reverse=True,
)
for feat, imp in importances:
    bar = "█" * int(imp * 50)
    print(f"  {feat:<20} {imp:.4f}  {bar}")

# ── 7. Salvar modelo ──────────────────────────────────────────────────────────
model_path = MODEL_DIR / "triagem_model.pkl"
joblib.dump(model, model_path)
print(f"\nModelo salvo em: {model_path}")