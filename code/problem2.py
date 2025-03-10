import numpy as np
from datetime import datetime, timedelta
import time
from enum import Enum
import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, List

class AlertPriority(Enum):
    P0 = "P0"  # Critical
    P1 = "P1"  # Major
    P2 = "P2"  # Minor

@dataclass
class Thresholds:
    P0_LATENCY = 2000
    P0_FAILURE_RATE = 10
    P1_LATENCY = 1000
    P1_FAILURE_RATE = 5
    P2_LATENCY = 500
    P2_FAILURE_RATE = 2

@dataclass
class NotificationIntervals:
    P0 = timedelta(hours=2)
    P1 = timedelta(hours=12)
    P2 = timedelta(hours=48)

@dataclass
class Alert:
    priority: AlertPriority
    start_time: datetime
    last_notification: datetime
    latency: float
    failure_rate: float
    resolved: bool = False

class MetricGenerator:
    def __init__(self, base_latency=200, base_failure_rate=1):
        self.base_latency = base_latency
        self.base_failure_rate = base_failure_rate
        self.issue_duration = 0
        self.is_persistent = False
        self.logger = logging.getLogger('MonitoringSystem')

    def generate_metrics(self) -> tuple[float, float]:
        # Randomly introduce issues
        if np.random.random() < 0.05 and self.issue_duration == 0:  # 5% chance of new issue
            self.is_persistent = np.random.random() < 0.3  # 30% chance of persistent issue
            self.issue_duration = np.random.randint(1, 288 if self.is_persistent else 12)  # Up to 1 day or 1 hour

        if self.issue_duration > 0:
            # Generate elevated metrics during issues
            latency = np.random.poisson(self.base_latency * (5 if self.is_persistent else 3))
            failure_rate = np.random.poisson(self.base_failure_rate * (4 if self.is_persistent else 2))

            # If this is a persistent issue that's about to end, mock PR merges
            if self.is_persistent and self.issue_duration == 1:
                pr_count = np.random.randint(1, 4)  # Random number of PRs between 1 and 3
                for i in range(pr_count):
                    commit_id = ''.join(np.random.choice(list('0123456789abcdef'), 7))
                    self.logger.info(f"INFO: Commit {commit_id} submitted to fix the persistent issue")

            self.issue_duration -= 1
        else:
            # Normal operation metrics
            latency = np.random.poisson(self.base_latency)
            failure_rate = np.random.poisson(self.base_failure_rate)

        return float(latency), float(failure_rate)

class AlertManager:
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('MonitoringSystem')
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # File handler
        fh = logging.FileHandler('logs/monitoring.log')
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('[%(asctime)s] %(message)s',
                                    datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def determine_priority(self, latency: float, failure_rate: float) -> Optional[AlertPriority]:
        if latency > Thresholds.P0_LATENCY or failure_rate > Thresholds.P0_FAILURE_RATE:
            return AlertPriority.P0
        elif latency > Thresholds.P1_LATENCY or failure_rate > Thresholds.P1_FAILURE_RATE:
            return AlertPriority.P1
        elif latency > Thresholds.P2_LATENCY or failure_rate > Thresholds.P2_FAILURE_RATE:
            return AlertPriority.P2
        return None

    def check_metrics(self, latency: float, failure_rate: float):
        current_time = datetime.now()
        priority = self.determine_priority(latency, failure_rate)

        if priority:
            alert_key = f"{priority.value}"

            # Check if alert already exists
            if alert_key in self.active_alerts:
                existing_alert = self.active_alerts[alert_key]
                # Update priority if conditions are worse
                if priority.value < existing_alert.priority.value:  # P0 < P1 < P2
                    self._upgrade_alert(existing_alert, priority, latency, failure_rate)
            else:
                # Create new alert
                self._create_alert(priority, latency, failure_rate)
        else:
            # Check if any active alerts can be resolved
            self._resolve_alerts()

        # Log current status
        self.logger.info(f"Latency: {latency}ms, Failure Rate: {failure_rate}%")

    def _create_alert(self, priority: AlertPriority, latency: float, failure_rate: float):
        current_time = datetime.now()
        alert = Alert(
            priority=priority,
            start_time=current_time,
            last_notification=current_time,
            latency=latency,
            failure_rate=failure_rate
        )
        self.active_alerts[priority.value] = alert
        self._send_notification(alert, is_initial=True)

    def _upgrade_alert(self, alert: Alert, new_priority: AlertPriority, latency: float, failure_rate: float):
        old_priority = alert.priority
        alert.priority = new_priority
        alert.latency = latency
        alert.failure_rate = failure_rate
        self.logger.info(f"Alert upgraded from {old_priority.value} to {new_priority.value}")
        self._send_notification(alert, is_upgrade=True)

    def _resolve_alerts(self):
        for alert_key in list(self.active_alerts.keys()):
            alert = self.active_alerts[alert_key]
            if not alert.resolved:
                alert.resolved = True
                self.logger.info(f"Alert {alert.priority.value} resolved.")
                del self.active_alerts[alert_key]

    def _send_notification(self, alert: Alert, is_initial=False, is_upgrade=False):
        current_time = datetime.now()
        notification_interval = getattr(NotificationIntervals, alert.priority.value)

        if is_initial:
            self.logger.info(f"{alert.priority.value} Alert Triggered! "
                           f"Latency: {alert.latency}ms, Failure Rate: {alert.failure_rate}%")
        elif is_upgrade:
            self.logger.info(f"Alert upgraded to {alert.priority.value}! "
                           f"Latency: {alert.latency}ms, Failure Rate: {alert.failure_rate}%")
        else:
            self.logger.info(f"ALERT: Resending {alert.priority.value} alert (Still unresolved)")

        # Check for escalation to skip-level boss
        time_active = current_time - alert.start_time
        escalation_threshold = notification_interval * 5
        if time_active > escalation_threshold:
            self.logger.info(f"ESCALATION: Notifying skip-level boss about unresolved {alert.priority.value} alert")

        alert.last_notification = current_time

    def check_notifications(self):
        current_time = datetime.now()
        for alert in self.active_alerts.values():
            if alert.resolved:
                continue

            notification_interval = getattr(NotificationIntervals, alert.priority.value)
            time_since_last = current_time - alert.last_notification

            if time_since_last >= notification_interval:
                self._send_notification(alert)

def cleanup_old_logs():
    """Delete logs older than 90 days"""
    cutoff = datetime.now() - timedelta(days=90)
    log_dir = 'logs'

    if not os.path.exists(log_dir):
        return

    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
        if file_time < cutoff:
            os.remove(filepath)

def main():
    metric_generator = MetricGenerator()
    alert_manager = AlertManager()

    # Share the logger with the metric generator
    metric_generator.logger = alert_manager.logger

    try:
        while True:
            # Generate new metrics
            latency, failure_rate = metric_generator.generate_metrics()

            # Check metrics and handle alerts
            alert_manager.check_metrics(latency, failure_rate)

            # Check if notifications need to be resent
            alert_manager.check_notifications()

            # Cleanup old logs
            cleanup_old_logs()

            # Wait for 5 minutes
            time.sleep(300)  # 5 minutes in seconds
            # Wait for 0.5 second
            #time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nMonitoring system stopped.")

if __name__ == "__main__":
    main()