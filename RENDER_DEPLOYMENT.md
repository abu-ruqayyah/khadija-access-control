# Render Deployment Protocol — Khadija Bukar Access Control Audit Platform (CS-15)

**Student:** Khadija Bukar  
**Fellow ID:** `FE/26/4554984566`  
**Project ID:** CS-15  
**GitHub Repository:** [abu-ruqayyah/khadija-access-control](https://github.com/abu-ruqayyah/khadija-access-control.git)  

---

## 🚀 Quick Deployment Methods

### Option A: Automatic Blueprint Deployment (Recommended)
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Blueprint**.
3. Connect your GitHub repository: `abu-ruqayyah/khadija-access-control`.
4. Render will automatically detect `render.yaml` and provision both:
   - **PostgreSQL Managed Database** (`khadija-access-control-db`)
   - **Web Service** (`khadija-access-control`)
5. Fill in the required secret values (`ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`).
6. Click **Apply**.

---

### Option B: Manual Web Service & Database Setup

#### Step 1: Create Render PostgreSQL Database
1. Go to **Render Dashboard** → **New +** → **PostgreSQL**.
2. Configure:
   - **Name**: `khadija-access-control-db`
   - **Database**: `access_audit_db`
   - **User**: `audit_user`
   - **Plan**: Free
3. Click **Create Database** and copy the **Internal Database URL**.

#### Step 2: Create Web Service
1. Go to **Render Dashboard** → **New +** → **Web Service**.
2. Connect repository `abu-ruqayyah/khadija-access-control`.
3. Configure Details:
   - **Name**: `khadija-access-control`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`
   - **Plan**: Free

#### Step 3: Environment Variables
Add the following in the **Environment** tab of the Web Service:

| Environment Variable | Value / Setting | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | *[Paste PostgreSQL URL]* | Render PostgreSQL connection URI. |
| `SECRET_KEY` | *[32+ character random string]* | Session & CSRF signing key. |
| `FLASK_ENV` | `production` | Enables production validation. |
| `FLASK_APP` | `wsgi.py` | Application entry point. |
| `FLASK_DEBUG` | `False` | Disables debug tracebacks. |
| `SESSION_COOKIE_SECURE` | `True` | Forces HTTPS-only cookies. |
| `ADMIN_USERNAME` | `khadija_auditor` | Production lead auditor username. |
| `ADMIN_EMAIL` | `khadijahbukarbiu@gmail.com` | Production lead auditor email. |
| `ADMIN_PASSWORD` | *[Strong Admin Password]* | Production lead auditor password. |
| `SEED_DEMO_DATA` | `True` *(or `False`)* | Controls initial baseline audit seeding. |

---

## 🔍 Verification & Health Check

Once deployed and status reads **Live**:
- **Health Check Endpoint**:  
  `https://<your-render-app>.onrender.com/health`  
  *Response:* `{"app":"Khadija Bukar Access Control Audit","fellow_id":"FE/26/4554984566","status":"ok","student":"Khadija Bukar"}`
- **Login Verification**:  
  Access `/auth/login` and log in with your configured `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
