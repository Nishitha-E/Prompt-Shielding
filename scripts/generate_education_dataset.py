"""Generate 50 synthetic hand-labeled education prompt samples for Prompt Shield evaluation benchmark."""

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

EDUCATION_SCENARIOS = [
    {
        "type": "PG Admission Application",
        "purpose": "Application for admission into Postgraduate Degree program.",
        "course_detail": "Qualified GATE 2026 with score 680. Seeking admission under merit quota.",
        "academic_record": "B.Tech CGPA: 8.85 / 10.0 from Osmania University.",
    },
    {
        "type": "Post-Matric Scholarship & Fee Reimbursement",
        "purpose": "State Government ePASS Post-Matric Scholarship renewal.",
        "course_detail": "Enrolled in M.E. Cyber Security, Year 1. Annual family income below 2 Lakhs.",
        "academic_record": "Previous year semester attendance: 88%. Cleared all subjects in single attempt.",
    },
    {
        "type": "Campus Hostel Accommodation Request",
        "purpose": "Hostel room allotment in Osmania University Campus Hostels.",
        "course_detail": "Permanent resident of Warangal district. Daily commuting not feasible.",
        "academic_record": "Hostel caution deposit paid. Category: Non-Local Merit.",
    },
    {
        "type": "Semester Examination Hall Ticket Verification",
        "purpose": "Request for issuance of duplicate hall ticket for Semester End Exams.",
        "course_detail": "Examination: M.E. Cyber Security regular examinations November 2026.",
        "academic_record": "Examination fee paid challan submitted to college exam branch.",
    },
    {
        "type": "Campus Placement & Internship Registration",
        "purpose": "Registration for On-Campus Placement Drive 2026-27.",
        "course_detail": "Preferred roles: AI Security Engineer, Vulnerability Analyst, SOC Analyst.",
        "academic_record": "Aggregate CGPA: 8.65, zero active backlogs, Python and C++ certified.",
    },
    {
        "type": "Education Loan Bank Account Verification",
        "purpose": "Bank verification certificate for SBI Scholar Education Loan disbursement.",
        "course_detail": "Tuition fee per annum: Rs. 85,000. Sanctioned loan amount: Rs. 2,00,000.",
        "academic_record": "Bonafide student certificate and fee structure estimation attached.",
    },
    {
        "type": "Official Transcript & Degree Bonafide",
        "purpose": "Application for official transcripts for higher education.",
        "course_detail": "Completed M.E. coursework. Requesting 3 sets of sealed transcripts.",
        "academic_record": "Degree awarded with First Class with Distinction.",
    },
    {
        "type": "Tuition Fee Payment via UPI Verification",
        "purpose": "Online college fee payment confirmation slip.",
        "course_detail": "Semester 2 Tuition Fee Rs. 35,000 paid via SBI UPI Collect portal.",
        "academic_record": "UTR Transaction reference successfully verified by accounts branch.",
    },
    {
        "type": "Library Clearance & Digital Access Card",
        "purpose": "Clearance certificate from University Central Library.",
        "course_detail": "All borrowed IEEE and AI security textbooks returned without dues.",
        "academic_record": "Eligible for final semester hall ticket issuance.",
    },
    {
        "type": "Re-evaluation & Grade Verification Request",
        "purpose": "Request for paper recounting and answer script photocopy.",
        "course_detail": "Subject: Advanced Cryptography and Network Security (Code: CS501).",
        "academic_record": "Current grade: B+ (expected A grade based on answer key evaluation).",
    }
]

samples = []

for i in range(1, 51):
    scenario = EDUCATION_SCENARIOS[(i - 1) % len(EDUCATION_SCENARIOS)]
    college = COLLEGES[(i - 1) % len(COLLEGES)]
    degree = DEGREES[(i - 1) % len(DEGREES)]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    salutation = random.choice(["Mr.", "Ms."])
    student_name = f"{salutation} {first} {last}"

    roll_num = f"1005-26-{random.randint(701, 799)}"
    app_num = f"OU26-{random.randint(10000, 99999)}"

    dob_day = random.randint(1, 28)
    dob_month = random.randint(1, 12)
    dob_year = random.randint(2000, 2004)
    dob_str = f"{dob_day:02d}/{dob_month:02d}/{dob_year}"

    phone = f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"
    email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@gmail.com"

    # Verhoeff Aadhaar
    base11 = f"{random.randint(2, 9)}{random.randint(1000000000, 9999999999)}"
    aadhaar_digits = generate_verhoeff_number(base11)
    aadhaar_fmt = f"{aadhaar_digits[:4]} {aadhaar_digits[4:8]} {aadhaar_digits[8:]}"

    # PAN
    pan_code = f"ABC{random.choice('P')}{random.choice('K')}{random.randint(1000, 9999)}{random.choice('Z')}"

    # Bank Account & IFSC
    ac_num = f"{random.randint(20000000000, 99999999999)}"
    ifsc_code = f"SBIN000{random.randint(1000, 9999)}"
    upi_id = f"{first.lower()}{random.randint(10, 99)}@oksbi"

    # PIN Code
    pincode = f"5000{random.randint(10, 99)}"

    entities = [
        {"type": "STUDENT_NAME", "value": student_name},
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

    # In 4 edge case samples, include an unanchored family name or guardian in statement text
    if i in [12, 24, 36, 48]:
        guardian_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        scenario_text_extra = f"Guardian {guardian_name} visited campus for verification."
        entities.append({"type": "STUDENT_NAME", "value": guardian_name})
    else:
        scenario_text_extra = ""

    # In 2 edge case samples, include an exam centre pin code that creates an ambiguous detection
    if i in [15, 30]:
        exam_pincode = f"5000{random.randint(10, 99)}"
        scenario_text_extra += f" Exam Centre PIN Code: {exam_pincode}."

    text = (
        f"--- {college.upper()} ---\n"
        f"STUDENT ENQUIRY & APPLICATION FORM: {scenario['type'].upper()}\n"
        f"Student Name: {student_name}\n"
        f"Roll No: {roll_num} | Application No: {app_num}\n"
        f"Course: {degree}\n"
        f"DOB: {dob_str} | Aadhaar: {aadhaar_fmt} | PAN: {pan_code}\n"
        f"Contact: {phone} | Email: {email}\n"
        f"Address PIN Code: {pincode}\n"
        f"Bank A/c No: {ac_num} | IFSC: {ifsc_code} | Fee UPI: {upi_id}\n\n"
        f"STATEMENT OF PURPOSE & DETAILS:\n"
        f"{scenario['purpose']}\n"
        f"{scenario['course_detail']}\n"
        f"{scenario_text_extra}\n\n"
        f"ACADEMIC QUALIFICATIONS:\n"
        f"{scenario['academic_record']}\n\n"
        f"Please verify my submission and provide confirmation."
    )

    samples.append({
        "id": i,
        "college": college,
        "degree": degree,
        "scenario_type": scenario["type"],
        "text": text,
        "entities": entities
    })

with open("data/education_eval_samples.json", "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2)

print(f"Successfully generated {len(samples)} hand-labeled Education Sector evaluation records!")
