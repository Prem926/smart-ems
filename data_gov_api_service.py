%%writefile IITG_VAI/services/data_gov_api_service.py
import requests
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataGovAPIService:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Base URL for a hypothetical Data.gov.in energy dataset
        self.base_url = "https://api.data.gov.in/resource/some_energy_resource_id"
        self.headers = {"X-API-KEY": self.api_key} if api_key else {}

    def fetch_data(self, params=None, fallback_data_generator=None, **kwargs):
        """
        Fetches data from Data.gov.in API. If API fails, uses fallback generator.
        """
        if not self.api_key:
            logging.warning("DataGov API key not provided. Falling back to synthetic data if available.")
            if fallback_data_generator:
                logging.info("Using synthetic data for DataGovAPIService.")
                return fallback_data_generator(**kwargs)
            return pd.DataFrame()

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            # Process data specific to Data.gov.in API response structure
            # This is a placeholder; actual parsing depends on the API's JSON format.
            if 'records' in data:
                df = pd.DataFrame(data['records'])
                # Assuming 'date' and 'value' columns for simplification
                if 'date' in df.columns and 'value' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['date'])
                    df = df.set_index('timestamp').sort_index()
                    return df[['value']] # Return relevant columns
            logging.warning("DataGov API response format not as expected or no 'records' key found.")
            return pd.DataFrame()
        except requests.exceptions.Timeout:
            logging.error("DataGov API request timed out.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from DataGov API: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while processing DataGov API response: {e}")

        # Fallback if API call fails
        if fallback_data_generator:
            logging.info("DataGov API failed. Using synthetic data for DataGovAPIService.")
            return fallback_data_generator(**kwargs)
        return pd.DataFrame()

    def fetch_state_wise_electricity_data(self, state=None, period_start=None, period_end=None):
        """
        Example method to fetch state-wise electricity data.
        Needs specific Data.gov.in resource ID and parameters.
        """
        params = {
            "api-key": self.api_key, # Some APIs might need key as param
            "format": "json",
            "filters[state]": state,
            "filters[start_date]": period_start.isoformat() if period_start else None,
            "filters[end_date]": period_end.isoformat() if period_end else None,
            "limit": 1000 # Example limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        logging.info(f"Fetching state-wise data for {state} with params: {params}")
        # Replace 'some_energy_resource_id' with the actual resource ID from Data.gov.in
        self.base_url = "https://api.data.gov.in/resource/YOUR_ACTUAL_ENERGY_RESOURCE_ID"
        
        # Placeholder for synthetic data generation specific to this method
        def generate_state_data(state_name, start, end):
            dates = pd.date_range(start=start, end=end, freq='D')
            data = {
                'timestamp': dates,
                'state': [state_name] * len(dates),
                'total_demand_gwh': np.random.uniform(50, 500, len(dates)).round(2),
                'renewable_share_percent': np.random.uniform(10, 60, len(dates)).round(2)
            }
            return pd.DataFrame(data).set_index('timestamp')

        # Dummy fallback: for a real implementation, you'd integrate generate_synthetic_data
        # from utils.data_generator and tailor it or create a specific one.
        fallback_params = {
            'state_name': state if state else 'Maharashtra',
            'start': period_start if period_start else (datetime.now() - timedelta(days=7)),
            'end': period_end if period_end else datetime.now()
        }
        
        # In a real setup, `fetch_data` would directly use `generate_synthetic_data` from `utils.data_generator`
        # for a more consistent fallback. For now, this internal one is a simple placeholder.
        return self.fetch_data(params=params, fallback_data_generator=generate_state_data, **fallback_params)

if __name__ == "__main__":
    from utils.config import GEMINI_API_KEY # Assuming you might use this for enhanced data
    data_service = DataGovAPIService(api_key="YOUR_DATAGOV_API_KEY_HERE") # Replace with actual
    
    # Example usage:
    # Fetch state-wise data for a week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print("Fetching data for Maharashtra (API key not set or failed, falling back to synthetic)...")
    maharashtra_data = data_service.fetch_state_wise_electricity_data(
        state="Maharashtra", period_start=start_date, period_end=end_date
    )
    print(maharashtra_data.head())
    
    print("\nFetching data for Karnataka (API key not set or failed, falling back to synthetic)...")
    karnataka_data = data_service.fetch_state_wise_electricity_data(
        state="Karnataka", period_start=start_date, period_end=end_date
    )
    print(karnataka_data.head())