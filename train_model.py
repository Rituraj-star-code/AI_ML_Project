
import pandas as pd
import os
import json
import joblib

# Step 1: Load original dataset
df = pd.read_csv("dataset/student_performance.csv")

print("Dataset loaded successfully!")

# Step 2: Dataset dimensions
print("\nDataset shape:")
print(df.shape)

# Step 3: Column names
print("\nDataset columns:")
print(df.columns.tolist())

# Step 4: Missing values
print("\nMissing values:")
print(df.isnull().sum())

# Step 5: Grade distribution
print("\nGrade distribution:")
print(df["final_grade"].value_counts().sort_index())

# Step 6: Minimum class size
print("\nMinimum class size:")
print(df["final_grade"].value_counts().min())

# Step 7: Check duplicate student IDs
print("\nDuplicate student IDs:")
print(df["student_id"].duplicated().sum())


from sklearn.model_selection import train_test_split

# Step 8: Create assignment completion rate
df["assignment_completion_rate"] = (
    df["assignments_completed"]
    .div(df["assignments_total"].replace(0, float("nan")))
    .fillna(0)
)

# Step 9: Select input features
features = [
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

X = df[features]

# Step 10: Regression dataset
y_reg = df["final_score"]

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
    X,
    y_reg,
    test_size=0.2,
    random_state=42
)

# Step 11: Classification dataset
y_clf = df["final_grade"]

X_train_clf, X_test_clf, y_train_clf, y_test_clf = train_test_split(
    X,
    y_clf,
    test_size=0.2,
    random_state=42,
    stratify=y_clf
)

# Step 12: Display split information
print("\n========== REGRESSION DATA SPLIT ==========")
print("Training features:", X_train_reg.shape)
print("Testing features:", X_test_reg.shape)
print("Training target:", y_train_reg.shape)
print("Testing target:", y_test_reg.shape)

print("\n========== CLASSIFICATION DATA SPLIT ==========")
print("Training features:", X_train_clf.shape)
print("Testing features:", X_test_clf.shape)
print("Training target:", y_train_clf.shape)
print("Testing target:", y_test_clf.shape)

print("\nTraining grade distribution:")
print(y_train_clf.value_counts().sort_index())

print("\nTesting grade distribution:")
print(y_test_clf.value_counts().sort_index())

# Step 13: Verify no student appears in both sets
print("\n========== DATA LEAKAGE CHECK ==========")

print(
    "Regression overlap:",
    len(set(X_train_reg.index) & set(X_test_reg.index))
)

print(
    "Classification overlap:",
    len(set(X_train_clf.index) & set(X_test_clf.index))
)

print("\nDataset splitting completed successfully!")



# ==========================================
# STEP 2: PREPROCESSING PIPELINES
# ==========================================

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from sklearn.dummy import DummyRegressor, DummyClassifier

from sklearn.linear_model import LinearRegression, LogisticRegression

from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier

from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from sklearn.model_selection import cross_validate


# ==========================================
# STEP 3: DEFINE REGRESSION MODELS
# ==========================================

regression_models = {

    "Dummy Regressor": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DummyRegressor(strategy="mean"))
    ]),

    "Linear Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ]),

    "Decision Tree Regressor": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DecisionTreeRegressor(random_state=42))
    ]),

    "Random Forest Regressor": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        ))
    ])
}


# ==========================================
# STEP 4: DEFINE CLASSIFICATION MODELS
# ==========================================

classification_models = {

    "Dummy Classifier": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DummyClassifier(strategy="most_frequent"))
    ]),

    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "Decision Tree Classifier": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", DecisionTreeClassifier(
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "Random Forest Classifier": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
}


print("\nAll regression and classification pipelines created successfully!")
print("Regression models:", list(regression_models.keys()))
print("Classification models:", list(classification_models.keys()))



# ==========================================
# STEP 5: REGRESSION MODEL EVALUATION
# USING 5-FOLD CROSS-VALIDATION
# ==========================================

regression_scoring = {
    "MAE": "neg_mean_absolute_error",
    "RMSE": "neg_root_mean_squared_error",
    "R2": "r2"
}

regression_results = []

print("\n========== REGRESSION CROSS-VALIDATION ==========")

for name, model in regression_models.items():

    scores = cross_validate(
        model,
        X_train_reg,
        y_train_reg,
        cv=5,
        scoring=regression_scoring,
        n_jobs=1
    )

    result = {"Model": name}

    for metric in regression_scoring:

        values = scores["test_" + metric]

        # sklearn returns negative values for error metrics
        if metric in ["MAE", "RMSE"]:
            values = -values

        result[metric + " Mean"] = values.mean()
        result[metric + " Std"] = values.std()

    regression_results.append(result)

    print("\nModel:", name)
    print(result)


# ==========================================
# STEP 6: CLASSIFICATION MODEL EVALUATION
# USING 5-FOLD CROSS-VALIDATION
# ==========================================

classification_scoring = {
    "Accuracy": "accuracy",
    "Precision": "precision_macro",
    "Recall": "recall_macro",
    "F1": "f1_macro",
    "Balanced Accuracy": "balanced_accuracy"
}

classification_results = []

print("\n========== CLASSIFICATION CROSS-VALIDATION ==========")

for name, model in classification_models.items():

    scores = cross_validate(
        model,
        X_train_clf,
        y_train_clf,
        cv=5,
        scoring=classification_scoring,
        n_jobs=1
    )

    result = {"Model": name}

    for metric in classification_scoring:

        values = scores["test_" + metric]

        result[metric + " Mean"] = values.mean()
        result[metric + " Std"] = values.std()

    classification_results.append(result)

    print("\nModel:", name)
    print(result)


print("\n========== CROSS-VALIDATION COMPLETED ==========")



# ==========================================
# STEP 7: FINAL MODEL TRAINING
# AND TEST SET EVALUATION
# ==========================================

import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# REGRESSION: LINEAR REGRESSION
# ==========================================

print("\n========== REGRESSION TEST EVALUATION ==========")

best_reg_model = regression_models["Linear Regression"]

# Train using all training records
best_reg_model.fit(X_train_reg, y_train_reg)

# Predict scores for unseen test records
reg_predictions = best_reg_model.predict(X_test_reg)

# Calculate regression metrics
reg_mae = mean_absolute_error(y_test_reg, reg_predictions)

reg_rmse = np.sqrt(
    mean_squared_error(y_test_reg, reg_predictions)
)

reg_r2 = r2_score(y_test_reg, reg_predictions)

print("Selected Model: Linear Regression")
print("MAE:", reg_mae)
print("RMSE:", reg_rmse)
print("R2 Score:", reg_r2)


# ==========================================
# CLASSIFICATION: RANDOM FOREST
# ==========================================

print("\n========== CLASSIFICATION TEST EVALUATION ==========")

best_clf_model = classification_models["Random Forest Classifier"]

# Train using all training records
best_clf_model.fit(X_train_clf, y_train_clf)

# Predict grades for unseen test records
clf_predictions = best_clf_model.predict(X_test_clf)

# Calculate classification metrics
clf_accuracy = accuracy_score(
    y_test_clf, clf_predictions
)

clf_precision = precision_score(
    y_test_clf, clf_predictions,
    average="macro",
    zero_division=0
)

clf_recall = recall_score(
    y_test_clf, clf_predictions,
    average="macro",
    zero_division=0
)

clf_f1 = f1_score(
    y_test_clf, clf_predictions,
    average="macro",
    zero_division=0
)

clf_balanced_accuracy = balanced_accuracy_score(
    y_test_clf, clf_predictions
)

print("Selected Model: Random Forest Classifier")
print("Accuracy:", clf_accuracy)
print("Macro Precision:", clf_precision)
print("Macro Recall:", clf_recall)
print("Macro F1:", clf_f1)
print("Balanced Accuracy:", clf_balanced_accuracy)


# ==========================================
# DETAILED CLASSIFICATION REPORT
# ==========================================

print("\n========== CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test_clf,
        clf_predictions,
        labels=sorted(y_clf.unique()),
        zero_division=0
    )
)


# ==========================================
# CONFUSION MATRIX
# ==========================================

print("\n========== CONFUSION MATRIX ==========")

labels = sorted(y_clf.unique())

cm = confusion_matrix(
    y_test_clf,
    clf_predictions,
    labels=labels
)

print("Grade labels:", labels)
print(cm)


print("\n========== TEST EVALUATION COMPLETED ==========")


# ==========================================
# STEP 8: REGRESSION-BASED GRADE PREDICTION
# ==========================================

print("\n========== REGRESSION-BASED GRADE PREDICTION ==========")

# Convert predicted numerical scores into provisional grades
def score_to_grade(score):

    if score < 40:
        return "F"
    elif score < 50:
        return "D"
    elif score < 60:
        return "C"
    elif score < 70:
        return "B"
    elif score < 80:
        return "A"
    elif score < 90:
        return "A+"
    else:
        return "O"


# Convert regression predictions into grade labels
score_grade_predictions = [
    score_to_grade(score) for score in reg_predictions
]

# Evaluate predicted grades
score_grade_accuracy = accuracy_score(
    y_test_clf,
    score_grade_predictions
)

score_grade_f1 = f1_score(
    y_test_clf,
    score_grade_predictions,
    average="macro",
    zero_division=0
)

score_grade_balanced_accuracy = balanced_accuracy_score(
    y_test_clf,
    score_grade_predictions
)

print("Regression-based Grade Accuracy:", score_grade_accuracy)
print("Regression-based Macro F1:", score_grade_f1)
print("Regression-based Balanced Accuracy:", score_grade_balanced_accuracy)

print("\nRegression-based Classification Report:")

print(
    classification_report(
        y_test_clf,
        score_grade_predictions,
        labels=labels,
        zero_division=0
    )
)

print("\nRegression-based Confusion Matrix:")

print(
    confusion_matrix(
        y_test_clf,
        score_grade_predictions,
        labels=labels
    )
)


# ==========================================
# STEP 9: LOGISTIC REGRESSION TEST EVALUATION
# ==========================================

print("\n========== LOGISTIC REGRESSION TEST EVALUATION ==========")

# Select Logistic Regression pipeline
log_model = classification_models["Logistic Regression"]

# Train using training data only
log_model.fit(X_train_clf, y_train_clf)

# Predict grades for test data
log_predictions = log_model.predict(X_test_clf)

# Calculate evaluation metrics
log_accuracy = accuracy_score(
    y_test_clf,
    log_predictions
)

log_precision = precision_score(
    y_test_clf,
    log_predictions,
    average="macro",
    zero_division=0
)

log_recall = recall_score(
    y_test_clf,
    log_predictions,
    average="macro",
    zero_division=0
)

log_f1 = f1_score(
    y_test_clf,
    log_predictions,
    average="macro",
    zero_division=0
)

log_balanced_accuracy = balanced_accuracy_score(
    y_test_clf,
    log_predictions
)

# Display metrics
print("Selected Model: Logistic Regression")
print("Accuracy:", log_accuracy)
print("Macro Precision:", log_precision)
print("Macro Recall:", log_recall)
print("Macro F1:", log_f1)
print("Balanced Accuracy:", log_balanced_accuracy)

# Classification report
print("\n========== LOGISTIC REGRESSION CLASSIFICATION REPORT ==========")

print(
    classification_report(
        y_test_clf,
        log_predictions,
        labels=labels,
        zero_division=0
    )
)

# Confusion matrix
print("\n========== LOGISTIC REGRESSION CONFUSION MATRIX ==========")

print("Grade labels:", labels)

print(
    confusion_matrix(
        y_test_clf,
        log_predictions,
        labels=labels
    )
)

print("\n========== LOGISTIC REGRESSION EVALUATION COMPLETED ==========")


# ==========================================
# STEP 10: MODEL PERSISTENCE
# ==========================================

print("\n========== SAVING TRAINED MODELS ==========")

# Create models directory if it does not exist
os.makedirs("models", exist_ok=True)

# Save regression model
joblib.dump(
    best_reg_model,
    "models/regression_model.pkl"
)

print("Regression model saved successfully!")

# Save selected classification model
joblib.dump(
    log_model,
    "models/classification_model.pkl"
)

print("Classification model saved successfully!")

# Feature names used by both models
feature_columns = [
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

# Store model information and evaluation metrics
metadata = {
    "regression_model": {
        "name": "Linear Regression",
        "target": "final_score",
        "MAE": 5.7422,
        "RMSE": 7.2377,
        "R2": 0.6056
    },

    "classification_model": {
        "name": "Logistic Regression",
        "target": "final_grade",
        "accuracy": 0.3825,
        "macro_f1": 0.3418,
        "balanced_accuracy": 0.4136
    },

    "features": feature_columns,
    "training_records": 1600,
    "testing_records": 400,
    "random_state": 42
}

# Save metadata as JSON
with open("models/model_metadata.json", "w") as file:
    json.dump(metadata, file, indent=4)

print("Model metadata saved successfully!")

print("\nAll model files saved successfully!")


