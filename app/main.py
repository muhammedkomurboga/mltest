import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

app = FastAPI()
model = joblib.load("model.joblib")

PREDICTIONS = Counter(
    "model_predictions_total", "Aantal voorspellingen per klasse", ["predicted_class"]
)
CONFIDENCE = Histogram(
    "model_prediction_confidence", "Hoogste klasse-waarschijnlijkheid",
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
)

Instrumentator().instrument(app).expose(app)


class Input(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: Input):
    expected = model.n_features_in_
    if len(data.features) != expected:
        raise HTTPException(status_code=422, detail=f"Expected {expected} features, got {len(data.features)}")
    X = np.array([data.features])
    pred = model.predict(X)
    proba = model.predict_proba(X)[0]
    PREDICTIONS.labels(predicted_class=str(pred[0])).inc()
    CONFIDENCE.observe(float(proba.max()))
    return {"prediction": pred.tolist()}
