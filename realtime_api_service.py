import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from typing import Dict, Optional, List
import warnings
warnings.filterwarnings('ignore')

class RealTimeAPIService:
    """Real-time API service for fetching live data from various sources"""
    
    def __init__(self):
        # API endpoints
        self.weather_api_url = "https://api.open-meteo.com/v1/forecast"
        self.energy_api_url = "https://api.eia.gov/v2/electricity/rto/region-data/data/"  # US Energy Information Administration
        
        # API keys (get these from respective websites)
        self.eia_api_key = os.getenv("EIA_API_KEY", "your_eia_api_key_here")  # Get from https://www.eia.gov/opendata/
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY", "your_alpha_vantage_key_here")  # Get from https://www.alphavantage.co/
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY", "your_openweather_api_key_here")  # Get from https://openweathermap.org/

        # Cache for API responses
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        
    def get_current_weather(self, latitude: float = 22.0, longitude: float = 79.0) -> Dict:
        """Get current weather data from Open-Meteo API"""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", 
                           "precipitation", "weather_code", "cloud_cover", "pressure_msl", 
                           "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
                "hourly": ["temperature_2m", "irradiation", "cloud_cover", "wind_speed_10m", 
                          "precipitation_probability", "weather_code"],
                "daily": ["sunrise", "sunset", "uv_index_max", "precipitation_sum"],
                "timezone": "auto"
            }
            
            response = requests.get(self.weather_api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process current weather
            current = data.get('current', {})
            weather_data = {
                'timestamp': datetime.now(),
                'temperature': current.get('temperature_2m', 25),
                'humidity': current.get('relative_humidity_2m', 50),
                'apparent_temperature': current.get('apparent_temperature', 25),
                'precipitation': current.get('precipitation', 0),
                'weather_code': current.get('weather_code', 0),
                'cloud_cover': current.get('cloud_cover', 0),
                'pressure': current.get('pressure_msl', 1013),
                'wind_speed': current.get('wind_speed_10m', 0),
                'wind_direction': current.get('wind_direction_10m', 0)
            }
            
            # Process hourly forecast
            hourly = data.get('hourly', {})
            if hourly:
                hourly_data = []
                for i in range(min(24, len(hourly['time']))):
                    hourly_data.append({
                        'datetime': pd.to_datetime(hourly['time'][i]),
                        'temperature': hourly['temperature_2m'][i],
                        'irradiation': hourly.get('irradiation', [0] * len(hourly['time']))[i],
                        'cloud_cover': hourly['cloud_cover'][i],
                        'wind_speed': hourly['wind_speed_10m'][i],
                        'precipitation_probability': hourly.get('precipitation_probability', [0] * len(hourly['time']))[i],
                        'weather_code': hourly['weather_code'][i]
                    })
                weather_data['hourly_forecast'] = hourly_data
            
            # Process daily forecast
            daily = data.get('daily', {})
            if daily:
                daily_data = []
                for i in range(min(7, len(daily['time']))):
                    daily_data.append({
                        'date': pd.to_datetime(daily['time'][i]),
                        'sunrise': daily['sunrise'][i],
                        'sunset': daily['sunset'][i],
                        'uv_index_max': daily['uv_index_max'][i],
                        'precipitation_sum': daily['precipitation_sum'][i]
                    })
                weather_data['daily_forecast'] = daily_data
            
            return weather_data
            
        except Exception as e:
            print(f"❌ Weather API error: {e}")
            return self._get_mock_weather_data()
    
    def get_energy_prices(self, region: str = "US") -> Dict:
        """Get current energy prices from EIA API"""
        try:
            if self.eia_api_key == "YOUR_EIA_API_KEY_HERE":
                print("⚠️ EIA API key not configured. Using mock data.")
                return self._get_mock_energy_prices()
            
            # EIA API call for electricity prices
            url = f"{self.energy_api_url}"
            params = {
                "api_key": self.eia_api_key,
                "frequency": "hourly",
                "data[0]": "value",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": 0,
                "length": 24
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process energy price data
            prices = []
            if 'data' in data:
                for record in data['data'][:24]:  # Last 24 hours
                    prices.append({
                        'datetime': pd.to_datetime(record['period']),
                        'price': record['value'],
                        'region': record.get('region', region)
                    })
            
            return {
                'prices': prices,
                'current_price': prices[0]['price'] if prices else 0.12,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            print(f"❌ Energy API error: {e}")
            return self._get_mock_energy_prices()
    
    def get_renewable_energy_data(self) -> Dict:
        """Get renewable energy data from data.gov.in"""
        try:
            # data.gov.in API endpoints (you provided these)
            endpoints = [
                '2a880b6e-4343-4873-9269-33d99855613a',
                'a19c2cdc-44c8-4924-b612-fd4304733d8a',
                '7ae606e1-58b0-4b62-b268-03f4d8d3ce09',
                '15ed3966-909a-4b51-b809-8e81f5b6bd41',
                'b4aed188-6ce1-4a80-ac77-6e458c65ca0e',
                '9ac005c2-403f-4d43-b57c-1f7b4ac86fde'
            ]
            
            renewable_data = []
            base_url = 'https://www.data.gov.in/resource/'
            
            for endpoint in endpoints[:2]:  # Use first 2 endpoints to avoid rate limiting
                try:
                    url = f"{base_url}{endpoint}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        renewable_data.extend(data.get('data', []))
                except Exception as e:
                    print(f"⚠️ Error fetching data from {endpoint}: {e}")
                    continue
            
            return {
                'renewable_data': renewable_data,
                'timestamp': datetime.now(),
                'sources': len(endpoints)
            }
            
        except Exception as e:
            print(f"❌ Renewable energy API error: {e}")
            return self._get_mock_renewable_data()
    
    def get_system_recommendations(self, weather_data: Dict, energy_prices: Dict) -> Dict:
        """Generate AI-powered system recommendations based on real-time data"""
        try:
            # Extract key metrics
            temperature = weather_data.get('temperature', 25)
            irradiation = weather_data.get('hourly_forecast', [{}])[0].get('irradiation', 0)
            cloud_cover = weather_data.get('cloud_cover', 0)
            current_price = energy_prices.get('current_price', 0.12)
            
            # AI logic for recommendations
            recommendations = {}
            
            # Solar generation prediction
            solar_potential = max(0, irradiation * (1 - cloud_cover / 100) * 0.8)
            recommendations['solar_generation'] = {
                'predicted_kw': solar_potential,
                'confidence': 0.85,
                'factors': {
                    'irradiation': irradiation,
                    'cloud_cover': cloud_cover,
                    'temperature_impact': max(0.8, 1 - abs(temperature - 25) / 50)
                }
            }
            
            # Battery management
            if solar_potential > 500 and current_price < 0.10:
                battery_action = "charge"
                battery_power = min(50, solar_potential * 0.3)
            elif solar_potential < 200 and current_price > 0.15:
                battery_action = "discharge"
                battery_power = min(50, 30)
            else:
                battery_action = "idle"
                battery_power = 0
            
            recommendations['battery_management'] = {
                'action': battery_action,
                'power_kw': battery_power,
                'reasoning': f"Solar: {solar_potential:.0f}kW, Price: ${current_price:.3f}/kWh"
            }
            
            # Grid interaction
            if solar_potential > 800 and current_price > 0.12:
                grid_export = min(100, solar_potential * 0.4)
                grid_action = "export"
            elif solar_potential < 300 and current_price < 0.10:
                grid_import = min(100, 50)
                grid_action = "import"
            else:
                grid_export = 0
                grid_import = 0
                grid_action = "balanced"
            
            recommendations['grid_interaction'] = {
                'action': grid_action,
                'export_kw': grid_export,
                'import_kw': grid_import,
                'price_advantage': current_price - 0.12
            }
            
            # Weather-based adjustments
            if temperature > 35:
                recommendations['weather_adjustments'] = {
                    'battery_cooling': True,
                    'efficiency_factor': 0.9,
                    'warning': 'High temperature - monitor battery health'
                }
            elif cloud_cover > 80:
                recommendations['weather_adjustments'] = {
                    'curtailment_recommended': True,
                    'efficiency_factor': 0.7,
                    'warning': 'Heavy cloud cover - reduced generation expected'
                }
            else:
                recommendations['weather_adjustments'] = {
                    'optimal_conditions': True,
                    'efficiency_factor': 1.0,
                    'warning': None
                }
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {e}")
            return self._get_mock_recommendations()
    
    def _get_mock_weather_data(self) -> Dict:
        """Generate mock weather data when API fails"""
        return {
            'timestamp': datetime.now(),
            'temperature': 25 + np.random.normal(0, 5),
            'humidity': 60 + np.random.normal(0, 10),
            'apparent_temperature': 25 + np.random.normal(0, 3),
            'precipitation': max(0, np.random.normal(0, 2)),
            'weather_code': np.random.randint(0, 10),
            'cloud_cover': np.random.randint(0, 100),
            'pressure': 1013 + np.random.normal(0, 10),
            'wind_speed': max(0, np.random.normal(5, 3)),
            'wind_direction': np.random.randint(0, 360),
            'hourly_forecast': self._generate_mock_hourly_forecast(),
            'daily_forecast': self._generate_mock_daily_forecast()
        }
    
    def _get_mock_energy_prices(self) -> Dict:
        """Generate mock energy prices when API fails"""
        prices = []
        base_time = datetime.now()
        base_price = 0.12
        
        for i in range(24):
            price = base_price + np.random.normal(0, 0.02)
            prices.append({
                'datetime': base_time - timedelta(hours=i),
                'price': max(0.05, price),
                'region': 'US'
            })
        
        return {
            'prices': prices,
            'current_price': prices[0]['price'],
            'timestamp': datetime.now()
        }
    
    def _get_mock_renewable_data(self) -> Dict:
        """Generate mock renewable energy data when API fails"""
        return {
            'renewable_data': [
                {
                    'source': 'Solar',
                    'capacity_mw': 100,
                    'generation_mw': 75 + np.random.normal(0, 10),
                    'efficiency': 0.85,
                    'timestamp': datetime.now()
                },
                {
                    'source': 'Wind',
                    'capacity_mw': 50,
                    'generation_mw': 30 + np.random.normal(0, 5),
                    'efficiency': 0.60,
                    'timestamp': datetime.now()
                }
            ],
            'timestamp': datetime.now(),
            'sources': 2
        }
    
    def _get_mock_recommendations(self) -> Dict:
        """Generate mock recommendations when AI fails"""
        return {
            'solar_generation': {
                'predicted_kw': 800 + np.random.normal(0, 100),
                'confidence': 0.75,
                'factors': {'irradiation': 500, 'cloud_cover': 30}
            },
            'battery_management': {
                'action': 'charge',
                'power_kw': 25,
                'reasoning': 'Excess solar generation available'
            },
            'grid_interaction': {
                'action': 'export',
                'export_kw': 50,
                'import_kw': 0,
                'price_advantage': 0.02
            },
            'weather_adjustments': {
                'optimal_conditions': True,
                'efficiency_factor': 0.95,
                'warning': None
            }
        }
    
    def _generate_mock_hourly_forecast(self) -> List[Dict]:
        """Generate mock hourly forecast data"""
        forecast = []
        base_time = datetime.now()
        
        for i in range(24):
            forecast.append({
                'datetime': base_time + timedelta(hours=i),
                'temperature': 25 + np.random.normal(0, 3),
                'irradiation': max(0, 500 + np.random.normal(0, 100)),
                'cloud_cover': np.random.randint(0, 100),
                'wind_speed': max(0, np.random.normal(5, 2)),
                'precipitation_probability': np.random.randint(0, 50),
                'weather_code': np.random.randint(0, 10)
            })
        
        return forecast
    
    def _generate_mock_daily_forecast(self) -> List[Dict]:
        """Generate mock daily forecast data"""
        forecast = []
        base_time = datetime.now()
        
        for i in range(7):
            forecast.append({
                'date': base_time + timedelta(days=i),
                'sunrise': f"{6 + i % 2:02d}:00:00",
                'sunset': f"{18 + i % 2:02d}:00:00",
                'uv_index_max': np.random.randint(1, 10),
                'precipitation_sum': max(0, np.random.normal(0, 5))
            })
        
        return forecast

# Usage example
if __name__ == "__main__":
    # Initialize API service
    api_service = RealTimeAPIService()
    
    # Get real-time data
    print("🌤️ Fetching weather data...")
    weather = api_service.get_current_weather()
    print(f"Temperature: {weather['temperature']:.1f}°C")
    print(f"Cloud Cover: {weather['cloud_cover']}%")
    
    print("\n💰 Fetching energy prices...")
    prices = api_service.get_energy_prices()
    print(f"Current Price: ${prices['current_price']:.3f}/kWh")
    
    print("\n⚡ Getting renewable energy data...")
    renewable = api_service.get_renewable_energy_data()
    print(f"Renewable Sources: {renewable['sources']}")
    
    print("\n🤖 Generating AI recommendations...")
    recommendations = api_service.get_system_recommendations(weather, prices)
    print(f"Solar Prediction: {recommendations['solar_generation']['predicted_kw']:.0f} kW")
    print(f"Battery Action: {recommendations['battery_management']['action']}")
    print(f"Grid Action: {recommendations['grid_interaction']['action']}")
