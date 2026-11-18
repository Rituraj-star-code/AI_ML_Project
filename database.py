
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "student_performance.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                age INTEGER NOT NULL,
                attendance_percentage REAL NOT NULL,
                study_hours_per_week REAL NOT NULL,
                previous_grade REAL NOT NULL,
                assignments_total INTEGER NOT NULL,
                assignments_completed INTEGER NOT NULL,
                internal_marks REAL NOT NULL,
                quiz_average REAL NOT NULL,
                class_participation_score REAL NOT NULL,
                predicted_score REAL NOT NULL,
                predicted_grade TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_prediction(student_data, predicted_score, predicted_grade):
    keys = [
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

    values = tuple(student_data[key] for key in keys)

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO predictions (
                age, attendance_percentage,
                study_hours_per_week, previous_grade,
                assignments_total, assignments_completed,
                internal_marks, quiz_average,
                class_participation_score,
                predicted_score, predicted_grade
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, values + (predicted_score, predicted_grade))

        return cursor.lastrowid


def get_prediction_history(limit=50):
    with get_connection() as conn:
        records = conn.execute("""
            SELECT *
            FROM predictions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(record) for record in records]

def get_analytics():
    with get_connection() as conn:

        summary = conn.execute("""
            SELECT
                COUNT(*) AS total_predictions,
                AVG(predicted_score) AS average_score
            FROM predictions
        """).fetchone()

        grade_records = conn.execute("""
            SELECT
                predicted_grade,
                COUNT(*) AS total
            FROM predictions
            GROUP BY predicted_grade
        """).fetchall()

    return {
        "total_predictions": summary["total_predictions"],
        "average_score": round(summary["average_score"], 2)
            if summary["average_score"] is not None else 0,
        "grade_distribution": {
            record["predicted_grade"]: record["total"]
            for record in grade_records
        }
    }


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print("Database location:", DB_PATH)


