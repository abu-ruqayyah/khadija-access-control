import os
from app import create_app
from app.models import db, User, Role, Permission, AuditLog, LabEvidence
from app.services.audit_engine import AccessControlAuditEngine

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        
        # 1. Seed Permissions
        if Permission.query.count() == 0:
            permissions_list = [
                # System & Cloud Admin
                Permission(code='exec:root_sudo', name='Execute Root / Sudo Commands', category='System Admin', risk_level='CRITICAL', description='Full administrative privilege execution on system nodes.'),
                Permission(code='delete:audit_logs', name='Delete Security Audit Logs', category='System Admin', risk_level='CRITICAL', description='Ability to clear or manipulate system audit trails.'),
                Permission(code='manage:cloud_iam', name='Modify Cloud IAM Policies', category='Cloud Infrastructure', risk_level='CRITICAL', description='Create and alter cloud access control policies.'),
                Permission(code='assign:admin_role', name='Assign Administrative Roles', category='System Admin', risk_level='CRITICAL', description='Grant administrative privileges to user accounts.'),
                
                # Data Access
                Permission(code='read:customer_pii', name='Read Customer PII Data', category='Data Access', risk_level='HIGH', description='Access sensitive personally identifiable customer information.'),
                Permission(code='export:bulk_database', name='Export Bulk Database Dumps', category='Data Access', risk_level='HIGH', description='Download complete database backups and table exports.'),
                Permission(code='read:employee_records', name='Read Staff HR Records', category='Data Access', risk_level='MODERATE', description='View internal staff HR profiles and department details.'),
                Permission(code='write:employee_records', name='Modify Staff HR Records', category='Data Access', risk_level='MODERATE', description='Update staff HR information.'),
                
                # Financial
                Permission(code='write:payroll', name='Modify Payroll Records', category='Financial', risk_level='HIGH', description='Edit employee salary and payout figures.'),
                Permission(code='approve:payroll_payout', name='Approve Payroll Disbursement', category='Financial', risk_level='CRITICAL', description='Authorize payout disbursement to banking endpoints.'),
                Permission(code='read:financial_reports', name='Read Quarterly Financial Reports', category='Financial', risk_level='MODERATE', description='View internal organizational financial statements.'),
                
                # User Provisioning
                Permission(code='create:user_account', name='Create New User Accounts', category='User Provisioning', risk_level='HIGH', description='Provision new user identities in directory services.'),
                Permission(code='reset:user_password', name='Reset User Passwords', category='User Provisioning', risk_level='MODERATE', description='Trigger administrative password resets for accounts.'),
                Permission(code='disable:user_account', name='Disable / Lock Accounts', category='User Provisioning', risk_level='MODERATE', description='Lock or deactivate user directory accounts.')
            ]
            db.session.add_all(permissions_list)
            db.session.commit()
            print("Seeded 14 granular permissions across 4 categories.")

        perm_map = {p.code: p for p in Permission.query.all()}

        # 2. Seed Roles
        if Role.query.count() == 0:
            role_cloud_lead = Role(
                name='Cloud Infrastructure Lead',
                department='Cloud Infrastructure',
                description='Cloud system architect managing IAM, container deployment, and security.',
                is_system_role=True
            )
            role_cloud_lead.permissions.extend([
                perm_map['manage:cloud_iam'], perm_map['exec:root_sudo'],
                perm_map['assign:admin_role'], perm_map['create:user_account']
            ])

            role_payroll = Role(
                name='Payroll Accountant',
                department='Finance',
                description='Prepares monthly staff payroll statements.',
                is_system_role=False
            )
            role_payroll.permissions.extend([
                perm_map['write:payroll'], perm_map['read:financial_reports'], perm_map['read:employee_records']
            ])

            # Over-Privileged HR Assistant (Vulnerable Demo Role)
            role_overpriv_hr = Role(
                name='Over-Privileged HR Assistant',
                department='Human Resources',
                description='HR assistant role with excessive administrative and financial permissions.',
                is_system_role=False
            )
            role_overpriv_hr.permissions.extend([
                perm_map['read:employee_records'], perm_map['write:employee_records'],
                perm_map['exec:root_sudo'], perm_map['write:payroll'], perm_map['approve:payroll_payout']
            ])

            # Third-Party Vendor (Vulnerable Demo Role)
            role_vendor = Role(
                name='External Cloud Vendor Support',
                department='External Vendor',
                description='Third-party vendor account with excessive bulk export and log manipulation rights.',
                is_system_role=False
            )
            role_vendor.permissions.extend([
                perm_map['read:customer_pii'], perm_map['export:bulk_database'], perm_map['delete:audit_logs']
            ])

            role_helpdesk = Role(
                name='Junior Helpdesk Assistant',
                department='IT Support',
                description='Frontline IT support handling password resets and account creation.',
                is_system_role=False
            )
            role_helpdesk.permissions.extend([
                perm_map['reset:user_password'], perm_map['create:user_account'], perm_map['read:employee_records']
            ])

            db.session.add_all([role_cloud_lead, role_payroll, role_overpriv_hr, role_vendor, role_helpdesk])
            db.session.commit()
            print("Seeded 5 organizational roles.")

        # 3. Seed Admin User
        admin_username = app.config['ADMIN_USERNAME']
        admin_email = app.config['ADMIN_EMAIL']
        admin_password = app.config['ADMIN_PASSWORD']

        admin_user = User.query.filter_by(role='ADMIN').first()
        if not admin_user:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                full_name='Khadija Bukar (Lead Auditor)',
                department='IT Security & Compliance',
                job_title='Access Control Security Auditor',
                role='ADMIN',
                is_active_account=True
            )
            admin_user.set_password(admin_password)
            
            cloud_lead_role = Role.query.filter_by(name='Cloud Infrastructure Lead').first()
            if cloud_lead_role:
                admin_user.assigned_roles.append(cloud_lead_role)
                
            db.session.add(admin_user)
            print(f"Initial Lead Auditor account created: username='{admin_username}'")
        else:
            admin_user.username = admin_username
            admin_user.email = admin_email
            admin_user.set_password(admin_password)
            print(f"Auditor Admin account updated: username='{admin_username}'")

        if app.config.get('SEED_DEMO_DATA', True):
            if User.query.filter_by(username='aminu_hr').first() is None:
                aminu = User(
                    username='aminu_hr',
                    email='aminu.hr@accessaudit.local',
                    full_name='Aminu Bello',
                    department='Human Resources',
                    job_title='Junior HR Assistant',
                    role='AUDITEE',
                    is_active_account=True
                )
                aminu.set_password('StaffPassword123!')
                hr_role = Role.query.filter_by(name='Over-Privileged HR Assistant').first()
                if hr_role:
                    aminu.assigned_roles.append(hr_role)
                db.session.add(aminu)

            if User.query.filter_by(username='vendor_ext').first() is None:
                vendor = User(
                    username='vendor_ext',
                    email='support@externalvendor.com',
                    full_name='External Vendor User',
                    department='External Vendor',
                    job_title='Vendor Support',
                    role='ADMIN',
                    is_active_account=False # Inactive dormant admin!
                )
                vendor.set_password('VendorPassword123!')
                v_role = Role.query.filter_by(name='External Cloud Vendor Support').first()
                if v_role:
                    vendor.assigned_roles.append(v_role)
                db.session.add(vendor)

            if LabEvidence.query.count() == 0:
                demo_evidence_list = [
                    LabEvidence(
                        title='Wireshark Packet Analysis — Unencrypted Credential & Access Token Inspection',
                        tool_category='Wireshark',
                        filename='wireshark_access_control_traffic.pcapng',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'wireshark_access_control_traffic.pcapng'),
                        description='Captured HTTP GET request traffic revealing unencrypted administrative session tokens.',
                        findings_summary='Demonstrated OWASP A01:2021 Broken Access Control vulnerability where lower-tier user tokens accessed admin endpoints.',
                        uploaded_by='Khadija Bukar'
                    ),
                    LabEvidence(
                        title='Nmap Permission & Service Exposure Scan Report',
                        tool_category='Nmap',
                        filename='nmap_service_permission_audit.xml',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'nmap_service_permission_audit.xml'),
                        description='Targeted Nmap NSE script scan auditing exposed SMB/RDP administrative shares and unauthorized port bindings.',
                        findings_summary='Identified open SMB share allowing read/write access to HR payroll folders without active Kerberos authentication.',
                        uploaded_by='Khadija Bukar'
                    ),
                    LabEvidence(
                        title='OWASP ZAP Automated Access Control Assessment',
                        tool_category='OWASP ZAP',
                        filename='owasp_zap_access_control_report.json',
                        file_path=os.path.join(app.config['LAB_EVIDENCE_FOLDER'], 'owasp_zap_access_control_report.json'),
                        description='Automated OWASP ZAP Access Control Matrix scan executing horizontal and vertical privilege escalation vectors.',
                        findings_summary='Flagged 3 vertical privilege escalation vectors where lower-tier accounts accessed higher-tier administrative functions.',
                        uploaded_by='Khadija Bukar'
                    )
                ]
                db.session.add_all(demo_evidence_list)

            db.session.commit()

            AccessControlAuditEngine.run_full_audit(
                executed_by='Khadija Bukar (Lead Auditor)',
                session_title='Baseline Least Privilege Access Control Audit'
            )
            print("Executed initial Baseline Least Privilege Audit.")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5002)
