"""
Location Intelligence Service
Provides location-based personalization for EMS system.
Fetches state-wise tariffs, solar potential, and carbon intensity data.
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LocationData:
    """Location-specific data structure."""
    state: str
    city: str
    coordinates: Tuple[float, float]
    solar_potential: Dict[str, float]
    electricity_tariff: Dict[str, float]
    carbon_intensity: float
    renewable_percentage: float
    climate_zone: str
    last_updated: datetime

class LocationIntelligence:
    """Location-based intelligence for EMS personalization."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.location_cache = {}
        self.india_states_data = self._load_india_states_data()
        
        # API endpoints
        self.data_gov_base = "https://www.data.gov.in/resource/"
        self.electricity_maps_api = "https://api.electricitymap.org/v3/carbon-intensity"
        self.nrel_api = "https://developer.nrel.gov/api/solar"
        
    def _load_india_states_data(self) -> Dict[str, Dict[str, Any]]:
        """Load India states data with coordinates and basic info."""
        return {
            "Andhra Pradesh": {
                "coordinates": (15.9129, 79.7400),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.2,
                "wind_potential": "Medium"
            },
            "Assam": {
                "coordinates": (26.2006, 92.9376),
                "climate_zone": "Tropical",
                "solar_irradiance": 4.8,
                "wind_potential": "Low"
            },
            "Bihar": {
                "coordinates": (25.0961, 85.3131),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.0,
                "wind_potential": "Low"
            },
            "Chhattisgarh": {
                "coordinates": (21.2787, 81.8661),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.1,
                "wind_potential": "Low"
            },
            "Delhi": {
                "coordinates": (28.7041, 77.1025),
                "climate_zone": "Semi-arid",
                "solar_irradiance": 5.3,
                "wind_potential": "Low"
            },
            "Gujarat": {
                "coordinates": (23.0225, 72.5714),
                "climate_zone": "Arid",
                "solar_irradiance": 5.8,
                "wind_potential": "High"
            },
            "Haryana": {
                "coordinates": (29.0588, 76.0856),
                "climate_zone": "Semi-arid",
                "solar_irradiance": 5.4,
                "wind_potential": "Medium"
            },
            "Himachal Pradesh": {
                "coordinates": (31.1048, 77.1734),
                "climate_zone": "Temperate",
                "solar_irradiance": 4.5,
                "wind_potential": "High"
            },
            "Jharkhand": {
                "coordinates": (23.6102, 85.2799),
                "climate_zone": "Tropical",
                "solar_irradiance": 4.9,
                "wind_potential": "Low"
            },
            "Karnataka": {
                "coordinates": (15.3173, 75.7139),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.5,
                "wind_potential": "High"
            },
            "Kerala": {
                "coordinates": (10.8505, 76.2711),
                "climate_zone": "Tropical",
                "solar_irradiance": 4.7,
                "wind_potential": "Medium"
            },
            "Madhya Pradesh": {
                "coordinates": (22.9734, 78.6569),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.2,
                "wind_potential": "Medium"
            },
            "Maharashtra": {
                "coordinates": (19.7515, 75.7139),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.3,
                "wind_potential": "High"
            },
            "Odisha": {
                "coordinates": (20.9517, 85.0985),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.0,
                "wind_potential": "Medium"
            },
            "Punjab": {
                "coordinates": (31.1471, 75.3412),
                "climate_zone": "Semi-arid",
                "solar_irradiance": 5.1,
                "wind_potential": "Medium"
            },
            "Rajasthan": {
                "coordinates": (27.0238, 74.2179),
                "climate_zone": "Arid",
                "solar_irradiance": 6.0,
                "wind_potential": "High"
            },
            "Tamil Nadu": {
                "coordinates": (11.1271, 78.6569),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.4,
                "wind_potential": "High"
            },
            "Telangana": {
                "coordinates": (18.1124, 79.0193),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.3,
                "wind_potential": "Medium"
            },
            "Uttar Pradesh": {
                "coordinates": (26.8467, 80.9462),
                "climate_zone": "Tropical",
                "solar_irradiance": 5.0,
                "wind_potential": "Low"
            },
            "West Bengal": {
                "coordinates": (22.9868, 87.8550),
                "climate_zone": "Tropical",
                "solar_irradiance": 4.8,
                "wind_potential": "Medium"
            }
        }
    
    def get_location_details(self, state: str, city: str = None) -> LocationData:
        """Get comprehensive location details for EMS personalization."""
        location_key = f"{state}_{city}" if city else state
        
        # Check cache first
        if location_key in self.location_cache:
            cached_data = self.location_cache[location_key]
            if (datetime.now() - cached_data.last_updated).hours < 24:
                return cached_data
        
        # Get state data
        if state not in self.india_states_data:
            raise ValueError(f"State '{state}' not found in database")
        
        state_data = self.india_states_data[state]
        coordinates = state_data["coordinates"]
        
        # Fetch solar potential
        solar_potential = self._get_solar_potential(coordinates)
        
        # Fetch electricity tariff
        electricity_tariff = self._get_electricity_tariff(state)
        
        # Fetch carbon intensity
        carbon_intensity = self._get_carbon_intensity(coordinates)
        
        # Calculate renewable percentage
        renewable_percentage = self._get_renewable_percentage(state)
        
        # Create location data
        location_data = LocationData(
            state=state,
            city=city or "State Capital",
            coordinates=coordinates,
            solar_potential=solar_potential,
            electricity_tariff=electricity_tariff,
            carbon_intensity=carbon_intensity,
            renewable_percentage=renewable_percentage,
            climate_zone=state_data["climate_zone"],
            last_updated=datetime.now()
        )
        
        # Cache the data
        self.location_cache[location_key] = location_data
        
        return location_data
    
    def _get_solar_potential(self, coordinates: Tuple[float, float]) -> Dict[str, float]:
        """Get solar potential data for coordinates."""
        try:
            # Use NREL API for solar data
            lat, lon = coordinates
            
            # For demo, use simplified calculation based on coordinates
            # In production, use actual NREL API
            base_irradiance = 5.0  # kWh/m²/day
            
            # Adjust based on latitude (simplified)
            lat_factor = 1 - abs(lat - 20) / 50  # Peak at 20°N
            adjusted_irradiance = base_irradiance * lat_factor
            
            # Add seasonal variation
            day_of_year = datetime.now().timetuple().tm_yday
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            
            daily_irradiance = adjusted_irradiance * seasonal_factor
            
            return {
                "daily_irradiance": round(daily_irradiance, 2),
                "annual_irradiance": round(daily_irradiance * 365, 0),
                "peak_sun_hours": round(daily_irradiance, 1),
                "solar_potential_rating": self._rate_solar_potential(daily_irradiance)
            }
            
        except Exception as e:
            logger.error(f"Error fetching solar potential: {e}")
            return self._get_fallback_solar_data()
    
    def _get_electricity_tariff(self, state: str) -> Dict[str, float]:
        """Get electricity tariff data for state."""
        try:
            # State-wise tariff data (simplified)
            # In production, fetch from data.gov.in API
            tariff_data = {
                "Andhra Pradesh": {"domestic": 6.5, "commercial": 8.2, "industrial": 7.8},
                "Assam": {"domestic": 5.8, "commercial": 7.5, "industrial": 7.2},
                "Bihar": {"domestic": 6.2, "commercial": 8.0, "industrial": 7.5},
                "Chhattisgarh": {"domestic": 5.5, "commercial": 7.2, "industrial": 6.8},
                "Delhi": {"domestic": 7.0, "commercial": 9.5, "industrial": 8.5},
                "Gujarat": {"domestic": 6.8, "commercial": 8.8, "industrial": 8.2},
                "Haryana": {"domestic": 6.5, "commercial": 8.5, "industrial": 8.0},
                "Himachal Pradesh": {"domestic": 5.2, "commercial": 7.0, "industrial": 6.5},
                "Jharkhand": {"domestic": 6.0, "commercial": 7.8, "industrial": 7.2},
                "Karnataka": {"domestic": 6.8, "commercial": 8.8, "industrial": 8.2},
                "Kerala": {"domestic": 6.2, "commercial": 8.0, "industrial": 7.5},
                "Madhya Pradesh": {"domestic": 6.0, "commercial": 7.8, "industrial": 7.2},
                "Maharashtra": {"domestic": 7.2, "commercial": 9.2, "industrial": 8.8},
                "Odisha": {"domestic": 5.8, "commercial": 7.5, "industrial": 7.0},
                "Punjab": {"domestic": 6.5, "commercial": 8.5, "industrial": 8.0},
                "Rajasthan": {"domestic": 6.8, "commercial": 8.8, "industrial": 8.2},
                "Tamil Nadu": {"domestic": 6.5, "commercial": 8.5, "industrial": 8.0},
                "Telangana": {"domestic": 6.8, "commercial": 8.8, "industrial": 8.2},
                "Uttar Pradesh": {"domestic": 6.2, "commercial": 8.0, "industrial": 7.5},
                "West Bengal": {"domestic": 6.0, "commercial": 7.8, "industrial": 7.2}
            }
            
            return tariff_data.get(state, {"domestic": 6.5, "commercial": 8.2, "industrial": 7.8})
            
        except Exception as e:
            logger.error(f"Error fetching tariff data: {e}")
            return {"domestic": 6.5, "commercial": 8.2, "industrial": 7.8}
    
    def _get_carbon_intensity(self, coordinates: Tuple[float, float]) -> float:
        """Get carbon intensity for coordinates."""
        try:
            # Use ElectricityMaps API
            # For demo, use simplified calculation
            lat, lon = coordinates
            
            # Base carbon intensity for India
            base_intensity = 800  # gCO₂/kWh
            
            # Adjust based on location (simplified)
            # States with more renewable energy have lower intensity
            renewable_states = ["Gujarat", "Karnataka", "Tamil Nadu", "Rajasthan", "Maharashtra"]
            state_name = self._get_state_from_coordinates(coordinates)
            
            if state_name in renewable_states:
                intensity_factor = 0.8
            else:
                intensity_factor = 1.0
            
            # Add time-of-day variation
            hour = datetime.now().hour
            if 6 <= hour <= 18:  # Daytime
                time_factor = 0.9  # Lower intensity due to solar
            else:  # Nighttime
                time_factor = 1.1  # Higher intensity due to thermal
            
            carbon_intensity = base_intensity * intensity_factor * time_factor
            
            return round(carbon_intensity, 0)
            
        except Exception as e:
            logger.error(f"Error fetching carbon intensity: {e}")
            return 800.0
    
    def _get_renewable_percentage(self, state: str) -> float:
        """Get renewable energy percentage for state."""
        # State-wise renewable energy data (simplified)
        renewable_data = {
            "Andhra Pradesh": 45.2,
            "Assam": 12.8,
            "Bihar": 8.5,
            "Chhattisgarh": 15.2,
            "Delhi": 25.8,
            "Gujarat": 52.3,
            "Haryana": 35.6,
            "Himachal Pradesh": 68.9,
            "Jharkhand": 18.7,
            "Karnataka": 58.4,
            "Kerala": 42.1,
            "Madhya Pradesh": 38.9,
            "Maharashtra": 48.7,
            "Odisha": 22.3,
            "Punjab": 28.5,
            "Rajasthan": 61.2,
            "Tamil Nadu": 55.8,
            "Telangana": 41.6,
            "Uttar Pradesh": 15.8,
            "West Bengal": 18.9
        }
        
        return renewable_data.get(state, 30.0)
    
    def _rate_solar_potential(self, irradiance: float) -> str:
        """Rate solar potential based on irradiance."""
        if irradiance >= 5.5:
            return "Excellent"
        elif irradiance >= 5.0:
            return "Very Good"
        elif irradiance >= 4.5:
            return "Good"
        elif irradiance >= 4.0:
            return "Fair"
        else:
            return "Poor"
    
    def _get_state_from_coordinates(self, coordinates: Tuple[float, float]) -> str:
        """Get state name from coordinates (simplified)."""
        lat, lon = coordinates
        
        # Find closest state
        min_distance = float('inf')
        closest_state = "Delhi"
        
        for state, data in self.india_states_data.items():
            state_lat, state_lon = data["coordinates"]
            distance = np.sqrt((lat - state_lat)**2 + (lon - state_lon)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_state = state
        
        return closest_state
    
    def _get_fallback_solar_data(self) -> Dict[str, float]:
        """Fallback solar data when API fails."""
        return {
            "daily_irradiance": 5.0,
            "annual_irradiance": 1825,
            "peak_sun_hours": 5.0,
            "solar_potential_rating": "Good"
        }
    
    def generate_location_based_forecast(self, location_data: LocationData, 
                                       hours_ahead: int = 24) -> Dict[str, Any]:
        """Generate location-based energy forecast."""
        try:
            # Generate forecast data directly
            forecast_data = []
            current_time = datetime.now()
            
            # Get location factors
            solar_irradiance = location_data.solar_potential.get("daily_irradiance", 5.0)
            avg_tariff = np.mean(list(location_data.electricity_tariff.values())) if location_data.electricity_tariff else 7.0
            
            for i in range(hours_ahead):
                forecast_time = current_time + timedelta(hours=i)
                hour_of_day = forecast_time.hour
                
                # Solar generation forecast (peak at noon)
                solar_factor = max(0, np.sin(2 * np.pi * (hour_of_day - 6) / 24))
                solar_power = round(solar_irradiance * 20 * solar_factor * np.random.uniform(0.8, 1.2), 2)
                
                # Load forecast (peaks in morning and evening)
                if 6 <= hour_of_day < 10 or 18 <= hour_of_day < 22:
                    load_factor = 1.5
                else:
                    load_factor = 0.8
                
                base_load = 100
                load_demand = round(base_load * load_factor * np.random.uniform(0.9, 1.1), 2)
                
                # Price forecast
                price_factor = 1 + 0.2 * np.sin(2 * np.pi * (hour_of_day - 8) / 24)
                price = round(avg_tariff * price_factor * np.random.uniform(0.95, 1.05), 2)
                
                forecast_data.append({
                    "timestamp": forecast_time.isoformat(),
                    "hour": hour_of_day,
                    "solar_power_kw": solar_power,
                    "load_demand_kw": load_demand,
                    "price_per_kwh": price,
                    "carbon_intensity": location_data.carbon_intensity * np.random.uniform(0.9, 1.1)
                })
            
            return {
                "forecast_available": True,
                "location": f"{location_data.city}, {location_data.state}",
                "forecast_data": forecast_data,
                "solar_potential": solar_irradiance,
                "avg_tariff": avg_tariff,
                "carbon_intensity": location_data.carbon_intensity
            }
            
            return {
                "location": {
                    "state": location_data.state,
                    "city": location_data.city,
                    "coordinates": location_data.coordinates
                },
                "solar_forecast": solar_forecast,
                "load_forecast": load_forecast,
                "carbon_intensity": location_data.carbon_intensity,
                "renewable_percentage": location_data.renewable_percentage,
                "forecast_generated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating location-based forecast: {e}")
            return self._get_fallback_forecast()
    
    def _get_base_forecast(self, hours_ahead: int) -> Dict[str, Any]:
        """Get base forecast data."""
        solar_forecast = []
        load_forecast = []
        
        for hour in range(hours_ahead):
            # Solar forecast (simplified)
            hour_of_day = (datetime.now().hour + hour) % 24
            
            if 6 <= hour_of_day <= 18:
                solar_power = 100 * np.sin(np.pi * (hour_of_day - 6) / 12)
                irradiance = 1000 * np.sin(np.pi * (hour_of_day - 6) / 12)
            else:
                solar_power = 0
                irradiance = 0
            
            solar_forecast.append({
                "hour": hour_of_day,
                "power": max(0, solar_power),
                "irradiance": max(0, irradiance)
            })
            
            # Load forecast (simplified)
            base_load = 50
            if 6 <= hour_of_day <= 22:
                load = base_load + 20 * np.sin(np.pi * (hour_of_day - 6) / 16)
            else:
                load = base_load * 0.6
            
            load_forecast.append({
                "hour": hour_of_day,
                "load": max(10, load)
            })
        
        return {
            "solar": solar_forecast,
            "load": load_forecast
        }
    
    def _get_fallback_forecast(self) -> Dict[str, Any]:
        """Fallback forecast when generation fails."""
        return {
            "location": {"state": "Unknown", "city": "Unknown", "coordinates": (0, 0)},
            "solar_forecast": [{"hour": i, "power": 0, "irradiance": 0} for i in range(24)],
            "load_forecast": [{"hour": i, "load": 50, "tariff": 7.0} for i in range(24)],
            "carbon_intensity": 800,
            "renewable_percentage": 30,
            "forecast_generated_at": datetime.now()
        }
    
    def get_india_energy_map_data(self) -> Dict[str, Any]:
        """Get data for India energy map visualization."""
        map_data = []
        
        for state, data in self.india_states_data.items():
            try:
                location_data = self.get_location_details(state)
                
                map_data.append({
                    "state": state,
                    "coordinates": data["coordinates"],
                    "solar_potential": location_data.solar_potential["daily_irradiance"],
                    "electricity_tariff": np.mean(list(location_data.electricity_tariff.values())),
                    "carbon_intensity": location_data.carbon_intensity,
                    "renewable_percentage": location_data.renewable_percentage,
                    "climate_zone": data["climate_zone"],
                    "wind_potential": data["wind_potential"]
                })
                
            except Exception as e:
                logger.error(f"Error getting data for {state}: {e}")
                continue
        
        return {
            "states": map_data,
            "last_updated": datetime.now(),
            "total_states": len(map_data)
        }
    
    def get_location_recommendations(self, location_data: LocationData) -> Dict[str, Any]:
        """Get location-specific recommendations for EMS optimization."""
        recommendations = {
            "solar_optimization": [],
            "battery_management": [],
            "grid_interaction": [],
            "cost_optimization": []
        }
        
        # Solar optimization recommendations
        if location_data.solar_potential["solar_potential_rating"] in ["Excellent", "Very Good"]:
            recommendations["solar_optimization"].append({
                "priority": "High",
                "recommendation": "Maximize solar generation - excellent solar potential in this location",
                "action": "Consider expanding solar capacity or optimizing panel orientation"
            })
        elif location_data.solar_potential["solar_potential_rating"] == "Poor":
            recommendations["solar_optimization"].append({
                "priority": "Medium",
                "recommendation": "Limited solar potential - focus on other renewable sources",
                "action": "Consider wind energy or grid-tied solutions"
            })
        
        # Battery management recommendations
        avg_tariff = np.mean(list(location_data.electricity_tariff.values()))
        if avg_tariff > 8.0:
            recommendations["battery_management"].append({
                "priority": "High",
                "recommendation": "High electricity tariffs - maximize battery usage",
                "action": "Increase battery capacity and optimize charging/discharging cycles"
            })
        
        # Grid interaction recommendations
        if location_data.carbon_intensity > 900:
            recommendations["grid_interaction"].append({
                "priority": "High",
                "recommendation": "High carbon intensity grid - minimize grid dependency",
                "action": "Prioritize renewable energy and battery storage"
            })
        
        # Cost optimization recommendations
        if location_data.renewable_percentage < 30:
            recommendations["cost_optimization"].append({
                "priority": "Medium",
                "recommendation": "Low renewable percentage - consider renewable energy investments",
                "action": "Evaluate solar/wind investments for long-term cost savings"
            })
        
        return recommendations
