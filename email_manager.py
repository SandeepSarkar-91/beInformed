import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailManager:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, receiver_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def send_approval_email(self, proposal, approve_url, reject_url):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Trade Approval Required: {proposal['symbol']}"
        msg["From"] = self.sender_email
        msg["To"] = self.receiver_email

        html = f"""
        <html>
        <body>
            <h3>Trade Proposal</h3>
            <p><strong>Symbol:</strong> {proposal['symbol']}</p>
            <p><strong>Quantity:</strong> {proposal['quantity']}</p>
            <p><strong>Side:</strong> {proposal['side']}</p>
            <p><strong>Reason:</strong> {proposal['reason']}</p>
            <hr>
            <p>Please approve or reject this trade:</p>
            <a href="{approve_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">APPROVE</a>
            &nbsp;
            <a href="{reject_url}" style="background-color: #f44336; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">REJECT</a>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            print("Approval email sent successfully.")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
