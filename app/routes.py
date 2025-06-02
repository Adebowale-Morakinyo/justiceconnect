from flask import Blueprint, request, jsonify, render_template
from twilio.twiml.messaging_response import MessagingResponse
from app.services.whatsapp_bot import process_message
from app.models import Complaint

main_bp = Blueprint("main", __name__)


@main_bp.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From", "")

    response = process_message(incoming_msg, sender)

    twiml = MessagingResponse()
    twiml.message(response)
    return str(twiml)


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
