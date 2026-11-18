
import pandas as pd
import numpy as np

# 1. Load cleaned dataset
df = pd.read_csv("dataset/cleaned_student_performance.csv")

print("Original shape:", df.shape)

# 2. Create assignment completion rate
df["assignment_completion_rate"] = np.where(
    df["assignments_total"] > 0,
    df["assignments_completed"] / df["assignments_total"],
    0
)

# 3. Display the new feature
print("\nAssignment completion rate:")
print(
    df[
        [
            "assignments_total",
            "assignments_completed",
            "assignment_completion_rate"
        ]
    ].head(10)
)

# 4. Check grade distribution
print("\nGrade distribution:")
print(df["final_grade"].value_counts().sort_index())

# 5. Analyze grade against final score
print("\nFinal score statistics by grade:")
print(
    df.groupby("final_grade")["final_score"]
    .agg(["count", "mean", "min", "max"])
    .round(2)
)


# Check consistency of grades with inferred score ranges

bins = [-float("inf"), 40, 50, 60, 70, 80, 90, float("inf")]

labels = ["F", "D", "C", "B", "A", "A+", "O"]

df["expected_grade"] = pd.cut(
    df["final_score"],
    bins=bins,
    labels=labels,
    right=False
)

mismatches = df[df["final_grade"] != df["expected_grade"]]

print("\nGrade mapping validation:")
print("Total mismatched records:", len(mismatches))

if len(mismatches) > 0:
    print("\nSample mismatches:")
    print(mismatches[[
        "final_score", "final_grade", "expected_grade"
    ]].head(10))

# Remove temporary validation column
df = df.drop(columns=["expected_grade"])

# Check assignment completion rate correlation

print("\nAssignment completion rate correlation with final_score:")

print(
    df["assignment_completion_rate"]
    .corr(df["final_score"])
)


# 6. Save feature-engineered dataset
output_path = "dataset/feature_engineered_student_performance.csv"

df.to_csv(output_path, index=False)

print("\nFeature engineering completed!")
print("New shape:", df.shape)
print("Saved at:", output_path)
