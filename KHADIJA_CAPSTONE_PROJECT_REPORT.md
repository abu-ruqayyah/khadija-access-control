# 3MTT Cybersecurity Capstone Project Report
## Access Control Audit & Systems Hardening Platform (CS-15)

**Student Name**: Khadija Bukar  
**Email**: `khadijahbukarbiu@gmail.com`  
**Fellow ID**: `FE/26/4554984566`  
**Cohort**: 3MTT Cybersecurity NextGen Cohort  
**Project ID**: CS-15  
**GitHub Repository**: [abu-ruqayyah/khadija-access-control](https://github.com/abu-ruqayyah/khadija-access-control.git)  

---

## 1. Executive Summary

Over-privilege and toxic permission combinations represent major attack vectors in enterprise cybersecurity. When user accounts accumulate unnecessary administrative, financial, or system privileges beyond their operational duties, organizations face heightened risks of privilege escalation, lateral movement, data exfiltration, and internal fraud.

The **Access Control Audit & Systems Hardening Platform** is a web-based security auditing framework designed to evaluate organizational role-based access control (RBAC) structures aligned with **NIST SP 800-53 Access Control** concepts (specifically AC-2 Account Management, AC-3 Access Enforcement, AC-5 Separation of Duties, and AC-6 Least Privilege).

---

## 2. Key Features & Architectural Capabilities

### A. Dynamic RBAC Entitlement Matrix
- Maps organizational roles (`Cloud Infrastructure Lead`, `Payroll Accountant`, `Over-Privileged HR Assistant`, `External Cloud Vendor Support`, `Junior Helpdesk Assistant`) to granular permission codes.
- Categorizes permissions by risk levels (`CRITICAL`, `HIGH`, `MODERATE`, `LOW`).
- Provides real-time one-click permission granting and revocation for security right-sizing.

### B. Automated Access Control Audit Engine
- Evaluates permission concentration and calculates an aggregate **Least Privilege Score (0.0% – 100.0%)**.
- Detects **Separation of Duties (SoD) Toxic Pairs**:
  - `write:payroll` + `approve:payroll_payout` (Financial Fraud Risk)
  - `create:user_account` + `assign:admin_role` (Privilege Escalation Risk)
  - `manage:cloud_iam` + `delete:audit_logs` (Anti-Forensics Risk)
  - `read:customer_pii` + `export:bulk_database` (Mass Exfiltration Risk)
- Flags dormant administrative accounts and non-IT administrative assignments.

### C. Executive Audit Reporting Engine
- Generates downloadable **ReportLab PDF Audit Certificates** with executive summaries, metric breakdowns, and remediation plans.
- Exports structured **CSV Findings Spreadsheets** for compliance tracking.

### D. Safe Cyber Laboratory Evidence Portal
- Provides safe, restricted evidence tracking for Wireshark (`.pcapng`), Nmap (`.xml`/`.txt`), and OWASP ZAP (`.json`) security scans conducted exclusively within isolated virtual lab environments (`127.0.0.1` / VirtualBox host-only network).

---

## 3. Production Security & Hardening Controls

| Security Control | Implementation Method | Result |
| :--- | :--- | :--- |
| **Secrets Management** | Production env vars (`SECRET_KEY`, `ADMIN_PASSWORD`) | Zero hardcoded production credentials |
| **Rate Limiting** | `Flask-Limiter` (`15 req/min` on auth endpoints) | Brute-force protection enabled |
| **CSRF Protection** | `Flask-WTF CSRFProtect` across all POST forms | Prevents cross-site request forgery |
| **Password Security** | Werkzeug `scrypt` password hashing | Resists rainbow table & brute-force attacks |
| **HTTP Security Headers** | CSP, `nosniff`, `SAMEORIGIN`/`DENY`, Referrer-Policy | Mitigates XSS, clickjacking, MIME-sniffing |
| **Isolated File Uploads** | Files saved outside `app/static/` with extension whitelist | Prevents web shell execution |

---

## 4. Generated Artifacts & Reports

The following audit reports have been compiled and generated locally in the system:
1. **Executive PDF Audit Certificate**: `instance/uploads/reports/Khadija_Bukar_Least_Privilege_Audit_Report.pdf`
2. **Audit Findings CSV Spreadsheet**: `instance/uploads/reports/Khadija_Bukar_Access_Control_Findings.csv`

---

## 5. Verification & Test Suite Summary

- **Khadija Bukar Test Suite**: `5 passed, 0 failed`
- **Root Workspace Test Suite**: `18 passed, 0 failed`
