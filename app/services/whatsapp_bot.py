from app.models import Complaint

from app.services.acja_engine import ACJAEngine
from app.services.complaint_analyzer import ComplaintAnalyzer

engine = ACJAEngine()
analyzer = ComplaintAnalyzer()


def process_message(message, sender, language="en"):
    # Detect language if not specified
    if any(word in message.lower() for word in ["abeg", "na wa", "wetin"]):
        language = "pidgin"

    # Complaint handling
    if is_complaint(message):
        analysis = analyzer.analyze_complaint(message)
        response = generate_complaint_response(analysis, language)

    # Legal query
    else:
        legal_info = engine.get_legal_response(message, language)
        response = format_legal_response(legal_info, language)

    return response


def is_complaint(text):
    complaint_keywords = ["police", "arrest", "harass", "beat", "station"]
    return any(kw in text.lower() for kw in complaint_keywords)


def generate_complaint_response(analysis, lang):
    templates = {
        "en": {
            "high": "🚨 URGENT COMPLAINT RECEIVED about {locations}. We've alerted FCT Ministry of Justice. Ref: {ref}",
            "medium": "📝 Complaint logged about {locations}. Ref: {ref}",
        },
        "pidgin": {
            "high": "🚨 Wahala wey serious for {locations}. Ministry don hear. Ref: {ref}",
            "medium": "📝 We don write down your complain for {locations}. Ref: {ref}",
        },
    }
    urgency = "high" if analysis["urgency"] == "HIGH" else "medium"
    return templates[lang][urgency].format(
        locations=", ".join(analysis["locations"]), ref=generate_reference()
    )


def format_legal_response(legal_info, language):
    bullets = [f"• {legal_info['title']}", f"• {legal_info['explanation']}"]

    if language == "pidgin":
        bullets.append(f"• {legal_info['pidgin_translation']}")

    return (
        f"⚖️ ACJA Section {legal_info['section']}\n\n"
        + "\n".join(bullets)
        + "\n\nNeed more help?"
    )


def generate_reference():
    from datetime import datetime

    count = Complaint.query.count() + 1
    return f"JC{datetime.now().strftime('%Y%m%d')}{count:04d}"
