"""SQLite persistence layer."""
import sqlite3
from contextlib import contextmanager

DB_PATH = "patients.db"


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                glucose REAL NOT NULL,
                haemoglobin REAL NOT NULL,
                cholesterol REAL NOT NULL,
                remarks TEXT DEFAULT ''
            )"""
        )


def email_exists(email, exclude_id=None):
    with connect() as conn:
        row = conn.execute(
            "SELECT id FROM patients WHERE email = ? AND id IS NOT ?", (email, exclude_id)
        ).fetchone()
    return row is not None


def create_patient(p):
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO patients (full_name, dob, email, glucose, haemoglobin, cholesterol, remarks) "
            "VALUES (:full_name, :dob, :email, :glucose, :haemoglobin, :cholesterol, :remarks)", p)
        return cur.lastrowid


def list_patients():
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM patients ORDER BY id")]


def update_patient(patient_id, p):
    with connect() as conn:
        conn.execute(
            "UPDATE patients SET full_name=:full_name, dob=:dob, email=:email, glucose=:glucose, "
            "haemoglobin=:haemoglobin, cholesterol=:cholesterol, remarks=:remarks WHERE id=:id",
            {**p, "id": patient_id})


def delete_patient(patient_id):
    with connect() as conn:
        conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
