import requests
import os
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PayoneerService:
    def __init__(self):
        self.api_key = os.getenv("PAYONEER_API_KEY")
        self.secret_key = os.getenv("PAYONEER_SECRET_KEY")
        self.base_url = os.getenv("PAYONEER_BASE_URL", "https://api.sandbox.payoneer.com")
        self.program_id = os.getenv("PAYONEER_PROGRAM_ID")
        
        if not all([self.api_key, self.secret_key, self.program_id]):
            logger.warning("Payoneer credentials not fully configured")
    
    def _generate_signature(self, data: str) -> str:
        """Generate HMAC signature for Payoneer API"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to Payoneer API"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if data:
                data_str = json.dumps(data)
                signature = self._generate_signature(data_str)
                headers["X-Signature"] = signature
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Payoneer API request failed: {e}")
            raise
    
    async def create_payee_account(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Payoneer payee account for revenue distribution"""
        try:
            endpoint = "/v2/programs/{program_id}/payees"
            
            payee_data = {
                "payee_id": user_data.get("user_id"),
                "email": user_data.get("email"),
                "first_name": user_data.get("first_name", "Creator"),
                "last_name": user_data.get("last_name", "User"),
                "country": user_data.get("country", "US"),
                "currency": user_data.get("currency", "USD"),
                "status": "ACTIVE"
            }
            
            result = self._make_request(endpoint, "POST", payee_data)
            
            logger.info(f"Payoneer payee account created: {result.get('payee_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create Payoneer payee account: {e}")
            raise
    
    async def process_revenue_payout(self, user_id: str, amount: float, currency: str = "USD") -> Dict[str, Any]:
        """Process revenue payout to user's Payoneer account"""
        try:
            endpoint = "/v2/programs/{program_id}/payments"
            
            payment_data = {
                "payee_id": user_id,
                "amount": amount,
                "currency": currency,
                "description": f"YouTube AI Creator Revenue - {datetime.now().strftime('%B %Y')}",
                "payment_date": datetime.now().isoformat(),
                "payment_type": "REVENUE_SHARE"
            }
            
            result = self._make_request(endpoint, "POST", payment_data)
            
            logger.info(f"Revenue payout processed: ${amount} to user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process revenue payout: {e}")
            raise
    
    async def get_payee_balance(self, user_id: str) -> Dict[str, Any]:
        """Get user's Payoneer account balance"""
        try:
            endpoint = f"/v2/programs/{self.program_id}/payees/{user_id}/balance"
            
            result = self._make_request(endpoint)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payee balance: {e}")
            raise
    
    async def get_payment_history(self, user_id: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get user's payment history"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            endpoint = f"/v2/programs/{self.program_id}/payees/{user_id}/payments"
            params = f"?start_date={start_date}&end_date={end_date}"
            
            result = self._make_request(endpoint + params)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payment history: {e}")
            raise
    
    async def update_payee_status(self, user_id: str, status: str) -> Dict[str, Any]:
        """Update payee account status (ACTIVE, SUSPENDED, etc.)"""
        try:
            endpoint = f"/v2/programs/{self.program_id}/payees/{user_id}"
            
            update_data = {
                "status": status
            }
            
            result = self._make_request(endpoint, "PUT", update_data)
            
            logger.info(f"Payee status updated: {user_id} -> {status}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update payee status: {e}")
            raise
    
    async def get_global_payout_options(self, country: str) -> Dict[str, Any]:
        """Get available payout options for a specific country"""
        try:
            endpoint = f"/v2/countries/{country}/payout-methods"
            
            result = self._make_request(endpoint)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get payout options: {e}")
            raise
    
    async def process_affiliate_commission(self, affiliate_id: str, commission_amount: float, 
                                         sale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process affiliate commission payout"""
        try:
            endpoint = "/v2/programs/{program_id}/payments"
            
            payment_data = {
                "payee_id": affiliate_id,
                "amount": commission_amount,
                "currency": "USD",
                "description": f"Affiliate Commission - {sale_data.get('product_name', 'Product')}",
                "payment_date": datetime.now().isoformat(),
                "payment_type": "AFFILIATE_COMMISSION",
                "metadata": {
                    "sale_id": sale_data.get("sale_id"),
                    "product_id": sale_data.get("product_id"),
                    "commission_rate": sale_data.get("commission_rate")
                }
            }
            
            result = self._make_request(endpoint, "POST", payment_data)
            
            logger.info(f"Affiliate commission processed: ${commission_amount} to {affiliate_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process affiliate commission: {e}")
            raise
    
    async def get_platform_revenue_summary(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get platform revenue summary for analytics"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).isoformat()
            if not end_date:
                end_date = datetime.now().isoformat()
            
            endpoint = f"/v2/programs/{self.program_id}/reports/revenue"
            params = f"?start_date={start_date}&end_date={end_date}"
            
            result = self._make_request(endpoint + params)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get revenue summary: {e}")
            raise 

    def get_receiving_account_details(self, currency: str = "USD") -> Dict[str, Any]:
        """
        Get the platform's receiving bank account details (Global Payment Service)
        for manual bank transfer instructions.
        """
        # In a production environment, these should ideally be loaded from a secure config or vault.
        # Hardcoded here as per immediate configuration request.
        
        accounts = {
            "USD": {
                "bank_name": "Citibank",
                "bank_address": "111 Wall Street New York, NY 10043 USA",
                "routing_aba": "031100209",
                "swift_code": "CITIUS33",
                "account_number": "70586870001480850",
                "account_type": "CHECKING",
                "beneficiary_name": "Kagan Dolek",
                "customer_id": "90477987"
            },
            "EUR": {
                "bank_name": "Banking Circle S.A.",
                "bank_address": "2, Boulevard de la Foire L-1528 LUXEMBOURG",
                "iban": "LU644080000052510508",
                "bic": "BCIRLULL",
                "beneficiary_name": "Kagan Dolek",
                "customer_id": "90477987"
            },
            "GBP": {
                "bank_name": "Barclays",
                "sort_code": "231486",
                "account_number": "15487955",
                "beneficiary_name": "Kagan Dolek",
                "customer_id": "90477987"
            }
        }
        
        return accounts.get(currency.upper())

    def get_admin_payoneer_cards(self) -> Dict[str, str]:
        """
        Returns admin Payoneer card identifiers.
        NOTE: Sensitive card details should be managed carefully. 
        Returning masked or reference IDs here.
        """
        return {
            "USD": "5226********4807",
            "EUR": "5170********7309",
            "GBP": "5170********2948"
        }