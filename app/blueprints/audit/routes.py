from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Role, Permission, AuditSession, AuditFinding, AuditLog
from app.services.audit_engine import AccessControlAuditEngine

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')

def admin_or_auditor_required(func):
    from functools import wraps
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access Denied. Administrative or Auditor privileges required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return func(*args, **kwargs)
    return decorated_view

@audit_bp.route('/roles')
@login_required
def role_matrix():
    roles = Role.query.all()
    permissions = Permission.query.order_by(Permission.category, Permission.code).all()
    categories = sorted(list({p.category for p in permissions}))
    
    return render_template(
        'audit/role_review.html',
        roles=roles,
        permissions=permissions,
        categories=categories
    )

@audit_bp.route('/run', methods=['GET', 'POST'])
@admin_or_auditor_required
def run_audit():
    if request.method == 'POST':
        session_title = request.form.get('session_title', 'Access Control & Least Privilege Audit').strip()
        
        audit_session = AccessControlAuditEngine.run_full_audit(
            executed_by=current_user.full_name or current_user.username,
            session_title=session_title
        )
        
        flash(f'Audit #{audit_session.id} completed! Least Privilege Score: {audit_session.least_privilege_score}%.', 'success')
        return redirect(url_for('audit.findings', session_id=audit_session.id))
        
    return render_template('audit/audit_run.html')

@audit_bp.route('/findings')
@login_required
def findings():
    session_id = request.args.get('session_id', type=int)
    
    if session_id:
        audit_session = AuditSession.query.get_or_404(session_id)
    else:
        audit_session = AuditSession.query.order_by(AuditSession.created_at.desc()).first()
        
    all_sessions = AuditSession.query.order_by(AuditSession.created_at.desc()).all()
    findings_list = AuditFinding.query.filter_by(audit_session_id=audit_session.id).all() if audit_session else []
    
    return render_template(
        'audit/findings.html',
        audit_session=audit_session,
        all_sessions=all_sessions,
        findings=findings_list
    )

@audit_bp.route('/findings/<int:finding_id>/remediate', methods=['POST'])
@admin_or_auditor_required
def remediate_finding(finding_id):
    finding = AuditFinding.query.get_or_404(finding_id)
    new_status = request.form.get('status', 'REMEDIATED')
    
    finding.status = new_status
    
    log = AuditLog(
        event_type='ROLE_UPDATED',
        username=current_user.username,
        details=f"Updated Finding #{finding.id} status to '{new_status}' for {finding.target_name}."
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Finding #{finding.id} marked as {new_status}.', 'success')
    return redirect(url_for('audit.findings', session_id=finding.audit_session_id))

@audit_bp.route('/roles/<int:role_id>/toggle-permission', methods=['POST'])
@admin_or_auditor_required
def toggle_permission(role_id):
    role = Role.query.get_or_404(role_id)
    perm_id = request.form.get('permission_id', type=int)
    permission = Permission.query.get_or_404(perm_id)
    
    if permission in role.permissions:
        role.permissions.remove(permission)
        action = "revoked from"
    else:
        role.permissions.append(permission)
        action = "granted to"
        
    log = AuditLog(
        event_type='ROLE_UPDATED',
        username=current_user.username,
        details=f"Permission '{permission.code}' {action} role '{role.name}'."
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Permission '{permission.code}' successfully {action} role '{role.name}'.", 'success')
    return redirect(url_for('audit.role_matrix'))
