class HealthMonitor:
    def __init__(self, database):
        self.db = database
        self.metrics = {
            'query_performance': [],
            'memory_usage': [],
            'disk_usage': [],
            'connection_count': 0
        }
        self.alerts = []
    
    def start_monitoring(self):
        """Start continuous health monitoring"""
        import threading
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while True:
            self.check_performance()
            self.check_resources()
            self.check_integrity()
            time.sleep(60)  # Check every minute
    
    def check_performance(self):
        """Monitor query performance"""
        slow_queries = self.detect_slow_queries()
        for query, duration in slow_queries:
            self.alert(f"Slow query detected: {query} took {duration}s")
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        return {
            'status': self.get_overall_status(),
            'performance_metrics': self.calculate_performance_metrics(),
            'recommendations': self.generate_recommendations(),
            'alerts': self.alerts[-10:]  # Last 10 alerts
        }
    
    def generate_recommendations(self):
        """AI-powered database optimization recommendations"""
        recommendations = []
        
        if self.metrics['query_performance'] and \
           max(self.metrics['query_performance']) > 5.0:
            recommendations.append("Consider adding indexes for slow queries")
        
        if self.get_disk_usage() > 0.8:
            recommendations.append("Database approaching storage limit")
        
        return recommendations