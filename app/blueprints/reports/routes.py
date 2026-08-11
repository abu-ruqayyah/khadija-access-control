import os
from flask import Blueprint, send_file, current_app
from flask_login import login_required, current_user
from app.models import db, AuditSession, AuditLog
from app.services.report_generator import AuditReportGenerator

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/pdf/<int:session_id>')
@login_required
def download_pdf(session_id):
    audit_session = AuditSession.query.get_or_404(session_id)
    
    reports_dir = current_app.config['REPORTS_FOLDER']
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"Khadija_Access_Control_Audit_Report_Session_{audit_session.id}.pdf"
    file_path = os.path.join(reports_dir, filename)
    
    AuditReportGenerator.generate_pdf_report(session_id, file_path)
    
    log = AuditLog(
        event_type='REPORT_GENERATED',
        username=current_user.username,
        details=f"Generated PDF Executive Report for Audit Session #{session_id}."
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@reports_bp.route('/csv/<int:session_id>')
@login_required
def download_csv(session_id):
    audit_session = AuditSession.query.get_or_404(session_id)
    
    reports_dir = current_app.config['REPORTS_FOLDER']
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"Khadija_Access_Control_Audit_Findings_Session_{audit_session.id}.csv"
    file_path = os.path.join(reports_dir, filename)
    
    AuditReportGenerator.generate_csv_report(session_id, file_path)
    
    log = AuditLog(
        event_type='REPORT_GENERATED',
        username=current_user.username,
        details=f"Generated CSV Audit Findings for Audit Session #{session_id}."
    )
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )
