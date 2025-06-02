from twilio.twiml.messaging_response import MessagingResponse


def create_response_with_buttons(text, buttons):
    """
    Simulates quick replies by sending numbered options
    Format:
    [1] Option 1
    [2] Option 2
    """
    options = "\n".join([f"[{i+1}] {btn['label']}" for i, btn in enumerate(buttons)])
    return f"{text}\n\n{options}"


def parse_button_selection(message):
    """Extract selected option from user's response"""
    if message.isdigit():
        return int(message)
    return None
