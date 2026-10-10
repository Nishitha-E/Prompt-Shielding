"""Generate 50 synthetic hand-labeled medical clinical report samples for Prompt Shield evaluation benchmark."""

import json
import random
from promptshield.verhoeff import generate_verhoeff_number

random.seed(2026)

FIRST_NAMES = [
    "Rajesh", "Sunita", "Amit", "Priya", "Vikram", "Sneha", "Rohan", "Ananya",
    "Suresh", "Kavita", "Manoj", "Deepa", "Arun", "Pooja", "Harish", "Meera",
    "Karthik", "Swati", "Naveen", "Divya", "Ganesh", "Lakshmi", "Ramesh", "Shalini"
]

LAST_NAMES = [
    "Sharma", "Patel", "Reddy", "Nair", "Verma", "Rao", "Gupta", "Kulkarni",
    "Joshi", "Mehta", "Bose", "Chatterjee", "Mishra", "Deshmukh", "Singhania", "Iyer"
]

DOCTORS = [
    "Dr. Arvind Swaminathan", "Dr. Shalini Mukhopadhyay", "Dr. Rajesh Kothari",
    "Dr. Sunita Kulkarni", "Dr. Pradeep Venkat", "Dr. Ananya Roy", "Dr. Vikram Sethi"
]

HOSPITALS = [
    "Apollo Hospitals, Hyderabad", "AIIMS, New Delhi", "Fortis Healthcare, Bengaluru",
    "Manipal Hospital, Chennai", "Care Hospital, Banjara Hills", "KIMS Hospitals, Secunderabad"
]

CLINICAL_CASES = [
    {
        "type": "Discharge Summary - Cardiology",
        "diagnosis": "Coronary Artery Disease, Acute Inferior Wall Myocardial Infarction",
        "rx": "Tab Aspirin 75mg OD, Tab Clopidogrel 75mg OD, Tab Atorvastatin 40mg HS, Tab Metoprolol 25mg BD",
        "lab": "Troponin-I 4.8 ng/mL, Serum Creatinine 1.0 mg/dL, Total Cholesterol 230 mg/dL",
    },
    {
        "type": "Consultation Note - Endocrinology",
        "diagnosis": "Type 2 Diabetes Mellitus with Diabetic Peripheral Neuropathy",
        "rx": "Tab Metformin 1000mg BD, Tab Glimepiride 2mg OD, Cap Pregabalin 75mg HS",
        "lab": "HbA1c 8.9%, Fasting Blood Sugar 168 mg/dL, Postprandial Blood Sugar 245 mg/dL",
    },
    {
        "type": "Radiology Report - Chest HRCT",
        "diagnosis": "Bilateral Ground Glass Opacities consistent with Viral Pneumonitis",
        "rx": "Inhaler Budesonide 200mcg BD, Tab Azithromycin 500mg OD x 5 days, Tab Paracetamol 650mg SOS",
        "lab": "SpO2 94% on room air, CRP 42 mg/L, D-Dimer 0.6 mcg/mL",
    },
    {
        "type": "Pathology / CBC Blood Report",
        "diagnosis": "Microcytic Hypochromic Anemia",
        "rx": "Tab Ferrous Ascorbate 100mg + Folic Acid 1.5mg OD x 3 months",
        "lab": "Hemoglobin 8.4 g/dL, RBC 3.2 million/mcL, MCV 68 fL, Serum Ferritin 12 ng/mL",
    },
    {
        "type": "Orthopedic Consultation Slip",
        "diagnosis": "Grade II Osteoarthritis of Bilateral Knee Joints",
        "rx": "Tab Etoricoxib 90mg OD x 7 days, Tab Glucosamine 1500mg OD, Quadriceps strengthening physiotherapy",
        "lab": "Uric Acid 5.2 mg/dL, RA Factor Negative, ESR 18 mm/hr",
    },
    {
        "type": "Gastroenterology Discharge Note",
        "diagnosis": "Acute Pancreatitis, resolving; Cholelithiasis",
        "rx": "Tab Pantoprazole 40mg OD, Tab Ursodeoxycholic Acid 300mg BD, Low fat diet advised",
        "lab": "Serum Amylase 420 U/L, Serum Lipase 680 U/L, Total Bilirubin 1.2 mg/dL",
    },
    {
        "type": "Nephrology Progress Note",
        "diagnosis": "Chronic Kidney Disease Stage 3b, Hypertension",
        "rx": "Tab Amlodipine 5mg OD, Tab Torsemide 10mg OD, Tab Sodium Bicarbonate 500mg TDS",
        "lab": "eGFR 38 mL/min/1.73m2, Serum Creatinine 2.2 mg/dL, Blood Urea 65 mg/dL, Serum K+ 4.6 mEq/L",
    },
    {
        "type": "Dermatology Prescription Slip",
        "diagnosis": "Chronic Plaque Psoriasis",
        "rx": "Clobetasol Propionate 0.05% ointment local application, Tab Methotrexate 10mg weekly, Tab Folic Acid 5mg",
        "lab": "LFT normal, CBC normal, PASI Score 12.4",
    },
    {
        "type": "Neurology Consultation Summary",
        "diagnosis": "Migraine with Aura, Tension Type Headache",
        "rx": "Tab Propranolol 40mg OD, Tab Naproxen 500mg SOS during acute attack",
        "lab": "MRI Brain normal, Fundus examination normal",
    },
    {
        "type": "Pediatric / General Clinical Note",
        "diagnosis": "Acute Bronchiolitis, Mild Dehydration",
        "rx": "Saline nasal drops TDS, Paracetamol syrup 15mg/kg SOS, Oral rehydration therapy",
        "lab": "WBC 11,200/mcL, Platelets 280,000/mcL, CRP 14 mg/L",
    }
]

samples = []

for i in range(1, 51):
    case = CLINICAL_CASES[(i - 1) % len(CLINICAL_CASES)]
    hosp = HOSPITALS[(i - 1) % len(HOSPITALS)]
    
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    salutation = random.choice(["Mr.", "Mrs.", "Ms.", "Smt."])
    pt_name = f"{salutation} {first} {last}"
    
    doc = random.choice(DOCTORS)
    
    uhid_num = f"{random.randint(100000, 999999)}"
    mrn_num = f"MRN-{random.randint(10000, 99999)}"
    
    dob_day = random.randint(1, 28)
    dob_month = random.randint(1, 12)
    dob_year = random.randint(1955, 2005)
    dob_str = f"{dob_day:02d}/{dob_month:02d}/{dob_year}"
    age_yrs = 2026 - dob_year
    
    phone = f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
    email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"
    
    # 14-digit ABHA ID
    abha_p1 = random.randint(11, 99)
    abha_p2 = random.randint(1000, 9999)
    abha_p3 = random.randint(1000, 9999)
    abha_p4 = random.randint(1000, 9999)
    abha_id = f"{abha_p1}-{abha_p2}-{abha_p3}-{abha_p4}"
    
    # Checksum-valid Aadhaar
    base11 = f"{random.randint(2, 9)}{random.randint(1000000000, 9999999999)}"
    aadhaar_digits = generate_verhoeff_number(base11)
    aadhaar_fmt = f"{aadhaar_digits[:4]} {aadhaar_digits[4:8]} {aadhaar_digits[8:]}"
    
    entities = [
        {"type": "PATIENT_NAME", "value": pt_name},
        {"type": "PATIENT_ID", "value": uhid_num},
        {"type": "PATIENT_ID", "value": mrn_num.replace("MRN-", "")},
        {"type": "DOCTOR_NAME", "value": doc},
        {"type": "DOB", "value": dob_str},
        {"type": "ABHA", "value": abha_id},
        {"type": "MOBILE", "value": phone},
        {"type": "EMAIL", "value": email},
        {"type": "AADHAAR", "value": aadhaar_fmt},
    ]

    # Clinical Report Text Template
    text = (
        f"--- {hosp.upper()} ---\n"
        f"CLINICAL REPORT / {case['type'].upper()}\n"
        f"Patient Name: {pt_name}\n"
        f"UHID: {uhid_num} | MRN: {mrn_num}\n"
        f"DOB: {dob_str} | Age: {age_yrs} Y | Gender: {'Male' if salutation in ['Mr.', 'Shri'] else 'Female'}\n"
        f"ABHA ID: {abha_id} | Aadhaar: {aadhaar_fmt}\n"
        f"Contact: {phone} | Email: {email}\n"
        f"Consultant: {doc}\n\n"
        f"CLINICAL SUMMARY & DIAGNOSIS:\n"
        f"{case['diagnosis']}\n\n"
        f"INVESTIGATIONS & LAB FINDINGS:\n"
        f"{case['lab']}\n\n"
        f"MEDICATIONS & TREATMENT PLAN:\n"
        f"{case['rx']}\n\n"
        f"Follow-up in OPD after 14 days with repeat blood investigations."
    )

    samples.append({
        "id": i,
        "hospital": hosp,
        "report_type": case["type"],
        "text": text,
        "entities": entities
    })

with open("data/medical_eval_samples.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2)

print(f"Successfully generated {len(samples)} hand-labeled clinical evaluation records!")
