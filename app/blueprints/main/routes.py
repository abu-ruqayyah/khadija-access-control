from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import db, Role, User, Permission, AuditSession, AuditFinding, LabEvidence, AuditLog

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    latest_audit = AuditSession.query.order_by(AuditSession.created_at.desc()).first()
    roles_count = Role.query.count()
    users_count = User.query.count()
    evidence_count = LabEvidence.query.count()
    return render_template('main/index.html', latest_audit=latest_audit, roles_count=roles_count, users_count=users_count, evidence_count=evidence_count)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    latest_audit = AuditSession.query.order_by(AuditSession.created_at.desc()).first()
    recent_findings = AuditFinding.query.order_by(AuditFinding.created_at.desc()).limit(5).all() if latest_audit else []
    
    roles = Role.query.all()
    users = User.query.all()
    permissions = Permission.query.all()
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    critical_roles = [r for r in roles if any(p.risk_level == 'CRITICAL' for p in r.permissions)]
    high_roles = [r for r in roles if any(p.risk_level == 'HIGH' for p in r.permissions) and r not in critical_roles]
    moderate_roles = [r for r in roles if r not in critical_roles and r not in high_roles]
    
    chart_data = {
        "critical_count": len(critical_roles),
        "high_count": len(high_roles),
        "moderate_count": len(moderate_roles),
        "total_roles": len(roles),
        "total_permissions": len(permissions),
        "total_users": len(users)
    }
    
    return render_template(
        'main/dashboard.html',
        latest_audit=latest_audit,
        recent_findings=recent_findings,
        roles=roles,
        users=users,
        chart_data=chart_data,
        recent_logs=recent_logs
    )
