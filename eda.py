
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load dataset
df = pd.read_csv("dataset/student_performance.csv")

# Create folder for EDA results
os.makedirs("reports", exist_ok=True)

print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)
print("\nFirst 5 records:")
print(df.head())

print("\n========== DATASET INFORMATION ==========")
df.info()

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())
print("Total missing cells:", df.isnull().sum().sum())

print("\n========== DUPLICATE RECORDS ==========")
print("Duplicates:", df.duplicated().sum())

print("\n========== STATISTICAL SUMMARY ==========")
print(df.describe().round(2))

print("\n========== GRADE DISTRIBUTION ==========")
print(df["final_grade"].value_counts().sort_index())

print("\n========== ASSIGNMENT CONSISTENCY ==========")
invalid = df[
    df["assignments_completed"] > df["assignments_total"]
]
print("Invalid assignment records:", len(invalid))

print("\n========== TARGET ANALYSIS ==========")
print("Final score range:")
print(df["final_score"].min(), "to", df["final_score"].max())

print("\nAverage final score by grade:")
print(df.groupby("final_grade")["final_score"].mean().round(2))

# 2. Missing values visualization
plt.figure(figsize=(12, 5))
sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
plt.title("Missing Values in Student Dataset")
plt.tight_layout()
plt.savefig("reports/missing_values.png")
plt.close()

# 3. Final score distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["final_score"].dropna(), bins=30, kde=True)
plt.title("Distribution of Final Scores")
plt.xlabel("Final Score")
plt.tight_layout()
plt.savefig("reports/final_score_distribution.png")
plt.close()

# 4. Grade distribution
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x="final_grade", order=sorted(df["final_grade"].dropna().unique()))
plt.title("Student Grade Distribution")
plt.xlabel("Final Grade")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig("reports/grade_distribution.png")
plt.close()

# 5. Correlation analysis
numeric_df = df.select_dtypes(include=np.number)
corr = numeric_df.corr()

print("\n========== CORRELATION WITH FINAL SCORE ==========")
print(corr["final_score"].sort_values(ascending=False).round(3))

plt.figure(figsize=(11, 8))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig("reports/correlation_heatmap.png")
plt.close()

# 6. Final score against grade
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x="final_grade", y="final_score")
plt.title("Final Score Distribution by Grade")
plt.tight_layout()
plt.savefig("reports/score_by_grade.png")
plt.close()

print("\nEDA completed. Check the reports folder for graphs.")
