from fastapi import FastAPI
from pydantic import BaseModel
import joblib, numpy as np

app = FastAPI()
model = joblib.load("model.joblib")

class Input(BaseModel):
    features: list[float]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: Input):
    pred = model.predict(np.array([data.features]))
    return {"prediction": pred.tolist()}
