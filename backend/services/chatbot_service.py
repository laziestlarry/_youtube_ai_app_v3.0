"""
Customer Service Chatbot Service
Handles automated customer interactions, FAQ responses, and sales assistance
"""

import os
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class IntentType(Enum):
    ORDER_STATUS = "order_status"
    DOWNLOAD_HELP = "download_help"
    REFUND_REQUEST = "refund_request"
    PRODUCT_QUESTION = "product_question"
    PRICING_INQUIRY = "pricing_inquiry"
    CUSTOM_REQUEST = "custom_request"
    GREETING = "greeting"
    THANK_YOU = "thank_you"
    COMPLAINT = "complaint"
    PURCHASE_INTENT = "purchase_intent"
    UNKNOWN = "unknown"


class EscalationLevel(Enum):
    BOT = "bot"
    AI_ASSISTANT = "ai_assistant"
    HUMAN = "human"


@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    intent: Optional[IntentType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatSession:
    session_id: str
    customer_email: Optional[str] = None
    messages: List[ChatMessage] = field(default_factory=list)
    escalation_level: EscalationLevel = EscalationLevel.BOT
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class CustomerServiceChatbot:
    """
    Multi-level customer service chatbot with:
    - Level 1: Rule-based FAQ responses
    - Level 2: AI-assisted complex queries
    - Level 3: Human escalation
    """

    def __init__(self):
        self.faq_responses = self._load_faq_responses()
        self.product_catalog = self._load_product_catalog()
        self.sessions: Dict[str, ChatSession] = {}

    def _load_faq_responses(self) -> Dict[str, str]:
        """Load FAQ responses for common queries."""
        return {
            "order_status": """
To check your order status:
1. Check your email for the order confirmation
2. Your download links are included in that email
3. If you can't find it, check your spam folder

Need more help? Reply with your order number and I'll look it up!
            """.strip(),

            "download_help": """
Having trouble downloading? Here's what to do:

1. **Check your email** - Download links are sent immediately after purchase
2. **Check spam/promotions** - Sometimes emails land there
3. **Use a desktop** - Some files are large and download better on computers
4. **Try a different browser** - Chrome or Firefox work best

Still stuck? Send me your order email and I'll resend your links!
            """.strip(),

            "refund_policy": """
Our refund policy is simple:

✅ **30-day money-back guarantee** on all digital products
✅ No questions asked if you're not satisfied
✅ Refunds processed within 3-5 business days

To request a refund, reply with your order number and reason.
            """.strip(),

            "file_formats": """
Our digital products come in multiple formats:

📄 **Documents**: PDF (universal), DOCX (editable)
🖼️ **Images**: PNG (transparent), JPG (web), PDF (print-ready)
📊 **Templates**: Notion, Google Sheets, Excel
🎨 **Art Files**: 300 DPI for print, multiple sizes included

All files are included in every purchase!
            """.strip(),

            "commercial_license": """
License information:

🏠 **Personal Use**: Included with all purchases - use for yourself, home, office
💼 **Commercial Use**: Available on select products - check product description
🚫 **Not Allowed**: Reselling the original files, redistribution

Need a commercial license? Ask about our business packages!
            """.strip(),

            "bulk_discount": """
We offer bulk discounts for larger orders:

📦 5+ items: 10% off
📦 10+ items: 15% off
📦 20+ items: 20% off
📦 Custom orders: Contact us for pricing

Use code BULK10, BULK15, or BULK20 at checkout, or message for custom quotes!
            """.strip(),

            "greeting": """
Hi there! 👋 Welcome to AutonomaX!

I'm here to help you with:
• Order questions
• Download assistance
• Product recommendations
• Pricing information

What can I help you with today?
            """.strip(),

            "thank_you": """
You're welcome! 😊

Is there anything else I can help you with?

If you love your purchase, we'd appreciate a review! It helps other customers find us.
            """.strip(),
        }

    def _load_product_catalog(self) -> Dict[str, Dict]:
        """Load product information for recommendations."""
        return {
            "ZEN-ART-BASE": {
                "title": "Zen Art Printables Bundle",
                "price": "$9-79",
                "description": "Minimalist wall art for calm, modern spaces",
                "best_for": "Home decor, office spaces, gifts",
                "includes": "50+ designs, multiple sizes, print-ready files",
            },
            "MASTERY-PACK-ULTIMATE": {
                "title": "AutonomaX Mastery Pack",
                "price": "$497",
                "description": "Complete bundle for automated income",
                "best_for": "Entrepreneurs, creators, side-hustlers",
                "includes": "All products, templates, SOPs, community access",
            },
            "CREATOR-KIT-01": {
                "title": "Creator Starter Kit",
                "price": "$49-199",
                "description": "Launch your digital product business",
                "best_for": "New creators, digital product sellers",
                "includes": "Templates, playbooks, launch checklist",
            },
            "YT-AUTO-01": {
                "title": "YouTube Automation Studio",
                "price": "$299-1499",
                "description": "End-to-end YouTube content automation",
                "best_for": "YouTubers, content creators, brands",
                "includes": "Strategy, scripts, thumbnails, workflows",
            },
        }

    def detect_intent(self, message: str) -> IntentType:
        """Detect the intent of a customer message."""
        message_lower = message.lower()

        # Order-related
        if any(w in message_lower for w in ["order", "tracking", "status", "where is"]):
            return IntentType.ORDER_STATUS

        # Download-related
        if any(w in message_lower for w in ["download", "access", "link", "file", "can't open"]):
            return IntentType.DOWNLOAD_HELP

        # Refund-related
        if any(w in message_lower for w in ["refund", "money back", "return", "cancel"]):
            return IntentType.REFUND_REQUEST

        # Product questions
        if any(w in message_lower for w in ["what is", "does it include", "format", "size", "license"]):
            return IntentType.PRODUCT_QUESTION

        # Pricing
        if any(w in message_lower for w in ["price", "cost", "discount", "coupon", "bulk"]):
            return IntentType.PRICING_INQUIRY

        # Purchase intent
        if any(w in message_lower for w in ["buy", "purchase", "want", "need", "interested"]):
            return IntentType.PURCHASE_INTENT

        # Greetings
        if any(w in message_lower for w in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return IntentType.GREETING

        # Thanks
        if any(w in message_lower for w in ["thank", "thanks", "appreciate"]):
            return IntentType.THANK_YOU

        # Complaints
        if any(w in message_lower for w in ["problem", "issue", "broken", "doesn't work", "frustrated"]):
            return IntentType.COMPLAINT

        return IntentType.UNKNOWN

    def get_response(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a customer message and return an appropriate response.
        """
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(session_id=session_id)

        session = self.sessions[session_id]

        # Detect intent
        intent = self.detect_intent(message)

        # Add user message to history
        session.messages.append(ChatMessage(
            role="user",
            content=message,
            intent=intent
        ))

        # Generate response based on intent
        response_text, should_escalate = self._generate_response(intent, message, session)

        # Check if escalation needed
        if should_escalate:
            session.escalation_level = EscalationLevel.HUMAN
            response_text += "\n\n🔔 I'm connecting you with a human agent who can help better. Please hold..."

        # Add assistant message to history
        session.messages.append(ChatMessage(
            role="assistant",
            content=response_text,
            intent=intent
        ))

        return {
            "response": response_text,
            "intent": intent.value,
            "escalation_level": session.escalation_level.value,
            "session_id": session_id,
            "suggested_actions": self._get_suggested_actions(intent),
        }

    def _generate_response(self, intent: IntentType, message: str, session: ChatSession) -> tuple[str, bool]:
        """Generate response based on intent. Returns (response, should_escalate)."""

        if intent == IntentType.GREETING:
            return self.faq_responses["greeting"], False

        if intent == IntentType.THANK_YOU:
            return self.faq_responses["thank_you"], False

        if intent == IntentType.ORDER_STATUS:
            return self.faq_responses["order_status"], False

        if intent == IntentType.DOWNLOAD_HELP:
            return self.faq_responses["download_help"], False

        if intent == IntentType.REFUND_REQUEST:
            return self.faq_responses["refund_policy"], False

        if intent == IntentType.PRICING_INQUIRY:
            return self.faq_responses["bulk_discount"], False

        if intent == IntentType.PRODUCT_QUESTION:
            if "format" in message.lower():
                return self.faq_responses["file_formats"], False
            if "license" in message.lower() or "commercial" in message.lower():
                return self.faq_responses["commercial_license"], False
            return self._recommend_products(message), False

        if intent == IntentType.PURCHASE_INTENT:
            return self._recommend_products(message), False

        if intent == IntentType.COMPLAINT:
            # Escalate complaints to human
            return "I'm sorry you're experiencing issues. Let me get someone who can help you right away.", True

        # Unknown intent - try to be helpful
        return """
I'm not sure I understood that correctly. Here's what I can help with:

• **Order questions** - Track your order, resend download links
• **Product info** - Formats, sizes, licenses, what's included
• **Pricing** - Discounts, bulk orders, custom quotes
• **Technical help** - Download issues, file problems

Which of these can I help you with?
        """.strip(), False

    def _recommend_products(self, message: str) -> str:
        """Recommend products based on customer query."""
        message_lower = message.lower()

        recommendations = []

        if any(w in message_lower for w in ["art", "print", "wall", "decor", "home"]):
            recommendations.append("ZEN-ART-BASE")

        if any(w in message_lower for w in ["youtube", "video", "content", "channel"]):
            recommendations.append("YT-AUTO-01")

        if any(w in message_lower for w in ["start", "launch", "begin", "creator", "digital"]):
            recommendations.append("CREATOR-KIT-01")

        if any(w in message_lower for w in ["everything", "complete", "all", "bundle", "best"]):
            recommendations.append("MASTERY-PACK-ULTIMATE")

        if not recommendations:
            recommendations = ["ZEN-ART-BASE", "CREATOR-KIT-01"]

        response = "Based on what you're looking for, I recommend:\n\n"

        for sku in recommendations[:3]:
            product = self.product_catalog.get(sku, {})
            response += f"**{product.get('title', sku)}** ({product.get('price', 'varies')})\n"
            response += f"→ {product.get('description', '')}\n"
            response += f"Best for: {product.get('best_for', '')}\n\n"

        response += "Would you like more details on any of these? Or shall I point you to the purchase page?"

        return response

    def _get_suggested_actions(self, intent: IntentType) -> List[Dict[str, str]]:
        """Get suggested quick actions based on intent."""
        actions = {
            IntentType.ORDER_STATUS: [
                {"label": "Resend download links", "action": "resend_links"},
                {"label": "Contact support", "action": "escalate"},
            ],
            IntentType.DOWNLOAD_HELP: [
                {"label": "Get download links", "action": "resend_links"},
                {"label": "File format help", "action": "format_help"},
            ],
            IntentType.PURCHASE_INTENT: [
                {"label": "View best sellers", "action": "view_bestsellers"},
                {"label": "See all products", "action": "view_catalog"},
                {"label": "Get discount code", "action": "get_discount"},
            ],
            IntentType.PRICING_INQUIRY: [
                {"label": "Get bulk quote", "action": "bulk_quote"},
                {"label": "View current offers", "action": "view_offers"},
            ],
        }
        return actions.get(intent, [])


# Singleton instance
_chatbot_instance: Optional[CustomerServiceChatbot] = None


def get_chatbot() -> CustomerServiceChatbot:
    """Get or create the chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = CustomerServiceChatbot()
    return _chatbot_instance
