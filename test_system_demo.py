#!/usr/bin/env python3
"""
Smart EMS System Demo
Demonstrates the core functionality of the Smart Energy Management System.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.iot_data_ingestion import IoTDataStream
from services.diagnostics_engine import DiagnosticsEngine
from services.alert_system import AlertSystem, AlertSeverity
from services.location_intelligence import LocationIntelligence
import json

def main():
    print("🌞 Smart Energy Management System - Demo")
    print("=" * 50)
    
    # Initialize configuration
    config = {
        'streaming_interval': 1,
        'data_retention_hours': 24,
        'enable_anomaly_detection': True,
        'location': {'state': 'Delhi', 'city': 'New Delhi'}
    }
    
    print("\n1. 🔌 Initializing IoT Data Stream...")
    iot_stream = IoTDataStream(config)
    device_summary = iot_stream.get_device_summary()
    print(f"   Connected devices: {sum(d['count'] for d in device_summary.values())}")
    for device_type, info in device_summary.items():
        print(f"   - {device_type.title()}: {info['count']} devices, {info['average_health']:.1f}% health")
    
    print("\n2. 🔍 Running Diagnostics Engine...")
    diagnostics_engine = DiagnosticsEngine(config)
    system_health = diagnostics_engine.get_system_health_summary()
    print(f"   Overall System Health: {system_health['overall_health_index']:.1f}% ({system_health['overall_status']})")
    
    for component, diag in system_health['component_diagnostics'].items():
        print(f"   - {component.title()}: {diag['health_index']:.1f}% ({diag['status']})")
        print(f"     Message: {diag['message']}")
        if diag['warnings']:
            print(f"     Warnings: {', '.join(diag['warnings'])}")
    
    print("\n3. 🚨 Checking Alert System...")
    alert_system = AlertSystem(config)
    alerts = alert_system.check_for_alerts(system_health['component_diagnostics'])
    print(f"   Generated {len(alerts)} alerts")
    
    for alert in alerts:
        print(f"   - [{alert.severity.value}] {alert.title}")
        print(f"     Action: {alert.recommended_action}")
        print(f"     Impact: {alert.impact}")
    
    print("\n4. 📍 Location Intelligence...")
    location_service = LocationIntelligence(config)
    location_data = location_service.get_location_details("Delhi", "New Delhi")
    print(f"   Location: {location_data.state}, {location_data.city}")
    print(f"   Electricity Tariff: ₹{location_data.electricity_tariff}/kWh")
    print(f"   Solar Potential: {location_data.solar_potential} kWh/kWp/day")
    print(f"   Carbon Intensity: {location_data.carbon_intensity} gCO2/kWh")
    print(f"   Renewable %: {location_data.renewable_percentage}%")
    
    print("\n5. 📊 Generating Location-based Forecast...")
    forecast = location_service.generate_location_based_forecast(location_data, hours=6)
    print(f"   Generated {len(forecast['location_forecast'])} hour forecast")
    for i, hour_data in enumerate(forecast['location_forecast'][:3]):
        print(f"   Hour {i+1}: Solar {hour_data['predicted_solar_kw']:.1f}kW, "
              f"Load {hour_data['predicted_load_kw']:.1f}kW, "
              f"Price ₹{hour_data['predicted_price_per_kwh']:.2f}/kWh")
    
    print("\n6. 🎯 System Performance Summary...")
    alert_summary = alert_system.get_alert_summary()
    print(f"   Active Alerts: {alert_summary['active_alerts_count']}")
    print(f"   Critical Alerts: {alert_summary['critical_alerts_count']}")
    print(f"   Warning Alerts: {alert_summary['warning_alerts_count']}")
    
    print("\n✅ Smart EMS System Demo Complete!")
    print("\n🚀 To run the full dashboard:")
    print("   streamlit run dashboard/app_streamlit.py")
    print("\n📱 Dashboard will be available at: http://localhost:8501")

if __name__ == "__main__":
    main()
