import os
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.models import db, AuditSession, AuditFinding

class AuditReportGenerator:

    @classmethod
    def generate_pdf_report(cls, audit_session_id, output_path):
        session = db.session.get(AuditSession, audit_session_id)
        if not session:
            raise ValueError(f"AuditSession #{audit_session_id} not found.")

        findings = AuditFinding.query.filter_by(audit_session_id=session.id).all()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubTitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=15
        )

        heading2_style = ParagraphStyle(
            'Heading2Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )

        badge_critical = ParagraphStyle('CriticalBadge', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#DC2626'))
        badge_high = ParagraphStyle('HighBadge', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#EA580C'))
        badge_moderate = ParagraphStyle('ModerateBadge', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#D97706'))

        story = []

        story.append(Paragraph("ACCESS CONTROL AUDIT & LEAST PRIVILEGE REPORT", title_style))
        story.append(Paragraph(f"<b>Student Project:</b> Khadija Bukar (FE/26/4554984566) &nbsp;|&nbsp; <b>Execution Date:</b> {session.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} &nbsp;|&nbsp; <b>Auditor:</b> {session.executed_by}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284C7'), spaceAfter=15))

        metric_score = f"<font size=16 color='#0284C7'><b>{session.least_privilege_score}%</b></font><br/><font size=8 color='#64748B'>LEAST PRIVILEGE SCORE</font>"
        metric_roles = f"<font size=16 color='#0F172A'><b>{session.total_roles_audited}</b></font><br/><font size=8 color='#64748B'>ROLES AUDITED</font>"
        metric_overpriv = f"<font size=16 color='#DC2626'><b>{session.overprivileged_roles_count}</b></font><br/><font size=8 color='#64748B'>OVER-PRIVILEGED ROLES</font>"
        metric_sod = f"<font size=16 color='#EA580C'><b>{session.sod_conflicts_count}</b></font><br/><font size=8 color='#64748B'>SoD CONFLICTS</font>"

        summary_table_data = [[
            Paragraph(metric_score, body_style),
            Paragraph(metric_roles, body_style),
            Paragraph(metric_overpriv, body_style),
            Paragraph(metric_sod, body_style)
        ]]

        summary_table = Table(summary_table_data, colWidths=[135, 135, 135, 135])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph("1. Executive Summary & Compliance Overview", heading2_style))
        exec_text = f"An automated Access Control Audit was conducted by <b>Khadija Bukar</b> to evaluate alignment with the <b>Principle of Least Privilege (PoLP)</b>, NIST SP 800-53 Access Control concepts, and Separation of Duties (SoD) guidelines. The evaluation identified <b>{len(findings)} security findings</b> across the organization's role and user access matrix."
        story.append(Paragraph(exec_text, body_style))
        story.append(Spacer(1, 10))

        story.append(Paragraph("2. Access Control Findings & Vulnerability Matrix", heading2_style))
        
        findings_table_data = [
            [Paragraph("<b>Severity</b>", body_style), Paragraph("<b>Finding Category</b>", body_style), Paragraph("<b>Target Role / User</b>", body_style), Paragraph("<b>Details & Risk</b>", body_style)]
        ]

        for f in findings:
            if f.severity == 'CRITICAL':
                sev_p = Paragraph("CRITICAL", badge_critical)
            elif f.severity == 'HIGH':
                sev_p = Paragraph("HIGH", badge_high)
            else:
                sev_p = Paragraph(f.severity, badge_moderate)

            cat_p = Paragraph(f.finding_type.replace('_', ' '), body_style)
            target_p = Paragraph(f.target_name, body_style)
            desc_p = Paragraph(f"<b>{f.details}</b><br/><i>Risk:</i> {f.risk_explanation}", body_style)

            findings_table_data.append([sev_p, cat_p, target_p, desc_p])

        findings_table = Table(findings_table_data, colWidths=[65, 95, 110, 270])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        for i in range(4):
            findings_table_data[0][i].style.textColor = colors.white

        story.append(findings_table)
        story.append(Spacer(1, 15))

        story.append(Paragraph("3. System Hardening & Access Remediation Plan", heading2_style))
        
        for idx, f in enumerate(findings, 1):
            rec_html = f"<b>{idx}. {f.target_name} ({f.finding_type})</b><br/>" \
                       f"<b>Remediation:</b> {f.remediation_recommendation}<br/>"
            story.append(Paragraph(rec_html, body_style))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
        sign_text = "<b>Report Certification:</b> Generated by Khadija Bukar's Access Control Audit Platform. Verified for Least Privilege Compliance."
        story.append(Paragraph(sign_text, subtitle_style))

        doc.build(story)
        return output_path

    @classmethod
    def generate_csv_report(cls, audit_session_id, output_path):
        session = db.session.get(AuditSession, audit_session_id)
        if not session:
            raise ValueError(f"AuditSession #{audit_session_id} not found.")

        findings = AuditFinding.query.filter_by(audit_session_id=session.id).all()

        with open(output_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Audit ID', 'Timestamp', 'Finding ID', 'Severity', 'Category', 'Target Name', 'Details', 'Risk Explanation', 'Remediation Recommendation', 'Status'])
            
            for f in findings:
                writer.writerow([
                    session.id,
                    session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    f.id,
                    f.severity,
                    f.finding_type,
                    f.target_name,
                    f.details,
                    f.risk_explanation,
                    f.remediation_recommendation,
                    f.status
                ])

        return output_path
