---
noteID: 02411b9e-33c0-4879-ba42-075eae9c2c1b
---
# CS130: Software Engineering
## Homework 2
### Winter 2025
#### Jan Kasen
#### Due Mar 12 2025 11:55pm

## Problem 1: SMT Formulas and Z3 Implementation

The first problem involves analyzing code paths, generating SMT formulas, and implementing constraints using Z3.

### Files:
- `docs/HW2.md`: Contains all the SMT formulas, test inputs, and analysis for Problem 1
- `code/problem1.py`: Z3 implementation for the "All Positive" SMT constraint

### Running the Z3 Implementation:
```
python code/problem1.py
```

## Problem 2: Cloud Service Monitoring System

The second problem involves implementing a monitoring system that tracks latency and failure rates, triggers alerts based on thresholds, and handles notifications.

### Features:
- Metric generation using Poisson distribution
- Alert classification (P0, P1, P2) based on severity
- Notification handling with appropriate intervals
- Alert resolution and escalation
- Logging and cleanup of old logs

### Files:
- `code/problem2.py`: Complete implementation of the monitoring system

### Running the Monitoring System:
```
python code/problem2.py
```

The system will generate metrics every 5 minutes, check for alert conditions, and log the results to the console.

## Documentation

For detailed explanations of the solutions, refer to `docs/HW2.md`.
