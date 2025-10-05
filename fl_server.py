import flwr as fl
from typing import List, Tuple, Dict, Optional
from flwr.common import Metrics
from flwr.server.client_proxy import ClientProxy

class FedAvgWithMetrics(fl.server.strategy.FedAvg):
    def aggregate_evaluate(self, rnd: int, results: List[Tuple[ClientProxy, Dict[str, float]]], failures: List[BaseException]) -> Optional[float]:
        """Aggregate evaluation metrics across clients"""
        if not results:
            return None

        # Aggregate loss metrics
        loss_aggregated = sum([r[1]["loss"] * r[1]["num_examples"] for r in results]) / sum([r[1]["num_examples"] for r in results])
        
        print(f"Round {rnd} - Aggregated loss: {loss_aggregated}")
        return loss_aggregated

def start_server(num_rounds: int = 10, min_clients: int = 2):
    """Start Flower server for federated learning"""
    # Define strategy
    strategy = FedAvgWithMetrics(
        fraction_fit=1.0,  # Sample 100% of available clients for training
        fraction_evaluate=1.0,  # Sample 100% of available clients for evaluation
        min_fit_clients=min_clients,  # Minimum number of clients for training
        min_evaluate_clients=min_clients,  # Minimum number of clients for evaluation
        min_available_clients=min_clients,  # Minimum number of available clients
    )

    # Start server
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )

if __name__ == "__main__":
    start_server()