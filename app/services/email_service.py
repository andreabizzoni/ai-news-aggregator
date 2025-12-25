import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import datetime
from dotenv import load_dotenv

from ..models.llm_response import EmailLLMResponse

load_dotenv()
logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.email_from = os.getenv("EMAIL_FROM")
        self.email_to = os.getenv("EMAIL_TO")
        self.email_password = os.getenv("EMAIL_PASSWORD")

        if not all([self.email_from, self.email_to, self.email_password]):
            logger.warning("Email credentials not fully configured in .env file")

    def render_email_html(
        self, email_content: EmailLLMResponse, user: str = "Andrea"
    ) -> str:
        items_html = ""
        for item in email_content.digest_items:
            items_html += f"""
            <div style="background-color: #f8f9fa; border-left: 4px solid #4a90e2; padding: 20px; margin: 20px 0; border-radius: 4px;">
                <h2 style="color: #2c3e50; margin: 0 0 10px 0; font-size: 20px;">{item.title}</h2>
                <p style="color: #555; line-height: 1.6; margin: 10px 0;">{item.summary}</p>
                <div style="margin-top: 15px;">
                    <a href="{item.url}" style="display: inline-block; background-color: #4a90e2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">Read More</a>
                    <div style="color: #888; font-size: 14px; margin-top: 15px;">Source: {item.source}</div>
                </div>
            </div>
            """

        html = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI News Digest</title>
        </head>
        <body style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4a90e2; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">AI News Digest</h1>
            </div>
            
            <div style="background-color: white; padding: 30px; border: 1px solid #e0e0e0; border-top: none;">
                <p style="font-size: 16px; margin: 0 0 10px 0;">Hi {user},</p>
                <p style="font-size: 18px; color: #4a90e2; font-weight: bold; margin: 0 0 20px 0;">Your AI digest for {datetime.now().strftime("%B %d, %Y")} is ready!</p>
                <p style="color: #555; line-height: 1.8; margin-bottom: 30px;">{email_content.introduction}</p>
                
                {items_html}
            </div>
            
            <div style="text-align: center; padding: 20px; color: #888; font-size: 12px;">
                <p>AI News Aggregator | Automated Daily Digest</p>
            </div>
        </body>
        </html>"""

        return html

    def send_email(self, email_content: EmailLLMResponse | None) -> bool:
        if not all([self.email_from, self.email_to, self.email_password]):
            logger.error("Cannot send email: missing credentials in .env file")
            return False

        if email_content is None:
            subject = "AI News Digest - Content Generation Failed"
            html_content = """
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <p>Oops! We had some issues generating your news digest today.</p>
                <p>Please hang tight while we squash a few bugs.</p>
            </body>
            </html>
            """
        else:
            subject = "Your AI News Digest"
            html_content = self.render_email_html(email_content)

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_from
            message["To"] = self.email_to

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_from, self.email_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {self.email_to}")
            return True

        except Exception as e:
            logger.exception(f"Failed to send email: {e}")
            return False
