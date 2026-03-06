import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Notification Configuration from .env
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

def send_full_email_report(recipient_email, subject, analysis_text):
    """
    Sends the full Gemini analysis directly in the HTML body of the email.
    No PDF attachment needed.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return "⚠️ Error: Please set SENDER_EMAIL and SENDER_PASSWORD in your .env file."

    try:
        msg = MIMEMultipart()
        msg['From'] = f"Smart Cough Monitor <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Convert the Markdown-like analysis into simple HTML
        formatted_analysis = analysis_text.replace('\n', '<br>')
        
        # Add some styling to section headers (e.g. lines starting with emojis)
        lines = analysis_text.split('\n')
        styled_html = ""
        for line in lines:
            if any(emoji in line for emoji in ['🩺', '🫁', '📖', '🥗', '⚠️', '📊', '🤧', '🔊']):
                styled_html += f'<h3 style="color: #2f9a91; margin-top: 20px; border-bottom: 1px solid #eee;">{line}</h3>'
            elif line.strip().startswith('-') or line.strip().startswith('*'):
                styled_html += f'<li style="margin-left: 20px;">{line.strip()[1:].strip()}</li>'
            else:
                styled_html += f'<p style="margin: 5px 0;">{line}</p>'

        html_content = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f4f7f6; padding: 20px;">
            <div style="max-width: 700px; margin: auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4ECDC4; margin: 0; font-size: 28px;">🫁 AI Cough Analysis Report</h1>
                    <p style="color: #888; margin: 5px 0;">Smart Respiratory Health Monitor</p>
                </div>
                
                <div style="padding: 20px; border: 1px solid #eef2f1; border-radius: 8px; background-color: #fafdfc;">
                    {styled_html}
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background: #fff5f5; border-radius: 6px; font-size: 0.85rem; color: #c53030; border-left: 4px solid #fc8181;">
                    <strong>Disclaimer:</strong> This is a computer-generated analysis for informational purposes. It is NOT a medical diagnosis. Please consult a qualified healthcare professional.
                </div>
                
                <p style="text-align: center; font-size: 0.8rem; color: #aaa; margin-top: 30px;">
                    Report generated on {os.popen('date /t').read().strip()} | Sent by Cough Monitor System
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        return "✅ Success: Full report sent to your Gmail!"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"
