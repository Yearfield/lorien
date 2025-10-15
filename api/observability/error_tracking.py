"""
Error tracking and alerting system for the Lorien API.

Provides:
- Error aggregation and tracking
- Alert thresholds and notifications
- Error pattern detection
- Health status monitoring
- Integration with external alerting systems
"""

import asyncio
import json
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .context import get_context_dict, get_request_id, get_trace_id
from .logging import get_logger
from .metrics import increment_counter, set_gauge
from ..exceptions import ErrorCodes


class ErrorSeverity(Enum):
    """Error severity levels for alerting."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Alert notification channels."""
    LOG = "log"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    PAGERDUTY = "pagerduty"


@dataclass
class ErrorEvent:
    """Represents a single error event."""
    timestamp: datetime
    error_code: str
    status_code: int
    message: str
    severity: ErrorSeverity
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    count: int = 1


@dataclass
class AlertRule:
    """Defines when to trigger an alert."""
    name: str
    error_codes: Set[str]
    threshold_count: int
    time_window_seconds: int
    severity: ErrorSeverity
    channels: Set[AlertChannel]
    cooldown_seconds: int = 300  # 5 minutes default cooldown
    enabled: bool = True


class ErrorTracker:
    """
    Tracks errors and manages alerting.
    
    Features:
    - Real-time error aggregation
    - Configurable alert rules
    - Multiple notification channels
    - Pattern detection and analysis
    - Health status monitoring
    """
    
    def __init__(self):
        """Initialize the error tracker."""
        self.logger = get_logger(__name__)
        
        # Error storage (in-memory for now, could be externalized)
        self._error_events: deque = deque(maxlen=10000)  # Keep last 10k errors
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._error_patterns: Dict[str, List[ErrorEvent]] = defaultdict(list)
        
        # Alerting
        self._alert_rules: List[AlertRule] = []
        self._alert_history: Dict[str, datetime] = {}  # Track last alert time per rule
        
        # Health status
        self._health_status = "healthy"
        self._last_health_check = datetime.now(UTC)
        
        # Load default alert rules
        self._setup_default_rules()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _setup_default_rules(self):
        """Set up default alert rules for common scenarios."""
        default_rules = [
            # Critical errors (500s)
            AlertRule(
                name="critical_server_errors",
                error_codes={ErrorCodes.INTERNAL_SERVER_ERROR},
                threshold_count=5,
                time_window_seconds=300,  # 5 minutes
                severity=ErrorSeverity.CRITICAL,
                channels={AlertChannel.LOG},
                cooldown_seconds=600,  # 10 minutes
            ),
            
            # High error rate
            AlertRule(
                name="high_error_rate",
                error_codes=set(),  # All errors
                threshold_count=50,
                time_window_seconds=300,  # 5 minutes
                severity=ErrorSeverity.HIGH,
                channels={AlertChannel.LOG},
                cooldown_seconds=900,  # 15 minutes
            ),
            
            # Authentication failures
            AlertRule(
                name="auth_failures",
                error_codes={
                    ErrorCodes.AUTHENTICATION_REQUIRED,
                    ErrorCodes.INVALID_TOKEN,
                    ErrorCodes.TOKEN_EXPIRED,
                },
                threshold_count=10,
                time_window_seconds=300,  # 5 minutes
                severity=ErrorSeverity.MEDIUM,
                channels={AlertChannel.LOG},
                cooldown_seconds=1800,  # 30 minutes
            ),
            
            # Database errors
            AlertRule(
                name="database_errors",
                error_codes={
                    ErrorCodes.DATABASE_ERROR,
                    ErrorCodes.DATABASE_CONNECTION_ERROR,
                    ErrorCodes.INTEGRITY_ERROR,
                },
                threshold_count=3,
                time_window_seconds=300,  # 5 minutes
                severity=ErrorSeverity.HIGH,
                channels={AlertChannel.LOG},
                cooldown_seconds=600,  # 10 minutes
            ),
            
            # Rate limiting
            AlertRule(
                name="rate_limiting",
                error_codes={ErrorCodes.RATE_LIMIT_EXCEEDED},
                threshold_count=20,
                time_window_seconds=300,  # 5 minutes
                severity=ErrorSeverity.MEDIUM,
                channels={AlertChannel.LOG},
                cooldown_seconds=1800,  # 30 minutes
            ),
        ]
        
        self._alert_rules.extend(default_rules)
    
    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        # Start health monitoring task
        asyncio.create_task(self._health_monitoring_task())
        
        # Start alert processing task
        asyncio.create_task(self._alert_processing_task())
    
    async def track_error(
        self,
        error_code: str,
        status_code: int,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Track an error event.
        
        Args:
            error_code: Internal error code
            status_code: HTTP status code
            message: Error message
            severity: Error severity level
            context: Additional context
        """
        # Get correlation IDs
        context_dict = get_context_dict()
        
        # Create error event
        error_event = ErrorEvent(
            timestamp=datetime.now(UTC),
            error_code=error_code,
            status_code=status_code,
            message=message,
            severity=severity,
            request_id=context_dict.get("request_id"),
            trace_id=context_dict.get("trace_id"),
            context=context or {},
        )
        
        # Store the error event
        self._error_events.append(error_event)
        
        # Update counters
        self._error_counts[error_code] += 1
        self._error_patterns[error_code].append(error_event)
        
        # Keep only recent errors in patterns (last 100 per code)
        if len(self._error_patterns[error_code]) > 100:
            self._error_patterns[error_code] = self._error_patterns[error_code][-100:]
        
        # Update metrics
        increment_counter(
            "error_tracker.errors",
            tags={
                "error_code": error_code,
                "severity": severity.value,
                "status_code": str(status_code),
            },
        )
        
        # Check for alerts
        await self._check_alerts(error_event)
        
        # Update health status
        self._update_health_status()
    
    async def _check_alerts(self, error_event: ErrorEvent):
        """Check if any alert rules should be triggered."""
        current_time = datetime.now(UTC)
        
        for rule in self._alert_rules:
            if not rule.enabled:
                continue
            
            # Check if rule applies to this error
            if rule.error_codes and error_event.error_code not in rule.error_codes:
                continue
            
            # Check cooldown
            last_alert = self._alert_history.get(rule.name)
            if last_alert and (current_time - last_alert).total_seconds() < rule.cooldown_seconds:
                continue
            
            # Count errors in time window
            window_start = current_time - timedelta(seconds=rule.time_window_seconds)
            error_count = sum(
                1 for event in self._error_events
                if event.timestamp >= window_start
                and (not rule.error_codes or event.error_code in rule.error_codes)
            )
            
            # Check if threshold is exceeded
            if error_count >= rule.threshold_count:
                await self._trigger_alert(rule, error_count, error_event)
                self._alert_history[rule.name] = current_time
    
    async def _trigger_alert(self, rule: AlertRule, error_count: int, trigger_event: ErrorEvent):
        """Trigger an alert for the given rule."""
        self.logger.warning(
            f"ALERT TRIGGERED: {rule.name} - {error_count} errors in {rule.time_window_seconds}s",
            extra_fields={
                "alert": {
                    "rule_name": rule.name,
                    "error_count": error_count,
                    "threshold": rule.threshold_count,
                    "time_window": rule.time_window_seconds,
                    "severity": rule.severity.value,
                    "trigger_event": {
                        "error_code": trigger_event.error_code,
                        "status_code": trigger_event.status_code,
                        "message": trigger_event.message,
                        "timestamp": trigger_event.timestamp.isoformat(),
                    },
                }
            },
        )
        
        # Send alerts to configured channels
        for channel in rule.channels:
            await self._send_alert(channel, rule, error_count, trigger_event)
        
        # Update metrics
        increment_counter(
            "error_tracker.alerts_triggered",
            tags={
                "rule_name": rule.name,
                "severity": rule.severity.value,
            },
        )
    
    async def _send_alert(
        self,
        channel: AlertChannel,
        rule: AlertRule,
        error_count: int,
        trigger_event: ErrorEvent,
    ):
        """Send alert to the specified channel."""
        try:
            if channel == AlertChannel.LOG:
                # Already handled in _trigger_alert
                pass
            elif channel == AlertChannel.WEBHOOK:
                await self._send_webhook_alert(rule, error_count, trigger_event)
            elif channel == AlertChannel.EMAIL:
                await self._send_email_alert(rule, error_count, trigger_event)
            elif channel == AlertChannel.SLACK:
                await self._send_slack_alert(rule, error_count, trigger_event)
            elif channel == AlertChannel.PAGERDUTY:
                await self._send_pagerduty_alert(rule, error_count, trigger_event)
        except Exception as e:
            self.logger.error(f"Failed to send alert via {channel.value}: {e}")
    
    async def _send_webhook_alert(
        self,
        rule: AlertRule,
        error_count: int,
        trigger_event: ErrorEvent,
    ):
        """Send alert via webhook."""
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if not webhook_url:
            return
        
        import aiohttp
        
        payload = {
            "alert": {
                "rule_name": rule.name,
                "severity": rule.severity.value,
                "error_count": error_count,
                "threshold": rule.threshold_count,
                "time_window": rule.time_window_seconds,
                "trigger_event": {
                    "error_code": trigger_event.error_code,
                    "status_code": trigger_event.status_code,
                    "message": trigger_event.message,
                    "timestamp": trigger_event.timestamp.isoformat(),
                    "request_id": trigger_event.request_id,
                    "trace_id": trigger_event.trace_id,
                },
                "service": "lorien-api",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    self.logger.error(f"Webhook alert failed: {response.status}")
    
    async def _send_email_alert(
        self,
        rule: AlertRule,
        error_count: int,
        trigger_event: ErrorEvent,
    ):
        """Send alert via email (placeholder)."""
        # Implementation would depend on email service (SendGrid, SES, etc.)
        self.logger.info(f"Email alert would be sent for rule: {rule.name}")
    
    async def _send_slack_alert(
        self,
        rule: AlertRule,
        error_count: int,
        trigger_event: ErrorEvent,
    ):
        """Send alert via Slack (placeholder)."""
        # Implementation would depend on Slack webhook
        self.logger.info(f"Slack alert would be sent for rule: {rule.name}")
    
    async def _send_pagerduty_alert(
        self,
        rule: AlertRule,
        error_count: int,
        trigger_event: ErrorEvent,
    ):
        """Send alert via PagerDuty (placeholder)."""
        # Implementation would depend on PagerDuty API
        self.logger.info(f"PagerDuty alert would be sent for rule: {rule.name}")
    
    def _update_health_status(self):
        """Update the overall health status based on recent errors."""
        current_time = datetime.now(UTC)
        recent_window = timedelta(minutes=5)
        recent_errors = [
            event for event in self._error_events
            if event.timestamp >= current_time - recent_window
        ]
        
        # Count errors by severity
        severity_counts = defaultdict(int)
        for event in recent_errors:
            severity_counts[event.severity] += 1
        
        # Determine health status
        if severity_counts[ErrorSeverity.CRITICAL] > 0:
            self._health_status = "critical"
        elif severity_counts[ErrorSeverity.HIGH] > 5:
            self._health_status = "unhealthy"
        elif severity_counts[ErrorSeverity.MEDIUM] > 20:
            self._health_status = "degraded"
        elif len(recent_errors) > 100:
            self._health_status = "degraded"
        else:
            self._health_status = "healthy"
        
        # Update health metric
        set_gauge(
            "error_tracker.health_status",
            value=1 if self._health_status == "healthy" else 0,
            tags={"status": self._health_status},
        )
    
    async def _health_monitoring_task(self):
        """Background task to monitor health status."""
        while True:
            try:
                self._update_health_status()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Health monitoring task error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _alert_processing_task(self):
        """Background task to process alerts."""
        while True:
            try:
                # Process any pending alerts
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                self.logger.error(f"Alert processing task error: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status and error statistics."""
        current_time = datetime.now(UTC)
        
        # Recent error counts (last 5 minutes)
        recent_window = timedelta(minutes=5)
        recent_errors = [
            event for event in self._error_events
            if event.timestamp >= current_time - recent_window
        ]
        
        # Count by severity
        severity_counts = defaultdict(int)
        error_code_counts = defaultdict(int)
        
        for event in recent_errors:
            severity_counts[event.severity] += 1
            error_code_counts[event.error_code] += 1
        
        return {
            "status": self._health_status,
            "last_check": self._last_health_check.isoformat(),
            "recent_errors": {
                "total": len(recent_errors),
                "by_severity": {k.value: v for k, v in severity_counts.items()},
                "by_code": dict(error_code_counts),
            },
            "total_errors_tracked": len(self._error_events),
            "active_alert_rules": len([r for r in self._alert_rules if r.enabled]),
        }
    
    def get_error_patterns(self, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent error patterns for analysis."""
        patterns = {}
        
        for error_code, events in self._error_patterns.items():
            recent_events = events[-limit:]
            patterns[error_code] = [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "status_code": event.status_code,
                    "message": event.message,
                    "severity": event.severity.value,
                    "request_id": event.request_id,
                    "trace_id": event.trace_id,
                    "context": event.context,
                }
                for event in recent_events
            ]
        
        return patterns


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


async def track_error(
    error_code: str,
    status_code: int,
    message: str,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
):
    """Track an error event using the global error tracker."""
    tracker = get_error_tracker()
    await tracker.track_error(error_code, status_code, message, severity, context)


def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    tracker = get_error_tracker()
    return tracker.get_health_status()


def get_error_patterns(limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
    """Get recent error patterns."""
    tracker = get_error_tracker()
    return tracker.get_error_patterns(limit)
