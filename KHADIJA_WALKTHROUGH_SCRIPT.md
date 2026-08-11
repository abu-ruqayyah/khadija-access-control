# 🎬 Khadija Bukar — Access Control Audit Capstone Presentation Script (2-3 Minutes)

**Student Name**: Khadija Bukar  
**Email**: `khadijahbukarbiu@gmail.com`  
**Fellow ID**: `FE/26/4554984566`  
**Cohort**: Cybersecurity NextGen Cohort (Project ID: CS-15)  
**Project Title**: Access Control Audit & Systems Hardening Platform  
**Live Render Deployment URL**: *(Update upon Render deployment)*  

---

### ⏱️ Video Presentation Outline (Target: 2 min 30 sec)

| Timecode | Screen Action | Narration Script |
| :--- | :--- | :--- |
| **0:00 - 0:25** | Open Landing Page (`/`) showing Hero Title, Fellow ID `FE/26/4554984566`, and Least Privilege Score badge. | *"Hello evaluators, my name is **Khadija Bukar** (Fellow ID: FE/26/4554984566), and this is my 3MTT Cybersecurity Capstone Project titled **Access Control Audit & Systems Hardening Platform**.<br/><br/>Over-privilege is a primary security risk in modern enterprise networks. When users accumulate unnecessary administrative or financial rights, it leads to privilege escalation, data exfiltration, and internal fraud. My application systematically audits organizational roles against the Principle of Least Privilege (PoLP)."* |
| **0:25 - 0:55** | Click **Log In** and log in as `khadija_auditor` (`AuditAdminPassword123!`). Show Command Center Dashboard (`/dashboard`) with Chart.js role risk breakdown and KPI cards. | *"Here in the **Command Center Dashboard**, security auditors get an immediate high-level view of organizational access health. We see our **Least Privilege Score (85%)**, the total number of audited roles, active Separation of Duties conflicts, and granular permission distribution.<br/><br/>Notice the Role Risk Distribution chart, which categorizes roles by risk level based on the sensitivity of their assigned entitlements."* |
| **0:55 - 1:30** | Click on **Role Matrix** (`/audit/roles`) showing the role vs permission grid. Demonstrate revoking a permission. | *"Next, we inspect the **Role & Permission Entitlement Matrix**. This grid maps organizational roles—such as Cloud Infrastructure Lead, Payroll Accountant, and Over-Privileged HR Assistant—against granular system permissions.<br/><br/>As an auditor, I can perform one-click right-sizing. For example, if I notice that the HR Assistant role has been assigned root execution rights (`exec:root_sudo`), I can click to immediately revoke that permission, enforcing least privilege in real time."* |
| **1:30 - 2:05** | Navigate to **Audit Findings** (`/audit/findings`) and click **Download PDF Report**. | *"In the **Audit Findings** view, our automated audit engine highlights specific vulnerability categories such as **Separation of Duties (SoD) toxic pairs**—for instance, when a single role has both `write:payroll` and `approve:payroll_payout`.<br/><br/>The system provides step-by-step hardening recommendations for each finding, and allows auditors to generate professional **ReportLab PDF Executive Reports** and **CSV audit spreadsheets** for IT compliance sign-off."* |
| **2:05 - 2:30** | Navigate to **Safe Lab Evidence** (`/lab/methodology`) showing VirtualBox / Kali / Wireshark / Nmap documentation. | *"Finally, the project includes a **Technical Safe Cyber Lab** component. Using VirtualBox, Kali Linux, Wireshark, Nmap, and OWASP ZAP in an isolated virtual lab (`192.168.56.0/24`), I conducted packet analysis and broken access control testing against authorized target VMs.<br/><br/>All evidence artifacts are stored and documented within the platform. Thank you for watching!"* |

---

### 🔑 Demo Credentials for Video Recording & Evaluators:

- **Role**: Lead Auditor & Security Admin
- **Username / Email**: `khadija_auditor` *(or `khadijahbukarbiu@gmail.com`)*
- **Password**: `AuditAdminPassword123!`

---

### 💡 Presentation Recording Instructions for Khadija Bukar:
1. **Screen Recorder**: Use OBS Studio, Loom, or Windows Game Bar (`Win + G`) to record your screen and microphone.
2. **Resolution**: Set to 1080p full screen.
3. **Pacing**: Follow the timecode outline above to keep your video strictly within 2 to 3 minutes.
