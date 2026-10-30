"""Input validation for patient records."""
import re
from datetime import datetime, date

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,99}$")

# (min, max, unit) - plausibility limits, not diagnostic limits
RANGES = {
    "glucose": (20, 600, "mg/dL"),
    "haemoglobin": (3, 25, "g/dL"),
    "cholesterol": (50, 700, "mg/dL"),
}


def validate_name(value):
    value = value.strip()
    if not NAME_RE.match(value):
        raise ValueError("Full name must contain letters only (2-100 characters).")
    return value


def validate_dob(value):
    """Accepts dd/mm/yyyy (dd.mm.yyyy and dd-mm-yyyy are normalised to dd/mm/yyyy)."""
    text = re.sub(r"[.\-]", "/", value.strip())
    try:
        dob = datetime.strptime(text, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("Date of birth must be a real date in dd/mm/yyyy format.")
    if dob > date.today():
        raise ValueError("Date of birth cannot be in the future.")
    if (date.today() - dob).days > 120 * 366:
        raise ValueError("Date of birth is more than 120 years ago.")
    return dob.strftime("%d/%m/%Y")


def validate_email(value):
    value = value.strip()
    if not EMAIL_RE.match(value):
        raise ValueError("Email address format is invalid (e.g. name@example.com).")
    return value.lower()


def validate_number(field, value):
    low, high, unit = RANGES[field]
    try:
        number = float(str(value).strip())
    except ValueError:
        raise ValueError(f"{field.capitalize()} must be a number.")
    if not low <= number <= high:
        raise ValueError(f"{field.capitalize()} must be between {low} and {high} {unit}.")
    return number


def validate_patient(form):
    """Validate a dict of raw strings. Returns (clean_dict, list_of_errors)."""
    checks = {
        "full_name": lambda v: validate_name(v),
        "dob": lambda v: validate_dob(v),
        "email": lambda v: validate_email(v),
        "glucose": lambda v: validate_number("glucose", v),
        "haemoglobin": lambda v: validate_number("haemoglobin", v),
        "cholesterol": lambda v: validate_number("cholesterol", v),
    }
    clean, errors = {}, []
    for key, check in checks.items():
        try:
            clean[key] = check(form.get(key, ""))
        except ValueError as exc:
            errors.append(str(exc))
    return clean, errors
