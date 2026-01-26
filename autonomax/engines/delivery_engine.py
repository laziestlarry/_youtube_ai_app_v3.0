"""
Delivery Engine - Automated product delivery and customer fulfillment
Handles auto-delivery, email sequences, and customer satisfaction tracking
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_engine import BaseEngine, Job


class DeliveryStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    REFUNDED = "refunded"


class EmailSequenceType(Enum):
    WELCOME = "welcome"
    ONBOARDING = "onboarding"
    REVIEW_REQUEST = "review_request"
    UPSELL = "upsell"
    WIN_BACK = "win_back"


@dataclass
class Delivery:
    """Delivery record"""
    id: str
    order_id: str
    product_sku: str
    customer_email: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    download_links: List[str] = field(default_factory=list)
    access_credentials: Optional[Dict[str, str]] = None
    delivered_at: Optional[datetime] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmailTemplate:
    """Email template for sequences"""
    id: str
    sequence_type: EmailSequenceType
    subject: str
    body_template: str
    delay_hours: int = 0
    active: bool = True


class DeliveryEngine(BaseEngine):
    """
    Engine for automated product delivery and customer communication.
    
    Responsibilities:
    - Process instant digital deliveries
    - Manage email sequences (welcome, onboarding, review requests)
    - Track delivery success rates
    - Handle delivery failures and retries
    - Generate download links and access credentials
    """
    
    def __init__(self):
        super().__init__(
            name="delivery",
            objective="Automate product delivery and customer fulfillment with 100% success rate"
        )
        self.deliveries: List[Delivery] = []
        self.email_templates = self._load_email_templates()
        self.scheduled_emails: List[Dict] = []
    
    def _load_email_templates(self) -> Dict[str, EmailTemplate]:
        """Load email templates for various sequences"""
        templates = {
            "welcome": EmailTemplate(
                id="welcome",
                sequence_type=EmailSequenceType.WELCOME,
                subject="Welcome to AutonomaX! Your Download is Ready",
                body_template="""
Hi {customer_name},

Thank you for your purchase of {product_title}!

Your download links are ready:
{download_links}

Quick Start Guide:
1. Download all files to your computer
2. Unzip the package
3. Start with the README.txt file
4. Join our community: {community_link}

If you have any questions, just reply to this email.

To your success,
The AutonomaX Team
""",
                delay_hours=0,
            ),
            "onboarding_day1": EmailTemplate(
                id="onboarding_day1",
                sequence_type=EmailSequenceType.ONBOARDING,
                subject="Day 1: Getting Started with {product_title}",
                body_template="""
Hi {customer_name},

Hope you've had a chance to download your files!

Today's Quick Win:
{day1_action}

This should take about 15 minutes and will give you immediate results.

Need help? Reply to this email or check our FAQ: {faq_link}

Cheers,
AutonomaX Team
""",
                delay_hours=24,
            ),
            "onboarding_day3": EmailTemplate(
                id="onboarding_day3",
                sequence_type=EmailSequenceType.ONBOARDING,
                subject="Day 3: How's It Going?",
                body_template="""
Hi {customer_name},

Just checking in! By now you should have:
- Downloaded all files
- Completed the Day 1 action
- Explored the main resources

Common Questions at This Stage:
{common_questions}

Pro Tip: {pro_tip}

Any questions? Hit reply!

AutonomaX Team
""",
                delay_hours=72,
            ),
            "review_request": EmailTemplate(
                id="review_request",
                sequence_type=EmailSequenceType.REVIEW_REQUEST,
                subject="Quick Favor? Share Your Experience",
                body_template="""
Hi {customer_name},

You've had {product_title} for a week now. We'd love to hear how it's going!

Would you mind leaving a quick review?
{review_link}

It only takes 30 seconds and helps other creators find us.

As a thank you, here's an exclusive 20% off your next purchase: {discount_code}

Thanks for being part of our community!

AutonomaX Team
""",
                delay_hours=168,  # 7 days
            ),
            "upsell": EmailTemplate(
                id="upsell",
                sequence_type=EmailSequenceType.UPSELL,
                subject="Unlock More with {upsell_product}",
                body_template="""
Hi {customer_name},

Enjoying {product_title}? Here's what's next:

{upsell_product} includes:
{upsell_features}

Exclusive offer for existing customers:
{upsell_offer}

{upsell_link}

This offer expires in 48 hours.

AutonomaX Team
""",
                delay_hours=336,  # 14 days
            ),
        }
        return templates
    
    def get_inputs(self) -> List[str]:
        return [
            "order_data",
            "customer_data",
            "product_data",
            "delivery_config",
        ]
    
    def get_outputs(self) -> List[str]:
        return [
            "delivery_confirmation",
            "download_links",
            "email_sequence",
            "delivery_report",
        ]
    
    def process_delivery(
        self,
        order_id: str,
        product_sku: str,
        customer_email: str,
        customer_name: Optional[str] = None,
    ) -> Delivery:
        """Process a new delivery"""
        delivery = Delivery(
            id=f"DEL_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            order_id=order_id,
            product_sku=product_sku,
            customer_email=customer_email,
        )
        
        self.deliveries.append(delivery)
        
        # Enqueue delivery processing
        self.enqueue("execute_delivery", {
            "delivery_id": delivery.id,
            "product_sku": product_sku,
            "customer_email": customer_email,
            "customer_name": customer_name or customer_email.split("@")[0],
        }, priority=10)
        
        return delivery
    
    def process_job(self, job: Job) -> Dict[str, Any]:
        """Process delivery engine jobs"""
        
        if job.job_type == "execute_delivery":
            return self._execute_delivery(job.payload)
        
        elif job.job_type == "send_email":
            return self._send_email(job.payload)
        
        elif job.job_type == "schedule_sequence":
            return self._schedule_sequence(job.payload)
        
        elif job.job_type == "retry_delivery":
            return self._retry_delivery(job.payload)
        
        elif job.job_type == "generate_report":
            return self._generate_delivery_report(job.payload)
        
        else:
            raise ValueError(f"Unknown job type: {job.job_type}")
    
    def _execute_delivery(self, payload: Dict) -> Dict[str, Any]:
        """Execute product delivery"""
        delivery_id = payload["delivery_id"]
        product_sku = payload["product_sku"]
        customer_email = payload["customer_email"]
        customer_name = payload.get("customer_name", "Valued Customer")
        
        # Find the delivery record
        delivery = next((d for d in self.deliveries if d.id == delivery_id), None)
        if not delivery:
            raise ValueError(f"Delivery not found: {delivery_id}")
        
        delivery.status = DeliveryStatus.PROCESSING
        
        try:
            # Generate download links
            download_links = self._generate_download_links(product_sku)
            delivery.download_links = download_links
            
            # Generate access credentials if needed
            if self._product_requires_credentials(product_sku):
                delivery.access_credentials = self._generate_credentials(customer_email)
            
            # Send welcome email with download links
            self._send_welcome_email(
                customer_email=customer_email,
                customer_name=customer_name,
                product_sku=product_sku,
                download_links=download_links,
            )
            
            # Schedule onboarding sequence
            self.enqueue("schedule_sequence", {
                "delivery_id": delivery_id,
                "customer_email": customer_email,
                "customer_name": customer_name,
                "product_sku": product_sku,
                "sequence_type": "onboarding",
            }, priority=5)
            
            delivery.status = DeliveryStatus.DELIVERED
            delivery.delivered_at = datetime.utcnow()
            
            self.logger.info(f"Delivered {product_sku} to {customer_email}")
            
            return {
                "delivery_id": delivery_id,
                "status": "delivered",
                "download_links": download_links,
                "credentials": delivery.access_credentials,
            }
            
        except Exception as e:
            delivery.status = DeliveryStatus.FAILED
            delivery.retry_count += 1
            
            if delivery.retry_count < 3:
                self.enqueue("retry_delivery", {
                    "delivery_id": delivery_id,
                }, priority=8)
            
            raise e
    
    def _generate_download_links(self, product_sku: str) -> List[str]:
        """Generate secure, time-limited download links"""
        # In production, these would be signed URLs with expiration
        base_url = "https://downloads.autonomax.com"
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        
        links = [
            f"{base_url}/{product_sku}/main_{timestamp}.zip",
            f"{base_url}/{product_sku}/bonuses_{timestamp}.zip",
        ]
        
        # Add product-specific files
        if "MASTERY" in product_sku:
            links.append(f"{base_url}/{product_sku}/community_access_{timestamp}.json")
            links.append(f"{base_url}/{product_sku}/video_training_{timestamp}.zip")
        
        return links
    
    def _product_requires_credentials(self, product_sku: str) -> bool:
        """Check if product requires login credentials"""
        credential_products = ["MASTERY", "YT-AUTO", "B2B"]
        return any(c in product_sku for c in credential_products)
    
    def _generate_credentials(self, customer_email: str) -> Dict[str, str]:
        """Generate access credentials for gated content"""
        import hashlib
        import secrets
        
        # Generate secure password
        password = secrets.token_urlsafe(12)
        
        return {
            "email": customer_email,
            "password": password,
            "portal_url": "https://portal.autonomax.com/login",
        }
    
    def _send_welcome_email(
        self,
        customer_email: str,
        customer_name: str,
        product_sku: str,
        download_links: List[str],
    ) -> Dict[str, Any]:
        """Send welcome email with download links"""
        template = self.email_templates["welcome"]
        
        # Format download links as HTML
        links_html = "\n".join([f"- {link}" for link in download_links])
        
        # In production, this would call an email service
        email_data = {
            "to": customer_email,
            "subject": template.subject,
            "body": template.body_template.format(
                customer_name=customer_name,
                product_title=self._get_product_title(product_sku),
                download_links=links_html,
                community_link="https://discord.gg/autonomax",
            ),
            "sent_at": datetime.utcnow().isoformat(),
        }
        
        self.logger.info(f"Sent welcome email to {customer_email}")
        return email_data
    
    def _get_product_title(self, product_sku: str) -> str:
        """Get human-readable product title"""
        titles = {
            "ZEN-ART-BASE": "Zen Art Printables Bundle",
            "ZEN-ART-PREMIUM": "Zen Art Premium Collection",
            "CREATOR-KIT-01": "Creator Starter Kit",
            "CREATOR-KIT-PRO": "Creator Pro Kit",
            "MASTERY-PACK-ULTIMATE": "AutonomaX Mastery Pack",
            "YT-AUTO-DIY": "YouTube Automation DIY Kit",
            "NOTION-DASHBOARD": "Notion Passive Income Dashboard",
            "HYBRID-STACK": "Hybrid Passive Income Stack",
        }
        return titles.get(product_sku, product_sku)
    
    def _schedule_sequence(self, payload: Dict) -> Dict[str, Any]:
        """Schedule an email sequence"""
        delivery_id = payload["delivery_id"]
        customer_email = payload["customer_email"]
        customer_name = payload["customer_name"]
        product_sku = payload["product_sku"]
        sequence_type = payload["sequence_type"]
        
        scheduled = []
        
        if sequence_type == "onboarding":
            # Schedule onboarding emails
            for template_id in ["onboarding_day1", "onboarding_day3"]:
                template = self.email_templates.get(template_id)
                if template:
                    send_at = datetime.utcnow() + timedelta(hours=template.delay_hours)
                    scheduled_email = {
                        "template_id": template_id,
                        "customer_email": customer_email,
                        "customer_name": customer_name,
                        "product_sku": product_sku,
                        "send_at": send_at.isoformat(),
                    }
                    self.scheduled_emails.append(scheduled_email)
                    scheduled.append(scheduled_email)
            
            # Schedule review request
            review_template = self.email_templates["review_request"]
            send_at = datetime.utcnow() + timedelta(hours=review_template.delay_hours)
            review_email = {
                "template_id": "review_request",
                "customer_email": customer_email,
                "customer_name": customer_name,
                "product_sku": product_sku,
                "send_at": send_at.isoformat(),
            }
            self.scheduled_emails.append(review_email)
            scheduled.append(review_email)
        
        return {
            "delivery_id": delivery_id,
            "sequence_type": sequence_type,
            "emails_scheduled": len(scheduled),
            "schedule": scheduled,
        }
    
    def _send_email(self, payload: Dict) -> Dict[str, Any]:
        """Send a scheduled email"""
        template_id = payload["template_id"]
        customer_email = payload["customer_email"]
        
        template = self.email_templates.get(template_id)
        if not template:
            raise ValueError(f"Unknown template: {template_id}")
        
        # In production, call email service
        return {
            "template_id": template_id,
            "customer_email": customer_email,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "sent",
        }
    
    def _retry_delivery(self, payload: Dict) -> Dict[str, Any]:
        """Retry a failed delivery"""
        delivery_id = payload["delivery_id"]
        
        delivery = next((d for d in self.deliveries if d.id == delivery_id), None)
        if not delivery:
            raise ValueError(f"Delivery not found: {delivery_id}")
        
        # Re-enqueue for processing
        self.enqueue("execute_delivery", {
            "delivery_id": delivery_id,
            "product_sku": delivery.product_sku,
            "customer_email": delivery.customer_email,
        }, priority=9)
        
        return {
            "delivery_id": delivery_id,
            "retry_count": delivery.retry_count,
            "status": "retry_scheduled",
        }
    
    def _generate_delivery_report(self, payload: Dict) -> Dict[str, Any]:
        """Generate delivery performance report"""
        period_days = payload.get("period_days", 7)
        start = datetime.utcnow() - timedelta(days=period_days)
        
        period_deliveries = [d for d in self.deliveries if d.created_at >= start]
        
        delivered = [d for d in period_deliveries if d.status == DeliveryStatus.DELIVERED]
        failed = [d for d in period_deliveries if d.status == DeliveryStatus.FAILED]
        
        return {
            "period_days": period_days,
            "total_deliveries": len(period_deliveries),
            "delivered": len(delivered),
            "failed": len(failed),
            "success_rate": len(delivered) / len(period_deliveries) * 100 if period_deliveries else 100,
            "average_delivery_time_seconds": 5,  # Instant for digital
            "scheduled_emails": len(self.scheduled_emails),
        }
    
    def get_delivery_dashboard(self) -> Dict[str, Any]:
        """Get delivery dashboard data"""
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_deliveries = [d for d in self.deliveries if d.created_at >= today]
        
        return {
            "total_deliveries": len(self.deliveries),
            "today_deliveries": len(today_deliveries),
            "pending": len([d for d in self.deliveries if d.status == DeliveryStatus.PENDING]),
            "delivered": len([d for d in self.deliveries if d.status == DeliveryStatus.DELIVERED]),
            "failed": len([d for d in self.deliveries if d.status == DeliveryStatus.FAILED]),
            "scheduled_emails": len(self.scheduled_emails),
            "success_rate": f"{self.metrics.success_rate:.1f}%",
        }
