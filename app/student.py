import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app import db
from app.models import Student, PlacementDrive, Application
from datetime import date

student = Blueprint('student', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Student access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_student():
    return Student.query.filter_by(user_id=current_user.id).first()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    s = get_student()
    today = date.today()

    # All approved & not-expired drives
    available_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline >= today
    ).all()

    # Drives the student has already applied to
    my_applications = Application.query.filter_by(student_id=s.id).all()
    applied_drive_ids = {app.drive_id for app in my_applications}

    return render_template('student/dashboard.html',
                           student=s,
                           available_drives=available_drives,
                           my_applications=my_applications,
                           applied_drive_ids=applied_drive_ids)


@student.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
@student_required
def apply(drive_id):
    s = get_student()
    drive = PlacementDrive.query.get_or_404(drive_id)

    # Check drive is still open
    if drive.status != 'approved':
        flash('This drive is not open for applications.', 'warning')
        return redirect(url_for('student.dashboard'))

    if drive.application_deadline < date.today():
        flash('Application deadline has passed.', 'warning')
        return redirect(url_for('student.dashboard'))

    # Prevent duplicate application
    existing = Application.query.filter_by(student_id=s.id, drive_id=drive_id).first()
    if existing:
        flash('You have already applied for this drive.', 'warning')
        return redirect(url_for('student.dashboard'))

    application = Application(student_id=s.id, drive_id=drive_id)
    db.session.add(application)
    db.session.commit()
    flash(f'Successfully applied for {drive.job_title}!', 'success')
    return redirect(url_for('student.dashboard'))


@student.route('/history')
@login_required
@student_required
def history():
    s = get_student()
    applications = Application.query.filter_by(student_id=s.id).order_by(
        Application.applied_at.desc()
    ).all()
    return render_template('student/history.html', applications=applications)


@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    s = get_student()

    if request.method == 'POST':
        s.full_name = request.form.get('full_name')
        s.department = request.form.get('department')
        s.cgpa = request.form.get('cgpa') or None
        s.phone = request.form.get('phone')

        # Handle resume upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"resume_{s.roll_number}_{file.filename}")
                upload_path = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_path, exist_ok=True)
                file.save(os.path.join(upload_path, filename))
                s.resume_filename = filename

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', student=s)