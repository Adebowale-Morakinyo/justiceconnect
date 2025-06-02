from flask import Blueprint, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from app.services.whatsapp_bot import process_message
from app.models import Complaint

main_bp = Blueprint("main", __name__)


@main_bp.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Twilio webhook verification
        return "Webhook setup complete", 200

    # Handle POST requests
    try:
        response = process_message(request.form, request.form.get("From"))
        twiml = MessagingResponse()
        twiml.message(response)
        return str(twiml), 200
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        twiml = MessagingResponse()
        twiml.message(error_msg)
        return str(twiml), 500


@main_bp.route("/admin")
def admin_dashboard():
    # Efficient database queries - let the DB do the counting
    total_complaints = Complaint.query.count()
    resolved_count = Complaint.query.filter_by(status="RESOLVED").count()
    pending_count = Complaint.query.filter_by(status="PENDING").count()
    investigating_count = Complaint.query.filter_by(status="INVESTIGATING").count()

    high_priority_count = Complaint.query.filter_by(urgency="HIGH").count()
    medium_priority_count = Complaint.query.filter_by(urgency="MEDIUM").count()
    low_priority_count = Complaint.query.filter_by(urgency="LOW").count()

    # Only load full complaint data for the table display
    complaints = Complaint.query.all()

    # Urgency data for chart
    urgency_counts = [high_priority_count, medium_priority_count, low_priority_count]
    urgency_labels = ["HIGH", "MEDIUM", "LOW"]

    return render_template(
        "admin.html",
        complaints=complaints,
        total_complaints=total_complaints,
        resolved_count=resolved_count,
        pending_count=pending_count,
        investigating_count=investigating_count,
        high_priority_count=high_priority_count,
        medium_priority_count=medium_priority_count,
        low_priority_count=low_priority_count,
        urgency_counts=urgency_counts,
        urgency_labels=urgency_labels,
    )
