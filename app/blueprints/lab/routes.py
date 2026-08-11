import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app.models import db, LabEvidence, AuditLog

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@lab_bp.route('/evidence')
def list_evidence():
    evidences = LabEvidence.query.order_by(LabEvidence.uploaded_at.desc()).all()
    return render_template('lab/evidence.html', evidences=evidences)

@lab_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_evidence():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        tool_category = request.form.get('tool_category', '').strip()
        description = request.form.get('description', '').strip()
        findings_summary = request.form.get('findings_summary', '').strip()
        
        file = request.files.get('file')
        
        if not file or file.filename == '':
            flash('No file selected for upload.', 'warning')
            return render_template('lab/upload.html')
            
        if file and allowed_file(file.filename):
            orig_filename = secure_filename(file.filename)
            unique_filename = f"{tool_category.lower().replace(' ', '_')}_{orig_filename}"
            
            upload_dir = current_app.config['LAB_EVIDENCE_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            evidence = LabEvidence(
                title=title,
                tool_category=tool_category,
                filename=unique_filename,
                file_path=file_path,
                description=description,
                findings_summary=findings_summary,
                uploaded_by=current_user.full_name or current_user.username
            )
            db.session.add(evidence)
            
            log = AuditLog(
                event_type='LAB_EVIDENCE_UPLOADED',
                username=current_user.username,
                details=f"Uploaded lab evidence '{title}' ({tool_category})."
            )
            db.session.add(log)
            db.session.commit()
            
            flash('Lab evidence uploaded and recorded successfully!', 'success')
            return redirect(url_for('lab.list_evidence'))
        else:
            flash('Invalid file extension. Allowed: PNG, JPG, PDF, PCAP, PCAPNG, TXT, JSON, XML, CSV.', 'danger')
            
    return render_template('lab/upload.html')

@lab_bp.route('/methodology')
def methodology():
    return render_template('lab/methodology.html')

@lab_bp.route('/download/<int:evidence_id>')
@login_required
def download_evidence(evidence_id):
    evidence = LabEvidence.query.get_or_404(evidence_id)
    
    if not os.path.exists(evidence.file_path):
        flash('Evidence file not found on disk.', 'danger')
        return redirect(url_for('lab.list_evidence'))
        
    return send_file(
        evidence.file_path,
        as_attachment=True,
        download_name=evidence.filename
    )
