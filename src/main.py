from client import Client
from consensus import ConsensusAlgorithm
from server import Server
import random
import time

# Create a cluster of servers

def Cluster(server_settings):
    return [
        Server(
            id=s["id"],
            weight=s["weight"],
            failure_prob=s["failure_prob"],
            recovery_delay_min=s["recovery_delay_min"],
            recovery_delay_max=s["recovery_delay_max"]
        )
        for s in server_settings
    ]

def run_simulation(server_settings, retry_limit, retry_period_ms, ack_timeout_ms, num_updates=5):
    servers = Cluster(server_settings)
    consensus = ConsensusAlgorithm(servers=servers)
    client = Client(servers=servers, consensus=consensus)

    # Create and distribute the initial file

    client.create_initial_file(file_name="initial_file.txt", content="This is the initial content.")
    client.distribute_file()

    # Sequential updates

    for _ in range(num_updates):
        wait_time = random.randint(10, 30) / 1000.0
        print(f"Waiting for {wait_time * 1000:.1f} ms before the next update\n")
        time.sleep(wait_time)

        client.update_file()
        client.apply_update()
        consensus.retry_unresponsive_servers(client.current_file)

    # Retrieve the file

    restored_file = client.consensus.restore_consensus(
        retry_limit=retry_limit,
        retry_period_ms=retry_period_ms
    )

    return restored_file, client.current_file


if __name__ == "__main__":
    servers = [
        {"id": 1, "failure_prob": 0.1, "weight": 10, "recovery_delay_min": 10, "recovery_delay_max": 25},
        {"id": 2, "failure_prob": 0.2, "weight": 7,  "recovery_delay_min": 20, "recovery_delay_max": 35},
        {"id": 3, "failure_prob": 0.4, "weight": 2,  "recovery_delay_min": 25, "recovery_delay_max": 45},
    ]

    restored, expected = run_simulation(
        server_settings=servers,
        retry_limit=3,
        retry_period_ms=10,
        ack_timeout_ms=5,
        num_updates=5
    )

    print("\n========== FINAL RESTORE ==========")
    print("RESTORED FILE:", restored)
    print("EXPECTED VERSION:", expected.version)
