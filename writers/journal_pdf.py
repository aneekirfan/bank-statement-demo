from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import mm

def generate_journal_pdf(entries, output_path, account_holder_name):
    # Setup Document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=10*mm, leftMargin=10*mm,
        topMargin=10*mm, bottomMargin=10*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # 1. Title
    header_style = styles["Heading1"]
    header_style.alignment = 1  # Center
    title = Paragraph(f"{account_holder_name}'s Journal", header_style)
    elements.append(title)
    elements.append(Spacer(1, 10*mm))
    
    # 2. Prepare Table Data
    # Headers
    data = [[
        Paragraph("<b>Date</b>", styles["Normal"]),
        Paragraph("<b>Particulars</b>", styles["Normal"]),
        Paragraph("<b>Debit (Rs.)</b>", styles["Normal"]),
        Paragraph("<b>Credit (Rs.)</b>", styles["Normal"])
    ]]
    
    normal_style = styles["Normal"]
    
    for e in entries:
        date = e["date"]
        debit_ledger = e["debit"]
        credit_ledger = e["credit"]
        amount = f"{e['amount']:,.2f}"
        narration = e.get("narration", "")
        
        # Format Particulars Column:
        # Debit A/c ... Dr
        #   To Credit A/c
        #   (Being Narration...)
        particulars_html = f"""
        <b>{debit_ledger} Dr.</b><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;To {credit_ledger}<br/>
        <font color="grey" size="9"><i>(Being {narration})</i></font>
        """
        
        row = [
            Paragraph(date, normal_style),
            Paragraph(particulars_html, normal_style),
            Paragraph(amount, normal_style),
            Paragraph(amount, normal_style)
        ]
        data.append(row)
        
    # 3. Create Table with Grid Lines
    # Widths: Date(25), Particulars(95), Dr(35), Cr(35) -> Fits A4
    cw = [25*mm, 95*mm, 35*mm, 35*mm]
    
    t = Table(data, colWidths=cw, repeatRows=1)
    
    # Add Excel-like Grid Styling
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), # Header Grey
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),               # Default Left Align
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),              # Amounts Right Align
        ('VALIGN', (0,0), (-1,-1), 'TOP'),               # Vertical Top Align
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),     # SOLID BLACK LINES
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),   # Header Bold
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),            # Padding
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    
    elements.append(t)
    
    # 4. Build PDF
    doc.build(elements)