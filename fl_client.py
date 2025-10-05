import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from collections import OrderedDict
import flwr as fl

class TimeSeriesDataset(Dataset):
    def __init__(self, data, seq_length=24):
        self.data = torch.FloatTensor(data)
        self.seq_length = seq_length

    def __len__(self):
        return len(self.data) - self.seq_length

    def __getitem__(self, idx):
        x = self.data[idx:idx + self.seq_length]
        y = self.data[idx + self.seq_length]
        return x, y

class LSTMForecaster(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(LSTMForecaster, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])
        return predictions

class FLClient(fl.client.NumPyClient):
    def __init__(self, plant_data, feature_columns):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.feature_columns = feature_columns
        
        # Prepare data
        self.data = plant_data[feature_columns].values
        self.dataset = TimeSeriesDataset(self.data)
        self.dataloader = DataLoader(self.dataset, batch_size=32, shuffle=True)
        
        # Initialize model
        self.model = LSTMForecaster(len(feature_columns)).to(self.device)
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters())

    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        
        # Training loop
        self.model.train()
        total_loss = 0
        for epoch in range(config["local_epochs"]):
            for batch_x, batch_y in self.dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                self.optimizer.zero_grad()
                y_pred = self.model(batch_x)
                loss = self.criterion(y_pred, batch_y)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()

        # Return updated model parameters and metrics
        return self.get_parameters(config), len(self.dataloader), {"loss": total_loss / len(self.dataloader)}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        
        # Evaluation loop
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in self.dataloader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                y_pred = self.model(batch_x)
                loss = self.criterion(y_pred, batch_y)
                total_loss += loss.item()

        return total_loss, len(self.dataloader), {"loss": total_loss / len(self.dataloader)}

def start_client(plant_data, feature_columns, server_address):
    """Start a Flower client for federated learning"""
    client = FLClient(plant_data, feature_columns)
    fl.client.start_numpy_client(server_address, client=client)