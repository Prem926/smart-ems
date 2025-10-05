"""
Intelligent Diagnostics Engine
Provides clear, actionable diagnostic insights for all EMS subsystems.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DiagnosticResult:
    """Diagnostic result with clear messages and recommendations."""
    component: str
    health_index: float
    status: str
    diagnostic_message: str
    warnings: List[str]
    recommendations: List[str]
    root_cause_analysis: Dict[str, float]
    expected_lifespan: Optional[str] = None

class DiagnosticsEngine:
    """Diagnoses health and performance of EMS components with clear messages."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.diagnostic_history = []
        
    def calculate_battery_health(self, device_data: Dict[str, Any]) -> DiagnosticResult:
        """Calculate battery health with detailed diagnostics."""
        soc = device_data.get('soc', 50)
        temperature = device_data.get('temperature', 25)
        cycle_count = device_data.get('cycle_count', 0)
        age_years = device_data.get('age_years', 0)
        
        # Health index calculation
        cycle_penalty = min(1.0, cycle_count / 6000) * 100
        temp_penalty = max(0, abs(temperature - 25) / 20) * 100
        dod_penalty = max(0, (50 - soc) / 50) * 100
        age_penalty = min(1.0, age_years / 15) * 100
        
        health_index = 100 - (0.2 * cycle_penalty + 0.3 * temp_penalty + 0.3 * dod_penalty + 0.2 * age_penalty)
        
        # Status determination
        if health_index >= 90:
            status = "Excellent"
        elif health_index >= 75:
            status = "Good"
        elif health_index >= 60:
            status = "Fair"
        elif health_index >= 40:
            status = "Poor"
        else:
            status = "Critical"
        
        # Diagnostic message
        if status == "Excellent":
            message = f"Battery health: {health_index:.1f}% (Excellent). All parameters within optimal ranges. Continue normal operation."
        elif status == "Good":
            message = f"Battery health: {health_index:.1f}% (Good). Minor degradation observed. Monitor temperature and cycling patterns."
        elif status == "Fair":
            message = f"Battery health: {health_index:.1f}% (Fair). Moderate degradation detected. Consider preventive maintenance."
        elif status == "Poor":
            message = f"Battery health: {health_index:.1f}% (Poor). Significant degradation. Schedule maintenance within 30 days."
        else:
            message = f"Battery health: {health_index:.1f}% (Critical). Immediate attention required. Risk of failure within 6 months."
        
        # Warnings
        warnings = []
        if temperature > 35:
            warnings.append(f"High temperature: {temperature:.1f}°C (Optimal: 25°C). Heat exposure reduces lifespan by 2-3% per 10°C above optimal.")
        if cycle_count > 4000:
            warnings.append(f"High cycle count: {cycle_count} cycles. Approaching 80% of expected lifespan.")
        if soc < 20:
            warnings.append(f"Low state of charge: {soc:.1f}%. Deep discharge can reduce lifespan by 10-15%.")
        
        # Recommendations
        recommendations = []
        if temperature > 35:
            recommendations.append("Install additional cooling or relocate to shaded area.")
        if cycle_count > 4000:
            recommendations.append("Plan for battery replacement within 12-18 months.")
        if soc < 20:
            recommendations.append("Switch load to grid immediately. Reduce non-critical loads.")
        if health_index < 60:
            recommendations.append("Schedule comprehensive battery health assessment.")
        
        # Root cause analysis
        root_causes = {
            'thermal_stress': temp_penalty / 100,
            'cycling_degradation': cycle_penalty / 100,
            'deep_discharge': dod_penalty / 100,
            'age_related': age_penalty / 100
        }
        
        # Expected lifespan
        remaining_life = max(0, 15 - age_years - (cycle_count / 400))
        expected_lifespan = f"{remaining_life:.1f} years" if remaining_life > 0 else "End of life"
        
        return DiagnosticResult(
            component="Battery",
            health_index=health_index,
            status=status,
            diagnostic_message=message,
            warnings=warnings,
            recommendations=recommendations,
            root_cause_analysis=root_causes,
            expected_lifespan=expected_lifespan
        )
    
    def calculate_solar_health(self, device_data: Dict[str, Any]) -> DiagnosticResult:
        """Calculate solar panel health with detailed diagnostics."""
        efficiency = device_data.get('efficiency', 18)
        temperature = device_data.get('module_temperature', 25)
        power = device_data.get('dc_power', 0)
        irradiance = device_data.get('irradiance', 0)
        age_years = device_data.get('age_years', 0)
        
        # Health index calculation
        expected_efficiency = 18 * (1 - age_years * 0.005)  # 0.5% degradation per year
        efficiency_penalty = max(0, (expected_efficiency - efficiency) / expected_efficiency) * 100
        temp_penalty = max(0, (temperature - 25) / 30) * 100
        age_penalty = min(1.0, age_years / 25) * 100
        
        health_index = 100 - (0.5 * efficiency_penalty + 0.3 * temp_penalty + 0.2 * age_penalty)
        
        # Status determination
        status = self._get_status_from_health(health_index)
        
        # Diagnostic message
        if efficiency < expected_efficiency * 0.9:
            message = f"Solar panel efficiency: {efficiency:.1f}% (Expected: {expected_efficiency:.1f}%). Likely cause: Dust accumulation on panels (70% probability). Recommendation: Schedule cleaning maintenance within 7 days to prevent further 2-3% efficiency loss."
        else:
            message = f"Solar panel health: {health_index:.1f}% ({status}). Performance within expected range. Continue normal operation."
        
        # Warnings and recommendations
        warnings, recommendations = self._get_solar_warnings_recommendations(
            efficiency, temperature, age_years, expected_efficiency
        )
        
        return DiagnosticResult(
            component="Solar Panel",
            health_index=health_index,
            status=status,
            diagnostic_message=message,
            warnings=warnings,
            recommendations=recommendations,
            root_cause_analysis={
                'efficiency_loss': efficiency_penalty / 100,
                'thermal_stress': temp_penalty / 100,
                'age_degradation': age_penalty / 100
            }
        )
    
    def calculate_inverter_health(self, device_data: Dict[str, Any]) -> DiagnosticResult:
        """Calculate inverter health with detailed diagnostics."""
        efficiency = device_data.get('efficiency', 96)
        temperature = device_data.get('temperature', 25)
        age_years = device_data.get('age_years', 0)
        
        # Health index calculation
        expected_efficiency = 96 * (1 - age_years * 0.002)
        efficiency_penalty = max(0, (expected_efficiency - efficiency) / expected_efficiency) * 100
        temp_penalty = max(0, (temperature - 25) / 20) * 100
        age_penalty = min(1.0, age_years / 15) * 100
        
        health_index = 100 - (0.4 * efficiency_penalty + 0.3 * temp_penalty + 0.3 * age_penalty)
        
        status = self._get_status_from_health(health_index)
        
        # Diagnostic message
        if efficiency < expected_efficiency * 0.95:
            message = f"Inverter efficiency dropped {expected_efficiency - efficiency:.1f}% in last week. Likely cause: Dust accumulation on heat sinks (70% probability). Recommendation: Schedule cleaning maintenance within 7 days to prevent further 2-3% efficiency loss."
        else:
            message = f"Inverter health: {health_index:.1f}% ({status}). Performance within expected range."
        
        warnings, recommendations = self._get_inverter_warnings_recommendations(
            efficiency, temperature, age_years, expected_efficiency
        )
        
        return DiagnosticResult(
            component="Inverter",
            health_index=health_index,
            status=status,
            diagnostic_message=message,
            warnings=warnings,
            recommendations=recommendations,
            root_cause_analysis={
                'efficiency_loss': efficiency_penalty / 100,
                'thermal_stress': temp_penalty / 100,
                'age_degradation': age_penalty / 100
            }
        )
    
    def calculate_ev_charger_health(self, device_data: Dict[str, Any]) -> DiagnosticResult:
        """Calculate EV charger health with detailed diagnostics."""
        temperature = device_data.get('temperature', 25)
        age_years = device_data.get('age_years', 0)
        is_charging = device_data.get('is_charging', False)
        charging_power = device_data.get('charging_power', 0)
        
        # Health index calculation
        temp_penalty = max(0, (temperature - 25) / 15) * 100
        age_penalty = min(1.0, age_years / 10) * 100
        usage_penalty = 0 if is_charging else 10  # Penalty for not being used
        
        health_index = 100 - (0.4 * temp_penalty + 0.4 * age_penalty + 0.2 * usage_penalty)
        
        status = self._get_status_from_health(health_index)
        
        # Diagnostic message
        if temperature > 40:
            message = f"EV charger temperature: {temperature:.1f}°C (High). Likely cause: Poor ventilation or high ambient temperature. Recommendation: Check ventilation and consider thermal management upgrade."
        elif not is_charging and age_years > 3:
            message = f"EV charger health: {health_index:.1f}% ({status}). No recent usage detected. Consider maintenance check."
        else:
            message = f"EV charger health: {health_index:.1f}% ({status}). Operating normally."
        
        warnings, recommendations = self._get_ev_charger_warnings_recommendations(
            temperature, age_years, is_charging
        )
        
        return DiagnosticResult(
            component="EV Charger",
            health_index=health_index,
            status=status,
            diagnostic_message=message,
            warnings=warnings,
            recommendations=recommendations,
            root_cause_analysis={
                'thermal_stress': temp_penalty / 100,
                'age_degradation': age_penalty / 100,
                'underutilization': usage_penalty / 100
            }
        )
    
    def calculate_grid_health(self, device_data: Dict[str, Any]) -> DiagnosticResult:
        """Calculate grid connection health with detailed diagnostics."""
        frequency = device_data.get('frequency', 50)
        voltage = device_data.get('voltage', 415)
        power_factor = device_data.get('power_factor', 0.95)
        
        # Health index calculation
        freq_penalty = max(0, abs(frequency - 50) / 0.5) * 100
        voltage_penalty = max(0, abs(voltage - 415) / 20) * 100
        pf_penalty = max(0, (0.95 - power_factor) / 0.1) * 100
        
        health_index = 100 - (0.4 * freq_penalty + 0.4 * voltage_penalty + 0.2 * pf_penalty)
        
        status = self._get_status_from_health(health_index)
        
        # Diagnostic message
        if abs(frequency - 50) > 0.2:
            message = f"Grid frequency deviation: {frequency:.2f} Hz (Expected: 50.0 Hz). Likely cause: Grid instability or load imbalance. Recommendation: Monitor grid conditions and consider backup power activation."
        elif abs(voltage - 415) > 15:
            message = f"Grid voltage deviation: {voltage:.1f} V (Expected: 415 V). Likely cause: Grid voltage regulation issues. Recommendation: Contact utility provider for voltage regulation check."
        else:
            message = f"Grid connection health: {health_index:.1f}% ({status}). Grid parameters within acceptable range."
        
        warnings, recommendations = self._get_grid_warnings_recommendations(
            frequency, voltage, power_factor
        )
        
        return DiagnosticResult(
            component="Grid Connection",
            health_index=health_index,
            status=status,
            diagnostic_message=message,
            warnings=warnings,
            recommendations=recommendations,
            root_cause_analysis={
                'frequency_deviation': freq_penalty / 100,
                'voltage_deviation': voltage_penalty / 100,
                'power_factor': pf_penalty / 100
            }
        )
    
    def _get_status_from_health(self, health_index: float) -> str:
        """Convert health index to status string."""
        if health_index >= 90:
            return "Excellent"
        elif health_index >= 75:
            return "Good"
        elif health_index >= 60:
            return "Fair"
        elif health_index >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def _get_solar_warnings_recommendations(self, efficiency: float, temperature: float, 
                                          age_years: float, expected_efficiency: float) -> Tuple[List[str], List[str]]:
        """Get warnings and recommendations for solar panels."""
        warnings = []
        recommendations = []
        
        if efficiency < expected_efficiency * 0.9:
            warnings.append(f"Efficiency below expected: {efficiency:.1f}% vs {expected_efficiency:.1f}%")
            recommendations.append("Schedule panel cleaning and inspection")
        
        if temperature > 45:
            warnings.append(f"High module temperature: {temperature:.1f}°C")
            recommendations.append("Check ventilation and consider cooling measures")
        
        if age_years > 15:
            warnings.append(f"Panels aging: {age_years:.1f} years old")
            recommendations.append("Plan for panel replacement assessment")
        
        return warnings, recommendations
    
    def _get_inverter_warnings_recommendations(self, efficiency: float, temperature: float,
                                             age_years: float, expected_efficiency: float) -> Tuple[List[str], List[str]]:
        """Get warnings and recommendations for inverters."""
        warnings = []
        recommendations = []
        
        if efficiency < expected_efficiency * 0.95:
            warnings.append(f"Inverter efficiency below expected: {efficiency:.1f}%")
            recommendations.append("Schedule inverter maintenance and cleaning")
        
        if temperature > 50:
            warnings.append(f"High inverter temperature: {temperature:.1f}°C")
            recommendations.append("Check cooling system and ventilation")
        
        if age_years > 10:
            warnings.append(f"Inverter aging: {age_years:.1f} years old")
            recommendations.append("Plan for inverter replacement assessment")
        
        return warnings, recommendations
    
    def _get_ev_charger_warnings_recommendations(self, temperature: float, age_years: float,
                                               is_charging: bool) -> Tuple[List[str], List[str]]:
        """Get warnings and recommendations for EV chargers."""
        warnings = []
        recommendations = []
        
        if temperature > 40:
            warnings.append(f"High charger temperature: {temperature:.1f}°C")
            recommendations.append("Check ventilation and thermal management")
        
        if age_years > 5:
            warnings.append(f"Charger aging: {age_years:.1f} years old")
            recommendations.append("Schedule preventive maintenance")
        
        if not is_charging and age_years > 2:
            warnings.append("No recent charging activity detected")
            recommendations.append("Test charger functionality")
        
        return warnings, recommendations
    
    def _get_grid_warnings_recommendations(self, frequency: float, voltage: float,
                                         power_factor: float) -> Tuple[List[str], List[str]]:
        """Get warnings and recommendations for grid connection."""
        warnings = []
        recommendations = []
        
        if abs(frequency - 50) > 0.2:
            warnings.append(f"Frequency deviation: {frequency:.2f} Hz")
            recommendations.append("Monitor grid stability and consider backup power")
        
        if abs(voltage - 415) > 15:
            warnings.append(f"Voltage deviation: {voltage:.1f} V")
            recommendations.append("Contact utility provider for voltage regulation")
        
        if power_factor < 0.9:
            warnings.append(f"Low power factor: {power_factor:.3f}")
            recommendations.append("Consider power factor correction equipment")
        
        return warnings, recommendations
    
    def diagnose_all_components(self, iot_data: List[Dict[str, Any]]) -> List[DiagnosticResult]:
        """Diagnose all components from IoT data."""
        results = []
        
        for device_data in iot_data:
            device_type = device_data.get('device_type', '')
            
            try:
                if device_type == 'battery':
                    result = self.calculate_battery_health(device_data)
                elif device_type == 'solar_panel':
                    result = self.calculate_solar_health(device_data)
                elif device_type == 'inverter':
                    result = self.calculate_inverter_health(device_data)
                elif device_type == 'ev_charger':
                    result = self.calculate_ev_charger_health(device_data)
                elif device_type == 'grid_connection':
                    result = self.calculate_grid_health(device_data)
                else:
                    continue
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error diagnosing {device_type}: {e}")
                continue
        
        # Store in history
        self.diagnostic_history.extend(results)
        if len(self.diagnostic_history) > 1000:
            self.diagnostic_history = self.diagnostic_history[-1000:]
        
        return results
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        if not self.diagnostic_history:
            return {"error": "No diagnostic data available"}
        
        recent_diagnostics = [d for d in self.diagnostic_history 
                            if (datetime.now() - d.timestamp).seconds < 300]  # Last 5 minutes
        
        if not recent_diagnostics:
            return {"error": "No recent diagnostic data"}
        
        # Calculate average health indices
        component_health = {}
        for diagnostic in recent_diagnostics:
            component = diagnostic.component
            if component not in component_health:
                component_health[component] = []
            component_health[component].append(diagnostic.health_index)
        
        # Calculate averages
        avg_health = {}
        for component, health_scores in component_health.items():
            avg_health[component] = np.mean(health_scores)
        
        # Overall system health
        overall_health = np.mean(list(avg_health.values())) if avg_health else 0
        
        return {
            'overall_health': round(overall_health, 1),
            'component_health': {k: round(v, 1) for k, v in avg_health.items()},
            'total_components': len(avg_health),
            'last_update': datetime.now(),
            'status': self._get_status_from_health(overall_health)
        }
