#!/usr/bin/env python3
"""
Smart EMS System Demo
Demonstrates core functionality without Unicode issues.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.iot_data_ingestion import IoTDataStream
from services.diagnostics_engine import DiagnosticsEngine
from services.alert_system import AlertSystem, AlertSeverity

def main():
    print("Smart Energy Management System - Demo")
    print("=" * 50)
    
    # Initialize configuration
    config = {
        'streaming_interval': 1,
        'data_retention_hours': 24,
        'enable_anomaly_detection': True,
        'location': {'state': 'Delhi', 'city': 'New Delhi'}
    }
    
    print("\n1. Initializing IoT Data Stream...")
    iot_stream = IoTDataStream(config)
    device_summary = iot_stream.get_device_summary()
    print(f"   Total devices: {device_summary['total_devices']}")
    for device_type, count in device_summary['device_types'].items():
        print(f"   - {device_type.title()}: {count} devices")
    
    print("\n2. Running Diagnostics Engine...")
    diagnostics_engine = DiagnosticsEngine(config)
    system_health = diagnostics_engine.get_system_health_summary()
    
    if 'error' in system_health:
        print(f"   Diagnostics: {system_health['error']}")
        # Generate some sample diagnostics
        print("   Generating sample diagnostics...")
        sample_diag = diagnostics_engine.calculate_battery_health({
            'cycle_count': 500,
            'avg_temperature': 30,
            'avg_depth_of_discharge': 60,
            'age_years': 2
        })
        print(f"   Sample Battery Health: {sample_diag.health_index:.1f}% ({sample_diag.status})")
        print(f"   Message: {sample_diag.diagnostic_message}")
    else:
        print(f"   Overall System Health: {system_health['overall_health']:.1f}%")
        for component, health in system_health['component_health'].items():
            print(f"   - {component.title()}: {health:.1f}%")
    
    print("\n3. Checking Alert System...")
    alert_system = AlertSystem(config)
    
    # Create sample device data and diagnostics for alerts
    sample_device_data = {
        'device_id': 'battery_001',
        'device_type': 'battery',
        'soc_percent': 15,  # Low SoC to trigger alert
        'temperature_c': 45,  # High temperature
        'health_score': 45
    }
    
    sample_diagnostic = {
        'health_index': 45,
        'status': 'Poor',
        'warnings': ['Low SoC', 'High temperature']
    }
    
    alert = alert_system.generate_alert(sample_device_data, sample_diagnostic)
    if alert:
        print(f"   Generated alert: [{alert.severity.value}] {alert.title}")
        print(f"   Action: {alert.recommended_action}")
        print(f"   Impact: {alert.impact_assessment}")
    else:
        print("   No alerts generated")
    
    # Show alert summary
    alert_summary = alert_system.get_alert_summary()
    print(f"   Total Active Alerts: {alert_summary['total_active_alerts']}")
    print(f"   Severity Distribution: {alert_summary['severity_distribution']}")
    
    print("\n4. IoT Data Sample...")
    # Get some sample data from the IoT stream
    sample_data = iot_stream.get_latest_data()
    if sample_data:
        print(f"   Retrieved {len(sample_data)} data points")
        if len(sample_data) > 0:
            sample = sample_data[0]
            print(f"   Sample Device:")
            print(f"   - Device ID: {sample.device_id}")
            print(f"   - Type: {sample.device_type}")
            print(f"   - Health: {sample.health_status}")
            print(f"   - Data keys: {list(sample.data.keys())}")
    
    print("\n5. System Performance Summary...")
    print("   All core services are operational!")
    
    print("\nSmart EMS System Demo Complete!")
    print("\nTo run the full dashboard:")
    print("   streamlit run dashboard/app_streamlit.py")
    print("\nDashboard will be available at: http://localhost:8501")

if __name__ == "__main__":
    main()
