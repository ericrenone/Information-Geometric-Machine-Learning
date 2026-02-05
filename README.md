# Dual-Path Convergence: KL Drift vs Gain Control

Real-time visualization comparing two distinct optimization strategies that both minimize variational free energy through different mechanisms.

## Overview

This simulation demonstrates how gradient descent can achieve the same objective (minimizing KL divergence) through two fundamentally different paths:

- **Purification Path**: Direct geometric correction toward the target
- **Annealing Path**: Adaptive gain scaling that decays learning sensitivity

Both regimes minimize the same variational free-energy functional but employ different optimization dynamics.


## What It Shows

The visualization tracks three key metrics across 100 optimization steps:

1. **Information Drift (KL Divergence)** - Distance from true distribution (no clipping)
2. **Prediction Loss (MSE)** - Mean squared error on sampled data  
3. **Sensitivity Parameter α** - Adaptive learning gain (annealing path only)

## Architecture

### Core Components

**`SimulationState`** - Manages dual-path optimization state
- Generates Gaussian samples from true distribution N(μ=2.0, σ=1.0)
- Computes variational free-energy gradients
- Updates θ via two parallel gradient descent regimes
- Tracks full KL divergence and prediction loss (no arbitrary clipping)

**`PlotCanvas`** - Modular plotting component
- Encapsulates rendering logic for reusability
- Auto-scaled axes with gridlines
- Smooth anti-aliased line plots
- Dynamic legends for multi-series data

**`SimulationWindow`** - Main application controller
- Coordinates UI layout and event handling
- Real-time metric updates (50ms refresh)
- Clean separation of concerns (MVC pattern)

### Key Functions

## Theoretical Foundations

Both optimization regimes minimize the variational free energy:
```
F = E_q[log q - log p]
```

Where `q` is the learned distribution and `p` is the true (target) distribution.

- **Purification** reduces KL by direct geometric correction
- **Annealing** achieves the same via sensitivity reduction

This demonstrates that multiple optimization dynamics can converge to the same information-theoretic objective.
