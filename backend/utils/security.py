import hashlib
import hmac
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from fastapi import Request, HTTPException
import re

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(32)
        self.rate_limit_cache: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: set = set()
        self.api_key_patterns = {
            "youtube": re.compile(r'^[A-Za-z0-9_-]{39}$'),
            "general": re.compile(r'^[A-Za-z0-9_-]{32,}$')
        }
    
    async def validate_request(self, request: Request, api_key: str) -> bool:
        """Validate incoming request for security."""
        try:
            client_ip = self._get_client_ip(request)
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                raise HTTPException(status_code=403, detail="IP address blocked")
            
            # Validate API key format
            if not self._validate_api_key_format(api_key):
                await self._log_security_event("invalid_api_key", client_ip, api_key[:10])
                raise HTTPException(status_code=400, detail="Invalid API key format")
            
            # Check for suspicious patterns
            await self._check_suspicious_activity(request, client_ip)
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            raise HTTPException(status_code=500, detail="Security validation error")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format."""
        try:
            # Check general format
            if not self.api_key_patterns["general"].match(api_key):
                return False
            
            # Additional entropy check
            if len(set(api_key)) < 10:  # Too few unique characters
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False
    
    async def _check_suspicious_activity(self, request: Request, client_ip: str):
        """Check for suspicious request patterns."""
        try:
            current_time = datetime.utcnow()
            
            # Initialize IP tracking if not exists
            if client_ip not in self.rate_limit_cache:
                self.rate_limit_cache[client_ip] = {
                    "requests": [],
                    "failed_attempts": 0,
                    "last_request": current_time
                }
            
            ip_data = self.rate_limit_cache[client_ip]
            
            # Clean old requests (older than 1 hour)
            hour_ago = current_time - timedelta(hours=1)
            ip_data["requests"] = [
                req_time for req_time in ip_data["requests"] 
                if req_time > hour_ago
            ]
            
            # Add current request
            ip_data["requests"].append(current_time)
            ip_data["last_request"] = current_time
            
            # Check for rate limiting (more than 100 requests per hour)
            if len(ip_data["requests"]) > 100:
                await self._log_security_event("rate_limit_exceeded", client_ip)
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Check for rapid requests (more than 10 in 1 minute)
            minute_ago = current_time - timedelta(minutes=1)
            recent_requests = [
                req_time for req_time in ip_data["requests"] 
                if req_time > minute_ago
            ]
            
            if len(recent_requests) > 10:
                await self._log_security_event("rapid_requests", client_ip)
                # Temporary block for 5 minutes
                await self._temporary_block_ip(client_ip, minutes=5)
                raise HTTPException(status_code=429, detail="Too many rapid requests")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Suspicious activity check failed: {e}")
    
    async def _log_security_event(self, event_type: str, client_ip: str, details: str = ""):
        """Log security events for monitoring."""
        try:
            security_event = {
                "event_type": event_type,
                "client_ip": client_ip,
                "details": details,
                "timestamp": datetime.utcnow().isoformat(),
                "severity": self._get_event_severity(event_type)
            }
            
            logger.warning(f"Security event: {security_event}")
            
            # Store in security log (implement as needed)
            await self._store_security_event(security_event)
            
        except Exception as e:
            logger.error(f"Security event logging failed: {e}")
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for security event."""
        severity_map = {
            "invalid_api_key": "medium",
            "rate_limit_exceeded": "high",
            "rapid_requests": "medium",
            "blocked_ip_attempt": "high",
            "suspicious_pattern": "medium"
        }
        return severity_map.get(event_type, "low")
    
    async def _store_security_event(self, event: Dict[str, Any]):
        """Store security event in database."""
        try:
            # This would store in a security events table
            pass
        except Exception as e:
            logger.error(f"Security event storage failed: {e}")
    
    async def _temporary_block_ip(self, ip: str, minutes: int = 5):
        """Temporarily block an IP address."""
        try:
            self.blocked_ips.add(ip)
            
            # Schedule unblock
            async def unblock_later():
                await asyncio.sleep(minutes * 60)
                self.blocked_ips.discard(ip)
                logger.info(f"IP {ip} unblocked after {minutes} minutes")
            
            import asyncio
            asyncio.create_task(unblock_later())
            
            logger.warning(f"IP {ip} temporarily blocked for {minutes} minutes")
            
        except Exception as e:
            logger.error(f"IP blocking failed: {e}")
    
    def generate_secure_token(self, payload: Dict[str, Any], expires_hours: int = 24) -> str:
        """Generate secure JWT token."""
        try:
            payload.update({
                "exp": datetime.utcnow() + timedelta(hours=expires_hours),
                "iat": datetime.utcnow()
            })
            
            return jwt.encode(payload, self.secret_key, algorithm="HS256")
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for storage."""
        try:
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Data hashing failed: {e}")
            raise
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Verify data against hash."""
        try:
            return hmac.compare_digest(
                hashlib.sha256(data.encode()).hexdigest(),
                hash_value
            )
        except Exception as e:
            logger.error(f"Hash verification failed: {e}")
            return False
    
    async def get_security_report(self) -> Dict[str, Any]:
        """Get security status and statistics."""
        try:
            current_time = datetime.utcnow()
            
            # Count recent security events
            recent_events = 0  # This would query from security log
            
            # Active blocks
            active_blocks = len(self.blocked_ips)
            
            # Rate limit statistics
            active_ips = len(self.rate_limit_cache)
            
            return {
                "status": "active",
                "blocked_ips": active_blocks,
                "monitored_ips": active_ips,
                "recent_security_events": recent_events,
                "last_updated": current_time.isoformat(),
                "security_level": self._calculate_security_level()
            }
            
        except Exception as e:
            logger.error(f"Security report generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _calculate_security_level(self) -> str:
        """Calculate current security threat level."""
        try:
            # Simple threat level calculation
            blocked_count = len(self.blocked_ips)
            
            if blocked_count > 10:
                return "high"
            elif blocked_count > 5:
                return "medium"
            else:
                return "low"
                
        except Exception:
            return "unknown"

def validate_password(password: str) -> tuple[bool, list[str]]:
    issues = []
    if len(password) < 12:
        issues.append("Password must be at least 12 characters")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one number")
    common_passwords = ['password', '123456', 'admin', 'root', 'user', 'qwerty']
    if password.lower() in common_passwords:
        issues.append("Password is too common")
    is_valid = len(issues) == 0
    return is_valid, issues

def validate_api_key(api_key: str) -> bool:
    if not api_key or len(api_key) < 32:
        return False
    if len(set(api_key)) < 10:
        return False
    return True