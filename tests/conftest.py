import os
import pytest
from app import create_app
from app.models import db, User, Role, Permission

@pytest.fixture
def app():
    os.environ['FLASK_ENV'] = 'testing'
    test_db_path = os.path.join(os.path.dirname(__file__), 'test_khadija_audit.db').replace('\\', '/')
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key-khadija-bukar'

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        if not Permission.query.filter_by(code='exec:root_sudo').first():
            p1 = Permission(code='exec:root_sudo', name='Execute Root', category='System Admin', risk_level='CRITICAL')
            p2 = Permission(code='delete:audit_logs', name='Delete Logs', category='System Admin', risk_level='CRITICAL')
            p3 = Permission(code='write:payroll', name='Write Payroll', category='Financial', risk_level='HIGH')
            p4 = Permission(code='approve:payroll_payout', name='Approve Payout', category='Financial', risk_level='CRITICAL')
            db.session.add_all([p1, p2, p3, p4])
            db.session.commit()
        
        if not User.query.filter_by(username='test_admin').first():
            admin = User(username='test_admin', email='admin@test.local', full_name='Test Admin Khadija', role='ADMIN')
            admin.set_password('AdminPass123!')
            db.session.add(admin)
            db.session.commit()
        
        yield app

        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
