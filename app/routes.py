from flask import Blueprint, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from app.services.whatsapp_bot import process_whatsapp_message

main_bp = Blueprint('main', __name__)

@main_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    sender = request.values.get('From', '')
    
    response = process_whatsapp_message(incoming_msg, sender)
    
    twiml = MessagingResponse()
    twiml.message(response)
    return str(twiml)