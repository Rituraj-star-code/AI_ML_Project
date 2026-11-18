
import os
import joblib
import json
import pandas as pd

from flask import Flask, request, jsonify, render_template

from database import (
    init_db,
    save_prediction,
    get_prediction_history,
    get_analytics
)


# --------------------------------------------------
# 1. Flask application configuration
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REGRESSION_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "regression_model.pkl"
)

CLASSIFICATION_MODEL_PATH = os.path.join(
    BASE_DIR, "models", "classification_model.pkl"
)

MODEL_METADATA_PATH = os.path.join(
    BASE_DIR, "models", "model_metadata.json"
)


# --------------------------------------------------
# 2. Load trained ML models
# --------------------------------------------------

regression_model = joblib.load(REGRESSION_MODEL_PATH)
classification_model = joblib.load(CLASSIFICATION_MODEL_PATH)

print("Regression model loaded successfully!")
print("Classification model loaded successfully!")

# --------------------------------------------------
# 2A. Load model evaluation metadata
# --------------------------------------------------

with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as file:
    model_metadata = json.load(file)

print("Model metadata loaded successfully!")


# --------------------------------------------------
# 3. Initialize database
# --------------------------------------------------

init_db()


# --------------------------------------------------
# 4. Define model input features
# --------------------------------------------------

FEATURES = [
    "age",
    "attendance_percentage",
    "study_hours_per_week",
    "previous_grade",
    "assignments_total",
    "assignment_completion_rate",
    "internal_marks",
    "quiz_average",
    "class_participation_score"
]


# --------------------------------------------------
# 5. Validate student input
# --------------------------------------------------

def validate_student_data(data):

    required_fields = [
        "age",
        "attendance_percentage",
        "study_hours_per_week",
        "previous_grade",
        "assignments_total",
        "assignments_completed",
        "internal_marks",
        "quiz_average",
        "class_participation_score"
    ]

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")

    numeric_data = {}

    for field in required_fields:
        try:
            value = float(data[field])
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be numeric")

        if not pd.notna(value):
            raise ValueError(f"{field} must be a valid number")

        numeric_data[field] = value

    if not numeric_data["age"].is_integer():
        raise ValueError("Age must be a whole number")

    if numeric_data["age"] < 10 or numeric_data["age"] > 100:
        raise ValueError("Age must be between 10 and 100")

    if numeric_data["assignments_total"].is_integer() is False:
        raise ValueError("Total assignments must be a whole number")

    if numeric_data["assignments_completed"].is_integer() is False:
        raise ValueError("Completed assignments must be a whole number")

    total = int(numeric_data["assignments_total"])
    completed = int(numeric_data["assignments_completed"])

    if total < 0:
        raise ValueError("Total assignments cannot be negative")

    if completed < 0 or completed > total:
        raise ValueError("Invalid completed assignment count")

    if numeric_data["study_hours_per_week"] < 0 or numeric_data["study_hours_per_week"] > 168:
        raise ValueError("Study hours must be between 0 and 168")

    score_fields = [
        "attendance_percentage",
        "previous_grade",
        "internal_marks",
        "quiz_average",
        "class_participation_score"
    ]

    for field in score_fields:
        if not 0 <= numeric_data[field] <= 100:
            raise ValueError(f"{field} must be between 0 and 100")

    return numeric_data


# --------------------------------------------------
# 6. Home route
# --------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# 7. Prediction route
# --------------------------------------------------

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Please provide valid JSON data"}), 400

        student_data = validate_student_data(data)

        # Calculate engineered feature
        total = student_data["assignments_total"]
        completed = student_data["assignments_completed"]

        completion_rate = completed / total if total > 0 else 0

        # Prepare model input
        model_input = {
            "age": student_data["age"],
            "attendance_percentage": student_data["attendance_percentage"],
            "study_hours_per_week": student_data["study_hours_per_week"],
            "previous_grade": student_data["previous_grade"],
            "assignments_total": total,
            "assignment_completion_rate": completion_rate,
            "internal_marks": student_data["internal_marks"],
            "quiz_average": student_data["quiz_average"],
            "class_participation_score": student_data["class_participation_score"]
        }

        input_df = pd.DataFrame(
            [model_input],
            columns=FEATURES
        )

        # Independent model predictions
        predicted_score = float(
            regression_model.predict(input_df)[0]
        )

        predicted_grade = str(
            classification_model.predict(input_df)[0]
        )

        # Save prediction to database
        record_id = save_prediction(
            student_data,
            predicted_score,
            predicted_grade
        )

        return jsonify({
            "status": "success",
            "prediction_id": record_id,
            "predicted_score": round(predicted_score, 2),
            "predicted_grade": predicted_grade
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "An internal error occurred during prediction"
        }), 500


# --------------------------------------------------
# 8. Prediction history route
# --------------------------------------------------

@app.route("/api/history", methods=["GET"])
def history():

    try:
        records = get_prediction_history()

        return jsonify({
            "status": "success",
            "total_records": len(records),
            "records": records
        })

    except Exception:
        app.logger.exception("History retrieval failed")
        return jsonify({
            "error": "Unable to retrieve prediction history"
        }), 500

@app.route("/api/analytics", methods=["GET"])
def analytics():
    try:
        data = get_analytics()

        return jsonify({
            "status": "success",
            "total_predictions": data["total_predictions"],
            "average_score": data["average_score"],
            "grade_distribution": data["grade_distribution"]
        }), 200

    except Exception:
        app.logger.exception("Analytics retrieval failed")

        return jsonify({
            "error": "Unable to retrieve analytics"
        }), 500


# --------------------------------------------------
# 9. Model performance route
# --------------------------------------------------

@app.route("/api/model-performance", methods=["GET"])
def model_performance():

    try:
        return jsonify({
            "status": "success",
            "model_performance": model_metadata
        }), 200

    except Exception:
        app.logger.exception("Model performance retrieval failed")

        return jsonify({
            "error": "Unable to retrieve model performance"
        }), 500


# --------------------------------------------------
# 10. Run Flask application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
