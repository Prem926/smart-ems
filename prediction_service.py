%%writefile IITG_VAI/services/prediction_service.py
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from prophet import Prophet
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PredictionService:
    def __init__(self, models_dir):
        self.models_dir = models_dir
        self.solar_scaler = MinMaxScaler()
        self.load_scaler = MinMaxScaler()
        self.solar_model = None
        self.prophet_model = None
        self.load_lstm_model = None

    def _create_lstm_model(self, input_shape, output_steps):
        model = Sequential([
            LSTM(64, activation='relu', input_shape=input_shape, return_sequences=True),
            LSTM(32, activation='relu'),
            Dense(output_steps)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def train_solar_forecast_model(self, data, features, target_col='solar_generation_kw', output_steps=24, look_back=24):
        """
        Trains an LSTM model for solar generation forecasting.
        Data should be preprocessed and feature-engineered.
        """
        if data.empty or target_col not in data.columns:
            logging.warning(f"Insufficient data or missing target column '{target_col}' for solar forecasting.")
            return False

        df = data[features + [target_col]].copy()
        
        # Scale the target column for LSTM
        scaled_target = self.solar_scaler.fit_transform(df[[target_col]])
        df[target_col + '_scaled'] = scaled_target

        X, y = [], []
        for i in range(len(df) - look_back - output_steps + 1):
            X.append(df.iloc[i:(i + look_back)][features].values)
            y.append(df.iloc[(i + look_back):(i + look_back + output_steps)][target_col + '_scaled'].values)

        if not X:
            logging.warning("Not enough data to create sequences for solar LSTM training.")
            return False
            
        X = np.array(X)
        y = np.array(y)

        self.solar_model = self._create_lstm_model(input_shape=(look_back, X.shape[2]), output_steps=output_steps)
        logging.info("Training Solar Forecast LSTM model...")
        self.solar_model.fit(X, y, epochs=50, batch_size=32, verbose=0)
        self.solar_model.save(os.path.join(self.models_dir, 'solar_forecast.h5'))
        logging.info("Solar Forecast model trained and saved.")
        return True

    def predict_solar_generation(self, current_data_slice, features, output_steps=24, look_back=24):
        if self.solar_model is None:
            solar_model_path = os.path.join(self.models_dir, 'solar_forecast.h5')
            if os.path.exists(solar_model_path):
                self.solar_model = load_model(solar_model_path)
                logging.info("Loaded pre-trained Solar Forecast model.")
            else:
                logging.warning("Solar Forecast model not trained or found. Returning dummy prediction.")
                return np.zeros(output_steps) # Dummy prediction

        # Ensure current_data_slice has enough history and correct features
        if len(current_data_slice) < look_back:
            logging.warning(f"Not enough historical data ({len(current_data_slice)} rows) for solar prediction (needs {look_back} rows).")
            # Pad with zeros or earlier data if possible, or raise error
            return np.zeros(output_steps) # Dummy prediction

        input_data = current_data_slice[features].tail(look_back).values.reshape(1, look_back, -