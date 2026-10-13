import sys

import joblib
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score

THRESHOLD = 1.10

X, y = load_iris(return_X_y=True)
model = joblib.load("model.joblib")
accuracy = accuracy_score(y, model.predict(X))

print(f"accuracy: {accuracy:.3f} (minimum: {THRESHOLD})")
if accuracy < THRESHOLD:
    print("Model validation FAILED")
    sys.exit(1)
print("Model validation passed")
