# Distributed consensus in a star topology

This repository contains Python code for simulating and evaluating a consensus protocol designed to maintain a replicated file across external and potentially unreliable servers arranged in a star topology.

The simulation models failures, delays, and temporary unavailability of the servers in order to analyse how the protocol behaves under different reliability conditions and whether it can correctly restore the latest version of the file.

The implementation is organised as a modular framework: the logic of each component (client, servers, and consensus mechanism) is encapsulated in separate modules.  
This structure makes it easy to modify, extend, or experiment with the behaviour of individual agents and with different consensus strategies.


## Repository structure

```text
src/
  main.py               # Runs a single simulation scenario (updates + final restore)
  client.py             # Client logic: creates file versions and coordinates update/restore
  server.py             # Server model with failures, recovery delays and replica storage
  file.py               # File abstraction: content, versioning and basic validation
  consensus.py          # Consensus mechanism for update and restore phases (majority + weighted fallback)
  simulation_runner.py  # Runs multiple scenarios and collects accuracy metrics into CSV outputs
```

## How to run

To execute a single simulation scenario:

```bash
python src/main.py
```

To execute a full batch of scenarios and collect accuracy metrics:

```bash
python src/simulation_runner.py
```

## Requirements

This project uses only the Python standard library.



