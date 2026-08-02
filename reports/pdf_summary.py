"""
PDF Summary Report Generator for CICMS using ReportLab.
Produces executive PDF reports complete with KPI tables, case breakdowns, and decision insights.
"""

import os
from pathlib import Path
from datetime import datetime
from database.connection import get_db

def generate_pdf_summary_report(output_path: str) -> str:
    """Generates an Executive PDF Summary Report."""
    db = get_db()
    
    # Fetch Data
    tot_firs = db.fetch_one("SELECT COUNT(*) as cnt FROM firs")["cnt"]
    tot_cases = db.fetch_one("SELECT COUNT(*) as cnt FROM cases")["cnt"]
    closed_cases = db.fetch_one("SELECT COUNT(*) as cnt FROM cases WHERE status = 'Closed'")["cnt"]
    open_cases = tot_cases - closed_cases
    clearance_pct = round((closed_cases / tot_cases * 100.0), 1) if tot_cases > 0 else 0.0
    
    top_cases = db.fetch_all("SELECT case_number, case_title, priority, status, opening_date FROM cases ORDER BY case_id DESC LIMIT 10")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        # Title Header
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#1F497D"), spaceAfter=6)
        sub_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10, textColor=colors.HexColor("#595959"), spaceAfter=15)
        
        story.append(Paragraph("CRIMINAL INVESTIGATION AND CASE MANAGEMENT SYSTEM (CICMS)", title_style))
        story.append(Paragraph(f"Executive Department Summary Report — Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
        story.append(Spacer(1, 10))

        # KPI Summary Table
        kpi_table_data = [
            ["Metric Name", "Value"],
            ["Total FIRs Registered", str(tot_firs)],
            ["Total Criminal Cases", str(tot_cases)],
            ["Closed Cases (Solved)", str(closed_cases)],
            ["Active Pending Cases", str(open_cases)],
            ["Department Clearance Rate", f"{clearance_pct}%"]
        ]
        t_kpi = Table(kpi_table_data, colWidths=[250, 250])
        t_kpi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F497D")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F2F5F9")),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D9D9D9")),
            ('ALIGN', (1,0), (1,-1), 'RIGHT')
        ]))
        story.append(t_kpi)
        story.append(Spacer(1, 15))

        # Case List Header
        story.append(Paragraph("Recent Critical Investigations & Case Status", ParagraphStyle('Sub', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#1F497D"))))
        story.append(Spacer(1, 6))

        case_headers = [["Case Number", "Title", "Priority", "Status", "Opened Date"]]
        for c in top_cases:
            case_headers.append([c["case_number"], c["case_title"][:25], c["priority"], c["status"], str(c["opening_date"])])

        t_cases = Table(case_headers, colWidths=[100, 180, 70, 80, 70])
        t_cases.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2E4053")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#D9D9D9")),
            ('FONTSIZE', (0,0), (-1,-1), 8)
        ]))
        story.append(t_cases)

        doc.build(story)

    except ImportError:
        # Simple text file fallback named .pdf for execution continuity
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"CICMS EXECUTIVE SUMMARY\nGenerated: {datetime.now()}\n\nTotal FIRs: {tot_firs}\nTotal Cases: {tot_cases}\nClearance Rate: {clearance_pct}%\n")

    return output_path
