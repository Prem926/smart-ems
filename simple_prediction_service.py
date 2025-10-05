import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SimplePredictionService:
    def __init__(self, data_dir: str = ".."):
        self.data_loader = DataLoader(data_dir)
        self.training_data = None
        self._load_data()
    
    def _load_data(self):
        """Load and prepare training data"""
        try:
            print("Loading training data...")
            self.training_data = self.data_loader.prepare_training_data()
            print(f"✅ Loaded {len(self.training_data)} data points")
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.training_data = pd.DataFrame()
    
    def get_current_recommendations(self, current_data: dict = None) -> dict:
        """Get current energy management recommendations using rule-based approach"""
        if self.training_data.empty:
            return {"error": "No data available"}
        
        try:
            # Use current data or get latest from dataset
            if current_data is None:
                current_data = self.training_data.iloc[-1].to_dict()
            
            # Extract key metrics
            dc_power = current_data.get('DC_POWER', 0)
            ac_power = current_data.get('AC_POWER', 0)
            ambient_temp = current_data.get('AMBIENT_TEMPERATURE', 25)
            module_temp = current_data.get('MODULE_TEMPERATURE', 30)
            irradiation = current_data.get('IRRADIATION', 0)
            hour = current_data.get('HOUR', 12)
            
            # Rule-based recommendations
            battery_power = self._calculate_battery_power(dc_power, ac_power, hour)
            curtail_frac = self._calculate_curtailment(dc_power, ac_power, hour)
            export_power = self._calculate_export_power(dc_power, ac_power, battery_power)
            
            recommendations = {
                "battery_action": {
                    "power_kw": float(battery_power),
                    "action_type": "charge" if battery_power > 0 else "discharge" if battery_power < 0 else "idle",
                    "recommendation": self._get_battery_recommendation(battery_power)
                },
                "solar_curtailment": {
                    "fraction": float(curtail_frac),
                    "recommendation": self._get_curtailment_recommendation(curtail_frac)
                },
                "grid_export": {
                    "power_kw": float(export_power),
                    "recommendation": self._get_export_recommendation(export_power)
                },
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.75
            }
            
            return recommendations
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def _calculate_battery_power(self, dc_power: float, ac_power: float, hour: int) -> float:
        """Calculate recommended battery power based on generation and demand"""
        # Simple rule-based logic
        net_power = dc_power - ac_power
        
        # Peak generation hours (10-16) - charge battery
        if 10 <= hour <= 16:
            if net_power > 50:
                return min(100, net_power * 0.8)  # Charge at 80% of excess
            elif net_power > 0:
                return min(50, net_power * 0.5)   # Charge at 50% of excess
            else:
                return 0
        
        # Peak demand hours (18-22) - discharge battery
        elif 18 <= hour <= 22:
            if net_power < -50:
                return max(-100, net_power * 0.8)  # Discharge to meet demand
            elif net_power < 0:
                return max(-50, net_power * 0.5)   # Discharge moderately
            else:
                return 0
        
        # Night hours (0-6) - discharge battery
        elif 0 <= hour <= 6:
            return max(-50, -ac_power * 0.3)  # Discharge to meet 30% of demand
        
        # Other hours - balance
        else:
            if net_power > 20:
                return min(30, net_power * 0.3)   # Light charging
            elif net_power < -20:
                return max(-30, net_power * 0.3)  # Light discharging
            else:
                return 0
    
    def _calculate_curtailment(self, dc_power: float, ac_power: float, hour: int) -> float:
        """Calculate recommended solar curtailment fraction"""
        # Only curtail during peak generation if there's excess
        if 10 <= hour <= 16 and dc_power > ac_power * 1.5:
            excess_ratio = (dc_power - ac_power) / dc_power
            return min(0.3, excess_ratio * 0.5)  # Curtail up to 30%
        return 0.0
    
    def _calculate_export_power(self, dc_power: float, ac_power: float, battery_power: float) -> float:
        """Calculate recommended grid export power"""
        net_after_battery = dc_power - ac_power + battery_power
        return max(0, net_after_battery)
    
    def _get_battery_recommendation(self, battery_power: float) -> str:
        """Get human-readable battery recommendation"""
        if battery_power > 50:
            return "Charge battery at high rate - excess solar available"
        elif battery_power > 10:
            return "Charge battery moderately"
        elif battery_power < -50:
            return "Discharge battery at high rate - high demand period"
        elif battery_power < -10:
            return "Discharge battery moderately"
        else:
            return "Maintain current battery state"
    
    def _get_curtailment_recommendation(self, curtail_frac: float) -> str:
        """Get human-readable curtailment recommendation"""
        if curtail_frac > 0.2:
            return "High curtailment recommended - excess generation"
        elif curtail_frac > 0.1:
            return "Moderate curtailment recommended"
        elif curtail_frac > 0:
            return "Low curtailment recommended"
        else:
            return "No curtailment needed - use all available solar"
    
    def _get_export_recommendation(self, export_power: float) -> str:
        """Get human-readable export recommendation"""
        if export_power > 100:
            return "Export significant power to grid - high generation"
        elif export_power > 20:
            return "Export moderate power to grid"
        elif export_power > 0:
            return "Export small amount to grid"
        else:
            return "No grid export recommended"
    
    def get_forecast_recommendations(self, hours_ahead: int = 24) -> list:
        """Get recommendations for the next N hours"""
        try:
            # Get weather forecast
            weather_data = self.data_loader.get_weather_forecast()
            
            if weather_data.empty:
                # Fallback to historical patterns
                return self._get_historical_forecast(hours_ahead)
            
            recommendations = []
            current_time = datetime.now()
            
            for i in range(min(hours_ahead, len(weather_data))):
                forecast_time = current_time + timedelta(hours=i)
                
                # Create synthetic data point for forecast
                if i < len(weather_data):
                    weather_point = weather_data.iloc[i]
                    forecast_data = {
                        'DC_POWER': max(0, weather_point.get('global_tilted_irradiance', 0) * 0.2),
                        'AC_POWER': 100 + np.random.normal(0, 20),
                        'AMBIENT_TEMPERATURE': weather_point.get('temperature_2m', 25),
                        'MODULE_TEMPERATURE': weather_point.get('temperature_2m', 25) + 10,
                        'IRRADIATION': weather_point.get('shortwave_radiation', 0),
                        'HOUR': forecast_time.hour
                    }
                    
                    rec = self.get_current_recommendations(forecast_data)
                    rec['forecast_time'] = forecast_time.isoformat()
                    recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            return [{"error": f"Forecast failed: {str(e)}"}]
    
    def _get_historical_forecast(self, hours_ahead: int) -> list:
        """Get forecast based on historical patterns"""
        if self.training_data.empty:
            return [{"error": "No historical data available"}]
        
        recommendations = []
        current_time = datetime.now()
        
        for i in range(hours_ahead):
            forecast_time = current_time + timedelta(hours=i)
            hour = forecast_time.hour
            
            # Find similar historical data
            similar_data = self.training_data[self.training_data['HOUR'] == hour]
            if not similar_data.empty:
                avg_data = similar_data.mean().to_dict()
                avg_data['HOUR'] = hour
                
                rec = self.get_current_recommendations(avg_data)
                rec['forecast_time'] = forecast_time.isoformat()
                recommendations.append(rec)
            else:
                # Default recommendation
                recommendations.append({
                    "forecast_time": forecast_time.isoformat(),
                    "battery_action": {"power_kw": 0, "action_type": "idle", "recommendation": "No data available"},
                    "solar_curtailment": {"fraction": 0, "recommendation": "No data available"},
                    "grid_export": {"power_kw": 0, "recommendation": "No data available"},
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.5
                })
        
        return recommendations
    
    def get_system_status(self) -> dict:
        """Get current system status and metrics"""
        try:
            if self.training_data.empty:
                return {"error": "No data available"}
            
            latest_data = self.training_data.iloc[-1]
            
            # Get current recommendations
            recommendations = self.get_current_recommendations()
            
            # Calculate efficiency metrics
            dc_power = latest_data.get('DC_POWER', 0)
            ac_power = latest_data.get('AC_POWER', 0)
            efficiency = (ac_power / max(dc_power, 1)) * 100 if dc_power > 0 else 0
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "current_generation": {
                    "dc_power": float(dc_power),
                    "ac_power": float(ac_power),
                    "efficiency": float(efficiency)
                },
                "weather": {
                    "ambient_temp": float(latest_data.get('AMBIENT_TEMPERATURE', 25)),
                    "module_temp": float(latest_data.get('MODULE_TEMPERATURE', 30)),
                    "irradiation": float(latest_data.get('IRRADIATION', 0))
                },
                "recommendations": recommendations,
                "system_health": "good" if dc_power > 0 and efficiency > 50 else "low_generation"
            }
            
            return status
            
        except Exception as e:
            return {"error": f"Status check failed: {str(e)}"}

if __name__ == "__main__":
    # Test the prediction service
    print("Initializing Simple Prediction Service...")
    service = SimplePredictionService()
    
    print("\n=== Current Recommendations ===")
    current_rec = service.get_current_recommendations()
    print(current_rec)
    
    print("\n=== System Status ===")
    status = service.get_system_status()
    print(status)
    
    print("\n=== 24h Forecast (first 5 hours) ===")
    forecast = service.get_forecast_recommendations(24)
    for i, rec in enumerate(forecast[:5]):
        print(f"Hour {i+1}: {rec}")
