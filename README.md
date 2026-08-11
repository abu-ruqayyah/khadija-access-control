# Access Control Audit & Systems Hardening Platform

**Student Name**: Khadija Bukar  
**Email**: `khadijahbukarbiu@gmail.com`  
**Fellow ID**: `FE/26/4554984566`  
**Cohort**: Cybersecurity NextGen Cohort (Project ID: CS-15)  
**Program**: 3MTT (3 Million Technical Talent) Program  
**Project Title**: Access Control Audit & Systems Hardening Platform  

---

## 🎯 Executive Summary
Over-privilege is a primary threat vector in modern enterprise environments. When users and roles accumulate unnecessary administrative, financial, or system privileges beyond their operational requirements, it leads to privilege escalation, insider threat abuse, and compliance violations.

The **Access Control Audit Platform** (`KhadijaAccessAudit`) systematically evaluates role-based access control (RBAC) structures aligned with **NIST SP 800-53 Access Control** concepts and the **Principle of Least Privilege (PoLP)**. The application features:
- **Interactive Role Review Matrix**: Map roles to granular permissions with real-time entitlement right-sizing.
- **Automated Audit Engine**: Calculates an organizational Least Privilege Score (LPS) and detects toxic Separation of Duties (SoD) permission pairs.
- **Executive Reporting Engine**: Generates dynamic ReportLab PDF audit certificates and CSV spreadsheets.
- **Technical Safe Cyber Lab**: Authoritative evidence portal documenting VM lab testing with VirtualBox, Kali Linux, Wireshark, Nmap, and OWASP ZAP.

---

## 🔑 Evaluator Test Credentials

- **Auditor Admin Username**: `khadija_auditor` *(or `khadijahbukarbiu@gmail.com`)*
- **Auditor Admin Password**: `AuditAdminPassword123!`

---

## 🏗️ Technology Architecture

- **Backend**: Python 3, Flask, SQLAlchemy ORM, Flask-Login
- **Production Server (WSGI)**: Gunicorn 26.0.0
- **Database Engine**: Render PostgreSQL (Production) / SQLite (Local)
- **Frontend & Visuals**: HTML5, Vanilla CSS, Bootstrap 5, Chart.js
- **Document Generation**: ReportLab PDF, Python CSV Module
- **Automated Testing**: PyTest (100% Pass Rate across 5 Test Modules)
- **Cloud Hosting**: Render Web Services

---

## 🚀 Quick Start (Local Development)

1. **Navigate to Project Directory**:
   ```bash
   cd khadija_bukar_access_control
   ```

2. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python run.py
   ```

4. **Access Local Portal**:
   - Open browser to `http://127.0.0.1:5002`
