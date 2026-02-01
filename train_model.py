# train_model.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
import joblib # Added for saving models
import os

# Create models directory if not exists
if not os.path.exists('models'):
    os.makedirs('models')

# --- Step 1: Data Loading ---
# Adjusted path for local/docker environment
try:
    df = pd.read_csv("credit_risk_dataset.csv")
    print("Dataset loaded successfully!")
except FileNotFoundError:
    print("Error: 'credit_risk_dataset.csv' not found. Please place it in the project root.")
    exit()

# Identify categorical and numerical columns
numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

if 'loan_status' in numerical_cols:
    numerical_cols.remove('loan_status')

# --- Step 2: Data Preprocessing ---
print("\n--- Step 2: Data Preprocessing ---")

# Simple imputation
for col in numerical_cols:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].mean(), inplace=True)

for col in categorical_cols:
    if df[col].isnull().sum() > 0:
        df[col].fillna(df[col].mode()[0], inplace=True)

# Define features (X) and target (y)
X = df.drop('loan_status', axis=1)
y = df['loan_status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])

# --- Step 3: Model Training ---

print("\n--- Step 3: Model Training ---")

# 1. Logistic Regression
logistic_regression_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(solver='liblinear', random_state=42))
])
logistic_regression_pipeline.fit(X_train, y_train)
print("Logistic Regression trained.")

# 2. Random Forest
random_forest_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])
random_forest_pipeline.fit(X_train, y_train)
print("Random Forest trained.")

# 3. XGBoost
xgboost_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42))
])
xgboost_pipeline.fit(X_train, y_train)
print("XGBoost trained.")

# --- Step 4: Save Models (New Addition) ---
print("\n--- Saving Models to Pickle ---")
joblib.dump(logistic_regression_pipeline, 'models/logistic_model.pkl')
joblib.dump(random_forest_pipeline, 'models/rf_model.pkl')
joblib.dump(xgboost_pipeline, 'models/xgb_model.pkl')
print("Models saved successfully in 'models/' folder.")