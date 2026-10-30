"""Health Prediction App - Streamlit frontend."""
import pandas as pd
import streamlit as st

import database as db
from ai_service import AIServiceError, predict_health_risk
from validators import validate_patient

st.set_page_config(page_title="Health Prediction App", page_icon="🩺", layout="wide")
db.init_db()

FIELDS = ["full_name", "dob", "email", "glucose", "haemoglobin", "cholesterol"]


def flash(kind, message):
    st.session_state["flash"] = (kind, message)


def show_flash():
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        getattr(st, kind)(message)
    if "warn" in st.session_state:
        st.warning(st.session_state.pop("warn"))


def process(form, patient_id=None):
    """Validate, run AI prediction and return (record, errors)."""
    clean, errors = validate_patient(form)
    if "email" in clean and db.email_exists(clean["email"], patient_id):
        errors.append("A record with this email already exists (duplicate).")
    if errors:
        return None, errors
    try:
        clean["remarks"] = predict_health_risk(clean)
    except AIServiceError as exc:
        clean["remarks"] = "AI prediction unavailable."
        st.session_state["warn"] = f"Record saved, but AI prediction failed: {exc}"
    return clean, []


def show_errors(errors):
    for err in errors:
        st.error(err)


st.title("🩺 Health Prediction App")
show_flash()
tab_add, tab_list, tab_edit, tab_delete = st.tabs(["➕ Add", "📋 Records", "✏️ Edit", "🗑️ Delete"])

with tab_add:
    with st.form("add_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        form = {
            "full_name": c1.text_input("Full Name"),
            "dob": c2.text_input("Date of Birth (dd/mm/yyyy)"),
            "email": c1.text_input("Email Address"),
            "glucose": c2.text_input("Glucose (mg/dL)"),
            "haemoglobin": c1.text_input("Haemoglobin (g/dL)"),
            "cholesterol": c2.text_input("Cholesterol (mg/dL)"),
        }
        submitted = st.form_submit_button("Save & Predict")
    if submitted:
        with st.spinner("Validating and calling AI API..."):
            record, errors = process(form)
        if errors:
            show_errors(errors)
        else:
            db.create_patient(record)
            flash("success", f"Saved {record['full_name']}. Remarks: {record['remarks']}")
            st.rerun()

patients = db.list_patients()

with tab_list:
    if patients:
        df = pd.DataFrame(patients).rename(columns={
            "id": "ID", "full_name": "Full Name", "dob": "Date of Birth", "email": "Email",
            "glucose": "Glucose", "haemoglobin": "Haemoglobin", "cholesterol": "Cholesterol",
            "remarks": "Remarks"})
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Total records: {len(df)}")
    else:
        st.info("No records yet.")


def picker(key):
    options = {f"{p['id']} - {p['full_name']} ({p['email']})": p for p in patients}
    return options[st.selectbox("Select record", list(options), key=key)]


with tab_edit:
    if not patients:
        st.info("No records to edit.")
    else:
        current = picker("edit_pick")
        with st.form(f"edit_form_{current['id']}"):
            c1, c2 = st.columns(2)
            edited = {
                "full_name": c1.text_input("Full Name", current["full_name"]),
                "dob": c2.text_input("Date of Birth (dd/mm/yyyy)", current["dob"]),
                "email": c1.text_input("Email Address", current["email"]),
                "glucose": c2.text_input("Glucose (mg/dL)", str(current["glucose"])),
                "haemoglobin": c1.text_input("Haemoglobin (g/dL)", str(current["haemoglobin"])),
                "cholesterol": c2.text_input("Cholesterol (mg/dL)", str(current["cholesterol"])),
            }
            update_clicked = st.form_submit_button("Update & Re-predict")
        if update_clicked:
            with st.spinner("Validating and calling AI API..."):
                record, errors = process(edited, current["id"])
            if errors:
                show_errors(errors)
            else:
                db.update_patient(current["id"], record)
                flash("success", f"Updated {record['full_name']}.")
                st.rerun()

with tab_delete:
    if not patients:
        st.info("No records to delete.")
    else:
        target = picker("delete_pick")
        confirm = st.checkbox("I confirm I want to delete this record")
        if st.button("Delete record", disabled=not confirm):
            db.delete_patient(target["id"])
            flash("success", f"Deleted {target['full_name']}.")
            st.rerun()
