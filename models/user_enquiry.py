from extensions import db
from datetime import datetime
from sqlalchemy import event
from flask_mail import Message
from flask import current_app

class Inquiry(db.Model):
    __tablename__ = 'user_enquiries'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=True)
    interested_in = db.Column(db.String(50))
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "property_id": self.property_id,
            "interested_in": self.interested_in,
            "message": self.message,
            "submitted_at": self.submitted_at.isoformat()
        }

from flask import current_app
from flask_mail import Message
from extensions import mail

@event.listens_for(Inquiry, 'after_insert')
def send_enquiry_email(mapper, connection, enquiry):
    with current_app.app_context():
        try:
            msg = Message(
                subject='New User Enquiry Received',
                sender=current_app.config['MAIL_USERNAME'],
                recipients=['admin@wallstreetllp.com'],
                body=f"""
New enquiry received:

Name: {enquiry.name}
Email: {enquiry.email}
Phone: {enquiry.phone}
Interested In: {enquiry.interested_in}
Message: {enquiry.message}
Submitted At: {enquiry.submitted_at}
                """
            )
            mail.send(msg)
            print("✅ Enquiry email sent successfully.")
        except Exception as e:
            print("❌ Error sending enquiry email:", e)

