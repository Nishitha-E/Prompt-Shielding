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

COLLEGES = [
    "University College of Engineering, Osmania University",
    "JNTU College of Engineering, Hyderabad",
    "National Institute of Technology, Warangal",
    "College of Technology, Osmania University",
    "Indian Institute of Technology, Hyderabad"
]

DEGREES = [
    "M.E. Cyber Security (Semester 1)",
    "B.Tech Computer Science and Engineering",
    "M.Tech Artificial Intelligence and Data Science",
    "B.Tech Information Technology",
    "M.Sc Computer Science"
]

SCENARIOS = [
    "I am applying for admission having qualified GATE 2026 with score {gate_score}. B.Tech CGPA: {cgpa} / 10.0.",
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

for i in range(1, 51):
    college = COLLEGES[(i - 1) % len(COLLEGES)]
    degree = DEGREES[(i - 1) % len(DEGREES)]
    scenario_sop = SCENARIOS[(i - 1) % len(SCENARIOS)]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    
    has_salutation = (i % 3 != 0)
    if has_salutation:
        salutation = "Mr." if i % 2 == 0 else "Ms."
        name_val = f"{salutation} {first} {last}"
    else:
        name_val = f"{first} {last}"

    roll_num = f"1005-26-{random.randint(701, 799)}"
    app_num = f"OU26-{random.randint(10000, 99999)}"
    dob = f"{random.randint(1, 28):02d}/{random.randint(1, 12):02d}/{random.randint(2000, 2004)}"

    phone = f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
    email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"

    base11 = f"{random.randint(2, 9)}{random.randint(1000000000, 9999999999)}"
    aadhaar_digits = generate_verhoeff_number(base11)
    aadhaar_fmt = f"{aadhaar_digits[:4]} {aadhaar_digits[4:8]} {aadhaar_digits[8:]}"

    pan_code = f"ABC{random.choice('P')}{random.choice('K')}{random.randint(1000, 9999)}{random.choice('Z')}"
    ac_num = f"{random.randint(20000000000, 99999999999)}"
    ifsc_code = f"SBIN000{random.randint(1000, 9999)}"
    upi_id = f"{first.lower()}{random.randint(10, 99)}@oksbi"
    pincode = f"5000{random.randint(10, 99)}"

    # Minimal Indian PII only: Aadhaar, PAN, Mobile, Email, Bank A/c, IFSC, UPI, PIN, Name
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

    # Real-world challenge 1: Unanchored names in body text (FN)
    if i % 3 == 0:
        guardian = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        extra_note += f" I consulted with my guardian {guardian}."
        entities.append({"type": "NAME", "value": name_val})
        entities.append({"type": "NAME", "value": guardian})
        name_line = f"Applicant: {name_val}" if i % 2 == 0 else f"I, {name_val}, submit this form."
    else:
        entities.append({"type": "NAME", "value": name_val})
        name_line = f"Student Name: {name_val}"

    # Real-world challenge 2: Ambiguous 6-digit campus venue PIN (FP)
    if i in [5, 11, 17, 23, 29, 35, 41, 47]:
        venue_code = f"5000{random.randint(10, 99)}"
        extra_note += f" Venue PIN Code: {venue_code}."

    # Real-world challenge 3: Inline address without "PIN Code:" keyword (FN)
    if i in [7, 14, 21, 28, 38, 44]:
        address_line = f"Address: Hyderabad - {pincode}"
    else:
        address_line = f"Address PIN Code: {pincode}"

    sop_formatted = scenario_sop.format(gate_score=random.randint(620, 750), cgpa=round(random.uniform(8.1, 9.4), 2))

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
        f"{sop_formatted}{extra_note}\n\n"
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

print(f"Generated {len(samples)} samples with minimal Indian PII only.")
