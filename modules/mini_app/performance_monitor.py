"""
Performance Monitor for YouTube Income Commander
Tracks system performance, resource usage, and optimization opportunities
"""
import os
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import sqlite3

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.metrics = defaultdict(deque)
        self.alerts = []
        self.config = self.load_config()
        self.db_path = "performance_metrics.db"
        self.init_database()
        
    def load_config(self):
        """Load monitoring configuration"""
        default_config = {
            "monitor_interval": 30,  # seconds
            "max_metrics_history": 1000,
            "cpu_alert_threshold": 90,
            "memory_alert_threshold": 85,
            "disk_alert_threshold": 95,
            "response_time_threshold": 5.0,
            "enable_alerts": True,
            "log_to_file": True
        }
        
        config_file = "config/performance_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return {**default_config, **json.load(f)}
        except Exception:
            pass
        
        return default_config
    
    def init_database(self):
        """Initialize performance metrics database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize performance database: {e}")
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.monitoring:
            print("⚠️ Monitoring already running")
            return
        
        print("🔍 Starting performance monitoring...")
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.monitoring:
            print("⚠️ Monitoring not running")
            return
        
        print("🛑 Stopping performance monitoring...")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("✅ Performance monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect application metrics
                self._collect_application_metrics()
                
                # Check for alerts
                if self.config['enable_alerts']:
                    self._check_alerts()
                
                # Sleep until next collection
                time.sleep(self.config['monitor_interval'])
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.config['monitor_interval'])
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        timestamp = datetime.now()
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            self._record_metric("system", "cpu_percent", cpu_percent, "%", timestamp)
            self._record_metric("system", "cpu_count", cpu_count, "cores", timestamp)
            if cpu_freq:
                self._record_metric("system", "cpu_freq", cpu_freq.current, "MHz", timestamp)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self._record_metric("system", "memory_percent", memory.percent, "%", timestamp)
            self._record_metric("system", "memory_available", memory.available / (1024**3), "GB", timestamp)
            self._record_metric("system", "memory_used", memory.used / (1024**3), "GB", timestamp)
            
            # Disk metrics
            disk = psutil.disk_usage('.')
            disk_percent = (disk.used / disk.total) * 100
            self._record_metric("system", "disk_percent", disk_percent, "%", timestamp)
            self._record_metric("system", "disk_free", disk.free / (1024**3), "GB", timestamp)
            
            # Network metrics (if available)
            try:
                net_io = psutil.net_io_counters()
                self._record_metric("system", "bytes_sent", net_io.bytes_sent, "bytes", timestamp)
                self._record_metric("system", "bytes_recv", net_io.bytes_recv, "bytes", timestamp)
            except:
                pass
            
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application-specific metrics"""
        timestamp = datetime.now()
        
        try:
            # Database metrics
            self._collect_database_metrics(timestamp)
            
            # File system metrics
            self._collect_filesystem_metrics(timestamp)
            
            # Process metrics
            current_process = psutil.Process()
            self._record_metric("application", "process_memory", 
                              current_process.memory_info().rss / (1024**2), "MB", timestamp)
            self._record_metric("application", "process_cpu", 
                              current_process.cpu_percent(), "%", timestamp)
            
        except Exception as e:
            print(f"Error collecting application metrics: {e}")
    
    def _collect_database_metrics(self, timestamp):
        """Collect database performance metrics"""
        try:
            db_files = ['youtube_projects.db', 'revenue_tracker.db', 'evidence_master.db']
            
            for db_file in db_files:
                if os.path.exists(db_file):
                    # Database size
                    size_mb = os.path.getsize(db_file) / (1024**2)
                    self._record_metric("database", f"{db_file}_size", size_mb, "MB", timestamp)
                    
                    # Query performance test
                    start_time = time.time()
                    try:
                        conn = sqlite3.connect(db_file)
                        conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        conn.close()
                        query_time = (time.time() - start_time) * 1000
                        self._record_metric("database", f"{db_file}_query_time", query_time, "ms", timestamp)
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error collecting database metrics: {e}")
    
    def _collect_filesystem_metrics(self, timestamp):
        """Collect file system metrics"""
        try:
            directories = ['outputs', 'evidence', 'config', 'logs']
            
            for directory in directories:
                if os.path.exists(directory):
                    # Directory size
                    total_size = 0
                    file_count = 0
                    
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except:
                                pass
                    
                    size_mb = total_size / (1024**2)
                    self._record_metric("filesystem", f"{directory}_size", size_mb, "MB", timestamp)
                    self._record_metric("filesystem", f"{directory}_files", file_count, "files", timestamp)
                    
        except Exception as e:
            print(f"Error collecting filesystem metrics: {e}")
    
    def _record_metric(self, metric_type, metric_name, value, unit, timestamp):
        """Record a metric value"""
        # Store in memory
        key = f"{metric_type}.{metric_name}"
        self.metrics[key].append({
            'timestamp': timestamp,
            'value': value,
            'unit': unit
        })
        
        # Limit memory usage
        if len(self.metrics[key]) > self.config['max_metrics_history']:
            self.metrics[key].popleft()
        
        # Store in database
        if self.config['log_to_file']:
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, metric_type, metric_name, value, unit)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp.isoformat(), metric_type, metric_name, value, unit))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error recording metric to database: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts"""
        try:
            current_time = datetime.now()
            
            # CPU alert
            cpu_key = "system.cpu_percent"
            if cpu_key in self.metrics and self.metrics[cpu_key]:
                latest_cpu = self.metrics[cpu_key][-1]['value']
                if latest_cpu > self.config['cpu_alert_threshold']:
                    self._create_alert("cpu_high", "warning", 
                                     f"High CPU usage: {latest_cpu:.1f}%")
            
            # Memory alert
            memory_key = "system.memory_percent"
            if memory_key in self.metrics and self.metrics[memory_key]:
                latest_memory = self.metrics[memory_key][-1]['value']
                if latest_memory > self.config['memory_alert_threshold']:
                    self._create_alert("memory_high", "warning", 
                                     f"High memory usage: {latest_memory:.1f}%")
            
            # Disk alert
            disk_key = "system.disk_percent"
            if disk_key in self.metrics and self.metrics[disk_key]:
                latest_disk = self.metrics[disk_key][-1]['value']
                if latest_disk > self.config['disk_alert_threshold']:
                    self._create_alert("disk_high", "critical", 
                                     f"High disk usage: {latest_disk:.1f}%")
            
        except Exception as e:
            print(f"Error checking alerts: {e}")
    
    def _create_alert(self, alert_type, severity, message):
        """Create a performance alert"""
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'severity': severity,
            'message': message,
            'resolved': False
        }
        
        # Check if similar alert already exists
        recent_alerts = [a for a in self.alerts 
                        if a['type'] == alert_type and not a['resolved']
                        and (datetime.now() - a['timestamp']).seconds < 300]  # 5 minutes
        
        if not recent_alerts:
            self.alerts.append(alert)
            print(f"🚨 ALERT [{severity.upper()}]: {message}")
            
            # Store in database
            try:
                conn = sqlite3.connect(self.db_path)
                conn.execute('''
                    INSERT INTO performance_alerts 
                    (timestamp, alert_type, severity, message)
                    VALUES (?, ?, ?, ?)
                ''', (alert['timestamp'].isoformat(), alert_type, severity, message))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error storing alert: {e}")
    
    def get_current_metrics(self):
        """Get current performance metrics"""
        current_metrics = {}
        
        for key, values in self.metrics.items():
            if values:
                latest = values[-1]
                current_metrics[key] = {
                    'value': latest['value'],
                    'unit': latest['unit'],
                    'timestamp': latest['timestamp'].isoformat()
                }
        
        return current_metrics
    
    def get_metric_history(self, metric_key, hours=24):
        """Get metric history for specified time period"""
        if metric_key not in self.metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        history = []
        for metric in self.metrics[metric_key]:
            if metric['timestamp'] >= cutoff_time:
                history.append({
                    'timestamp': metric['timestamp'].isoformat(),
                    'value': metric['value'],
                    'unit': metric['unit']
                })
        
        return history
    
    def get_performance_summary(self, hours=24):
        """Get performance summary for specified time period"""
        summary = {
            'period_hours': hours,
            'generated_at': datetime.now().isoformat(),
            'metrics': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Calculate metric summaries
        for key, values in self.metrics.items():
            if not values:
                continue
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_values = [v['value'] for v in values if v['timestamp'] >= cutoff_time]
            
            if recent_values:
                summary['metrics'][key] = {
                    'current': recent_values[-1],
                    'average': sum(recent_values) / len(recent_values),
                    'min': min(recent_values),
                    'max': max(recent_values),
                    'unit': values[-1]['unit'],
                    'samples': len(recent_values)
                }
        
        # Get recent alerts
        cutoff_time = datetime.now() - timedelta(hours=hours)
        summary['alerts'] = [
            {
                'timestamp': alert['timestamp'].isoformat(),
                'type': alert['type'],
                'severity': alert['severity'],
                'message': alert['message'],
                'resolved': alert['resolved']
            }
            for alert in self.alerts
            if alert['timestamp'] >= cutoff_time
        ]
        
        # Generate recommendations
        summary['recommendations'] = self._generate_recommendations(summary['metrics'])
        
        return summary
    
    def _generate_recommendations(self, metrics):
        """Generate performance recommendations"""
        recommendations = []
        
        # CPU recommendations
        if 'system.cpu_percent' in metrics:
            cpu_avg = metrics['system.cpu_percent']['average']
            cpu_max = metrics['system.cpu_percent']['max']
            
            if cpu_avg > 70:
                recommendations.append({
                    'type': 'cpu',
                    'priority': 'high',
                    'message': f'High average CPU usage ({cpu_avg:.1f}%). Consider optimizing processes or upgrading hardware.',
                    'actions': [
                        'Review running processes',
                        'Optimize database queries',
                        'Consider upgrading CPU'
                    ]
                })
            elif cpu_max > 90:
                recommendations.append({
                    'type': 'cpu',
                    'priority': 'medium',
                    'message': f'CPU spikes detected ({cpu_max:.1f}%). Monitor for performance bottlenecks.',
                    'actions': [
                        'Identify CPU-intensive operations',
                        'Implement process throttling',
                        'Schedule heavy tasks during off-peak hours'
                    ]
                })
        
        # Memory recommendations
        if 'system.memory_percent' in metrics:
            memory_avg = metrics['system.memory_percent']['average']
            memory_max = metrics['system.memory_percent']['max']
            
            if memory_avg > 80:
                recommendations.append({
                    'type': 'memory',
                    'priority': 'high',
                    'message': f'High memory usage ({memory_avg:.1f}%). Risk of system instability.',
                    'actions': [
                        'Clear unnecessary data from memory',
                        'Optimize data structures',
                        'Add more RAM',
                        'Implement memory cleanup routines'
                    ]
                })
            elif memory_max > 95:
                recommendations.append({
                    'type': 'memory',
                    'priority': 'critical',
                    'message': f'Memory usage reached critical levels ({memory_max:.1f}%).',
                    'actions': [
                        'Immediate memory cleanup required',
                        'Restart application if necessary',
                        'Investigate memory leaks'
                    ]
                })
        
        # Disk recommendations
        if 'system.disk_percent' in metrics:
            disk_current = metrics['system.disk_percent']['current']
            
            if disk_current > 90:
                recommendations.append({
                    'type': 'disk',
                    'priority': 'critical',
                    'message': f'Disk space critically low ({disk_current:.1f}%).',
                    'actions': [
                        'Clean up old files immediately',
                        'Archive or delete unnecessary data',
                        'Add more storage capacity'
                    ]
                })
            elif disk_current > 80:
                recommendations.append({
                    'type': 'disk',
                    'priority': 'medium',
                    'message': f'Disk space running low ({disk_current:.1f}%).',
                    'actions': [
                        'Schedule regular cleanup',
                        'Implement automatic archiving',
                        'Monitor disk usage trends'
                    ]
                })
        
        # Database recommendations
        db_metrics = {k: v for k, v in metrics.items() if k.startswith('database.')}
        if db_metrics:
            total_db_size = sum(v['current'] for k, v in db_metrics.items() if k.endswith('_size'))
            
            if total_db_size > 1000:  # 1GB
                recommendations.append({
                    'type': 'database',
                    'priority': 'medium',
                    'message': f'Large database size ({total_db_size:.1f} MB). Consider optimization.',
                    'actions': [
                        'Archive old data',
                        'Optimize database indexes',
                        'Implement data retention policies',
                        'Consider database partitioning'
                    ]
                })
        
        return recommendations
    
    def export_metrics(self, filename=None, format='json', hours=24):
        """Export performance metrics to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_export_{timestamp}.{format}"
        
        try:
            if format.lower() == 'json':
                data = self.get_performance_summary(hours)
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Metric', 'Value', 'Unit'])
                    
                    cutoff_time = datetime.now() - timedelta(hours=hours)
                    for key, values in self.metrics.items():
                        for metric in values:
                            if metric['timestamp'] >= cutoff_time:
                                writer.writerow([
                                    metric['timestamp'].isoformat(),
                                    key,
                                    metric['value'],
                                    metric['unit']
                                ])
            
            print(f"✅ Metrics exported to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def cleanup_old_data(self, days=30):
        """Clean up old performance data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            conn = sqlite3.connect(self.db_path)
            
            # Clean up old metrics
            result = conn.execute('''
                DELETE FROM performance_metrics 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            metrics_deleted = result.rowcount
            
            # Clean up old alerts
            result = conn.execute('''
                DELETE FROM performance_alerts 
                WHERE timestamp < ? AND resolved = TRUE
            ''', (cutoff_date.isoformat(),))
            
            alerts_deleted = result.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"✅ Cleaned up {metrics_deleted} old metrics and {alerts_deleted} resolved alerts")
            return True
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            return False
    
    def get_system_health_score(self):
        """Calculate overall system health score (0-100)"""
        if not self.metrics:
            return 0
        
        scores = []
        weights = []
        
        # CPU health (30% weight)
        if 'system.cpu_percent' in self.metrics and self.metrics['system.cpu_percent']:
            cpu_usage = self.metrics['system.cpu_percent'][-1]['value']
            cpu_score = max(0, 100 - cpu_usage)
            scores.append(cpu_score)
            weights.append(30)
        
        # Memory health (30% weight)
        if 'system.memory_percent' in self.metrics and self.metrics['system.memory_percent']:
            memory_usage = self.metrics['system.memory_percent'][-1]['value']
            memory_score = max(0, 100 - memory_usage)
            scores.append(memory_score)
            weights.append(30)
        
        # Disk health (25% weight)
        if 'system.disk_percent' in self.metrics and self.metrics['system.disk_percent']:
            disk_usage = self.metrics['system.disk_percent'][-1]['value']
            disk_score = max(0, 100 - disk_usage)
            scores.append(disk_score)
            weights.append(25)
        
        # Alert penalty (15% weight)
        recent_alerts = [a for a in self.alerts 
                        if not a['resolved'] and 
                        (datetime.now() - a['timestamp']).seconds < 3600]  # 1 hour
        
        alert_penalty = min(len(recent_alerts) * 10, 50)  # Max 50 point penalty
        alert_score = max(0, 100 - alert_penalty)
        scores.append(alert_score)
        weights.append(15)
        
        # Calculate weighted average
        if scores and weights:
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            total_weight = sum(weights)
            health_score = weighted_sum / total_weight
        else:
            health_score = 0
        
        return round(health_score, 1)
    
    def print_dashboard(self):
        """Print performance dashboard"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE DASHBOARD")
        print("="*60)
        
        # System health score
        health_score = self.get_system_health_score()
        if health_score >= 80:
            health_status = "🟢 EXCELLENT"
        elif health_score >= 60:
            health_status = "🟡 GOOD"
        elif health_score >= 40:
            health_status = "🟠 FAIR"
        else:
            health_status = "🔴 POOR"
        
        print(f"🏥 System Health: {health_score}/100 {health_status}")
        print()
        
        # Current metrics
        current_metrics = self.get_current_metrics()
        
        if 'system.cpu_percent' in current_metrics:
            cpu = current_metrics['system.cpu_percent']
            print(f"🖥️  CPU Usage: {cpu['value']:.1f}%")
        
        if 'system.memory_percent' in current_metrics:
            memory = current_metrics['system.memory_percent']
            print(f"🧠 Memory Usage: {memory['value']:.1f}%")
        
        if 'system.disk_percent' in current_metrics:
            disk = current_metrics['system.disk_percent']
            print(f"💾 Disk Usage: {disk['value']:.1f}%")
        
        if 'application.process_memory' in current_metrics:
            app_memory = current_metrics['application.process_memory']
            print(f"📱 App Memory: {app_memory['value']:.1f} MB")
        
        # Recent alerts
        recent_alerts = [a for a in self.alerts 
                        if not a['resolved'] and 
                        (datetime.now() - a['timestamp']).seconds < 3600]
        
        if recent_alerts:
            print(f"\n🚨 Active Alerts ({len(recent_alerts)}):")
            for alert in recent_alerts[-5:]:  # Show last 5
                severity_icon = "🔴" if alert['severity'] == 'critical' else "🟡"
                print(f"   {severity_icon} {alert['message']}")
        else:
            print(f"\n✅ No active alerts")
        
        print("\n" + "="*60)

def main():
    """Main performance monitor interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Income Commander Performance Monitor")
    parser.add_argument("action", choices=['start', 'stop', 'status', 'dashboard', 'export', 'cleanup'], 
                       help="Action to perform")
    parser.add_argument("--hours", type=int, default=24, help="Time period for reports (hours)")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', help="Export format")
    parser.add_argument("--days", type=int, default=30, help="Days of data to keep during cleanup")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    
    if args.action == "start":
        monitor.start_monitoring()
        print("🔍 Performance monitoring started in background")
        print("   Use 'python performance_monitor.py dashboard' to view metrics")
        print("   Use 'python performance_monitor.py stop' to stop monitoring")
        
        # Keep the script running
        try:
            while monitor.monitoring:
                time.sleep(10)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    elif args.action == "stop":
        monitor.stop_monitoring()
    
    elif args.action == "status":
        if monitor.monitoring:
            print("✅ Performance monitoring is running")
        else:
            print("❌ Performance monitoring is not running")
        
        current_metrics = monitor.get_current_metrics()
        if current_metrics:
            print(f"📊 {len(current_metrics)} metrics available")
            health_score = monitor.get_system_health_score()
            print(f"🏥 System health: {health_score}/100")
        else:
            print("📊 No metrics available")
    
    elif args.action == "dashboard":
        monitor.print_dashboard()
    
    elif args.action == "export":
        filename = monitor.export_metrics(format=args.format, hours=args.hours)
        if filename:
            print(f"📁 Metrics exported to: {filename}")
    
    elif args.action == "cleanup":
        success = monitor.cleanup_old_data(args.days)
        if success:
            print(f"✅ Cleaned up data older than {args.days} days")

if __name__ == "__main__":
    main()