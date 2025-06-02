from app import db
from app.mixins import ReferenceGenerationMixin


class Complaint(db.Model, ReferenceGenerationMixin):
    reference_prefix = "JC"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    urgency = db.Column(db.String(10))  # HIGH/MEDIUM/LOW
    status = db.Column(db.String(20), default="Pending")

    def __repr__(self):
        return f"<Complaint {self.reference}>"


class ACJASection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(10))
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pidgin_translation = db.Column(db.Text)

    def __repr__(self):
        return f"<ACJA Section {self.section}>"
