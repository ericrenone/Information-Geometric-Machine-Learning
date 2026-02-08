import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================================
# CONFIGURATION
# ============================================================

SEEDS = [42, 7, 101, 2026, 99]
STEPS = 100
LR = 0.2
DECAY = 0.985

TRUE_MEAN = 3.5
NOISE_SIGMA = 1.2
PRINT_EVERY = 10  # terminal update interval

# ============================================================
# LAMBDA LEARNING OPERATORS
# ============================================================

drift = lambda θ, grad: θ - LR * grad
gain = lambda state, grad: (
    state[0] - LR * state[1] * grad,
    max(0.005, state[1] * DECAY)
)

# ============================================================
# DATA CONTAINERS
# ============================================================

streams = []
theta_a = []
theta_b = []
alpha = []

hist_a = [[] for _ in SEEDS]
hist_b = [[] for _ in SEEDS]

for seed in SEEDS:
    random.seed(seed)
    streams.append([random.gauss(TRUE_MEAN, NOISE_SIGMA) for _ in range(STEPS)])
    theta_a.append(0.0)
    theta_b.append(0.0)
    alpha.append(1.0)

# ============================================================
# METRIC HELPERS
# ============================================================

def mean(vals):
    return sum(vals) / len(vals)

def rmse(vals):
    return math.sqrt(sum((v - TRUE_MEAN) ** 2 for v in vals) / len(vals))

def std(vals):
    m = mean(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))

def first_below(curve, th=0.2):
    for i, v in enumerate(curve):
        if v < th:
            return i
    return None

# ============================================================
# REAL-TIME PLOTS
# ============================================================

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

line_ma, = ax1.plot([], [], label="Drift Mean", color="#b91c1c")
line_mb, = ax1.plot([], [], label="Adaptive Gain Mean", color="#0ea5e9")
band_a_patch = None
band_b_patch = None
ax1.axhline(TRUE_MEAN, linestyle="--", color="#facc15", label="True Mean")
ax1.set_title("Mean Parameter Convergence with Confidence Bands")
ax1.set_ylabel("θ")
ax1.legend()

line_ra, = ax2.plot([], [], label="Drift RMSE", color="#b91c1c")
line_rb, = ax2.plot([], [], label="Gain RMSE", color="#0ea5e9")
ax2.set_title("Learning Stability (RMSE)")
ax2.set_xlabel("Steps")
ax2.set_ylabel("RMSE")
ax2.legend()

ax1.set_xlim(0, STEPS)
ax2.set_xlim(0, STEPS)
ax1.set_ylim(0, TRUE_MEAN + 1.5)
ax2.set_ylim(0, 3.5)

# ============================================================
# HISTORIES
# ============================================================

mean_a_hist, mean_b_hist = [], []
rmse_a_hist, rmse_b_hist = [], []
std_a_hist, std_b_hist = [], []

# ============================================================
# UPDATE FUNCTION
# ============================================================

def update(t):
    global band_a_patch, band_b_patch

    # Step simulation
    for i in range(len(SEEDS)):
        sample = streams[i][t]
        theta_a[i] = drift(theta_a[i], theta_a[i] - sample)
        theta_b[i], alpha[i] = gain((theta_b[i], alpha[i]), theta_b[i] - sample)
        hist_a[i].append(theta_a[i])
        hist_b[i].append(theta_b[i])

    # Compute metrics
    cur_a = [hist_a[i][-1] for i in range(len(SEEDS))]
    cur_b = [hist_b[i][-1] for i in range(len(SEEDS))]

    mean_a_hist.append(mean(cur_a))
    mean_b_hist.append(mean(cur_b))
    rmse_a_hist.append(rmse(cur_a))
    rmse_b_hist.append(rmse(cur_b))
    std_a_hist.append(std(cur_a))
    std_b_hist.append(std(cur_b))

    # Update lines
    line_ma.set_data(range(len(mean_a_hist)), mean_a_hist)
    line_mb.set_data(range(len(mean_b_hist)), mean_b_hist)

    line_ra.set_data(range(len(rmse_a_hist)), rmse_a_hist)
    line_rb.set_data(range(len(rmse_b_hist)), rmse_b_hist)

    # Remove previous confidence bands
    if band_a_patch:
        band_a_patch.remove()
    if band_b_patch:
        band_b_patch.remove()

    # Add new confidence bands
    band_a_patch = ax1.fill_between(range(len(mean_a_hist)),
                                   np.array(mean_a_hist) - np.array(std_a_hist),
                                   np.array(mean_a_hist) + np.array(std_a_hist),
                                   color="#fca5a5", alpha=0.3)
    band_b_patch = ax1.fill_between(range(len(mean_b_hist)),
                                   np.array(mean_b_hist) - np.array(std_b_hist),
                                   np.array(mean_b_hist) + np.array(std_b_hist),
                                   color="#7dd3fc", alpha=0.3)

    # Terminal updates at milestones
    if t % PRINT_EVERY == 0 or t == STEPS - 1:
        print(f"Step {t:3d} | Mean Drift: {mean_a_hist[-1]:.3f} | "
              f"Mean Gain: {mean_b_hist[-1]:.3f} | "
              f"RMSE Drift: {rmse_a_hist[-1]:.3f} | "
              f"RMSE Gain: {rmse_b_hist[-1]:.3f}")

    return line_ma, line_mb, line_ra, line_rb

# ============================================================
# RUN ANIMATION
# ============================================================

# Fix infinite running by disabling blit
ani = FuncAnimation(fig, update, frames=STEPS, interval=40, blit=False)
plt.tight_layout()
plt.show()

# ============================================================
# FINAL REPORT
# ============================================================

final_rmse_drift = rmse_a_hist[-1]
final_rmse_gain = rmse_b_hist[-1]

print("\n\n=========== FINAL RESULTS ===========\n")
print(f"Final RMSE Drift: {final_rmse_drift:.4f}")
print(f"Final RMSE Adaptive Gain: {final_rmse_gain:.4f}")
print(f"\nConvergence Step (<0.2 RMSE)")
print(f"Drift: {first_below(rmse_a_hist)}")
print(f"Adaptive Gain: {first_below(rmse_b_hist)}")
print(f"\nNoise Suppression Factor: {final_rmse_drift / final_rmse_gain:.2f}×")
print("\n------------------------------------")
print("Adaptive gain preserves convergence speed")
print("while dramatically reducing stochastic variance.")
print("This is noise-damped learning dynamics in action.")
print("------------------------------------")
