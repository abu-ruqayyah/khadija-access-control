from app.models import db, Role, Permission, AuditSession, AuditFinding
from app.services.audit_engine import AccessControlAuditEngine

def test_sod_toxic_pair_detection(app):
    with app.app_context():
        p_write = Permission.query.filter_by(code='write:payroll').first()
        p_approve = Permission.query.filter_by(code='approve:payroll_payout').first()
        
        toxic_role = Role.query.filter_by(name='Toxic Payroll Role').first()
        if not toxic_role:
            toxic_role = Role(name='Toxic Payroll Role', department='Finance')
            toxic_role.permissions.extend([p_write, p_approve])
            db.session.add(toxic_role)
            db.session.commit()
        
        session = AccessControlAuditEngine.run_full_audit(executed_by='Test Runner')
        
        assert session.sod_conflicts_count >= 1
        sod_findings = AuditFinding.query.filter_by(audit_session_id=session.id, finding_type='SOD_VIOLATION').all()
        assert len(sod_findings) >= 1
        assert 'write:payroll' in sod_findings[0].details

def test_least_privilege_score_calculation(app):
    with app.app_context():
        session = AccessControlAuditEngine.run_full_audit(executed_by='Test Runner')
        assert 0.0 <= session.least_privilege_score <= 100.0
