import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
UPLOADS_DIR = os.path.join(INSTANCE_DIR, 'uploads')
REPORTS_DIR = os.path.join(UPLOADS_DIR, 'reports')
LAB_EVIDENCE_DIR = os.path.join(UPLOADS_DIR, 'lab_evidence')

os.makedirs(INSTANCE_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LAB_EVIDENCE_DIR, exist_ok=True)

class Config:
    ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Secret Key Configuration
    _raw_secret_key = os.environ.get('SECRET_KEY')
    if not _raw_secret_key:
        if ENV == 'production':
            raise RuntimeError("CRITICAL SECURITY ERROR: 'SECRET_KEY' environment variable must be set in production.")
        _raw_secret_key = 'dev-fallback-khadija-access-control-key-2026'
    SECRET_KEY = _raw_secret_key
    
    # Environment-driven database configuration
    raw_db_url = os.environ.get('DATABASE_URL')
    if raw_db_url and not raw_db_url.startswith("sqlite:///"):
        if raw_db_url.startswith("postgres://"):
            raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        db_path = os.path.abspath(os.path.join(INSTANCE_DIR, 'khadija_access_audit.db')).replace('\\', '/')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload paths outside static directory
    UPLOAD_FOLDER = UPLOADS_DIR
    REPORTS_FOLDER = REPORTS_DIR
    LAB_EVIDENCE_FOLDER = LAB_EVIDENCE_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'pcap', 'pcapng', 'txt', 'json', 'xml', 'csv'}
    
    # Security Session Flags
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Admin Pre-seeding
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'khadija_auditor')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'khadijahbukarbiu@gmail.com')
    
    _raw_admin_pw = os.environ.get('ADMIN_PASSWORD')
    if not _raw_admin_pw:
        if ENV == 'production':
            raise RuntimeError("CRITICAL SECURITY ERROR: 'ADMIN_PASSWORD' environment variable must be set in production.")
        _raw_admin_pw = 'AuditAdminPassword123!'
    ADMIN_PASSWORD = _raw_admin_pw
    
    SEED_DEMO_DATA = os.environ.get('SEED_DEMO_DATA', 'True').lower() == 'true'
