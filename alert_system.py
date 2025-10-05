"""
Alert System with Severity Levels and Recommended Actions
Provides intelligent alerting with clear actions and impact assessment.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class Alert:
    """Alert data structure."""
    id: str
    timestamp: datetime
    severity: AlertSeverity
    component: str
    device_id: str
    title: str
    message: str
    recommended_action: str
    impact_assessment: str
    priority_score: int
    is_acknowledged: bool = False
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertSystem:
    """Intelligent alert system with severity levels and actionable recommendations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alerts = []
        self.alert_history = []
        self.alert_rules = self._initialize_alert_rules()
        
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize alert rules for different components."""
        return {
            'battery': {
                'soc_low': {'threshold': 20, 'severity': AlertSeverity.CRITICAL},
                'soc_critical': {'threshold': 10, 'severity': AlertSeverity.EMERGENCY},
                'temperature_high': {'threshold': 45, 'severity': AlertSeverity.WARNING},
                'temperature_critical': {'threshold': 55, 'severity': AlertSeverity.CRITICAL},
                'cycle_count_high': {'threshold': 5000, 'severity': AlertSeverity.WARNING},
                'efficiency_low': {'threshold': 85, 'severity': AlertSeverity.WARNING}
            },
            'solar_panel': {
                'efficiency_low': {'threshold': 15, 'severity': AlertSeverity.WARNING},
                'temperature_high': {'threshold': 60, 'severity': AlertSeverity.WARNING},
                'power_low': {'threshold': 0.5, 'severity': AlertSeverity.INFO},
                'irradiance_mismatch': {'threshold': 0.3, 'severity': AlertSeverity.WARNING}
            },
            'inverter': {
                'efficiency_low': {'threshold': 90, 'severity': AlertSeverity.WARNING},
                'temperature_high': {'threshold': 60, 'severity': AlertSeverity.CRITICAL},
                'frequency_deviation': {'threshold': 0.5, 'severity': AlertSeverity.WARNING},
                'voltage_deviation': {'threshold': 20, 'severity': AlertSeverity.WARNING}
            },
            'ev_charger': {
                'temperature_high': {'threshold': 50, 'severity': AlertSeverity.WARNING},
                'charging_failure': {'threshold': 0, 'severity': AlertSeverity.CRITICAL},
                'efficiency_low': {'threshold': 90, 'severity': AlertSeverity.WARNING}
            },
            'grid_connection': {
                'frequency_deviation': {'threshold': 0.5, 'severity': AlertSeverity.CRITICAL},
                'voltage_deviation': {'threshold': 25, 'severity': AlertSeverity.CRITICAL},
                'power_factor_low': {'threshold': 0.85, 'severity': AlertSeverity.WARNING},
                'connection_lost': {'threshold': 0, 'severity': AlertSeverity.EMERGENCY}
            }
        }
    
    def generate_alert(self, device_data: Dict[str, Any], diagnostic_result: Dict[str, Any]) -> Optional[Alert]:
        """Generate alert based on device data and diagnostic results."""
        device_type = device_data.get('device_type', '')
        device_id = device_data.get('device_id', '')
        
        if device_type not in self.alert_rules:
            return None
        
        rules = self.alert_rules[device_type]
        alerts_to_generate = []
        
        # Check battery alerts
        if device_type == 'battery':
            soc = device_data.get('soc', 50)
            temperature = device_data.get('temperature', 25)
            cycle_count = device_data.get('cycle_count', 0)
            health_score = device_data.get('health_score', 100)
            
            if soc <= rules['soc_critical']['threshold']:
                alerts_to_generate.append({
                    'rule': 'soc_critical',
                    'value': soc,
                    'threshold': rules['soc_critical']['threshold'],
                    'severity': rules['soc_critical']['severity']
                })
            elif soc <= rules['soc_low']['threshold']:
                alerts_to_generate.append({
                    'rule': 'soc_low',
                    'value': soc,
                    'threshold': rules['soc_low']['threshold'],
                    'severity': rules['soc_low']['severity']
                })
            
            if temperature >= rules['temperature_critical']['threshold']:
                alerts_to_generate.append({
                    'rule': 'temperature_critical',
                    'value': temperature,
                    'threshold': rules['temperature_critical']['threshold'],
                    'severity': rules['temperature_critical']['severity']
                })
            elif temperature >= rules['temperature_high']['threshold']:
                alerts_to_generate.append({
                    'rule': 'temperature_high',
                    'value': temperature,
                    'threshold': rules['temperature_high']['threshold'],
                    'severity': rules['temperature_high']['severity']
                })
            
            if cycle_count >= rules['cycle_count_high']['threshold']:
                alerts_to_generate.append({
                    'rule': 'cycle_count_high',
                    'value': cycle_count,
                    'threshold': rules['cycle_count_high']['threshold'],
                    'severity': rules['cycle_count_high']['severity']
                })
            
            if health_score <= rules['efficiency_low']['threshold']:
                alerts_to_generate.append({
                    'rule': 'efficiency_low',
                    'value': health_score,
                    'threshold': rules['efficiency_low']['threshold'],
                    'severity': rules['efficiency_low']['severity']
                })
        
        # Check solar panel alerts
        elif device_type == 'solar_panel':
            efficiency = device_data.get('efficiency', 18)
            temperature = device_data.get('module_temperature', 25)
            power = device_data.get('dc_power', 0)
            irradiance = device_data.get('irradiance', 0)
            
            if efficiency <= rules['efficiency_low']['threshold']:
                alerts_to_generate.append({
                    'rule': 'efficiency_low',
                    'value': efficiency,
                    'threshold': rules['efficiency_low']['threshold'],
                    'severity': rules['efficiency_low']['severity']
                })
            
            if temperature >= rules['temperature_high']['threshold']:
                alerts_to_generate.append({
                    'rule': 'temperature_high',
                    'value': temperature,
                    'threshold': rules['temperature_high']['threshold'],
                    'severity': rules['temperature_high']['severity']
                })
            
            if power <= rules['power_low']['threshold'] and irradiance > 500:
                alerts_to_generate.append({
                    'rule': 'power_low',
                    'value': power,
                    'threshold': rules['power_low']['threshold'],
                    'severity': rules['power_low']['severity']
                })
        
        # Check inverter alerts
        elif device_type == 'inverter':
            efficiency = device_data.get('efficiency', 96)
            temperature = device_data.get('temperature', 25)
            frequency = device_data.get('frequency', 50)
            voltage = device_data.get('voltage', 415)
            
            if efficiency <= rules['efficiency_low']['threshold']:
                alerts_to_generate.append({
                    'rule': 'efficiency_low',
                    'value': efficiency,
                    'threshold': rules['efficiency_low']['threshold'],
                    'severity': rules['efficiency_low']['severity']
                })
            
            if temperature >= rules['temperature_high']['threshold']:
                alerts_to_generate.append({
                    'rule': 'temperature_high',
                    'value': temperature,
                    'threshold': rules['temperature_high']['threshold'],
                    'severity': rules['temperature_high']['severity']
                })
            
            if abs(frequency - 50) >= rules['frequency_deviation']['threshold']:
                alerts_to_generate.append({
                    'rule': 'frequency_deviation',
                    'value': frequency,
                    'threshold': rules['frequency_deviation']['threshold'],
                    'severity': rules['frequency_deviation']['severity']
                })
            
            if abs(voltage - 415) >= rules['voltage_deviation']['threshold']:
                alerts_to_generate.append({
                    'rule': 'voltage_deviation',
                    'value': voltage,
                    'threshold': rules['voltage_deviation']['threshold'],
                    'severity': rules['voltage_deviation']['severity']
                })
        
        # Check EV charger alerts
        elif device_type == 'ev_charger':
            temperature = device_data.get('temperature', 25)
            is_charging = device_data.get('is_charging', False)
            charging_power = device_data.get('charging_power', 0)
            
            if temperature >= rules['temperature_high']['threshold']:
                alerts_to_generate.append({
                    'rule': 'temperature_high',
                    'value': temperature,
                    'threshold': rules['temperature_high']['threshold'],
                    'severity': rules['temperature_high']['severity']
                })
            
            if is_charging and charging_power == 0:
                alerts_to_generate.append({
                    'rule': 'charging_failure',
                    'value': 0,
                    'threshold': rules['charging_failure']['threshold'],
                    'severity': rules['charging_failure']['severity']
                })
        
        # Check grid connection alerts
        elif device_type == 'grid_connection':
            frequency = device_data.get('frequency', 50)
            voltage = device_data.get('voltage', 415)
            power_factor = device_data.get('power_factor', 0.95)
            
            if abs(frequency - 50) >= rules['frequency_deviation']['threshold']:
                alerts_to_generate.append({
                    'rule': 'frequency_deviation',
                    'value': frequency,
                    'threshold': rules['frequency_deviation']['threshold'],
                    'severity': rules['frequency_deviation']['severity']
                })
            
            if abs(voltage - 415) >= rules['voltage_deviation']['threshold']:
                alerts_to_generate.append({
                    'rule': 'voltage_deviation',
                    'value': voltage,
                    'threshold': rules['voltage_deviation']['threshold'],
                    'severity': rules['voltage_deviation']['severity']
                })
            
            if power_factor <= rules['power_factor_low']['threshold']:
                alerts_to_generate.append({
                    'rule': 'power_factor_low',
                    'value': power_factor,
                    'threshold': rules['power_factor_low']['threshold'],
                    'severity': rules['power_factor_low']['severity']
                })
        
        # Generate alerts
        generated_alerts = []
        for alert_data in alerts_to_generate:
            alert = self._create_alert(device_data, alert_data)
            if alert:
                generated_alerts.append(alert)
        
        return generated_alerts[0] if generated_alerts else None
    
    def _create_alert(self, device_data: Dict[str, Any], alert_data: Dict[str, Any]) -> Alert:
        """Create alert with detailed message and recommendations."""
        device_type = device_data.get('device_type', '')
        device_id = device_data.get('device_id', '')
        rule = alert_data['rule']
        value = alert_data['value']
        threshold = alert_data['threshold']
        severity = alert_data['severity']
        
        # Generate alert ID
        alert_id = f"{device_id}_{rule}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create title and message
        title, message, action, impact = self._generate_alert_content(
            device_type, rule, value, threshold, severity
        )
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(severity, device_type, rule)
        
        return Alert(
            id=alert_id,
            timestamp=datetime.now(),
            severity=severity,
            component=device_type.replace('_', ' ').title(),
            device_id=device_id,
            title=title,
            message=message,
            recommended_action=action,
            impact_assessment=impact,
            priority_score=priority_score
        )
    
    def _generate_alert_content(self, device_type: str, rule: str, value: float, 
                              threshold: float, severity: AlertSeverity) -> tuple:
        """Generate alert title, message, action, and impact."""
        
        if device_type == 'battery':
            if rule == 'soc_critical':
                title = "Battery SoC Critical"
                message = f"Battery SoC critical: {value:.1f}% (Threshold: {threshold}%)"
                action = "Switch load to grid immediately. Reduce non-critical loads. Check battery connections."
                impact = "Battery deep discharge can reduce lifespan by 10-15%. Risk of system shutdown."
            elif rule == 'soc_low':
                title = "Battery SoC Low"
                message = f"Battery SoC low: {value:.1f}% (Threshold: {threshold}%)"
                action = "Monitor closely. Consider reducing load or switching to grid power."
                impact = "Continued low SoC may lead to deep discharge and battery damage."
            elif rule == 'temperature_critical':
                title = "Battery Temperature Critical"
                message = f"Battery temperature critical: {value:.1f}°C (Threshold: {threshold}°C)"
                action = "Immediate cooling required. Reduce charging rate. Check ventilation system."
                impact = "High temperature can cause thermal runaway and permanent damage."
            elif rule == 'temperature_high':
                title = "Battery Temperature High"
                message = f"Battery temperature high: {value:.1f}°C (Threshold: {threshold}°C)"
                action = "Monitor temperature. Ensure proper ventilation. Consider reducing charging rate."
                impact = "High temperature reduces battery efficiency and lifespan."
            elif rule == 'cycle_count_high':
                title = "Battery Cycle Count High"
                message = f"Battery cycle count high: {value} cycles (Threshold: {threshold})"
                action = "Plan for battery replacement. Monitor performance degradation."
                impact = "High cycle count indicates approaching end of useful life."
            elif rule == 'efficiency_low':
                title = "Battery Health Low"
                message = f"Battery health low: {value:.1f}% (Threshold: {threshold}%)"
                action = "Schedule battery health assessment. Consider replacement planning."
                impact = "Low health indicates significant degradation and reduced capacity."
        
        elif device_type == 'solar_panel':
            if rule == 'efficiency_low':
                title = "Solar Panel Efficiency Low"
                message = f"Solar panel efficiency low: {value:.1f}% (Threshold: {threshold}%)"
                action = "Schedule panel cleaning and inspection. Check for shading or damage."
                impact = "Low efficiency reduces energy generation and system ROI."
            elif rule == 'temperature_high':
                title = "Solar Panel Temperature High"
                message = f"Solar panel temperature high: {value:.1f}°C (Threshold: {threshold}°C)"
                action = "Check ventilation. Consider cooling measures. Monitor performance."
                impact = "High temperature reduces panel efficiency and can cause damage."
            elif rule == 'power_low':
                title = "Solar Generation Low"
                message = f"Solar generation low: {value:.1f} kW despite good irradiance"
                action = "Check panel connections. Inspect for damage or shading."
                impact = "Low generation reduces system performance and energy savings."
        
        elif device_type == 'inverter':
            if rule == 'efficiency_low':
                title = "Inverter Efficiency Low"
                message = f"Inverter efficiency low: {value:.1f}% (Threshold: {threshold}%)"
                action = "Schedule inverter maintenance. Check cooling system and connections."
                impact = "Low efficiency reduces energy conversion and increases losses."
            elif rule == 'temperature_high':
                title = "Inverter Temperature High"
                message = f"Inverter temperature high: {value:.1f}°C (Threshold: {threshold}°C)"
                action = "Check cooling system. Ensure proper ventilation. Reduce load if necessary."
                impact = "High temperature can cause inverter failure and system shutdown."
            elif rule == 'frequency_deviation':
                title = "Inverter Frequency Deviation"
                message = f"Inverter frequency deviation: {value:.2f} Hz (Expected: 50.0 Hz)"
                action = "Check inverter settings. Monitor grid frequency. Contact technician if persistent."
                impact = "Frequency deviation can affect connected equipment and grid stability."
            elif rule == 'voltage_deviation':
                title = "Inverter Voltage Deviation"
                message = f"Inverter voltage deviation: {value:.1f} V (Expected: 415 V)"
                action = "Check inverter settings. Monitor grid voltage. Contact technician if persistent."
                impact = "Voltage deviation can damage connected equipment."
        
        elif device_type == 'ev_charger':
            if rule == 'temperature_high':
                title = "EV Charger Temperature High"
                message = f"EV charger temperature high: {value:.1f}°C (Threshold: {threshold}°C)"
                action = "Check ventilation. Reduce charging rate. Monitor temperature."
                impact = "High temperature can cause charger failure and safety issues."
            elif rule == 'charging_failure':
                title = "EV Charging Failure"
                message = "EV charger shows charging status but no power output"
                action = "Check charger connections. Restart charger. Contact technician if issue persists."
                impact = "Charging failure prevents EV charging and reduces system utilization."
        
        elif device_type == 'grid_connection':
            if rule == 'frequency_deviation':
                title = "Grid Frequency Deviation"
                message = f"Grid frequency deviation: {value:.2f} Hz (Expected: 50.0 Hz)"
                action = "Monitor grid stability. Consider backup power activation. Contact utility provider."
                impact = "Frequency deviation can affect system stability and connected equipment."
            elif rule == 'voltage_deviation':
                title = "Grid Voltage Deviation"
                message = f"Grid voltage deviation: {value:.1f} V (Expected: 415 V)"
                action = "Monitor grid voltage. Contact utility provider for voltage regulation."
                impact = "Voltage deviation can damage equipment and affect system performance."
            elif rule == 'power_factor_low':
                title = "Grid Power Factor Low"
                message = f"Grid power factor low: {value:.3f} (Threshold: {threshold})"
                action = "Consider power factor correction equipment. Check load characteristics."
                impact = "Low power factor increases energy costs and reduces system efficiency."
        
        else:
            title = "System Alert"
            message = f"Alert triggered for {device_type}: {rule}"
            action = "Monitor system and contact technician if needed."
            impact = "System performance may be affected."
        
        return title, message, action, impact
    
    def _calculate_priority_score(self, severity: AlertSeverity, device_type: str, rule: str) -> int:
        """Calculate priority score for alert prioritization."""
        base_scores = {
            AlertSeverity.INFO: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.CRITICAL: 3,
            AlertSeverity.EMERGENCY: 4
        }
        
        base_score = base_scores[severity]
        
        # Device type multipliers
        device_multipliers = {
            'battery': 1.2,
            'grid_connection': 1.1,
            'inverter': 1.0,
            'solar_panel': 0.9,
            'ev_charger': 0.8
        }
        
        # Rule-specific multipliers
        rule_multipliers = {
            'soc_critical': 1.5,
            'temperature_critical': 1.3,
            'connection_lost': 1.4,
            'charging_failure': 1.2,
            'frequency_deviation': 1.1,
            'voltage_deviation': 1.1
        }
        
        device_mult = device_multipliers.get(device_type, 1.0)
        rule_mult = rule_multipliers.get(rule, 1.0)
        
        return int(base_score * device_mult * rule_mult)
    
    def add_alert(self, alert: Alert):
        """Add alert to the system."""
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts in history
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.is_acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.is_resolved = True
                alert.resolved_at = datetime.now()
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.alerts if not alert.is_resolved]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level."""
        return [alert for alert in self.alerts if alert.severity == severity and not alert.is_resolved]
    
    def prioritize_alerts(self) -> List[Alert]:
        """Prioritize alerts by priority score and severity."""
        active_alerts = self.get_active_alerts()
        return sorted(active_alerts, key=lambda x: (x.priority_score, x.severity.value), reverse=True)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary."""
        active_alerts = self.get_active_alerts()
        
        severity_counts = {
            'info': len(self.get_alerts_by_severity(AlertSeverity.INFO)),
            'warning': len(self.get_alerts_by_severity(AlertSeverity.WARNING)),
            'critical': len(self.get_alerts_by_severity(AlertSeverity.CRITICAL)),
            'emergency': len(self.get_alerts_by_severity(AlertSeverity.EMERGENCY))
        }
        
        component_counts = {}
        for alert in active_alerts:
            component = alert.component
            component_counts[component] = component_counts.get(component, 0) + 1
        
        return {
            'total_active_alerts': len(active_alerts),
            'severity_distribution': severity_counts,
            'component_distribution': component_counts,
            'highest_priority': active_alerts[0] if active_alerts else None,
            'last_update': datetime.now()
        }
    
    def cleanup_old_alerts(self, hours: int = 24):
        """Remove old resolved alerts."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.alerts = [alert for alert in self.alerts 
                      if not alert.is_resolved or alert.resolved_at > cutoff_time]

