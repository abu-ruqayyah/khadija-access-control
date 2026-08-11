import os
from app.services.audit_engine import AccessControlAuditEngine
from app.services.report_generator import AuditReportGenerator

def test_report_generation(app):
    with app.app_context():
        session = AccessControlAuditEngine.run_full_audit(executed_by='Test Runner')
        
        pdf_path = os.path.join(app.config['REPORTS_FOLDER'], f'test_khadija_report_{session.id}.pdf')
        csv_path = os.path.join(app.config['REPORTS_FOLDER'], f'test_khadija_report_{session.id}.csv')
        
        AuditReportGenerator.generate_pdf_report(session.id, pdf_path)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0
        
        AuditReportGenerator.generate_csv_report(session.id, csv_path)
        assert os.path.exists(csv_path)
        assert os.path.getsize(csv_path) > 0
        
        if os.path.exists(pdf_path): os.remove(pdf_path)
        if os.path.exists(csv_path): os.remove(csv_path)
