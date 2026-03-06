from fpdf import FPDF
import datetime
import os
import re

class CoughReportPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(78, 205, 196) # Teal color
        # Centered header
        self.cell(0, 10, 'SMART COUGH MONITOR', align='C', new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(100)
        self.cell(0, 10, 'AI-Powered Respiratory Health Analysis', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(10)
        
        # Horizontal line
        self.set_draw_color(78, 205, 196)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', align='C')

def clean_text_for_pdf(text):
    """
    Replaces emojis and special characters with PDF-safe text equivalents.
    """
    replacements = {
        "🫁": "[LUNGS]",
        "🩺": "[DIAGNOSIS]",
        "📖": "[DESCRIPTION]",
        "🥗": "[NUTRITION]",
        "⚠️": "[WARNING]",
        "📊": "[SEVERITY]",
        "🤧": "[COUGH]",
        "🔊": "[NOISE]",
        "✓": "[OK]",
        "🔴": "[REC]",
    }
    
    for emoji, label in replacements.items():
        text = text.replace(emoji, label)
    
    # Ensure text is compatible with standard PDF encoding
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(analysis_text, filename="cough_report.pdf"):
    """
    Converts the analysis text into a professional PDF while handling Unicode and Layout errors.
    """
    safe_text = clean_text_for_pdf(analysis_text)
    
    pdf = CoughReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Define widths explicitly to avoid "horizontal space" errors
    # Page width is usually 210mm. Margins are 10mm each. Content width = 190mm.
    content_w = 190 

    # Split lines and process
    lines = safe_text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(5)
            continue
            
        # Ensure we are always at the left margin before starting a block
        pdf.set_x(10)

        # Check for headers (which now look like [SECTION])
        if "[" in stripped and "]" in stripped:
            pdf.set_font('helvetica', 'B', 14)
            pdf.set_text_color(47, 154, 145) # Darker teal
            pdf.multi_cell(content_w, 10, stripped)
            pdf.set_font('helvetica', '', 12)
            pdf.set_text_color(0)
        else:
            # Body text / bullet points
            clean_line = stripped.replace('-', '•')
            pdf.multi_cell(content_w, 8, clean_line)
            
    # Save the PDF to bytes
    return pdf.output()
