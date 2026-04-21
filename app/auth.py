from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Student, Company

auth = Blueprint('auth', __name__)


@auth.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))

        # Companies must be approved before they can log in
        if user.role == 'company':
            if user.company_profile.approval_status != 'approved':
                flash('Your company registration is pending admin approval.', 'warning')
                return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for(f'{user.role}.dashboard'))

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role')  # 'student' or 'company'
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Create the User
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get the new user's ID before committing

        # Create the role-specific profile
        if role == 'student':
            profile = Student(
                user_id=new_user.id,
                full_name=request.form.get('full_name'),
                roll_number=request.form.get('roll_number'),
                department=request.form.get('department'),
                cgpa=request.form.get('cgpa') or None,
                phone=request.form.get('phone')
            )
            db.session.add(profile)

        elif role == 'company':
            profile = Company(
                user_id=new_user.id,
                company_name=request.form.get('company_name'),
                hr_contact=request.form.get('hr_contact'),
                website=request.form.get('website'),
                description=request.form.get('description')
            )
            db.session.add(profile)

        db.session.commit()

        if role == 'student':
            flash('Registration successful! You can now log in.', 'success')
        else:
            flash('Registration submitted! Wait for admin approval.', 'info')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))