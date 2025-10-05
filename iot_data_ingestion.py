"""
IoT Data Ingestion Service
Simulates real-time IoT data streams from 50 devices across the EMS system.
Provides realistic synthetic data with proper patterns and noise.
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
import logging
from dataclasses import dataclass, asdict
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IoTDeviceData:
    """Data structure for IoT device readings"""
    device_id: str
    device_type: str
    timestamp: datetime
    location: str
    data: Dict[str, Any]
    health_status: str
    battery_level: Optional[float] = None

class IoTDataStream:
    """
    Simulates IoT data streams from various EMS devices.
    Generates realistic data patterns with proper temporal correlations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize IoT data stream with configuration."""
        self.config = config
        self.devices = self._initialize_devices()
        self.data_history = []
        self.current_time = datetime.now()
        
        # Device parameters for realistic simulation
        self.solar_params = {
            'base_capacity': 500,  # kW
            'efficiency': 0.18,
            'temp_coefficient': -0.004,  # per °C
            'degradation_rate': 0.005  # per year
        }
        
        self.battery_params = {
            'capacity': 1000,  # kWh
            'efficiency': 0.92,
            'max_charge_rate': 200,  # kW
            'max_discharge_rate': 200,  # kW
            'cycle_life': 6000,
            'temp_optimum': 25  # °C
        }
        
        self.inverter_params = {
            'efficiency': 0.96,
            'max_power': 500,  # kW
            'temp_coefficient': -0.002
        }
        
        self.ev_charger_params = {
            'max_power': 50,  # kW per charger
            'efficiency': 0.95,
            'num_chargers': 20
        }
        
        self.grid_params = {
            'base_frequency': 50.0,  # Hz
            'base_voltage': 415,  # V
            'price_range': (0.05, 0.25)  # ₹/kWh
        }
    
    def _initialize_devices(self) -> List[Dict[str, Any]]:
        """Initialize 50 IoT devices across the system."""
        devices = []
        
        # Solar panels (15 devices)
        for i in range(15):
            devices.append({
                'device_id': f'SP_{i+1:03d}',
                'device_type': 'solar_panel',
                'location': f'Array_{i//3 + 1}',
                'capacity': 33.3,  # kW per panel
                'age_years': random.uniform(0, 10),
                'orientation': random.choice(['South', 'South-East', 'South-West']),
                'tilt': random.uniform(20, 35)
            })
        
        # Battery systems (5 devices)
        for i in range(5):
            devices.append({
                'device_id': f'BAT_{i+1:03d}',
                'device_type': 'battery',
                'location': f'Battery_Rack_{i+1}',
                'capacity': 200,  # kWh per rack
                'age_years': random.uniform(0, 8),
                'chemistry': random.choice(['Li-ion', 'LiFePO4']),
                'cycle_count': random.randint(100, 3000)
            })
        
        # Inverters (8 devices)
        for i in range(8):
            devices.append({
                'device_id': f'INV_{i+1:03d}',
                'device_type': 'inverter',
                'location': f'Inverter_Bay_{i+1}',
                'capacity': 62.5,  # kW per inverter
                'age_years': random.uniform(0, 12),
                'manufacturer': random.choice(['SMA', 'Fronius', 'Huawei', 'Sungrow'])
            })
        
        # EV Chargers (20 devices)
        for i in range(20):
            devices.append({
                'device_id': f'EVC_{i+1:03d}',
                'device_type': 'ev_charger',
                'location': f'Charging_Station_{i//4 + 1}',
                'capacity': 50,  # kW per charger
                'age_years': random.uniform(0, 5),
                'connector_type': random.choice(['CCS', 'CHAdeMO', 'Type2'])
            })
        
        # Grid connection points (2 devices)
        for i in range(2):
            devices.append({
                'device_id': f'GRID_{i+1:03d}',
                'device_type': 'grid_connection',
                'location': f'Grid_Point_{i+1}',
                'capacity': 1000,  # kW
                'age_years': random.uniform(5, 20),
                'voltage_level': '415V'
            })
        
        return devices
    
    async def generate_solar_stream(self, device: Dict[str, Any]) -> IoTDeviceData:
        """Generate realistic solar panel data stream."""
        # Get current weather conditions (simplified)
        hour = self.current_time.hour
        day_of_year = self.current_time.timetuple().tm_yday
        
        # Solar irradiance calculation (simplified)
        solar_angle = self._calculate_solar_angle(hour, day_of_year)
        base_irradiance = max(0, 1000 * np.sin(np.radians(solar_angle)))
        
        # Add weather effects
        cloud_factor = random.uniform(0.3, 1.0)
        irradiance = base_irradiance * cloud_factor
        
        # Temperature effects
        ambient_temp = 25 + 10 * np.sin(2 * np.pi * hour / 24) + random.uniform(-5, 5)
        module_temp = ambient_temp + irradiance * 0.03
        
        # Power calculation
        temp_factor = 1 + self.solar_params['temp_coefficient'] * (module_temp - 25)
        degradation_factor = 1 - self.solar_params['degradation_rate'] * device['age_years']
        efficiency = self.solar_params['efficiency'] * temp_factor * degradation_factor
        
        dc_power = irradiance * device['capacity'] * efficiency / 1000  # kW
        dc_voltage = 400 + random.uniform(-20, 20)  # V
        dc_current = dc_power * 1000 / dc_voltage if dc_voltage > 0 else 0  # A
        
        # Health assessment
        health_score = self._assess_solar_health(device, dc_power, module_temp, efficiency)
        
        data = {
            'dc_power': round(dc_power, 2),
            'dc_voltage': round(dc_voltage, 1),
            'dc_current': round(dc_current, 2),
            'irradiance': round(irradiance, 1),
            'module_temperature': round(module_temp, 1),
            'ambient_temperature': round(ambient_temp, 1),
            'efficiency': round(efficiency * 100, 2),
            'health_score': health_score
        }
        
        return IoTDeviceData(
            device_id=device['device_id'],
            device_type=device['device_type'],
            timestamp=self.current_time,
            location=device['location'],
            data=data,
            health_status=self._get_health_status(health_score)
        )
    
    async def generate_battery_stream(self, device: Dict[str, Any]) -> IoTDeviceData:
        """Generate realistic battery system data stream."""
        # Simulate battery state based on usage patterns
        hour = self.current_time.hour
        
        # SOC varies based on time of day and usage
        base_soc = 0.5 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 24)
        soc = max(0.1, min(0.95, base_soc + random.uniform(-0.1, 0.1)))
        
        # Temperature effects
        ambient_temp = 25 + random.uniform(-5, 10)
        battery_temp = ambient_temp + random.uniform(2, 8)  # Battery heating during operation
        
        # Power flow (positive = charging, negative = discharging)
        if 6 <= hour <= 18:  # Daytime - likely charging
            power = random.uniform(0, device['capacity'] * 0.5)
        else:  # Nighttime - likely discharging
            power = random.uniform(-device['capacity'] * 0.3, 0)
        
        # Voltage and current
        voltage = 400 + soc * 50 + random.uniform(-10, 10)
        current = power * 1000 / voltage if voltage > 0 else 0
        
        # Health assessment
        cycle_penalty = min(1.0, device['cycle_count'] / device.get('cycle_life', 6000))
        temp_penalty = max(0, abs(battery_temp - self.battery_params['temp_optimum']) / 20)
        age_penalty = min(1.0, device['age_years'] / 15)
        
        health_score = 100 - (0.2 * cycle_penalty + 0.3 * temp_penalty + 0.3 * (1 - soc) + 0.2 * age_penalty) * 100
        
        data = {
            'soc': round(soc * 100, 1),
            'power': round(power, 2),
            'voltage': round(voltage, 1),
            'current': round(current, 2),
            'temperature': round(battery_temp, 1),
            'cycle_count': device['cycle_count'],
            'health_score': round(health_score, 1),
            'remaining_capacity': round(device['capacity'] * soc, 1)
        }
        
        return IoTDeviceData(
            device_id=device['device_id'],
            device_type=device['device_type'],
            timestamp=self.current_time,
            location=device['location'],
            data=data,
            health_status=self._get_health_status(health_score),
            battery_level=soc
        )
    
    async def generate_inverter_stream(self, device: Dict[str, Any]) -> IoTDeviceData:
        """Generate realistic inverter data stream."""
        # Input power (from solar panels)
        input_power = random.uniform(0, device['capacity'])
        
        # Temperature effects
        ambient_temp = 25 + random.uniform(-5, 10)
        inverter_temp = ambient_temp + input_power * 0.1 + random.uniform(5, 15)
        
        # Efficiency calculation
        temp_factor = 1 + self.inverter_params['temp_coefficient'] * (inverter_temp - 25)
        load_factor = min(1.0, input_power / device['capacity'])
        efficiency = self.inverter_params['efficiency'] * temp_factor * (0.8 + 0.2 * load_factor)
        
        # Output power
        output_power = input_power * efficiency
        
        # Health assessment
        temp_penalty = max(0, (inverter_temp - 40) / 20)
        age_penalty = min(1.0, device['age_years'] / 15)
        efficiency_penalty = max(0, (0.96 - efficiency) / 0.1)
        
        health_score = 100 - (0.4 * temp_penalty + 0.3 * age_penalty + 0.3 * efficiency_penalty) * 100
        
        data = {
            'input_power': round(input_power, 2),
            'output_power': round(output_power, 2),
            'efficiency': round(efficiency * 100, 2),
            'temperature': round(inverter_temp, 1),
            'frequency': round(50 + random.uniform(-0.1, 0.1), 2),
            'voltage': round(415 + random.uniform(-10, 10), 1),
            'health_score': round(health_score, 1)
        }
        
        return IoTDeviceData(
            device_id=device['device_id'],
            device_type=device['device_type'],
            timestamp=self.current_time,
            location=device['location'],
            data=data,
            health_status=self._get_health_status(health_score)
        )
    
    async def generate_ev_charger_stream(self, device: Dict[str, Any]) -> IoTDeviceData:
        """Generate realistic EV charger data stream."""
        # Charging status (simplified)
        is_charging = random.choice([True, False, False, False])  # 25% chance of charging
        
        if is_charging:
            # EV connected and charging
            charging_power = random.uniform(10, device['capacity'])
            soc = random.uniform(20, 90)  # EV battery SOC
            charging_time = random.uniform(30, 300)  # minutes
        else:
            # No EV connected or idle
            charging_power = 0
            soc = 0
            charging_time = 0
        
        # Temperature
        ambient_temp = 25 + random.uniform(-5, 10)
        charger_temp = ambient_temp + charging_power * 0.05 + random.uniform(2, 8)
        
        # Health assessment
        age_penalty = min(1.0, device['age_years'] / 10)
        temp_penalty = max(0, (charger_temp - 35) / 15)
        
        health_score = 100 - (0.6 * age_penalty + 0.4 * temp_penalty) * 100
        
        data = {
            'is_charging': is_charging,
            'charging_power': round(charging_power, 2),
            'ev_soc': round(soc, 1),
            'charging_time_remaining': round(charging_time, 0),
            'temperature': round(charger_temp, 1),
            'voltage': round(400 + random.uniform(-20, 20), 1),
            'current': round(charging_power * 1000 / 400, 2) if charging_power > 0 else 0,
            'health_score': round(health_score, 1)
        }
        
        return IoTDeviceData(
            device_id=device['device_id'],
            device_type=device['device_type'],
            timestamp=self.current_time,
            location=device['location'],
            data=data,
            health_status=self._get_health_status(health_score)
        )
    
    async def generate_grid_stream(self, device: Dict[str, Any]) -> IoTDeviceData:
        """Generate realistic grid connection data stream."""
        # Grid parameters vary throughout the day
        hour = self.current_time.hour
        
        # Frequency varies slightly
        frequency = self.grid_params['base_frequency'] + random.uniform(-0.2, 0.2)
        
        # Voltage varies with load
        voltage = self.grid_params['base_voltage'] + random.uniform(-15, 15)
        
        # Power flow (positive = import, negative = export)
        if 6 <= hour <= 22:  # High demand period
            power = random.uniform(100, device['capacity'] * 0.8)
        else:  # Low demand period
            power = random.uniform(-device['capacity'] * 0.3, 50)
        
        # Price varies with demand
        base_price = 0.12 + 0.05 * np.sin(2 * np.pi * (hour - 6) / 24)
        price = base_price + random.uniform(-0.02, 0.02)
        
        # Health assessment
        freq_penalty = max(0, abs(frequency - 50) / 0.5)
        voltage_penalty = max(0, abs(voltage - 415) / 20)
        
        health_score = 100 - (0.5 * freq_penalty + 0.5 * voltage_penalty) * 100
        
        data = {
            'power': round(power, 2),
            'frequency': round(frequency, 2),
            'voltage': round(voltage, 1),
            'current': round(power * 1000 / voltage, 2) if voltage > 0 else 0,
            'price': round(price, 3),
            'power_factor': round(0.95 + random.uniform(-0.05, 0.05), 3),
            'health_score': round(health_score, 1)
        }
        
        return IoTDeviceData(
            device_id=device['device_id'],
            device_type=device['device_type'],
            timestamp=self.current_time,
            location=device['location'],
            data=data,
            health_status=self._get_health_status(health_score)
        )
    
    def _calculate_solar_angle(self, hour: int, day_of_year: int) -> float:
        """Calculate solar elevation angle (simplified)."""
        # Simplified solar angle calculation
        hour_angle = (hour - 12) * 15  # degrees
        declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
        latitude = 22.0  # Approximate latitude for India
        
        elevation = np.degrees(np.arcsin(
            np.sin(np.radians(declination)) * np.sin(np.radians(latitude)) +
            np.cos(np.radians(declination)) * np.cos(np.radians(latitude)) * np.cos(np.radians(hour_angle))
        ))
        
        return max(0, elevation)
    
    def _assess_solar_health(self, device: Dict[str, Any], power: float, temp: float, efficiency: float) -> float:
        """Assess solar panel health based on performance metrics."""
        # Age penalty
        age_penalty = min(1.0, device['age_years'] / 20)
        
        # Temperature penalty
        temp_penalty = max(0, (temp - 25) / 30)
        
        # Efficiency penalty
        expected_efficiency = self.solar_params['efficiency'] * (1 - age_penalty * 0.1)
        efficiency_penalty = max(0, (expected_efficiency - efficiency) / expected_efficiency)
        
        # Power penalty (if significantly below expected)
        expected_power = device['capacity'] * 0.8  # Assume 80% of capacity is good
        power_penalty = max(0, (expected_power - power) / expected_power)
        
        health_score = 100 - (0.3 * age_penalty + 0.2 * temp_penalty + 0.3 * efficiency_penalty + 0.2 * power_penalty) * 100
        
        return max(0, min(100, health_score))
    
    def _get_health_status(self, health_score: float) -> str:
        """Convert health score to status string."""
        if health_score >= 90:
            return "Excellent"
        elif health_score >= 75:
            return "Good"
        elif health_score >= 60:
            return "Fair"
        elif health_score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    async def generate_all_streams(self) -> List[IoTDeviceData]:
        """Generate data streams for all devices."""
        streams = []
        
        for device in self.devices:
            try:
                if device['device_type'] == 'solar_panel':
                    stream = await self.generate_solar_stream(device)
                elif device['device_type'] == 'battery':
                    stream = await self.generate_battery_stream(device)
                elif device['device_type'] == 'inverter':
                    stream = await self.generate_inverter_stream(device)
                elif device['device_type'] == 'ev_charger':
                    stream = await self.generate_ev_charger_stream(device)
                elif device['device_type'] == 'grid_connection':
                    stream = await self.generate_grid_stream(device)
                else:
                    continue
                
                streams.append(stream)
                
            except Exception as e:
                logger.error(f"Error generating stream for {device['device_id']}: {e}")
                continue
        
        return streams
    
    async def start_streaming(self, interval_seconds: int = 5) -> AsyncGenerator[List[IoTDeviceData], None]:
        """Start continuous IoT data streaming."""
        logger.info(f"Starting IoT data streaming with {interval_seconds}s interval")
        
        while True:
            try:
                # Update current time
                self.current_time = datetime.now()
                
                # Generate all device streams
                streams = await self.generate_all_streams()
                
                # Store in history (keep last 1000 records)
                self.data_history.extend(streams)
                if len(self.data_history) > 1000:
                    self.data_history = self.data_history[-1000:]
                
                yield streams
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def get_device_summary(self) -> Dict[str, Any]:
        """Get summary of all devices and their current status."""
        summary = {
            'total_devices': len(self.devices),
            'device_types': {},
            'health_distribution': {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0, 'Critical': 0},
            'last_update': self.current_time
        }
        
        # Count device types
        for device in self.devices:
            device_type = device['device_type']
            summary['device_types'][device_type] = summary['device_types'].get(device_type, 0) + 1
        
        # Count health status from recent data
        if self.data_history:
            recent_data = [d for d in self.data_history if (self.current_time - d.timestamp).seconds < 60]
            for data in recent_data:
                summary['health_distribution'][data.health_status] += 1
        
        return summary
    
    def get_device_data(self, device_id: str) -> Optional[IoTDeviceData]:
        """Get latest data for a specific device."""
        if not self.data_history:
            return None
        
        # Find latest data for the device
        device_data = [d for d in self.data_history if d.device_id == device_id]
        if device_data:
            return max(device_data, key=lambda x: x.timestamp)
        
        return None
    
    def export_data(self, format: str = 'json') -> str:
        """Export current data history in specified format."""
        if format == 'json':
            data_list = [asdict(stream) for stream in self.data_history[-100:]]  # Last 100 records
            return json.dumps(data_list, default=str, indent=2)
        elif format == 'csv':
            # Convert to DataFrame and return CSV string
            data_list = [asdict(stream) for stream in self.data_history[-100:]]
            df = pd.json_normalize(data_list)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Usage example
async def main():
    """Example usage of IoT data ingestion service."""
    config = {
        'streaming_interval': 5,
        'data_retention_hours': 24,
        'enable_anomaly_detection': True
    }
    
    iot_stream = IoTDataStream(config)
    
    print("🌐 Starting IoT Data Ingestion Service")
    print(f"📊 Monitoring {len(iot_stream.devices)} devices")
    
    # Get initial summary
    summary = iot_stream.get_device_summary()
    print(f"Device Summary: {summary}")
    
    # Start streaming
    async for streams in iot_stream.start_streaming(interval_seconds=10):
        print(f"\n📡 Generated {len(streams)} device readings at {datetime.now()}")
        
        # Show sample data
        if streams:
            sample = streams[0]
            print(f"Sample: {sample.device_id} ({sample.device_type}) - {sample.health_status}")
            print(f"Data: {sample.data}")
        
        # Break after 3 iterations for demo
        if len(iot_stream.data_history) > 150:
            break
    
    print("\n📊 Final Summary:")
    final_summary = iot_stream.get_device_summary()
    print(json.dumps(final_summary, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
