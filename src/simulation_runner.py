import os
import pandas as pd
from main import run_simulation

os.makedirs("simulation_results", exist_ok=True)

# Configurations to test

configs = [
    {
        "name": "Stress_test", # worst case
        "retry_limit": 1,
        "retry_period_ms": 5,
        "ack_timeout_ms": 2,
        "server_settings": [
            {"id": 1, "failure_prob": 0.4, "weight": 10, "recovery_delay_min": 30, "recovery_delay_max": 50},
            {"id": 2, "failure_prob": 0.5, "weight": 5,  "recovery_delay_min": 40, "recovery_delay_max": 60},
            {"id": 3, "failure_prob": 0.6, "weight": 2,  "recovery_delay_min": 50, "recovery_delay_max": 70},
        ]
    },
    {
            "name": "Higher_retry", # test retry in the worst case
            "retry_limit": 5,
            "retry_period_ms": 20,
            "ack_timeout_ms": 10,
            "server_settings": [
                {"id": 1, "failure_prob": 0.4, "weight": 10, "recovery_delay_min": 30, "recovery_delay_max": 50},
                {"id": 2, "failure_prob": 0.5, "weight": 5,  "recovery_delay_min": 40, "recovery_delay_max": 60},
                {"id": 3, "failure_prob": 0.6, "weight": 2,  "recovery_delay_min": 50, "recovery_delay_max": 70},
            ]
    },
    {
            "name": "Low_retry_High_failure", # bad case
            "retry_limit": 3,
            "retry_period_ms": 10,
            "ack_timeout_ms": 5,
            "server_settings": [
                {"id": 1, "failure_prob": 0.2, "weight": 10, "recovery_delay_min": 15, "recovery_delay_max": 25},
                {"id": 2, "failure_prob": 0.3, "weight": 7,  "recovery_delay_min": 20, "recovery_delay_max": 30},
                {"id": 3, "failure_prob": 0.5, "weight": 2,  "recovery_delay_min": 25, "recovery_delay_max": 35},
            ]
    },
    {
        "name": "High_retry_Medium_failure", # medium (realistic) case
        "retry_limit": 5,
        "retry_period_ms": 20,
        "ack_timeout_ms": 10,
        "server_settings": [
            {"id": 1, "failure_prob": 0.1, "weight": 10, "recovery_delay_min": 5,  "recovery_delay_max": 15},
            {"id": 2, "failure_prob": 0.2, "weight": 7,  "recovery_delay_min": 15, "recovery_delay_max": 25},
            {"id": 3, "failure_prob": 0.3, "weight": 2,  "recovery_delay_min": 20, "recovery_delay_max": 30},
        ]
    },
    {
        "name": "Reliable", # best case
        "retry_limit": 3,
        "retry_period_ms": 10,
        "ack_timeout_ms": 5,
        "server_settings": [
            {"id": 1, "failure_prob": 0.05, "weight": 10, "recovery_delay_min": 5,  "recovery_delay_max": 15},
            {"id": 2, "failure_prob": 0.1,  "weight": 9,  "recovery_delay_min": 8,  "recovery_delay_max": 18},
            {"id": 3, "failure_prob": 0.1,  "weight": 8,  "recovery_delay_min": 10, "recovery_delay_max": 20},
        ]
    },

    {
       "name": "Low_retry_Low_failure", # good servers but strict protocol
       "retry_limit": 1,
       "retry_period_ms": 5,
       "ack_timeout_ms": 2,
       "server_settings": [
           {"id": 1, "failure_prob": 0.05, "weight": 10, "recovery_delay_min": 10, "recovery_delay_max": 25},
           {"id": 2, "failure_prob": 0.1, "weight": 9, "recovery_delay_min": 12, "recovery_delay_max": 30},
           {"id": 3, "failure_prob": 0.1, "weight": 8, "recovery_delay_min": 15, "recovery_delay_max": 35},
       ]
    },
    {
       "name": "High_Retry_High_Latency", # latency on recovery
       "retry_limit": 6,
       "retry_period_ms": 20,
       "ack_timeout_ms": 12,
       "server_settings": [
           {"id": 1, "failure_prob": 0.1, "weight": 10, "recovery_delay_min": 30, "recovery_delay_max": 60},
           {"id": 2, "failure_prob": 0.2, "weight": 7,  "recovery_delay_min": 25, "recovery_delay_max": 55},
           {"id": 3, "failure_prob": 0.3, "weight": 5,  "recovery_delay_min": 20, "recovery_delay_max": 50},
       ]
    },
    {
       "name": "Weight_fallback_test", # with 4 servers is better (majority of 2 and 3 could prevent the wighted fallback)
       "retry_limit": 3,
       "retry_period_ms": 10,
       "ack_timeout_ms": 6,
       "server_settings": [
           {"id": 1, "failure_prob": 0.1, "weight": 10, "recovery_delay_min": 10, "recovery_delay_max": 25},
           {"id": 2, "failure_prob": 0.5, "weight": 3, "recovery_delay_min": 10, "recovery_delay_max": 20},
           {"id": 3, "failure_prob": 0.5, "weight": 2, "recovery_delay_min": 10, "recovery_delay_max": 20},
       ]
    },

]


summary = []

for config in configs:
    print(f"\n Running configuration: {config['name']}")
    restore_success_count = 0

    # 100 simulazioni
    for i in range(100):
        restored, expected = run_simulation(
            server_settings=config["server_settings"],
            retry_limit=config["retry_limit"],
            retry_period_ms=config["retry_period_ms"],
            ack_timeout_ms=config["ack_timeout_ms"],
            num_updates=5
        )

        if restored and restored["version"] == expected.version:
            restore_success_count += 1

    accuracy = restore_success_count / 100

    summary.append({
        "Config": config["name"],
        "retry_limit": config["retry_limit"],
        "retry_period_ms": config["retry_period_ms"],
        "ack_timeout_ms": config["ack_timeout_ms"],
        "failure_probs": [s["failure_prob"] for s in config["server_settings"]],
        "recovery_delays": [(s["recovery_delay_min"], s["recovery_delay_max"]) for s in config["server_settings"]],
        "weights": [s["weight"] for s in config["server_settings"]],
        "restore_accuracy": round(accuracy, 3)
    })

# Save CSV

df_summary = pd.DataFrame(summary)
df_summary.to_csv("simulation_results/summary_accuracy.csv", index=False, sep=";")
