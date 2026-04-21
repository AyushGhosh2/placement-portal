from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Flask-Login needs this to load a user from the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─────────────────────────────────────────
# USER TABLE — stores admin, company, student logins
# ─────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # role: 'admin', 'company', 'student'
    role = db.Column(db.String(20), nullable=False)

    # If blacklisted, they cannot log in
    is_active = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login uses this to check if account is active
    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    company_profile = db.relationship('Company', backref='user', uselist=False)


# Fix: rename column to avoid conflict with Flask-Login property
User.is_active = db.Column(db.Boolean, default=True)


# ─────────────────────────────────────────
# STUDENT TABLE
# ─────────────────────────────────────────
class Student(db.Model):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    phone = db.Column(db.String(20))
    resume_filename = db.Column(db.String(200))  # uploaded file name

    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True)


# ─────────────────────────────────────────
# COMPANY TABLE
# ─────────────────────────────────────────
class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    company_name = db.Column(db.String(150), nullable=False)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)

    # 'pending', 'approved', 'rejected'
    approval_status = db.Column(db.String(20), default='pending')

    # Relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy=True)


# ─────────────────────────────────────────
# PLACEMENT DRIVE TABLE
# ─────────────────────────────────────────
class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text)
    package_lpa = db.Column(db.Float)  # salary in LPA
    location = db.Column(db.String(100))
    application_deadline = db.Column(db.Date, nullable=False)

    # 'pending', 'approved', 'closed'
    status = db.Column(db.String(20), default='pending')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='drive', lazy=True)


# ─────────────────────────────────────────
# APPLICATION TABLE
# ─────────────────────────────────────────
class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)

    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 'applied', 'shortlisted', 'selected', 'rejected'
    status = db.Column(db.String(20), default='applied')

    # Unique constraint: one student can apply to one drive only once
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )


# ─────────────────────────────────────────
# CREATE DEFAULT ADMIN (runs once at startup)
# ─────────────────────────────────────────
def create_default_admin():
    from app import db
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            email='admin@placement.com',
            role='admin'
        )
        admin_user.set_password('admin123')  # Change this!
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin created: admin / admin123")