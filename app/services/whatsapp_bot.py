from app.services.acja_engine import ACJAEngine
from app.services.complaint_analyzer import ComplaintAnalyzer

engine = ACJAEngine()
analyzer = ComplaintAnalyzer()

def process_message(message, sender, language="en"):
    # Detect language if not specified
    pass

def is_complaint(text):
    pass

def generate_complaint_response(analysis, lang):
    pass
