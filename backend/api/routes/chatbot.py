"""
Chatbot API Routes
Customer service chatbot endpoints for automated support
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from backend.services.chatbot_service import get_chatbot, IntentType


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    customer_email: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str
    session_id: str
    intent: str
    escalation_level: str
    suggested_actions: List[Dict[str, str]]
    timestamp: datetime


class FeedbackRequest(BaseModel):
    """Request model for chat feedback."""
    session_id: str
    message_index: int
    helpful: bool
    comment: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the customer service chatbot.

    The chatbot will:
    1. Detect the intent of your message
    2. Provide an appropriate response
    3. Suggest follow-up actions
    4. Escalate to human support if needed
    """
    chatbot = get_chatbot()

    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())

    # Get response from chatbot
    result = chatbot.get_response(
        session_id=session_id,
        message=request.message
    )

    return ChatResponse(
        response=result["response"],
        session_id=result["session_id"],
        intent=result["intent"],
        escalation_level=result["escalation_level"],
        suggested_actions=result["suggested_actions"],
        timestamp=datetime.utcnow()
    )


@router.get("/session/{session_id}")
async def get_session_history(session_id: str) -> Dict[str, Any]:
    """
    Get the conversation history for a chat session.
    """
    chatbot = get_chatbot()

    if session_id not in chatbot.sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chatbot.sessions[session_id]

    return {
        "session_id": session.session_id,
        "customer_email": session.customer_email,
        "escalation_level": session.escalation_level.value,
        "created_at": session.created_at.isoformat(),
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "intent": msg.intent.value if msg.intent else None,
            }
            for msg in session.messages
        ]
    }


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, str]:
    """
    Submit feedback for a chatbot response.
    Helps improve the chatbot over time.
    """
    # In production, this would store feedback in database
    # For now, just acknowledge receipt
    return {
        "status": "received",
        "message": "Thank you for your feedback! It helps us improve."
    }


@router.get("/faq")
async def get_faq_topics() -> Dict[str, Any]:
    """
    Get available FAQ topics that the chatbot can help with.
    """
    return {
        "topics": [
            {
                "id": "order_status",
                "title": "Order Status",
                "description": "Track your order or find download links",
                "sample_questions": [
                    "Where is my order?",
                    "I didn't receive my download",
                    "How do I access my files?"
                ]
            },
            {
                "id": "download_help",
                "title": "Download Help",
                "description": "Get help with downloading your files",
                "sample_questions": [
                    "How do I download my files?",
                    "The download link isn't working",
                    "Can I download on mobile?"
                ]
            },
            {
                "id": "refund_policy",
                "title": "Refunds & Returns",
                "description": "Learn about our refund policy",
                "sample_questions": [
                    "What's your refund policy?",
                    "How do I request a refund?",
                    "Can I exchange my purchase?"
                ]
            },
            {
                "id": "product_info",
                "title": "Product Information",
                "description": "Learn about product features and formats",
                "sample_questions": [
                    "What file formats are included?",
                    "Is commercial use allowed?",
                    "What sizes are available?"
                ]
            },
            {
                "id": "pricing",
                "title": "Pricing & Discounts",
                "description": "Information about pricing and bulk discounts",
                "sample_questions": [
                    "Do you offer bulk discounts?",
                    "Is there a coupon code?",
                    "Can I get a custom quote?"
                ]
            },
        ]
    }


@router.get("/quick-replies")
async def get_quick_replies() -> Dict[str, Any]:
    """
    Get quick reply options for the chat interface.
    """
    return {
        "quick_replies": [
            {"label": "Track my order", "message": "Where is my order?"},
            {"label": "Download help", "message": "I need help downloading my files"},
            {"label": "Refund request", "message": "I'd like to request a refund"},
            {"label": "Product question", "message": "What's included in the product?"},
            {"label": "Bulk discount", "message": "Do you offer bulk discounts?"},
            {"label": "Talk to human", "message": "I'd like to speak with a human"},
        ]
    }
