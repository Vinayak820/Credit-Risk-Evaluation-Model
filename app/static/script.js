document.addEventListener('DOMContentLoaded', function() {
    // --- 1. Auto-Calculation Logic ---
    const incomeInput = document.getElementById('person_income');
    const loanInput = document.getElementById('loan_amnt');
    const percentInput = document.getElementById('loan_percent_income');

    function calculatePercent() {
        const income = parseFloat(incomeInput.value);
        const loan = parseFloat(loanInput.value);

        if (!isNaN(income) && !isNaN(loan) && income > 0) {
            const percentage = ((loan / income) * 100).toFixed(2);
            percentInput.value = percentage;
        } else {
            percentInput.value = "0.00";
        }
    }

    incomeInput.addEventListener('input', calculatePercent);
    loanInput.addEventListener('input', calculatePercent);
    calculatePercent();
});

// --- 2. Dynamic Background Color Function ---
function updatePageBackground(probability) {
    const root = document.documentElement;
    let r, g, b;

    // TARGET DEFAULT COLOR: RGB(241, 245, 249) -> Matches CSS #f1f5f9

    if (probability < 0.5) {
        // --- SAFE ZONE (0% to 49%) ---
        // Blend: Mint Green (220, 252, 231)  ->  Default Gray (241, 245, 249)
        const p = probability * 2; 

        // Math: Start + (End - Start) * p
        r = Math.round(220 + (21 * p)); 
        g = Math.round(252 - (7 * p));  
        b = Math.round(231 + (18 * p)); 

    } else {
        // --- DANGER ZONE (50% to 100%) ---
        // Blend: Default Gray (241, 245, 249)  ->  Soft Red (254, 226, 226)
        const p = (probability - 0.5) * 2;

        r = Math.round(241 + (13 * p));
        g = Math.round(245 - (19 * p)); 
        b = Math.round(249 - (23 * p)); 
    }

    const newColor = `rgb(${r}, ${g}, ${b})`;
    root.style.setProperty('--bg-color', newColor);
}

// --- 3. Prediction Submission Logic ---
document.getElementById('predictionForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const btn = document.getElementById('predictBtn');
    btn.textContent = "Analyzing...";
    btn.disabled = true;

    const rawPercent = parseFloat(document.getElementById('loan_percent_income').value);
    const decimalPercent = rawPercent / 100;

    const formData = {
        person_age: parseInt(document.getElementById('person_age').value),
        person_income: parseFloat(document.getElementById('person_income').value),
        person_home_ownership: document.getElementById('person_home_ownership').value,
        person_emp_length: parseFloat(document.getElementById('person_emp_length').value),
        loan_intent: document.getElementById('loan_intent').value,
        loan_grade: document.getElementById('loan_grade').value,
        loan_amnt: parseFloat(document.getElementById('loan_amnt').value),
        loan_int_rate: parseFloat(document.getElementById('loan_int_rate').value),
        loan_percent_income: decimalPercent,
        cb_person_default_on_file: document.getElementById('cb_person_default_on_file').value,
        cb_person_cred_hist_length: parseInt(document.getElementById('cb_person_cred_hist_length').value),
        selected_model: document.getElementById('model_select').value
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        const resultDiv = document.getElementById('result');
        const predText = document.getElementById('res_pred');
        const probText = document.getElementById('res_prob');
        const riskText = document.getElementById('res_risk');

        resultDiv.classList.remove('hidden');
        predText.textContent = result.prediction;
        probText.textContent = (result.probability * 100).toFixed(2) + "%";
        riskText.textContent = result.risk_level;

        // Call the updated background function
        updatePageBackground(result.probability);

        if (result.prediction === "Default") {
            resultDiv.classList.add('danger-bg'); 
            predText.style.color = "#ef4444";
        } else {
            resultDiv.classList.remove('danger-bg');
            predText.style.color = "#10b981";
        }

        resultDiv.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during prediction.');
    } finally {
        btn.textContent = "Analyze Risk";
        btn.disabled = false;
    }
});