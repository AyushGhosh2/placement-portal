# PlacementHub — Placement Portal Application
### Modern Application Development Project | IIT Madras BS Data Science

---

## What is this?

PlacementHub is a web-based placement portal that allows an institute's placement cell (Admin), Companies, and Students to interact through a role-based system. It replaces the manual, spreadsheet-driven approach most institutes use for managing campus recruitment.

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3, Flask                     |
| Database   | SQLite (via Flask-SQLAlchemy ORM)   |
| Auth       | Flask-Login, Werkzeug               |
| Frontend   | Jinja2, Bootstrap 5, HTML5          |

---

## Project Structure

```
placement_portal/
│
├── app/
│   ├── __init__.py        ← App factory, initialises Flask + DB
│   ├── models.py          ← All database models (User, Student, Company, etc.)
│   ├── auth.py            ← Login, logout, registration routes
│   ├── admin.py           ← Admin dashboard and management routes
│   ├── company.py         ← Company dashboard, drives, applicants
│   ├── student.py         ← Student dashboard, applications, profile
│   │
│   ├── templates/         ← All Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── company/
│   │   └── student/
│   │
│   └── static/
│       ├── css/style.css
│       └── uploads/       ← Student resume uploads (auto-created)
│
├── run.py                 ← Entry point — run this to start the app
├── requirements.txt       ← All Python dependencies
└── README.md
```

---

## How to Run

### Step 1 — Make sure Python is installed

```bash
python --version
```

Should show Python 3.8 or higher. If not, download from https://www.python.org/downloads/

---

### Step 2 — Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Run the app

```bash
python run.py
```

You should see:
```
✅ Default admin created: admin / admin123
 * Running on http://127.0.0.1:5000
```

---

### Step 5 — Open in browser

Go to: **http://127.0.0.1:5000**

---

## Default Login Credentials

| Role    | Username | Password  | Notes                              |
|---------|----------|-----------|------------------------------------|
| Admin   | admin    | admin123  | Pre-created automatically          |
| Company | —        | —         | Register via /register, await approval |
| Student | —        | —         | Register via /register, login immediately |

> The database (`placement.db`) is created automatically on first run inside the `instance/` folder. You do not need to create it manually.

---

## How to Test the Full Flow

1. **Login as Admin** → `admin / admin123`
2. **Register a Company** → go to `/register`, select Company
3. **Admin approves the company** → Admin → Companies → Approve
4. **Company logs in** → creates a Placement Drive
5. **Admin approves the drive** → Admin → Drives → Approve
6. **Register a Student** → go to `/register`, select Student
7. **Student logs in** → sees the drive → clicks Apply
8. **Company logs in** → goes to Applicants → updates status to Shortlisted/Selected
9. **Student checks dashboard** → sees updated application status

---

## Features

### Admin
- Dashboard with total counts (students, companies, drives, applications)
- Approve / reject company registrations
- Approve / reject placement drives
- Search students by name, roll number, or phone
- Search companies by name
- Blacklist or delete students and companies

### Company
- Register and manage company profile
- Create, edit, close, and delete placement drives
- View all applicants for each drive
- Update application status (Shortlisted / Selected / Rejected)
- View student resumes

### Student
- Register, login, and edit profile
- Upload resume (PDF/DOC)
- Browse all open, approved placement drives
- Apply to drives (one application per drive enforced)
- Track application status in real time
- View full placement history

---

## Notes

- Do **not** include the `venv/` folder if sharing or submitting this project
- The `instance/placement.db` file is auto-generated — delete it to reset all data
- Resume uploads are saved to `app/static/uploads/`
- All passwords are stored as secure hashes — never in plain text

---

*PlacementHub © 2024 — IIT Madras BS Data Science | Ayush Ghosh (24f2008987)*
