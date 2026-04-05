import sqlite3
import random
from datetime import datetime, timedelta

def random_date(start_year, end_year, end_month=12):
    """Generates a random date between start_year and (end_year, end_month)."""
    start = datetime(start_year, 1, 1)
    # Use the current date as the hard limit if we are in the end year
    current_now = datetime.now()
    if end_year >= current_now.year:
        end = current_now
    else:
        end = datetime(end_year, end_month, 28) # Safety for Feb
    
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def setup_database():
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()

    # Step 1: Create Tables
    print("Initializing Clinical Database Structure...")
    cursor.execute('DROP TABLE IF EXISTS patients')
    cursor.execute('DROP TABLE IF EXISTS doctors')
    cursor.execute('DROP TABLE IF EXISTS appointments')
    cursor.execute('DROP TABLE IF EXISTS treatments')
    cursor.execute('DROP TABLE IF EXISTS invoices')

    cursor.execute('''
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        date_of_birth DATE,
        gender TEXT,
        city TEXT,
        registered_date DATE
    )''')

    cursor.execute('''
    CREATE TABLE doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT,
        department TEXT,
        phone TEXT
    )''')

    cursor.execute('''
    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        appointment_date DATETIME,
        status TEXT,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (id),
        FOREIGN KEY (doctor_id) REFERENCES doctors (id)
    )''')

    cursor.execute('''
    CREATE TABLE treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        treatment_name TEXT,
        cost REAL,
        duration_minutes INTEGER,
        FOREIGN KEY (appointment_id) REFERENCES appointments (id)
    )''')

    cursor.execute('''
    CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        invoice_date DATE,
        total_amount REAL,
        paid_amount REAL,
        status TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients (id)
    )''')

    # Step 2: High-Fidelity Seeding (2023-2026)
    print("Generating 2023-2026 Clinical Intelligence Data...")

    # 20 Professional Doctors
    specs = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology', 'Oncology', 'General Medicine']
    indian_fnames = ['Aarav', 'Ishani', 'Vihaan', 'Saanvi', 'Aditya', 'Anika', 'Arjun', 'Diya', 'Sai', 'Prisha', 'Amit', 'Neha', 'Sunil', 'Pooja', 'Rohan', 'Swati', 'Sweta', 'Rahul', 'Vikram', 'Ananya']
    indian_lnames = ['Sharma', 'Iyer', 'Gupta', 'Kapoor', 'Reddy', 'Chatterjee', 'Verma', 'Nair', 'Singh', 'Patel', 'Das', 'Joshi', 'Mehta', 'Kulkarni', 'Dubey', 'Agarwal', 'Bose', 'Choudhury', 'Desai', 'Gomes']
    
    doctors_data = []
    for i in range(20):
        spec = specs[i % len(specs)]
        doctors_data.append((f"Dr. {indian_fnames[i]} {indian_lnames[i]}", spec, f"{spec} Dept", f"+91-{random.randint(7000, 9999)}-{random.randint(100000, 999999)}"))
    cursor.executemany('INSERT INTO doctors (name, specialization, department, phone) VALUES (?, ?, ?, ?)', doctors_data)
    doctor_ids = list(range(1, 21))

    # 500 Diverse Patients
    patients_data = []
    indian_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow']
    for _ in range(500):
        fn = random.choice(indian_fnames)
        ln = random.choice(indian_lnames)
        dob = random_date(1950, 2015)
        # Registered spread across 2023-2026
        reg = random_date(2023, 2026)
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@clinical.com" if random.random() > 0.15 else None
        phone = f"+91 {random.randint(6000, 9999)}-{random.randint(100, 999)}-{random.randint(100, 999)}" if random.random() > 0.15 else None
        patients_data.append((fn, ln, email, phone, dob.strftime('%Y-%m-%d'), random.choice(['M', 'F']), random.choice(indian_cities), reg.strftime('%Y-%m-%d')))
    cursor.executemany('INSERT INTO patients (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', patients_data)
    patient_ids = list(range(1, 501))

    # 2500 Random Appointments (2023-2026)
    appointment_statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
    # Popular doctors (top 5 get 50% of the appointments)
    star_doctors = doctor_ids[:5]
    # Power Patients (top 50 get 40% of appointments)
    power_patients = patient_ids[:50]
    
    appointments_data = []
    for _ in range(2500):
        p_id = random.choice(power_patients) if random.random() < 0.4 else random.choice(patient_ids)
        d_id = random.choice(star_doctors) if random.random() < 0.5 else random.choice(doctor_ids)
        date = random_date(2023, 2026)
        status = random.choices(appointment_statuses, weights=[0.05, 0.8, 0.1, 0.05])[0]
        notes = "Patient complained of fatigue" if random.random() > 0.6 else (None if random.random() > 0.5 else "Routine checkup")
        appointments_data.append((p_id, d_id, date.strftime('%Y-%m-%d %H:%M:%S'), status, notes))
    cursor.executemany('INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes) VALUES (?, ?, ?, ?, ?)', appointments_data)
    
    # 1800 Treatments for completed appointments
    cursor.execute("SELECT id FROM appointments WHERE status = 'Completed'")
    comp_ids = [r[0] for r in cursor.fetchall()]
    treatment_types = ['Consultation', 'MRI Scan', 'Blood Panel', 'X-Ray', 'Flu Vaccination', 'Pediatric Care', 'Physiotherapy', 'Ultrasound']
    treatments_data = []
    for _ in range(1800):
        app_id = random.choice(comp_ids)
        treatments_data.append((app_id, random.choice(treatment_types), random.uniform(50, 5000), random.randint(15, 120)))
    cursor.executemany('INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes) VALUES (?, ?, ?, ?)', treatments_data)

    # 1200 Invoices (randomly spread)
    invoices_data = []
    for _ in range(1200):
        p_id = random.choice(patient_ids)
        date = random_date(2023, 2026)
        total = random.uniform(200, 15000)
        status = random.choice(['Paid', 'Pending', 'Overdue'])
        paid = total if status == 'Paid' else (total * random.random() if status == 'Pending' else 0)
        invoices_data.append((p_id, date.strftime('%Y-%m-%d'), total, paid, status))
    cursor.executemany('INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status) VALUES (?, ?, ?, ?, ?)', invoices_data)

    conn.commit()
    print(f"Done. clinic.db updated with 500 patients, 20 doctors, and 2500 multi-year appointments.")
    conn.close()

if __name__ == "__main__":
    setup_database()
