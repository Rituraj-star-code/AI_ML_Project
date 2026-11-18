
import joblib
import json

# Load regression model
reg_model = joblib.load(
    "models/regression_model.pkl"
)

# Load classification model
clf_model = joblib.load(
    "models/classification_model.pkl"
)

# Load metadata
with open("models/model_metadata.json", "r") as file:
    metadata = json.load(file)

print("Regression model loaded:", type(reg_model).__name__)
print("Classification model loaded:", type(clf_model).__name__)

print("\nModel metadata:")
print(metadata)

print("\nAll saved models loaded successfully!")
