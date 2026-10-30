# Health Prediction App

Streamlit + SQLite app to manage patient blood-test records (CRUD) with AI-generated remarks (Google Gemini API).

## Structure
- `app.py` - Streamlit UI (Add / Records / Edit / Delete)
- `validators.py` - input validation (name, dd/mm/yyyy DOB, email, numeric ranges)
- `database.py` - SQLite storage
- `ai_service.py` - Gemini API call that produces the Remarks

## Run
```
pip install -r requirements.txt
cp .env.example .env     # add your own GEMINI_API_KEY (free key: https://aistudio.google.com/apikey)
streamlit run app.py
```

## Validation rules
- Name: letters, spaces, . ' - only
- DOB: real date, dd/mm/yyyy (dd.mm.yyyy is accepted and normalised), not in the future
- Email: valid format and unique
- Glucose / Haemoglobin / Cholesterol: numeric and within plausible ranges
