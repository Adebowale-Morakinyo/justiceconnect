from app.models import Complaint, db
from app.services.acja_engine import ACJAEngine
from app.services.complaint_analyzer import ComplaintAnalyzer
from app.services.session_manager import SessionManager
from app.services.twilio_helpers import create_response_with_buttons

engine = ACJAEngine()
analyzer = ComplaintAnalyzer()
session_mgr = SessionManager()


def process_message(message_data, sender):
    """
    Process incoming WhatsApp message
    :param message_data: Dict
    :param sender: WhatsApp phone number
    """
    try:
        # Handle button selections
        if message_data.get("Body", "").strip().isdigit():
            return handle_button_selection(message_data["Body"], sender)

        message_text = message_data.get("Body", "").strip().lower()
        language = detect_language(message_text)
        session = session_mgr.get_session(sender)

        # New session greeting
        if session["state"] == "NEW":
            return handle_new_session(sender, language)

        # Complaint filing flow
        if session["state"].startswith("COMPLAINT"):
            return handle_complaint_flow(message_text, sender, session, language)

        # Legal queries
        return handle_legal_query(message_text, language)
    except Exception as e:
        return f"Sorry, an error occurred: {str(e)}"


def detect_language(message_text):
    """Detect if message is in Pidgin English"""
    pidgin_keywords = ["abeg", "na wa", "wetin"]
    return "pidgin" if any(word in message_text for word in pidgin_keywords) else "en"


def handle_new_session(sender, language):
    session_mgr.update_session(sender, "IDLE")
    greeting = (
        "👋 Hi! I'm JusticeConnect Bot. I can help with Administration of Criminal Justice Act (ACJA) issues.\n\n"
        "Would you like to file a complaint?"
    )
    buttons = [
        {"action": "file_complaint", "label": "✅ Yes, file complaint"},
        {"action": "learn_acja", "label": "❓ Learn more about ACJA"},
    ]
    return create_response_with_buttons(greeting, buttons)


def handle_complaint_flow(message, sender, session, language):
    # Step 1: Start complaint
    if session["state"] == "COMPLAINT_START":
        session["data"]["description"] = message
        session_mgr.update_session(sender, "COMPLAINT_LOCATION", session["data"])
        return "📍 Where did this happen?"

    # Step 2: Get location
    elif session["state"] == "COMPLAINT_LOCATION":
        session["data"]["location"] = message
        session_mgr.update_session(sender, "COMPLAINT_TIME", session["data"])
        return "📅 When did this happen? (e.g. Today at 2pm)"

    # Step 3: Finalize
    elif session["state"] == "COMPLAINT_TIME":
        session["data"]["time"] = message
        complaint = save_complaint(session["data"], sender, language)
        session_mgr.update_session(sender, "IDLE")
        return format_complaint_confirmation(complaint, language)


def handle_legal_query(message, language):
    legal_info = engine.get_legal_response(message, language)
    if not legal_info:
        return "I couldn't find relevant ACJA information. Try asking about arrest procedures or bail."

    # Add follow-up options
    response = format_legal_response(legal_info, language)
    buttons = [
        {"action": "file_complaint", "label": "📋 File complaint"},
        {"action": "more_info", "label": "📚 More ACJA info"},
    ]
    return create_response_with_buttons(response, buttons)


def handle_button_selection(selection, sender):
    options = {
        1: {"action": "file_complaint", "label": "File complaint"},
        2: {"action": "learn_acja", "label": "Learn about ACJA"},
    }

    selected = int(selection)
    if selected in options:
        return handle_button_action(options[selected]["action"], sender, "en")
    return "Invalid selection. Please try again."


def handle_button_action(action, sender, language):
    if action == "file_complaint":
        session_mgr.update_session(sender, "COMPLAINT_START")
        return (
            "Please describe what happened in detail (you can use English or Pidgin):"
        )
    elif action == "learn_acja":
        return "The ACJA covers:\n• Arrest procedures\n• Bail rights\n• Detention limits\n\nAsk about any specific topic!"
    return "How can I help you today?"


def save_complaint(data, phone_number, language):
    analysis = analyzer.analyze_complaint(data["description"])
    complaint = Complaint(
        description=data["description"],
        location=data.get("location", "Unknown"),
        phone_number=phone_number,
        urgency=analysis["urgency"],
        status="Pending",
    )
    db.session.add(complaint)
    db.session.commit()
    return complaint


def format_complaint_confirmation(complaint, language):
    templates = {
        "en": {
            "high": "🚨 URGENT COMPLAINT RECEIVED about {location}. We've alerted FCT Ministry of Justice.\n\n🔎 Reference: {ref}",
            "medium": "📝 Complaint logged about {location}.\n\n🔎 Reference: {ref}",
        },
        "pidgin": {
            "high": "🚨 Wahala wey serious for {location}. Ministry don hear.\n\n🔎 Ref: {ref}",
            "medium": "📝 We don write down your complain for {location}.\n\n🔎 Ref: {ref}",
        },
    }
    urgency = "high" if complaint.urgency == "HIGH" else "medium"
    return templates[language][urgency].format(
        location=complaint.location, ref=complaint.reference
    )


def format_legal_response(legal_info, language):
    bullets = [
        f"⚖️ ACJA Section {legal_info['section']} - {legal_info['title']}",
        f"\n📜 Legal Text:\n{legal_info['content']}",
        f"\n💡 Explanation:\n{legal_info['explanation']}",
    ]

    if language == "pidgin":
        bullets.append(f"\n🌍 Pidgin:\n{legal_info['pidgin_translation']}")

    return "\n".join(bullets)


# def generate_reference():
#     count = Complaint.query.count() + 1
#     return f"JC{datetime.now().strftime('%Y%m%d')}{count:04d}"
