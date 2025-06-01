from app import db


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    urgency = db.Column(db.String(10))  # HIGH/MEDIUM/LOW
    status = db.Column(db.String(20), default="Pending")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reference = self._generate_reference()
    
    def _generate_reference(self):
        from datetime import datetime
        return f"JC-{datetime.now().strftime('%Y%m%d')}-{self.id:04d}"
    
    def __repr__(self):
        return f'<Complaint {self.reference}>'


class ACJASection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(10))
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    pidgin_translation = db.Column(db.Text)

    def __repr__(self):
        return f'<ACJA Section {self.section}>'