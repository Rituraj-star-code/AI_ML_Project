
from app import app

client = app.test_client()

student_data = {
    "age": 21,
    "attendance_percentage": 85,
    "study_hours_per_week": 15,
    "previous_grade": 75,
    "assignments_total": 10,
    "assignments_completed": 9,
    "internal_marks": 80,
    "quiz_average": 78,
    "class_participation_score": 85
}

# Test prediction API
response = client.post(
    "/api/predict",
    json=student_data
)

print("Prediction API Status:", response.status_code)
print("\nPrediction Response:")
print(response.get_json())

# Test history API
history_response = client.get("/api/history")

print("\nHistory API Status:", history_response.status_code)
print("\nHistory Response:")
print(history_response.get_json())
