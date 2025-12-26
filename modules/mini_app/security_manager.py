"""
Security Manager for YouTube Income Commander
Handles security monitoring, access control, and threat detection
"""
import os
import json
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import ipaddress
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityManager:
    def __init__(self):
        self.config = self.load_config()
        self.db_path = "security_logs.db"
        self.init_database()
        self.failed_attempts = {}
        self.blocked_ips = set()
        self.session_tokens = {}
        # Load currently blocked IPs from DB on init
        self._load_blocked_ips_from_db()
        
    def load_config(self):
        """Load security configuration"""
        default_config = {
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "session_timeout_hours": 24,
            "password_min_length": 8,
            "require_special_chars": True,
            "enable_ip_blocking": True,
            "allowed_ip_ranges": [],
            "enable_encryption": True,
            "log_all_access": True,
            "enable_2fa": False
        }
        
        config_file = "config/security_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Ensure all default keys are present
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
        except Exception:
            pass # Fallback to default if file is corrupted or missing
        
        # If file doesn't exist or failed to load, create it with defaults
        Path("config").mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    def init_database(self):
        """Initialize security database"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Security events table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT,
                    user_agent TEXT,
                    description TEXT NOT NULL,
                    metadata TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Access logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    endpoint TEXT,
                    method TEXT,
                    status_code INTEGER,
                    user_agent TEXT,
                    response_time REAL
                )
            ''')
            
            # User sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Blocked IPs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS blocked_ips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_address TEXT UNIQUE NOT NULL,
                    blocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expires_at DATETIME,
                    reason TEXT,
                    auto_blocked BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize security database: {e}")

    def _load_blocked_ips_from_db(self):
        """Load active blocked IPs from database into memory."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Remove expired blocks
            conn.execute("DELETE FROM blocked_ips WHERE expires_at < ?", (datetime.now().isoformat(),))
            conn.commit()
            cursor = conn.execute("SELECT ip_address FROM blocked_ips")
            self.blocked_ips = {row[0] for row in cursor.fetchall()}
            conn.close()
        except Exception as e:
            print(f"Warning: Could not load blocked IPs from DB: {e}")
            self.blocked_ips = set()

    def generate_encryption_key(self, password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """Generate encryption key from password. Returns key and salt."""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000, # NIST recommends at least 10,000; 100,000 is a good modern value.
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_data(self, data: str, password: str) -> dict:
        """Encrypt sensitive data"""
        if not self.config.get('enable_encryption', False):
            return {'encrypted_data': data, 'salt': '', 'timestamp': datetime.now().isoformat(), 'unencrypted': True}
        try:
            key, salt = self.generate_encryption_key(password)
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data.encode())
            
            return {
                'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode(),
                'salt': base64.urlsafe_b64encode(salt).decode(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.log_security_event("encryption_error", "medium", 
                                   f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_package: dict, password: str) -> str:
        """Decrypt sensitive data"""
        if encrypted_package.get('unencrypted', False):
            return encrypted_package['encrypted_data']
        try:
            salt = base64.urlsafe_b64decode(encrypted_package['salt'])
            encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_package['encrypted_data'])
            
            key, _ = self.generate_encryption_key(password, salt)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data_bytes)
            
            return decrypted_data.decode()
        except Exception as e:
            self.log_security_event("decryption_error", "medium", 
                                   f"Decryption failed: {str(e)}")
            raise
    
    def validate_password(self, password: str) -> tuple[bool, list[str]]:
        """Validate password strength. Returns (is_valid, issues_list)."""
        issues = []
        
        if len(password) < self.config['password_min_length']:
            issues.append(f"Password must be at least {self.config['password_min_length']} characters")
        
        if self.config['require_special_chars']:
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                issues.append("Password must contain at least one special character")
            
            if not re.search(r'[A-Z]', password):
                issues.append("Password must contain at least one uppercase letter")
            
            if not re.search(r'[a-z]', password):
                issues.append("Password must contain at least one lowercase letter")
            
            if not re.search(r'\d', password):
                issues.append("Password must contain at least one number")
        
        # Check for common passwords (simple check, can be expanded)
        common_passwords = ['password', '123456', 'admin', 'root', 'user', 'qwerty']
        if password.lower() in common_passwords:
            issues.append("Password is too common")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def hash_password(self, password: str) -> str:
        """Hash password securely using PBKDF2"""
        salt = secrets.token_hex(16)
        # iterations should match generate_encryption_key if used for similar purposes,
        # but for password hashing, higher is often better.
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          260000) # OWASP recommendation for PBKDF2-SHA256
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, password_hash_hex = stored_hash.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', 
                                              password.encode('utf-8'), 
                                              salt.encode('utf-8'), 
                                              260000) # Must match iterations used in hash_password
            return secrets.compare_digest(computed_hash.hex(), password_hash_hex)
        except Exception:
            return False # Handles malformed stored_hash or other errors
    
    def check_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        if not self.config['enable_ip_blocking']:
            return True
        
        # Check if IP is currently blocked (in-memory check first for speed)
        if ip_address in self.blocked_ips:
            # Verify if the block might have expired in DB but not yet reloaded
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT expires_at FROM blocked_ips WHERE ip_address = ?", (ip_address,))
                row = cursor.fetchone()
                conn.close()
                if row and datetime.now() > datetime.fromisoformat(row[0]):
                    self.unblock_ip(ip_address) # Expired, unblock
                else:
                    return False # Still actively blocked
            except Exception as e:
                print(f"Error checking IP block expiration: {e}")
                return False # Safer to assume still blocked if DB check fails

        # Check allowed IP ranges
        if self.config['allowed_ip_ranges']:
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                for ip_range_str in self.config['allowed_ip_ranges']:
                    if ip_obj in ipaddress.ip_network(ip_range_str, strict=False):
                        return True
                # If ranges are defined and IP is not in any, it's disallowed.
                self.log_security_event("ip_not_in_allow_list", "medium",
                                        f"IP {ip_address} not in allowed ranges.",
                                        source_ip=ip_address)
                return False
            except ValueError: # Invalid IP address string
                self.log_security_event("invalid_ip_format", "low",
                                        f"Invalid IP address format for checking: {ip_address}",
                                        source_ip=ip_address)
                return False # Treat invalid IP as not allowed
        
        return True # If no ranges defined, all non-blocked IPs are allowed.
    
    def record_failed_attempt(self, ip_address: str, reason: str = "Invalid credentials"):
        """Record failed login attempt"""
        current_time = datetime.now()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = []
        
        # Clean old attempts (older than lockout_duration_minutes)
        lockout_period = timedelta(minutes=self.config['lockout_duration_minutes'])
        self.failed_attempts[ip_address] = [
            attempt_time for attempt_time in self.failed_attempts[ip_address] 
            if current_time - attempt_time < lockout_period
        ]
        
        # Add new attempt
        self.failed_attempts[ip_address].append(current_time)
        
        # Log security event for this specific failed attempt
        self.log_security_event("failed_login_attempt", "medium", 
                               f"Failed login attempt from {ip_address}: {reason}",
                               source_ip=ip_address)

        # Check if should block IP
        if len(self.failed_attempts[ip_address]) >= self.config['max_login_attempts']:
            if self.config['enable_ip_blocking']:
                self.block_ip(ip_address, f"Too many failed attempts: {reason}", auto_blocked=True)
            else:
                 self.log_security_event("ip_block_disabled", "warning",
                                   f"IP blocking disabled. IP {ip_address} would have been blocked due to excessive failed attempts.",
                                   source_ip=ip_address)
            # Clear attempts for this IP once it's decided to be blocked or noted.
            self.failed_attempts[ip_address] = []
    
    def block_ip(self, ip_address: str, reason: str, duration_hours: int = None, auto_blocked: bool = False):
        """Block IP address"""
        if not self.config['enable_ip_blocking']:
            self.log_security_event("ip_block_attempt_disabled", "info",
                                   f"Attempt to block IP {ip_address} but IP blocking is disabled.",
                                   source_ip=ip_address)
            return

        if duration_hours is None:
            duration_hours = self.config['lockout_duration_minutes'] / 60.0
        
        expires_at = datetime.now() + timedelta(hours=duration_hours)
        
        self.blocked_ips.add(ip_address) # Update in-memory set
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT OR REPLACE INTO blocked_ips 
                (ip_address, blocked_at, expires_at, reason, auto_blocked)
                VALUES (?, ?, ?, ?, ?)
            ''', (ip_address, datetime.now().isoformat(), expires_at.isoformat(), reason, auto_blocked))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error blocking IP in DB: {e}")
            self.log_security_event("db_error", "high", f"Failed to write IP block for {ip_address} to DB: {e}", source_ip=ip_address)
        
        severity = "high" if auto_blocked else "medium"
        self.log_security_event("ip_blocked", severity, 
                               f"IP {ip_address} blocked for {duration_hours} hours. Reason: {reason}",
                               source_ip=ip_address, metadata={"duration_hours": duration_hours, "expires_at": expires_at.isoformat()})
    
    def unblock_ip(self, ip_address: str):
        """Unblock IP address"""
        self.blocked_ips.discard(ip_address) # Update in-memory set
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('DELETE FROM blocked_ips WHERE ip_address = ?', (ip_address,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error unblocking IP in DB: {e}")
            self.log_security_event("db_error", "medium", f"Failed to remove IP block for {ip_address} from DB: {e}", source_ip=ip_address)

        self.log_security_event("ip_unblocked", "low", 
                               f"IP {ip_address} unblocked manually or due to expiration.",
                               source_ip=ip_address)
    
    def create_session(self, ip_address: str, user_agent: str = None) -> str:
        """Create user session"""
        session_token = secrets.token_urlsafe(32)
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.config['session_timeout_hours'])
        
        self.session_tokens[session_token] = {
            'created_at': created_at,
            'expires_at': expires_at,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO user_sessions 
                (session_token, created_at, expires_at, ip_address, user_agent, active)
                VALUES (?, ?, ?, ?, ?, TRUE)
            ''', (session_token, created_at.isoformat(), expires_at.isoformat(), ip_address, user_agent))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error creating session in DB: {e}")
            self.log_security_event("db_error", "medium", f"Failed to write session for {ip_address} to DB: {e}", source_ip=ip_address)

        self.log_security_event("session_created", "low", 
                               f"New session created for {ip_address}. Token: ...{session_token[-6:]}",
                               source_ip=ip_address, user_agent=user_agent, metadata={"expires_at": expires_at.isoformat()})
        
        return session_token
    
    def validate_session(self, session_token: str, ip_address: str = None, user_agent: str = None) -> bool:
        """Validate user session"""
        if session_token not in self.session_tokens:
            # Could be an old session or invalid token, check DB just in case
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.execute("SELECT expires_at, ip_address, user_agent, active FROM user_sessions WHERE session_token = ?", (session_token,))
                row = cursor.fetchone()
                conn.close()
                if not row or not row[3]: # Not found or not active
                    self.log_security_event("invalid_session_token", "medium", f"Invalid or inactive session token presented: ...{session_token[-6:]}", source_ip=ip_address, user_agent=user_agent)
                    return False
                
                db_expires_at, db_ip, db_user_agent = datetime.fromisoformat(row[0]), row[1], row[2]
                if datetime.now() > db_expires_at:
                    self.invalidate_session(session_token) # Mark as inactive in DB
                    self.log_security_event("expired_session_validated", "medium", f"Expired session token validated: ...{session_token[-6:]}", source_ip=ip_address, user_agent=user_agent)
                    return False
                # If valid in DB, load into memory for faster subsequent checks
                self.session_tokens[session_token] = {
                    'created_at': datetime.now(), # Placeholder, actual created_at is in DB
                    'expires_at': db_expires_at,
                    'ip_address': db_ip,
                    'user_agent': db_user_agent
                }
            except Exception as e:
                print(f"Error validating session from DB: {e}")
                self.log_security_event("db_error", "medium", f"DB error validating session token ...{session_token[-6:]}: {e}", source_ip=ip_address)
                return False # Fail safe

        session = self.session_tokens.get(session_token)
        if not session: # Should not happen if logic above is correct
             self.log_security_event("session_not_found_internal", "high", f"Session token ...{session_token[-6:]} not found internally after DB check.", source_ip=ip_address)
             return False

        # Check expiration
        if datetime.now() > session['expires_at']:
            self.invalidate_session(session_token)
            self.log_security_event("session_expired", "info", f"Session token ...{session_token[-6:]} expired.", source_ip=ip_address, user_agent=user_agent)
            return False
        
        # Check IP consistency (optional, can be strict)
        if ip_address and session['ip_address'] != ip_address:
            self.log_security_event("session_ip_mismatch", "medium", 
                                   f"Session IP mismatch for token ...{session_token[-6:]}. Expected: {session['ip_address']}, Got: {ip_address}",
                                   source_ip=ip_address, user_agent=user_agent)
            # Depending on policy, might invalidate session here
            # self.invalidate_session(session_token)
            # return False 
        
        # Check User-Agent consistency (optional, can be strict)
        if user_agent and session['user_agent'] != user_agent:
            self.log_security_event("session_ua_mismatch", "medium",
                                   f"Session User-Agent mismatch for token ...{session_token[-6:]}. Expected: {session['user_agent']}, Got: {user_agent}",
                                   source_ip=ip_address, user_agent=user_agent)
            # Depending on policy, might invalidate session here

        return True
    
    def invalidate_session(self, session_token: str):
        """Invalidate user session in memory and DB"""
        session_info = self.session_tokens.pop(session_token, None)
        ip_address = session_info['ip_address'] if session_info else None
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('UPDATE user_sessions SET active = FALSE WHERE session_token = ?', 
                        (session_token,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error invalidating session in DB: {e}")
            self.log_security_event("db_error", "medium", f"Failed to invalidate session token ...{session_token[-6:]} in DB: {e}", source_ip=ip_address)

        if session_info: # Only log if it was an active session in memory
            self.log_security_event("session_invalidated", "info", 
                                   f"Session token ...{session_token[-6:]} invalidated.",
                                   source_ip=ip_address, user_agent=session_info.get('user_agent'))
    
    def log_security_event(self, event_type: str, severity: str, description: str, 
                          source_ip: str = None, user_agent: str = None, metadata: dict = None):
        """Log security event to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO security_events 
                (timestamp, event_type, severity, source_ip, user_agent, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), event_type, severity, source_ip, user_agent, description, 
                  json.dumps(metadata) if metadata else None))
            conn.commit()
            conn.close()
            
            # Print high severity events to console for immediate attention
            if severity.lower() in ['high', 'critical']:
                print(f"🚨 SECURITY ALERT [{severity.upper()} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: {description} (IP: {source_ip or 'N/A'})")
                
        except Exception as e:
            # Fallback to print if DB logging fails
            print(f"CRITICAL: Error logging security event to DB: {e}")
            print(f"Original Event: Type={event_type}, Severity={severity}, Desc={description}, IP={source_ip}")
    
    def log_access(self, ip_address: str, endpoint: str, method: str, 
                   status_code: int, user_agent: str = None, response_time: float = None):
        """Log access attempt to database"""
        if not self.config.get('log_all_access', False):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO access_logs 
                (timestamp, ip_address, endpoint, method, status_code, user_agent, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now().isoformat(), ip_address, endpoint, method, status_code, user_agent, response_time))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging access to DB: {e}")
            # Fallback logging for access if DB fails
            print(f"Access Log (DB Fail): IP={ip_address}, Endpoint={endpoint}, Method={method}, Status={status_code}, Time={response_time}ms")

    def detect_threats(self, hours: int = 1) -> list:
        """Detect potential security threats from logs"""
        threats = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Detect brute force attacks (multiple failed logins from same IP)
            cursor = conn.execute('''
                SELECT source_ip, COUNT(*) as attempts
                FROM security_events 
                WHERE event_type = 'failed_login_attempt' 
                AND timestamp > ? 
                GROUP BY source_ip 
                HAVING attempts >= ? 
            ''', (cutoff_time.isoformat(), self.config['max_login_attempts']))
            
            for row in cursor.fetchall():
                threats.append({
                    'type': 'brute_force_attempt',
                    'severity': 'high',
                    'source_ip': row[0],
                    'description': f"Potential brute force attack from {row[0]} ({row[1]} failed login attempts in last {hours}h)."
                })
            
            # Detect unusual high volume of requests from a single IP
            # Threshold for "high volume" should be configurable or dynamically adjusted.
            # For now, a static example:
            high_volume_threshold = 200 # requests per hour from one IP
            cursor = conn.execute('''
                SELECT ip_address, COUNT(*) as requests
                FROM access_logs 
                WHERE timestamp > ? 
                GROUP BY ip_address 
                HAVING requests > ?
            ''', (cutoff_time.isoformat(), high_volume_threshold * hours)) # Adjust threshold by hours
            
            for row in cursor.fetchall():
                threats.append({
                    'type': 'high_request_volume',
                    'severity': 'medium',
                    'source_ip': row[0],
                    'description': f"Unusually high volume of requests ({row[1]}) from {row[0]} in last {hours}h."
                })

            # Detect high rate of server errors (status_code >= 500)
            error_rate_threshold = 20 # errors in the period
            cursor = conn.execute('''
                SELECT endpoint, COUNT(*) as errors
                FROM access_logs
                WHERE status_code >= 500
                AND timestamp > ?
                GROUP BY endpoint
                HAVING errors > ?
            ''', (cutoff_time.isoformat(), error_rate_threshold))

            for row in cursor.fetchall():
                threats.append({
                    'type': 'high_server_error_rate',
                    'severity': 'medium',
                    'endpoint': row[0] if row[0] else "Generic",
                    'description': f"High server error rate on endpoint '{row[0] if row[0] else 'various'}' ({row[1]} errors in last {hours}h)."
                })

            # Detect multiple failed encryption/decryption attempts (could indicate tampering or attack)
            crypto_failure_threshold = 5
            cursor = conn.execute('''
                SELECT event_type, description, COUNT(*) as attempts
                FROM security_events
                WHERE (event_type = 'encryption_error' OR event_type = 'decryption_error')
                AND timestamp > ?
                GROUP BY event_type, description 
                HAVING attempts > ?
            ''', (cutoff_time.isoformat(), crypto_failure_threshold))

            for row in cursor.fetchall():
                threats.append({
                    'type': 'crypto_operation_failures',
                    'severity': 'high',
                    'description': f"Multiple '{row[0]}' failures ({row[2]} attempts) for '{row[1]}' in last {hours}h. Potential data tampering attempt."
                })
            
            conn.close()
        except Exception as e:
            err_msg = f"Error during threat detection: {str(e)}"
            self.log_security_event("threat_detection_error", "high", err_msg)
            threats.append({'type': 'internal_error', 'severity': 'high', 'description': err_msg})


        # Log detected threats as security events themselves
        if threats:
            for threat in threats:
                # Avoid re-logging the internal_error threat from above
                if threat['type'] != 'internal_error':
                    self.log_security_event(
                        event_type=f"detected_threat_{threat['type']}",
                        severity=threat['severity'],
                        description=threat['description'],
                        source_ip=threat.get('source_ip'),
                        metadata=threat
                    )
        return threats

    def get_security_events(self, limit: int = 100, severity: str = None, event_type: str = None) -> list:
        """Get recent security events from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # To access columns by name
            
            query = "SELECT * FROM security_events"
            conditions = []
            params = []

            if severity:
                conditions.append("severity = ?")
                params.append(severity)
            if event_type:
                conditions.append("event_type = ?")
                params.append(event_type)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, tuple(params))
            events = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return events
        except Exception as e:
            print(f"Error getting security events: {e}")
            self.log_security_event("db_read_error", "medium", f"Failed to read security events: {e}")
            return []

    def get_access_logs(self, limit: int = 100, ip_address: str = None, status_code: int = None) -> list:
        """Get recent access logs from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM access_logs"
            conditions = []
            params = []

            if ip_address:
                conditions.append("ip_address = ?")
                params.append(ip_address)
            if status_code:
                conditions.append("status_code = ?")
                params.append(status_code)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, tuple(params))
            logs = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return logs
        except Exception as e:
            print(f"Error getting access logs: {e}")
            self.log_security_event("db_read_error", "medium", f"Failed to read access logs: {e}")
            return []

    def get_blocked_ips(self) -> list:
        """Get list of currently blocked IPs from the database, refreshing in-memory list."""
        self._load_blocked_ips_from_db() # Ensure in-memory is fresh and expired are cleared
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM blocked_ips ORDER BY blocked_at DESC")
            blocked_list = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return blocked_list
        except Exception as e:
            print(f"Error getting blocked IPs from DB: {e}")
            self.log_security_event("db_read_error", "medium", f"Failed to read blocked IPs: {e}")
            return []
            
    def get_active_sessions(self, limit: int = 100) -> list:
        """Get list of active user sessions from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Clean expired sessions in DB
            conn.execute("UPDATE user_sessions SET active = FALSE WHERE expires_at < ? AND active = TRUE", 
                         (datetime.now().isoformat(),))
            conn.commit()

            cursor = conn.execute("SELECT * FROM user_sessions WHERE active = TRUE ORDER BY created_at DESC LIMIT ?", (limit,))
            sessions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Optionally, refresh in-memory self.session_tokens here if it's meant to be a cache
            # For simplicity, this example assumes self.session_tokens is primarily for new/ongoing sessions
            
            return sessions
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            self.log_security_event("db_read_error", "medium", f"Failed to read active sessions: {e}")
            return []

    def generate_security_report(self, hours: int = 24) -> dict:
        """Generate a comprehensive security report."""
        report_time = datetime.now()
        report = {
            "report_generated_at": report_time.isoformat(),
            "reporting_period_hours": hours,
            "summary_stats": {},
            "detected_threats_in_period": [],
            "recent_critical_high_events": [],
            "current_blocked_ips_count": 0,
            "current_active_sessions_count": 0,
        }
        
        cutoff_iso = (report_time - timedelta(hours=hours)).isoformat()

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Summary Statistics
            event_counts_by_severity = conn.execute('''
                SELECT severity, COUNT(*) as count
                FROM security_events 
                WHERE timestamp > ? 
                GROUP BY severity
            ''', (cutoff_iso,)).fetchall()
            report["summary_stats"]["event_counts_by_severity"] = {r['severity']: r['count'] for r in event_counts_by_severity}

            failed_logins = conn.execute('''
                SELECT COUNT(*) as count
                FROM security_events 
                WHERE event_type = 'failed_login_attempt' AND timestamp > ?
            ''', (cutoff_iso,)).fetchone()
            report["summary_stats"]["failed_login_attempts_in_period"] = failed_logins['count'] if failed_logins else 0
            
            newly_blocked_ips = conn.execute('''
                SELECT COUNT(*) as count
                FROM blocked_ips
                WHERE blocked_at > ?
            ''', (cutoff_iso,)).fetchone()
            report["summary_stats"]["ips_blocked_in_period"] = newly_blocked_ips['count'] if newly_blocked_ips else 0

            # Detected Threats
            report["detected_threats_in_period"] = self.detect_threats(hours=hours)
            
            # Recent Critical/High Events
            critical_events_cursor = conn.execute('''
                SELECT * FROM security_events 
                WHERE severity IN ('critical', 'high') AND timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (cutoff_iso,))
            report["recent_critical_high_events"] = [dict(row) for row in critical_events_cursor.fetchall()]

            conn.close()

            # Current counts (uses methods that might interact with DB again, but ensures freshness)
            report["current_blocked_ips_count"] = len(self.get_blocked_ips())
            report["current_active_sessions_count"] = len(self.get_active_sessions(limit=10000)) # Get all for count

        except Exception as e:
            error_message = f"Error generating security report: {str(e)}"
            report["error"] = error_message
            self.log_security_event("report_generation_error", "high", error_message)
            
        return report

def main():
    """Main Security Manager interface for CLI operations."""
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Income Commander Security Manager CLI")
    
    subparsers = parser.add_subparsers(dest="action", title="actions", required=True)

    # log_event
    parser_log = subparsers.add_parser("log_event", help="Log a custom security event.")
    parser_log.add_argument("--type", required=True, help="Event type (e.g., 'manual_alert').")
    parser_log.add_argument("--severity", default="info", choices=['low', 'info', 'medium', 'high', 'critical'], help="Severity of the event.")
    parser_log.add_argument("--desc", required=True, help="Description of the event.")
    parser_log.add_argument("--ip", help="Source IP address, if applicable.")
    parser_log.add_argument("--ua", help="User agent, if applicable.")

    # block_ip
    parser_block = subparsers.add_parser("block_ip", help="Block an IP address.")
    parser_block.add_argument("ip_address", help="The IP address to block.")
    parser_block.add_argument("--reason", default="Manual block via CLI.", help="Reason for blocking.")
    parser_block.add_argument("--duration", type=float, default=None, help="Duration in hours for the block (uses config default if None).")

    # unblock_ip
    parser_unblock = subparsers.add_parser("unblock_ip", help="Unblock an IP address.")
    parser_unblock.add_argument("ip_address", help="The IP address to unblock.")

    # validate_password
    parser_valpass = subparsers.add_parser("validate_password", help="Validate password strength.")
    parser_valpass.add_argument("password", help="The password to validate.")
    
    # hash_password
    parser_hashpass = subparsers.add_parser("hash_password", help="Hash a password.")
    parser_hashpass.add_argument("password", help="The password to hash.")

    # encrypt_data
    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt data.")
    parser_encrypt.add_argument("data", help="The string data to encrypt.")
    parser_encrypt.add_argument("password", help="The password for encryption.")

    # decrypt_data
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt data.")
    parser_decrypt.add_argument("encrypted_package_json", help="The encrypted package as a JSON string (e.g., '{\"encrypted_data\": \"...\", \"salt\": \"...\"}').")
    parser_decrypt.add_argument("password", help="The password for decryption.")

    # detect_threats
    parser_threats = subparsers.add_parser("threats", help="Detect potential threats.")
    parser_threats.add_argument("--hours", type=int, default=1, help="Time window in hours to check for threats.")

    # security_report
    parser_report = subparsers.add_parser("report", help="Generate a security report.")
    parser_report.add_argument("--hours", type=int, default=24, help="Time window in hours for the report.")

    # list_blocked
    subparsers.add_parser("list_blocked_ips", help="List all currently blocked IP addresses.")
    
    # list_sessions
    subparsers.add_parser("list_active_sessions", help="List all active user sessions.")

    args = parser.parse_args()
    manager = SecurityManager()

    if args.action == "log_event":
        manager.log_security_event(args.type, args.severity, args.desc, source_ip=args.ip, user_agent=args.ua)
        print(f"✅ Event '{args.type}' logged with severity '{args.severity}'.")
    
    elif args.action == "block_ip":
        manager.block_ip(args.ip_address, args.reason, duration_hours=args.duration, auto_blocked=False)
        # block_ip logs internally
    
    elif args.action == "unblock_ip":
        manager.unblock_ip(args.ip_address)
        # unblock_ip logs internally

    elif args.action == "validate_password":
        is_valid, issues = manager.validate_password(args.password)
        if is_valid:
            print("✅ Password meets complexity requirements.")
        else:
            print("❌ Password does not meet complexity requirements:")
            for issue in issues:
                print(f"   - {issue}")
                
    elif args.action == "hash_password":
        hashed_pw = manager.hash_password(args.password)
        print(f"🔑 Hashed password: {hashed_pw}")

    elif args.action == "encrypt":
        try:
            encrypted_package = manager.encrypt_data(args.data, args.password)
            print("✅ Data encrypted successfully:")
            print(json.dumps(encrypted_package, indent=2))
        except Exception as e:
            print(f"❌ Encryption failed: {e}")

    elif args.action == "decrypt":
        try:
            package_dict = json.loads(args.encrypted_package_json)
            decrypted_data = manager.decrypt_data(package_dict, args.password)
            print(f"✅ Data decrypted successfully: {decrypted_data}")
        except json.JSONDecodeError:
            print("❌ Invalid JSON string for encrypted package.")
        except Exception as e:
            print(f"❌ Decryption failed: {e}")

    elif args.action == "threats":
        threats = manager.detect_threats(hours=args.hours)
        if threats:
            print(f"🚨 {len(threats)} potential threat(s) detected in the last {args.hours} hour(s):")
            for i, threat in enumerate(threats, 1):
                print(f"  {i}. Type: {threat['type']}, Severity: {threat['severity']}")
                print(f"     Description: {threat['description']}")
                if 'source_ip' in threat: print(f"     IP: {threat['source_ip']}")
        else:
            print(f"✅ No significant threats detected in the last {args.hours} hour(s).")

    elif args.action == "report":
        report = manager.generate_security_report(hours=args.hours)
        print("\n📊 Security Report:")
        print(json.dumps(report, indent=2, default=str)) # Use default=str for datetime objects if any

    elif args.action == "list_blocked_ips":
        blocked = manager.get_blocked_ips()
        if blocked:
            print("🚫 Currently Blocked IP Addresses:")
            for item in blocked:
                print(f"  - IP: {item['ip_address']}, Reason: {item['reason']}, Blocked At: {item['blocked_at']}, Expires At: {item['expires_at']}")
        else:
            print("✅ No IPs are currently blocked.")
            
    elif args.action == "list_active_sessions":
        sessions = manager.get_active_sessions()
        if sessions:
            print("🔑 Currently Active User Sessions:")
            for item in sessions:
                print(f"  - Token Suffix: ...{item['session_token'][-8:]}, IP: {item['ip_address']}, Created: {item['created_at']}, Expires: {item['expires_at']}")
        else:
            print("✅ No active user sessions found.")

if __name__ == "__main__":
    main()
