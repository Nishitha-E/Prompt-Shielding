import csv
import json
from pathlib import Path

csv_path = Path("data/indic_synthetic_profiles.csv")
if not csv_path.exists():
    raise FileNotFoundError("Missing data/indic_synthetic_profiles.csv dataset file.")

with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    dataset_rows = [next(reader) for _ in range(50)]

SCENARIOS = [
    "I am applying for admission having qualified GATE with score 680. B.Tech CGPA: 8.85 / 10.0.",
    "Submitting application for state post-matric scholarship fee reimbursement. Attendance 88%.",
    "Requesting hostel accommodation in campus hostel. Permanent resident of Warangal.",
    "Requesting duplicate hall ticket for semester exams. Paid exam challan fee of Rs. 1,500.",
    "Registering for campus placement drive. Preferred role: AI Security Analyst.",
    "Bank verification certificate for SBI Scholar education loan sanction of Rs. 2,00,000.",
    "Requesting official transcripts for higher education. Coursework completed with distinction.",
    "Paid semester tuition fee of Rs. 35,000 through online UPI portal. Transaction verified.",
    "Central library clearance request for semester hall ticket issuance. Books returned.",
    "Requesting recounting for Advanced Cryptography subject. Current grade B+, expected A."
]

samples = []

for i, row in enumerate(dataset_rows, start=1):
    college = row["college"] if row["college"] else "University College of Engineering, Osmania University"
    degree = row["degree"] if row["degree"] else "M.E. Cyber Security"
    scenario_sop = SCENARIOS[(i - 1) % len(SCENARIOS)]

    name_val = row["name"]
    roll_num = f"1005-26-{700 + i}"
    app_num = f"OU26-{40000 + i}"
    dob = row["dob"]

    phone = row["phone"]
    email = row["email"]
    aadhaar_fmt = row["aadhaar"]
    pan_code = row["pan"]
    ac_num = row["bank_account_account"]
    ifsc_code = row["bank_account_ifsc"]
    upi_id = row["upi_id"]
    pincode = row["pincode"]

    entities = [
        {"type": "AADHAAR", "value": aadhaar_fmt},
        {"type": "PAN", "value": pan_code},
        {"type": "MOBILE", "value": phone},
        {"type": "EMAIL", "value": email},
        {"type": "BANK_ACCOUNT", "value": ac_num},
        {"type": "IFSC", "value": ifsc_code},
        {"type": "UPI", "value": upi_id},
        {"type": "PINCODE", "value": pincode},
    ]

    extra_note = ""

    if i % 3 == 0:
        guardian = dataset_rows[(i + 5) % len(dataset_rows)]["name"]
        extra_note += f" I consulted with my guardian {guardian}."
        entities.append({"type": "NAME", "value": name_val})
        entities.append({"type": "NAME", "value": guardian})
        name_line = f"Applicant: {name_val}" if i % 2 == 0 else f"I, {name_val}, submit this form."
    else:
        entities.append({"type": "NAME", "value": name_val})
        name_line = f"Student Name: {name_val}"

    if i in [5, 11, 17, 23, 29, 35, 41, 47]:
        venue_code = f"5000{10 + i}"
        extra_note += f" Venue PIN Code: {venue_code}."

    if i in [7, 14, 21, 28, 38, 44]:
        address_line = f"Address: Hyderabad - {pincode}"
    else:
        address_line = f"Address PIN Code: {pincode}"

    text = (
        f"{college}\n"
        f"{name_line}\n"
        f"Roll No: {roll_num} | Application No: {app_num}\n"
        f"Course: {degree} | DOB: {dob}\n"
        f"Aadhaar: {aadhaar_fmt} | PAN: {pan_code}\n"
        f"Contact: {phone} | Email: {email}\n"
        f"{address_line}\n"
        f"Bank A/c No: {ac_num} | IFSC: {ifsc_code} | Fee UPI: {upi_id}\n\n"
        f"Statement:\n"
        f"{scenario_sop}{extra_note}\n\n"
        f"Please verify my details."
    )

    samples.append({
        "id": i,
        "college": college,
        "degree": degree,
        "text": text,
        "entities": entities
    })

with open("data/education_eval_samples.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2)

print(f"Generated {len(samples)} samples directly from data/indic_synthetic_profiles.csv")
