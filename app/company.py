from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
from app import db
from app.models import Company, PlacementDrive, Application, Student

company = Blueprint('company', __name__)


def company_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'company':
            flash('Company access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_company():
    return Company.query.filter_by(user_id=current_user.id).first()


@company.route('/dashboard')
@login_required
@company_required
def dashboard():
    comp = get_company()
    drives = PlacementDrive.query.filter_by(company_id=comp.id).all()

    # Count applicants per drive
    drive_data = []
    for drive in drives:
        count = Application.query.filter_by(drive_id=drive.id).count()
        drive_data.append({'drive': drive, 'applicant_count': count})

    return render_template('company/dashboard.html', company=comp, drive_data=drive_data)


@company.route('/drives/create', methods=['GET', 'POST'])
@login_required
@company_required
def create_drive():
    comp = get_company()

    if comp.approval_status != 'approved':
        flash('Your company must be approved before creating drives.', 'warning')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        deadline_str = request.form.get('application_deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()

        drive = PlacementDrive(
            company_id=comp.id,
            job_title=request.form.get('job_title'),
            job_description=request.form.get('job_description'),
            eligibility_criteria=request.form.get('eligibility_criteria'),
            package_lpa=request.form.get('package_lpa') or None,
            location=request.form.get('location'),
            application_deadline=deadline,
            status='pending'  # Needs admin approval
        )
        db.session.add(drive)
        db.session.commit()
        flash('Drive submitted for admin approval!', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/create_drive.html')


@company.route('/drives/<int:drive_id>/edit', methods=['GET', 'POST'])
@login_required
@company_required
def edit_drive(drive_id):
    comp = get_company()
    drive = PlacementDrive.query.get_or_404(drive_id)

    # Ensure this drive belongs to this company
    if drive.company_id != comp.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        drive.job_title = request.form.get('job_title')
        drive.job_description = request.form.get('job_description')
        drive.eligibility_criteria = request.form.get('eligibility_criteria')
        drive.package_lpa = request.form.get('package_lpa') or None
        drive.location = request.form.get('location')
        deadline_str = request.form.get('application_deadline')
        drive.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        drive.status = 'pending'  # Re-submit for approval after edit
        db.session.commit()
        flash('Drive updated and re-submitted for approval.', 'success')
        return redirect(url_for('company.dashboard'))

    return render_template('company/edit_drive.html', drive=drive)


@company.route('/drives/<int:drive_id>/close')
@login_required
@company_required
def close_drive(drive_id):
    comp = get_company()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != comp.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    drive.status = 'closed'
    db.session.commit()
    flash('Drive closed.', 'info')
    return redirect(url_for('company.dashboard'))


@company.route('/drives/<int:drive_id>/delete')
@login_required
@company_required
def delete_drive(drive_id):
    comp = get_company()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != comp.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    db.session.delete(drive)
    db.session.commit()
    flash('Drive deleted.', 'info')
    return redirect(url_for('company.dashboard'))


@company.route('/drives/<int:drive_id>/applicants')
@login_required
@company_required
def view_applicants(drive_id):
    comp = get_company()
    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.company_id != comp.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))

    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/applicants.html', drive=drive, applications=applications)


@company.route('/application/<int:app_id>/update', methods=['POST'])
@login_required
@company_required
def update_application(app_id):
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')

    if new_status in ['shortlisted', 'selected', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated.', 'success')

    return redirect(url_for('company.view_applicants', drive_id=application.drive_id))


@company.route('/profile', methods=['GET', 'POST'])
@login_required
@company_required
def profile():
    comp = get_company()

    if request.method == 'POST':
        comp.company_name = request.form.get('company_name')
        comp.hr_contact = request.form.get('hr_contact')
        comp.website = request.form.get('website')
        comp.description = request.form.get('description')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('company.profile'))

    return render_template('company/profile.html', company=comp)