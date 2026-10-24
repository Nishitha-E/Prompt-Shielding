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

SCENARIO_TEMPLATES = [
    {
        "type": "PG Admission Application",
        "sop": "I am applying for admission into Postgraduate Degree program having qualified GATE 2026 with score {gate_score}. B.Tech CGPA: {cgpa} / 10.0.",
    },
    {
        "type": "Post-Matric Scholarship & Fee Reimbursement",
        "sop": "Submitting application for State Government ePASS scholarship renewal. Cleared all semester exams with 88% attendance.",
    },
    {
        "type": "Campus Hostel Accommodation Request",
        "sop": "Requesting hostel room allotment in campus hostel. Permanent resident of Warangal district, daily travel not possible.",
    },
    {
        "type": "Semester Examination Hall Ticket Verification",
        "sop": "Requesting duplicate hall ticket for semester exams. Paid exam challan fee of Rs. 1,500.",
    },
    {
        "type": "Campus Placement & Internship Registration",
        "sop": "Registering for campus placement drive. Preferred role: AI Security Analyst. Completed Python and Network Security projects.",
    },
    {
        "type": "Education Loan Bank Verification",
        "sop": "Bank verification certificate for SBI Scholar education loan sanction of Rs. 2,00,000.",
    },
    {
        "type": "Official Transcript Application",
        "sop": "Requesting official transcripts for higher education. Completed M.E. coursework with distinction.",
    },
    {
        "type": "Tuition Fee Payment via UPI Verification",
        "sop": "Paid semester tuition fee of Rs. 35,000 through UPI portal. UTR transaction verified by bank.",
    },
    {
        "type": "Library Clearance Certificate",
        "sop": "Central library dues clearance request for semester hall ticket issuance. All borrowed books returned.",
    },
    {
        "type": "Re-evaluation & Recounting Request",
        "sop": "Requesting recounting for Advanced Cryptography subject. Current grade B+, expected A grade.",
    }
]

samples = []

for i in range(1, 51):
    template = SCENARIO_TEMPLATES[(i - 1) % len(SCENARIO_TEMPLATES)]
    college = COLLEGES[(i - 1) % len(COLLEGES)]
    degree = DEGREES[(i - 1) % len(DEGREES)]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    
    has_salutation = (i % 3 != 0)
    if has_salutation:
        salutation = "Mr." if i % 2 == 0 else "Ms."
        student_name = f"{salutation} {first} {last}"
    else:
        student_name = f"{first} {last}"

    roll_num = f"1005-26-{random.randint(701, 799)}"
    app_num = f"OU26-{random.randint(10000, 99999)}"

    dob_day = random.randint(1, 28)
    dob_month = random.randint(1, 12)
    dob_year = random.randint(2000, 2004)
    dob_str = f"{dob_day:02d}/{dob_month:02d}/{dob_year}"

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

    entities = [
        {"type": "STUDENT_ID", "value": roll_num},
        {"type": "STUDENT_ID", "value": app_num},
        {"type": "DOB", "value": dob_str},
        {"type": "AADHAAR", "value": aadhaar_fmt},
        {"type": "PAN", "value": pan_code},
        {"type": "MOBILE", "value": phone},
        {"type": "EMAIL", "value": email},
        {"type": "BANK_ACCOUNT", "value": ac_num},
        {"type": "IFSC", "value": ifsc_code},
        {"type": "UPI", "value": upi_id},
        {"type": "PINCODE", "value": pincode},
    ]

    extra_narrative = ""

    # Real-world challenge 1: Unanchored names in body text (FN)
    # In 14 samples, student or guardian name appears in narrative without header
    if i % 3 == 0:
        guardian = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        extra_narrative += f" I discussed my admission with my guardian {guardian}."
        entities.append({"type": "STUDENT_NAME", "value": student_name})
        entities.append({"type": "STUDENT_NAME", "value": guardian})
        name_line = f"Applicant: {student_name}" if i % 2 == 0 else f"I, {student_name}, submit this form."
    else:
        entities.append({"type": "STUDENT_NAME", "value": student_name})
        name_line = f"Student Name: {student_name}"

    # Real-world challenge 2: Ambiguous 6-digit numbers in text (causing FP)
    # In 8 samples, 6-digit challan or rank number triggers pincode regex or vice versa
    if i in [5, 11, 17, 23, 29, 35, 41, 47]:
        challan_no = f"5000{random.randint(10, 99)}"
        extra_narrative += f" Venue PIN Code: {challan_no}."

    # Real-world challenge 3: Pincode without header (FN)
    # In 6 samples, pincode is written inline like "Hyderabad 500007"
    if i in [7, 14, 21, 28, 38, 44]:
        address_line = f"Address: Near Tarnaka, Hyderabad - {pincode}"
    else:
        address_line = f"Address PIN Code: {pincode}"

    sop_text = template["sop"].format(gate_score=random.randint(620, 750), cgpa=round(random.uniform(8.1, 9.4), 2))

    text = (
        f"{college}\n"
        f"Application: {template['type']}\n"
        f"{name_line}\n"
        f"Roll No: {roll_num} | Application No: {app_num}\n"
        f"Course: {degree}\n"
        f"DOB: {dob_str} | Aadhaar: {aadhaar_fmt} | PAN: {pan_code}\n"
        f"Contact: {phone} | Email: {email}\n"
        f"{address_line}\n"
        f"Bank A/c No: {ac_num} | IFSC: {ifsc_code} | Fee UPI: {upi_id}\n\n"
        f"Statement:\n"
        f"{sop_text}{extra_narrative}\n\n"
        f"Please verify my details."
    )

    samples.append({
        "id": i,
        "college": college,
        "degree": degree,
        "scenario_type": template["type"],
        "text": text,
        "entities": entities
    })

with open("data/education_eval_samples.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2)

print(f"Generated {len(samples)} realistic test samples in data/education_eval_samples.json")
