# app/main.py
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Load Models
models = {}
try:
    models["Logistic Regression"] = joblib.load("models/logistic_model.pkl")
    models["Random Forest"] = joblib.load("models/rf_model.pkl")
    models["XGBoost"] = joblib.load("models/xgb_model.pkl")
    print("All models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}. Make sure you ran train_model.py first.")

class LoanInput(BaseModel):
    person_age: int
    person_income: float
    person_home_ownership: str
    person_emp_length: float
    loan_intent: str
    loan_grade: str
    loan_amnt: float
    loan_int_rate: float
    loan_percent_income: float
    cb_person_default_on_file: str
    cb_person_cred_hist_length: int
    selected_model: str

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_loan(data: LoanInput):
    # Convert input to DataFrame
    input_data = {
        'person_age': [data.person_age],
        'person_income': [data.person_income],
        'person_home_ownership': [data.person_home_ownership],
        'person_emp_length': [data.person_emp_length],
        'loan_intent': [data.loan_intent],
        'loan_grade': [data.loan_grade],
        'loan_amnt': [data.loan_amnt],
        'loan_int_rate': [data.loan_int_rate],
        'loan_percent_income': [data.loan_percent_income],
        'cb_person_default_on_file': [data.cb_person_default_on_file],
        'cb_person_cred_hist_length': [data.cb_person_cred_hist_length]
    }
    
    df = pd.DataFrame(input_data)
    
    # Select Model
    model = models.get(data.selected_model)
    if not model:
        return {"error": "Model not found"}
    
    # Predict
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]
    
    result = "Default" if prediction == 1 else "No Default"
    risk_level = "High" if probability > 0.7 else "Medium" if probability > 0.3 else "Low"

    return {
        "prediction": result,
        "probability": float(probability),
        "risk_level": risk_level,
        "model_used": data.selected_model
    }