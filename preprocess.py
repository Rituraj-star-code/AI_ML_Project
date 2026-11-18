
import os
import pandas as pd

# 1. Load original dataset
input_path = "dataset/student_performance.csv"

df = pd.read_csv(input_path)

print("Original dataset shape:", df.shape)

# 2. Check duplicate records
duplicate_count = df.duplicated().sum()

print("\nDuplicate records:", duplicate_count)

# Remove exact duplicate rows, if any
df = df.drop_duplicates()

# 3. Identify missing values
print("\nMissing values before cleaning:")
print(df.isnull().sum())

# 4. Handle missing values in numerical input features
# Do not impute target columns.
target_columns = ["final_score", "final_grade"]

numeric_columns = df.select_dtypes(include="number").columns

feature_columns = [
    col for col in numeric_columns
    if col not in target_columns
]

print("\nMedian values used for imputation:")

for col in feature_columns:
    if df[col].isnull().sum() > 0:
        median_value = df[col].median()
        df[col] = df[col].fillna(median_value)

        print(f"{col}: {median_value}")

# 5. Check missing target values separately
print("\nMissing target values:")
for col in target_columns:
    if col in df.columns:
        print(f"{col}: {df[col].isnull().sum()}")

# 6. Check assignment consistency
invalid_assignments = df[
    df["assignments_completed"] > df["assignments_total"]
]

print(
    "\nRecords where completed assignments exceed total:",
    len(invalid_assignments)
)

# 7. Check score-related columns for values outside 0-100
score_columns = [
    "attendance_percentage",
    "previous_grade",
    "internal_marks",
    "quiz_average",
    "class_participation_score",
    "final_score"
]

print("\nScore range validation:")

for col in score_columns:
    invalid_count = (
        ((df[col] < 0) | (df[col] > 100)).sum()
    )
    print(f"{col}: {invalid_count} invalid values")

# 8. Check missing values after cleaning
print("\nMissing values after cleaning:")
print(df.isnull().sum())

# 9. Save cleaned dataset
os.makedirs("dataset", exist_ok=True)

output_path = "dataset/cleaned_student_performance.csv"

df.to_csv(output_path, index=False)

print("\n================================")
print("DATA PREPROCESSING COMPLETED")
print("Original rows:", len(pd.read_csv(input_path)))
print("Cleaned rows:", len(df))
print("Cleaned dataset saved at:", output_path)
print("================================")
