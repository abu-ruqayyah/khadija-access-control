from app.models import db, User, Role, Permission, AuditSession, AuditFinding, AuditLog

class AccessControlAuditEngine:
    SOD_TOXIC_PAIRS = [
        {
            "codes": ("write:payroll", "approve:payroll_payout"),
            "title": "Financial Fraud SoD Conflict",
            "severity": "CRITICAL",
            "risk": "A single user/role can both modify payroll records and approve payouts, allowing unauthorized financial disbursement.",
            "remediation": "Enforce strict Separation of Duties. Split payroll creation and approval into distinct roles requiring dual authorization."
        },
        {
            "codes": ("create:user_account", "assign:admin_role"),
            "title": "Unrestricted Privilege Escalation",
            "severity": "CRITICAL",
            "risk": "Role can create new accounts and elevate them to Administrator status without secondary verification.",
            "remediation": "Revoke role assignment capability from standard account provisioning. Restrict admin role assignment to identity management team."
        },
        {
            "codes": ("manage:cloud_iam", "delete:audit_logs"),
            "title": "Cloud IAM & Anti-Forensics Risk",
            "severity": "HIGH",
            "risk": "Role can modify Cloud IAM identity policies and delete audit trails, enabling unmonitored privilege escalation.",
            "remediation": "Revoke audit log deletion permissions. Forward cloud audit logs to an immutable write-once read-many (WORM) repository."
        },
        {
            "codes": ("read:customer_pii", "export:bulk_database"),
            "title": "Mass Data Exfiltration Risk",
            "severity": "HIGH",
            "risk": "Role has both read access to sensitive customer PII and bulk database export privileges.",
            "remediation": "Restrict bulk export capabilities to dedicated automated backup accounts with multi-factor approval."
        }
    ]

    @classmethod
    def run_full_audit(cls, executed_by="Lead Auditor Khadija Bukar", session_title="Least Privilege Compliance Audit"):
        users = User.query.all()
        roles = Role.query.all()
        
        findings = []
        total_roles = len(roles)
        total_users = len(users)
        overprivileged_roles_count = 0
        sod_conflicts_count = 0
        dormant_admins_count = 0
        
        for role in roles:
            perm_codes = {p.code for p in role.permissions}
            critical_perms = [p for p in role.permissions if p.risk_level == 'CRITICAL']
            high_perms = [p for p in role.permissions if p.risk_level == 'HIGH']
            
            if len(critical_perms) >= 2 or (len(critical_perms) + len(high_perms)) >= 4:
                overprivileged_roles_count += 1
                findings.append({
                    "finding_type": "OVER_PRIVILEGED_ROLE",
                    "severity": "CRITICAL" if len(critical_perms) >= 2 else "HIGH",
                    "target_name": f"Role: {role.name}",
                    "details": f"Role '{role.name}' holds {len(critical_perms)} CRITICAL and {len(high_perms)} HIGH risk permissions.",
                    "risk_explanation": f"Excessive permission concentration in '{role.name}' violates Principle of Least Privilege and increases threat blast radius.",
                    "remediation_recommendation": f"Perform role right-sizing. Strip unnecessary permissions ({', '.join(p.code for p in critical_perms)}) into specialized administrative sub-roles."
                })
            
            if role.department.lower() not in ['it security & compliance', 'system administration', 'cloud infrastructure']:
                for p in role.permissions:
                    if p.code in ['exec:root_sudo', 'delete:audit_logs', 'manage:cloud_iam']:
                        overprivileged_roles_count += 1
                        findings.append({
                            "finding_type": "ROLE_MISALIGNMENT",
                            "severity": "CRITICAL",
                            "target_name": f"Role: {role.name} ({role.department})",
                            "details": f"Non-IT department role '{role.name}' in '{role.department}' holds sensitive admin permission '{p.code}'.",
                            "risk_explanation": "Cross-departmental over-privilege exposes administrative utilities to unauthorized operational personnel.",
                            "remediation_recommendation": f"Revoke '{p.code}' from '{role.name}'. Re-assign administrative tasks exclusively to IT Security personnel."
                        })
            
            for sod in cls.SOD_TOXIC_PAIRS:
                code_a, code_b = sod["codes"]
                if code_a in perm_codes and code_b in perm_codes:
                    sod_conflicts_count += 1
                    findings.append({
                        "finding_type": "SOD_VIOLATION",
                        "severity": sod["severity"],
                        "target_name": f"Role: {role.name}",
                        "details": f"Toxic permission pair detected in role '{role.name}': ('{code_a}' AND '{code_b}'). {sod['title']}.",
                        "risk_explanation": sod["risk"],
                        "remediation_recommendation": sod["remediation"]
                    })
        
        for user in users:
            user_perm_codes = set()
            user_roles_list = user.assigned_roles
            for r in user_roles_list:
                for p in r.permissions:
                    user_perm_codes.add(p.code)
            
            if user.role in ['ADMIN', 'AUDITOR'] and not user.is_active_account:
                dormant_admins_count += 1
                findings.append({
                    "finding_type": "DORMANT_ADMIN",
                    "severity": "HIGH",
                    "target_name": f"User: {user.username} ({user.email})",
                    "details": f"Administrative user account '{user.username}' is marked INACTIVE but retains active admin role privileges.",
                    "risk_explanation": "Dormant administrative accounts are high-priority targets for credential theft and persistence attacks.",
                    "remediation_recommendation": f"Deprovision and strip all administrative roles from inactive user account '{user.username}' immediately."
                })
            
            if len(user_roles_list) > 1:
                for sod in cls.SOD_TOXIC_PAIRS:
                    code_a, code_b = sod["codes"]
                    if code_a in user_perm_codes and code_b in user_perm_codes:
                        sod_conflicts_count += 1
                        findings.append({
                            "finding_type": "USER_SOD_VIOLATION",
                            "severity": sod["severity"],
                            "target_name": f"User: {user.username} ({user.full_name})",
                            "details": f"User '{user.username}' accumulates toxic permissions across multiple assigned roles ({', '.join(r.name for r in user_roles_list)}).",
                            "risk_explanation": sod["risk"],
                            "remediation_recommendation": f"Remove conflicting role from user '{user.username}' to maintain strict separation of duties."
                        })

        penalty = (overprivileged_roles_count * 12) + (sod_conflicts_count * 15) + (dormant_admins_count * 10)
        least_privilege_score = max(0.0, min(100.0, 100.0 - penalty))
        
        audit_session = AuditSession(
            title=session_title,
            executed_by=executed_by,
            total_roles_audited=total_roles,
            total_users_audited=total_users,
            least_privilege_score=round(least_privilege_score, 1),
            overprivileged_roles_count=overprivileged_roles_count,
            sod_conflicts_count=sod_conflicts_count,
            status='COMPLETED'
        )
        db.session.add(audit_session)
        db.session.flush()
        
        for f in findings:
            finding_obj = AuditFinding(
                audit_session_id=audit_session.id,
                finding_type=f["finding_type"],
                severity=f["severity"],
                target_name=f["target_name"],
                details=f["details"],
                risk_explanation=f["risk_explanation"],
                remediation_recommendation=f["remediation_recommendation"],
                status='OPEN'
            )
            db.session.add(finding_obj)
            
        log_entry = AuditLog(
            event_type='AUDIT_RUN',
            username=executed_by,
            details=f"Ran Access Control Audit ID #{audit_session.id}. Score: {least_privilege_score}%. Findings: {len(findings)}."
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return audit_session
