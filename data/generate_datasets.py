"""Synthetic Data Generator for Hackathon PS-019.

Generates:
- 5 realistic CSV datasets with messy formatting, decoys, nulls, and misleading names.
- 1 SQLite database (enterprise_vault.db) with 4 realistic tables.
- metadata.csv (with declared purpose and retention schedules, some deliberately missing).
- labels.csv (ground truth labels for precision/recall evaluation).
- rules.yaml (configurable detection rules).
Uses a fixed random seed for 100% reproducibility.
"""

import os
import random
import sqlite3
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import yaml

from src.detectors.verhoeff import generate_verhoeff

SEED = 42
random.seed(SEED)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Synthetic name parts
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Diya", "Saanvi", "Aanya", "Aadhya", "Pari", "Ananya", "Riya", "Myra", "Sneha", "Kavya",
    "Rajesh", "Pooja", "Vikram", "Sunita", "Amit", "Deepa", "Rahul", "Priya", "Suresh", "Meena",
]
LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Nair", "Iyer", "Rao", "Gupta", "Deshmukh", "Chatterjee",
    "Bose", "Mehta", "Joshi", "Kulkarni", "Singh", "Kumar", "Choudhury", "Bhatt", "Menon", "Pillai",
]
HONORIFICS = ["Mr. ", "Ms. ", "Mrs. ", "Dr. ", ""]

DOMAINS = [
    "gmail.com", "yahoo.co.in", "outlook.com", "enterprise.in", "cybercorp.org",
    "fintechvault.com", "techsecure.co.in", "globalinfra.net",
]

PRODUCTS = [
    "UltraScreen 4K Monitor", "Quantum SSD 2TB", "Ergonomic Mechanical Keyboard",
    "Noise-Cancelling Headset Pro", "USB-C Multiport Dock", "Thunderbolt Cable 2m",
    "Smart IoT Environmental Sensor", "Server Rack Mount 42U", "Cat6A Shielded Patch Cable",
]

DEPARTMENTS = ["Engineering", "Cybersecurity", "Human Resources", "Finance", "Legal & Compliance", "Operations"]


def generate_valid_aadhaar() -> str:
    """Generate a valid 12-digit Aadhaar number with correct Verhoeff check digit."""
    # First digit between 2 and 9
    first = str(random.randint(2, 9))
    middle = "".join([str(random.randint(0, 9)) for _ in range(10)])
    eleven = first + middle
    chk = generate_verhoeff(eleven)
    full = eleven + chk
    # Format with optional spaces
    if random.random() < 0.5:
        return f"{full[:4]} {full[4:8]} {full[8:]}"
    elif random.random() < 0.2:
        return f"{full[:4]}-{full[4:8]}-{full[8:]}"
    return full


def generate_valid_pan() -> str:
    """Generate a valid Indian PAN format."""
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    entity = random.choice(["P", "C", "H", "F", "A", "T", "B", "L", "J", "G"])
    surname_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    digits = f"{random.randint(1000, 9999)}"
    last_char = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{letters}{entity}{surname_initial}{digits}{last_char}"


def generate_indian_phone() -> str:
    """Generate valid Indian mobile contact number with realistic formatting."""
    start = random.choice(["6", "7", "8", "9"])
    rest = "".join([str(random.randint(0, 9)) for _ in range(9)])
    ten = start + rest
    style = random.choice(["raw", "plus91_space", "plus91_dash", "zero_prefix", "space_split", "dash_split"])
    if style == "raw":
        return ten
    elif style == "plus91_space":
        return f"+91 {ten[:5]} {ten[5:]}"
    elif style == "plus91_dash":
        return f"+91-{ten[:5]}-{ten[5:]}"
    elif style == "zero_prefix":
        return f"0{ten}"
    elif style == "space_split":
        return f"{ten[:5]} {ten[5:]}"
    else:
        return f"{ten[:5]}-{ten[5:]}"


def generate_dob() -> str:
    """Generate a plausible human birthdate with mixed calendar formats."""
    year = random.randint(1955, 2004)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    fmt = random.choice(["iso", "indian_slash", "indian_dash", "textual", "us_slash"])
    if fmt == "iso":
        return f"{year:04d}-{month:02d}-{day:02d}"
    elif fmt == "indian_slash":
        return f"{day:02d}/{month:02d}/{year:04d}"
    elif fmt == "indian_dash":
        return f"{day:02d}-{month:02d}-{year:04d}"
    elif fmt == "textual":
        m_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{day:02d}-{m_names[month-1]}-{year:04d}"
    else:
        return f"{month:02d}/{day:02d}/{year:04d}"


def build_synthetic_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    n_rows = 120

    # 1. customers_messy.csv
    cust_data = []
    for i in range(n_rows):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = random.choice(HONORIFICS) + first + " " + last
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 99)}@{random.choice(DOMAINS)}"
        phone = generate_indian_phone()
        dob = generate_dob()
        pan = generate_valid_pan()
        aadhaar = generate_valid_aadhaar()
        cust_id = f"CUST-{random.randint(100000, 999999)}"
        # Messy nulls
        if random.random() < 0.1:
            pan = ""
        if random.random() < 0.08:
            phone = ""
        if random.random() < 0.15:
            aadhaar = ""
        last_login_epoch = str(1720000000 + random.randint(10000, 5000000))
        temp_notes = "VIP Account" if random.random() < 0.15 else ""

        cust_data.append({
            "cust_id": cust_id,
            "full_name": name,
            "user_email": email,
            "contact_token": phone,  # Misleading name for Phone!
            "bday": dob,
            "pan_card": pan,
            "aadhaar_num": aadhaar,
            "temp_notes": temp_notes,
            "last_login_epoch": last_login_epoch,
        })
    df_cust = pd.DataFrame(cust_data)
    df_cust.to_csv(os.path.join(OUTPUT_DIR, "customers_messy.csv"), index=False)

    # 2. employees_hr.csv
    emp_data = []
    for i in range(n_rows):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = first + " " + last
        emp_code = f"EMP{i+1000:04d}"
        email = f"{first.lower()}_{last.lower()}@enterprise.in"
        phone = generate_indian_phone()
        dob = f"{random.randint(1965, 2001):04d}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        pan = generate_valid_pan()
        salary_band = random.choice(["L1", "L2", "L3", "L4", "L5", "Exec"])
        dept = random.choice(DEPARTMENTS)
        emerg_contact = generate_indian_phone()

        emp_data.append({
            "emp_code": emp_code,
            "emp_name": name,
            "work_email": email,
            "mobile_no": phone,
            "date_of_birth": dob,
            "tax_identifier": pan,
            "salary_band": salary_band,
            "department": dept,
            "emergency_contact": emerg_contact,
        })
    df_emp = pd.DataFrame(emp_data)
    df_emp.to_csv(os.path.join(OUTPUT_DIR, "employees_hr.csv"), index=False)

    # 3. transactions_logs.csv
    txn_data = []
    for i in range(n_rows):
        txn_id = f"TXN-2026-{random.randint(10000000, 99999999)}"
        product = random.choice(PRODUCTS)
        # Order date: recent 2026 dates (not DOB!)
        order_date = f"2026-0{random.randint(1, 9)}-{random.randint(10, 28):02d}"
        pincode = f"{random.randint(110001, 700099)}"
        pay_ref = f"REF{random.randint(100000, 999999)}XYZ"
        recip_phone = generate_indian_phone()
        buyer_email = f"buyer{i}@{random.choice(DOMAINS)}"
        # Decoy tracking number: 10 digits starting with 1 or 2 (fails Indian cellular 6-9 prefix!)
        tracking_num = f"{random.choice(['1', '2', '3'])}{random.randint(100000000, 999999999)}"

        txn_data.append({
            "txn_id": txn_id,
            "product_name": product,  # Decoy: contains 'name'
            "order_date": order_date,  # Decoy: date but not DOB
            "delivery_pincode": pincode,
            "payment_reference": pay_ref,
            "recipient_contact": recip_phone,
            "buyer_email": buyer_email,
            "tracking_num": tracking_num,  # Decoy: 10-digit number
        })
    df_txn = pd.DataFrame(txn_data)
    df_txn.to_csv(os.path.join(OUTPUT_DIR, "transactions_logs.csv"), index=False)

    # 4. kyc_onboarding.csv
    kyc_data = []
    for i in range(n_rows):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = first + " " + last
        app_id = f"KYC-APP-{i+5000}"
        phone = generate_indian_phone()
        dob = generate_dob()
        aadhaar = generate_valid_aadhaar()
        pan = generate_valid_pan()
        id_type = random.choice(["AADHAAR_CARD", "PAN_CARD"])
        timestamp = f"2026-08-{random.randint(1, 28):02d} 11:20:00"
        credit_score = random.randint(620, 850)

        kyc_data.append({
            "applicant_id": app_id,
            "applicant_name": name,
            "contact_mobile": phone,
            "applicant_dob": dob,
            "identity_doc_number": aadhaar,
            "pan_number": pan,
            "id_type": id_type,
            "verification_timestamp": timestamp,
            "score_credit": credit_score,
        })
    df_kyc = pd.DataFrame(kyc_data)
    df_kyc.to_csv(os.path.join(OUTPUT_DIR, "kyc_onboarding.csv"), index=False)

    # 5. support_tickets.csv
    ticket_data = []
    for i in range(n_rows):
        tck_id = f"TCK-{i+20000}"
        cust_name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
        email = f"ticket_user{i}@{random.choice(DOMAINS)}"
        cat = random.choice(["Billing Discrepancy", "Technical Login Error", "KYC Document Clarification", "Account Closure"])
        agent = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
        created_at = f"2026-10-{random.randint(1, 25):02d} 09:15:30"
        phone = generate_indian_phone()
        status = random.choice(["Open", "In-Progress", "Resolved", "Closed"])

        ticket_data.append({
            "ticket_id": tck_id,
            "customer_name": cust_name,
            "registered_email": email,
            "ticket_category": cat,
            "assigned_agent": agent,
            "created_at": created_at,
            "phone_support_num": phone,
            "resolution_status": status,
        })
    df_ticket = pd.DataFrame(ticket_data)
    df_ticket.to_csv(os.path.join(OUTPUT_DIR, "support_tickets.csv"), index=False)

    # 6. SQLite Database: enterprise_vault.db
    db_path = os.path.join(OUTPUT_DIR, "enterprise_vault.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Table 1: user_profiles
    cur.execute("""
    CREATE TABLE user_profiles (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        primary_email TEXT,
        phone_number TEXT,
        birthdate TEXT,
        aadhaar_vault_ref TEXT,
        account_status TEXT
    )
    """)
    for i in range(n_rows):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = first + " " + last
        email = f"vault_user_{i}@{random.choice(DOMAINS)}"
        phone = generate_indian_phone()
        dob = generate_dob()
        aadhaar = generate_valid_aadhaar()
        status = random.choice(["ACTIVE", "SUSPENDED", "PENDING_VERIFICATION"])
        cur.execute(
            "INSERT INTO user_profiles VALUES (?, ?, ?, ?, ?, ?, ?)",
            (i + 1, name, email, phone, dob, aadhaar, status)
        )

    # Table 2: billing_accounts
    cur.execute("""
    CREATE TABLE billing_accounts (
        account_id TEXT PRIMARY KEY,
        billing_contact_name TEXT,
        billing_email TEXT,
        pan_id TEXT,
        currency_code TEXT,
        tax_reg_no TEXT
    )
    """)
    for i in range(n_rows):
        acc_id = f"ACC-{random.randint(10000, 99999)}"
        name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
        email = f"billing_{i}@{random.choice(DOMAINS)}"
        pan = generate_valid_pan()
        tax_reg = generate_valid_pan()
        curr = random.choice(["INR", "USD", "EUR", "GBP"])
        cur.execute(
            "INSERT INTO billing_accounts VALUES (?, ?, ?, ?, ?, ?)",
            (acc_id, name, email, pan, curr, tax_reg)
        )

    # Table 3: activity_telemetry (Decoy Table)
    cur.execute("""
    CREATE TABLE activity_telemetry (
        session_id TEXT,
        ip_address TEXT,
        user_agent TEXT,
        event_timestamp TEXT,
        action_name TEXT,
        device_type TEXT
    )
    """)
    for i in range(n_rows):
        sess = f"SESS-{random.randint(100000, 999999)}"
        ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        ts = f"2026-10-31 {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"
        act = random.choice(["LOGIN_ATTEMPT", "VIEW_DASHBOARD", "EXPORT_REPORT", "TOKEN_REFRESH"])
        dev = random.choice(["desktop", "mobile", "tablet"])
        cur.execute(
            "INSERT INTO activity_telemetry VALUES (?, ?, ?, ?, ?, ?)",
            (sess, ip, ua, ts, act, dev)
        )

    # Table 4: vendor_registry
    cur.execute("""
    CREATE TABLE vendor_registry (
        vendor_id TEXT,
        vendor_company_name TEXT,
        contact_person TEXT,
        official_email TEXT,
        helpline_phone TEXT,
        incorporation_date TEXT
    )
    """)
    for i in range(n_rows):
        v_id = f"VEND-{random.randint(100, 999)}"
        comp = f"{random.choice(LAST_NAMES)} Technologies Pvt Ltd"
        contact = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
        email = f"support@{comp.lower().replace(' ', '')}.com"
        phone = generate_indian_phone()
        inc_date = f"{random.randint(2010, 2024)}-05-18"  # Corporate date (decoy)
        cur.execute(
            "INSERT INTO vendor_registry VALUES (?, ?, ?, ?, ?, ?)",
            (v_id, comp, contact, email, phone, inc_date)
        )

    conn.commit()
    conn.close()

    # 7. metadata.csv (Declared purpose and retention schedule; some deliberately missing)
    # Notice: legal_notes column stays blank for human reviewer as strictly required!
    metadata_entries = [
        # customers_messy.csv
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "cust_id", "declared_purpose": "Unique customer reference key", "retention_period": "Account lifespan + 7 years", "legal_notes": ""},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "full_name", "declared_purpose": "Customer identity verification and personalization", "retention_period": "Account lifespan + 5 years", "legal_notes": ""},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "user_email", "declared_purpose": "Transaction receipts and mandatory service notices", "retention_period": "Account lifespan + 5 years", "legal_notes": ""},
        # contact_token intentionally MISSING retention to trigger compliance gap!
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "contact_token", "declared_purpose": "Multi-factor authentication (SMS OTP)", "retention_period": "", "legal_notes": ""},
        # bday intentionally MISSING purpose and retention! (Critical Gap)
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "bday", "declared_purpose": "", "retention_period": "", "legal_notes": ""},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "pan_card", "declared_purpose": "Statutory financial tax compliance under IT Act", "retention_period": "7 years post-financial year", "legal_notes": ""},
        # aadhaar_num intentionally MISSING retention!
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "aadhaar_num", "declared_purpose": "Voluntary e-KYC identity onboarding", "retention_period": "", "legal_notes": ""},

        # employees_hr.csv
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emp_code", "declared_purpose": "Internal organizational identifier", "retention_period": "Permanent archive", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emp_name", "declared_purpose": "Employment contract execution and payroll processing", "retention_period": "Active tenure + 7 years", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "work_email", "declared_purpose": "Corporate communication and system access management", "retention_period": "Tenure + 90 days", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "mobile_no", "declared_purpose": "Emergency operational duty contact", "retention_period": "Tenure duration", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "date_of_birth", "declared_purpose": "Retirement superannuation and gratuity calculation", "retention_period": "Tenure + 7 years", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "tax_identifier", "declared_purpose": "TDS payroll withholding and Form 16 issuance", "retention_period": "8 financial years", "legal_notes": ""},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emergency_contact", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Critical Gap!

        # transactions_logs.csv
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "recipient_contact", "declared_purpose": "Courier delivery dispatch coordination", "retention_period": "90 days post-fulfillment", "legal_notes": ""},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "buyer_email", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Critical Gap!

        # kyc_onboarding.csv
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "applicant_name", "declared_purpose": "Anti-Money Laundering (AML) sanctions screening", "retention_period": "10 years statutory requirement", "legal_notes": ""},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "contact_mobile", "declared_purpose": "Applicant status alerts", "retention_period": "10 years post-application", "legal_notes": ""},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "applicant_dob", "declared_purpose": "Legal age of majority eligibility verification", "retention_period": "10 years post-application", "legal_notes": ""},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "identity_doc_number", "declared_purpose": "Statutory KYC verification", "retention_period": "10 years statutory requirement", "legal_notes": ""},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "pan_number", "declared_purpose": "Tax compliance and financial credit underwriting", "retention_period": "10 years post-application", "legal_notes": ""},

        # support_tickets.csv
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "customer_name", "declared_purpose": "Service ticket resolution addressing", "retention_period": "2 years post-ticket resolution", "legal_notes": ""},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "registered_email", "declared_purpose": "Ticket status updates dispatch", "retention_period": "2 years post-ticket resolution", "legal_notes": ""},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "assigned_agent", "declared_purpose": "Internal customer service performance audit", "retention_period": "1 year post-ticket resolution", "legal_notes": ""},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "phone_support_num", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Critical Gap!

        # enterprise_vault.db: user_profiles
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "full_name", "declared_purpose": "Platform user identity profile", "retention_period": "Account lifespan", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "primary_email", "declared_purpose": "Account authentication and security recovery", "retention_period": "Account lifespan", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "phone_number", "declared_purpose": "2FA hardware authentication binding", "retention_period": "Account lifespan", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "birthdate", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Critical Gap!
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "aadhaar_vault_ref", "declared_purpose": "Statutory Aadhaar Vault reference token", "retention_period": "7 years per UIDAI Circular", "legal_notes": ""},

        # enterprise_vault.db: billing_accounts
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "billing_contact_name", "declared_purpose": "Commercial invoice addressee", "retention_period": "7 years per Companies Act", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "billing_email", "declared_purpose": "Invoicing and payment receipt dispatch", "retention_period": "7 years per Companies Act", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "pan_id", "declared_purpose": "Commercial corporate tax reporting", "retention_period": "7 years per Companies Act", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "tax_reg_no", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Critical Gap!

        # enterprise_vault.db: vendor_registry
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "contact_person", "declared_purpose": "Supplier contract coordination", "retention_period": "Contract duration + 3 years", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "official_email", "declared_purpose": "Vendor RFQ and procurement communication", "retention_period": "Contract duration + 3 years", "legal_notes": ""},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "helpline_phone", "declared_purpose": "", "retention_period": "", "legal_notes": ""},  # Gap!
    ]
    df_meta = pd.DataFrame(metadata_entries)
    df_meta.to_csv(os.path.join(OUTPUT_DIR, "metadata.csv"), index=False)

    # 8. labels.csv (Hand-labelled ground truth for evaluation)
    labels_entries = [
        # customers_messy.csv
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "cust_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Alphanumeric internal synthetic customer surrogate key"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "full_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "Customer individual full name with honorifics"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "user_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Personal customer email address"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "contact_token", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Misleading column name containing Indian mobile numbers"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "bday", "ground_truth_class": "Date of Birth", "is_pii": True, "description_note": "Individual birthdate with mixed date formats"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "pan_card", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Indian statutory PAN tax identifier"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "aadhaar_num", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "12-digit Indian Aadhaar with Verhoeff check digits"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "temp_notes", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Sparse internal notes column with nulls"},
        {"dataset_name": "customers_messy.csv", "table_name": "customers_messy", "column_name": "last_login_epoch", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Epoch timestamp of recent login session"},

        # employees_hr.csv
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emp_code", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Internal employee employee badge alphanumeric code"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emp_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "Employee legal full name"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "work_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Corporate business email address"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "mobile_no", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Cellular phone number of employee"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "date_of_birth", "ground_truth_class": "Date of Birth", "is_pii": True, "description_note": "Employee birth date"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "tax_identifier", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Permanent Account Number (PAN)"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "salary_band", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Internal paygrade classification code"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "department", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Organizational department unit"},
        {"dataset_name": "employees_hr.csv", "table_name": "employees_hr", "column_name": "emergency_contact", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Emergency mobile contact number"},

        # transactions_logs.csv
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "txn_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Transaction reference UUID"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "product_name", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Decoy column: contains 'name' token but represents commercial hardware items"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "order_date", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Decoy date: order fulfillment timestamp, not person's birthdate"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "delivery_pincode", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Postal geographic area routing code"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "payment_reference", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Payment gateway alphanumeric transaction token"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "recipient_contact", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Customer delivery recipient phone number"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "buyer_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Buyer personal billing email"},
        {"dataset_name": "transactions_logs.csv", "table_name": "transactions_logs", "column_name": "tracking_num", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Decoy 10-digit package tracking code starting with 1-3"},

        # kyc_onboarding.csv
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "applicant_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Synthetic applicant identifier"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "applicant_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "Customer applicant legal name"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "contact_mobile", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Applicant mobile contact"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "applicant_dob", "ground_truth_class": "Date of Birth", "is_pii": True, "description_note": "Applicant birthdate for age qualification"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "identity_doc_number", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Aadhaar UIDAI statutory number with Verhoeff checksum"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "pan_number", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Permanent Account Number"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "id_type", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Document category tag string"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "verification_timestamp", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Audit log timestamp"},
        {"dataset_name": "kyc_onboarding.csv", "table_name": "kyc_onboarding", "column_name": "score_credit", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Numerical bureau credit score rating"},

        # support_tickets.csv
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "ticket_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Helpdesk ticket incident reference ID"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "customer_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "Customer requester full name"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "registered_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Customer account email address"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "ticket_category", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Incident issue categorization taxonomy"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "assigned_agent", "ground_truth_class": "Name", "is_pii": True, "description_note": "Support engineer employee personal name"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "created_at", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Ticket submission timestamp"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "phone_support_num", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Inbound telephone contact number"},
        {"dataset_name": "support_tickets.csv", "table_name": "support_tickets", "column_name": "resolution_status", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Ticket workflow status flag"},

        # enterprise_vault.db: user_profiles
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "user_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Integer primary database key"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "full_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "User personal full name"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "primary_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Account primary email"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "phone_number", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Primary mobile number"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "birthdate", "ground_truth_class": "Date of Birth", "is_pii": True, "description_note": "User birthdate"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "aadhaar_vault_ref", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "12-digit Aadhaar UID number"},
        {"dataset_name": "enterprise_vault.db", "table_name": "user_profiles", "column_name": "account_status", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Account lifecycle status string"},

        # enterprise_vault.db: billing_accounts
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "account_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Billing account identifier code"},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "billing_contact_name", "ground_truth_class": "Name", "is_pii": True, "description_note": "Individual billing representative name"},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "billing_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Commercial invoice dispatch email"},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "pan_id", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Statutory Indian PAN"},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "currency_code", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "ISO currency code symbol"},
        {"dataset_name": "enterprise_vault.db", "table_name": "billing_accounts", "column_name": "tax_reg_no", "ground_truth_class": "Government ID", "is_pii": True, "description_note": "Tax registration PAN identifier"},

        # enterprise_vault.db: activity_telemetry
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "session_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Browser web session token"},
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "ip_address", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Network telemetry IP address (technical telemetry)"},
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "user_agent", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Client browser technical user agent string"},
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "event_timestamp", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Telemetry event execution timestamp"},
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "action_name", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Application telemetry event trigger action"},
        {"dataset_name": "enterprise_vault.db", "table_name": "activity_telemetry", "column_name": "device_type", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Hardware device form factor"},

        # enterprise_vault.db: vendor_registry
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "vendor_id", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Supplier ERP master identifier"},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "vendor_company_name", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Decoy name: Corporate entity legal name, not an individual human person"},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "contact_person", "ground_truth_class": "Name", "is_pii": True, "description_note": "Vendor point of contact representative personal name"},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "official_email", "ground_truth_class": "Email", "is_pii": True, "description_note": "Business contact email address"},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "helpline_phone", "ground_truth_class": "Phone", "is_pii": True, "description_note": "Supplier telephone helpline"},
        {"dataset_name": "enterprise_vault.db", "table_name": "vendor_registry", "column_name": "incorporation_date", "ground_truth_class": "Non-PII", "is_pii": False, "description_note": "Decoy date: corporate business founding date, not human birthdate"},
    ]
    df_labels = pd.DataFrame(labels_entries)
    df_labels.to_csv(os.path.join(OUTPUT_DIR, "labels.csv"), index=False)

    # 9. rules.yaml (configurable detection rules)
    from src.rules.engine import DEFAULT_RULES
    with open(os.path.join(OUTPUT_DIR, "rules.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(DEFAULT_RULES, f, default_flow_style=False, sort_keys=False)

    print("Synthetic datasets, SQLite DB, metadata.csv, labels.csv, and rules.yaml generated successfully!")


if __name__ == "__main__":
    build_synthetic_data()
