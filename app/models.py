from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Join table for Role <-> Permission
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
    db.Column('is_essential', db.Boolean, default=True),
    db.Column('justification', db.String(255), nullable=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(80), nullable=False, default='General Staff')
    job_title = db.Column(db.String(80), nullable=False, default='Staff Member')
    role = db.Column(db.String(20), nullable=False, default='AUDITEE')  # 'ADMIN', 'AUDITOR', 'AUDITEE'
    is_active_account = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assigned_roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role in ['ADMIN', 'AUDITOR']

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False) # 'System Admin', 'Data Access', 'Financial', 'Cloud Infrastructure'
    risk_level = db.Column(db.String(20), nullable=False, default='MODERATE') # 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Permission {self.code} [{self.risk_level}]>'

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(80), nullable=False, default='General')
    is_system_role = db.Column(db.Boolean, default=False)
    
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))

    def risk_score(self):
        weight_map = {'CRITICAL': 10, 'HIGH': 7, 'MODERATE': 4, 'LOW': 1}
        score = 0
        for p in self.permissions:
            score += weight_map.get(p.risk_level, 1)
        return score

    def __repr__(self):
        return f'<Role {self.name}>'

class AuditSession(db.Model):
    __tablename__ = 'audit_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    executed_by = db.Column(db.String(80), nullable=False)
    total_roles_audited = db.Column(db.Integer, default=0)
    total_users_audited = db.Column(db.Integer, default=0)
    least_privilege_score = db.Column(db.Float, default=100.0)
    overprivileged_roles_count = db.Column(db.Integer, default=0)
    sod_conflicts_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='COMPLETED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    findings = db.relationship('AuditFinding', backref='session', lazy=True, cascade='all, delete-orphan')

class AuditFinding(db.Model):
    __tablename__ = 'audit_findings'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_session_id = db.Column(db.Integer, db.ForeignKey('audit_sessions.id'), nullable=False)
    finding_type = db.Column(db.String(50), nullable=False) # 'OVER_PRIVILEGED_ROLE', 'SOD_VIOLATION', 'DORMANT_ADMIN', 'EXCESSIVE_PERMISSIONS'
    severity = db.Column(db.String(20), nullable=False, default='MODERATE') # 'CRITICAL', 'HIGH', 'MODERATE', 'LOW'
    target_name = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, nullable=False)
    risk_explanation = db.Column(db.Text, nullable=False)
    remediation_recommendation = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='OPEN') # 'OPEN', 'REMEDIATED', 'RISK_ACCEPTED'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LabEvidence(db.Model):
    __tablename__ = 'lab_evidence'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    tool_category = db.Column(db.String(50), nullable=False) # 'VirtualBox VM', 'Kali/Parrot', 'Wireshark', 'Nmap', 'OWASP ZAP'
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    findings_summary = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.String(80), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
