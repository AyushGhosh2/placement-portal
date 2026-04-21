from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Student, Company, PlacementDrive, Application

admin = Blueprint('admin', __name__)


# Decorator: only allow admin users
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'total_applications': Application.query.count(),
        'pending_companies': Company.query.filter_by(approval_status='pending').count(),
        'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


# ── COMPANY MANAGEMENT ──────────────────

@admin.route('/companies')
@login_required
@admin_required
def companies():
    search = request.args.get('search', '')
    if search:
        results = Company.query.filter(Company.company_name.ilike(f'%{search}%')).all()
    else:
        results = Company.query.all()
    return render_template('admin/companies.html', companies=results, search=search)


@admin.route('/company/<int:company_id>/approve')
@login_required
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'approved'
    company.user.is_active = True
    db.session.commit()
    flash(f'{company.company_name} approved!', 'success')
    return redirect(url_for('admin.companies'))


@admin.route('/company/<int:company_id>/reject')
@login_required
@admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = 'rejected'
    db.session.commit()
    flash(f'{company.company_name} rejected.', 'warning')
    return redirect(url_for('admin.companies'))


@admin.route('/company/<int:company_id>/blacklist')
@login_required
@admin_required
def blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.user.is_active = False
    db.session.commit()
    flash(f'{company.company_name} has been blacklisted.', 'danger')
    return redirect(url_for('admin.companies'))


@admin.route('/company/<int:company_id>/delete')
@login_required
@admin_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    user = company.user
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    flash('Company deleted.', 'info')
    return redirect(url_for('admin.companies'))


# ── STUDENT MANAGEMENT ──────────────────

@admin.route('/students')
@login_required
@admin_required
def students():
    search = request.args.get('search', '')
    if search:
        results = Student.query.filter(
            (Student.full_name.ilike(f'%{search}%')) |
            (Student.roll_number.ilike(f'%{search}%')) |
            (Student.phone.ilike(f'%{search}%'))
        ).all()
    else:
        results = Student.query.all()
    return render_template('admin/students.html', students=results, search=search)


@admin.route('/student/<int:student_id>/blacklist')
@login_required
@admin_required
def blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.user.is_active = False
    db.session.commit()
    flash(f'{student.full_name} has been blacklisted.', 'danger')
    return redirect(url_for('admin.students'))


@admin.route('/student/<int:student_id>/activate')
@login_required
@admin_required
def activate_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.user.is_active = True
    db.session.commit()
    flash(f'{student.full_name} has been activated.', 'success')
    return redirect(url_for('admin.students'))


@admin.route('/student/<int:student_id>/delete')
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    flash('Student deleted.', 'info')
    return redirect(url_for('admin.students'))


# ── PLACEMENT DRIVE MANAGEMENT ──────────

@admin.route('/drives')
@login_required
@admin_required
def drives():
    all_drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    return render_template('admin/drives.html', drives=all_drives)


@admin.route('/drive/<int:drive_id>/approve')
@login_required
@admin_required
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'approved'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" approved!', 'success')
    return redirect(url_for('admin.drives'))


@admin.route('/drive/<int:drive_id>/reject')
@login_required
@admin_required
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'rejected'
    db.session.commit()
    flash(f'Drive "{drive.job_title}" rejected.', 'warning')
    return redirect(url_for('admin.drives'))


@admin.route('/drive/<int:drive_id>/applications')
@login_required
@admin_required
def drive_applications(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('admin/applications.html', drive=drive, applications=applications)