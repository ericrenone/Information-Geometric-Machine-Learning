import random
import tkinter as tk

# ========== FIXED-POINT Q.16 HELPERS ==========
SHIFT = 16
SCALE = 1 << SHIFT  # 65536

def to_q16(f): return int(f * SCALE)
def from_q16(q): return q / SCALE
def q16_mul(a, b): return (a * b) >> SHIFT

# ========== PRODUCTION CONFIGURATION (FIXED) ==========
STEPS = 600
# Learning Rate (ETA) 0.12
FX_ETA = to_q16(0.12)
# Decay Factor (GAMMA) 0.985 
FX_GAMMA = to_q16(0.985)
# Target Mean (OMEGA) 3.5
FX_OMEGA = to_q16(3.5)
# Noise Magnitude 1.5
FX_SIGMA = to_q16(1.5)
# Minimum Sensitivity Floor (0.005)
FX_MIN_ALPHA = to_q16(0.005)

# ========== SYSTEM OPERATORS (Q.16) ==========

# Path 1: Reactive Estimator
# theta = theta - (eta * gradient)
def op_reactive(theta, grad):
    return theta - q16_mul(FX_ETA, grad)

# Path 2: Adaptive Estimator
# theta = theta - (eta * alpha * gradient)
# alpha = alpha * gamma
def op_adaptive(theta, alpha, grad):
    new_theta = theta - q16_mul(q16_mul(FX_ETA, alpha), grad)
    new_alpha = max(FX_MIN_ALPHA, q16_mul(alpha, FX_GAMMA))
    return new_theta, new_alpha

# ========== CORE LOGIC ENGINE ==========
class EstimatorCore:
    def __init__(self, seed):
        random.seed(seed)
        # Generate signal stream
        self.stream = [to_q16(random.gauss(3.5, 1.5)) for _ in range(STEPS)]
        
        self.p1_theta = 0
        self.p2_theta = 0
        self.p2_alpha = to_q16(1.0)
        
        self.hist_p1 = []
        self.hist_p2 = []

    def process_step(self, t):
        sample = self.stream[t]
        
        # Calculate local gradient
        grad = self.p1_theta - sample
        
        # Update Estimators
        self.p1_theta = op_reactive(self.p1_theta, grad)
        self.p2_theta, self.p2_alpha = op_adaptive(self.p2_theta, self.p2_alpha, grad)
        
        self.hist_p1.append(self.p1_theta)
        self.hist_p2.append(self.p2_theta)

# ========== VISUALIZATION ==========
class SystemDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Fixed-Point Q.16 Dual-Path Estimator")
        self.canvas = tk.Canvas(root, width=1200, height=600, bg="#020617", highlightthickness=0)
        self.canvas.pack()

        self.seeds = [42, 7, 101, 2026, 99]
        self.cores = [EstimatorCore(s) for s in self.seeds]
        self.t = 0
        self.run()

    def run(self):
        if self.t < STEPS:
            for c in self.cores:
                c.process_step(self.t)
            self.draw()
            self.t += 1
            self.root.after(10, self.run)

    def draw(self):
        self.canvas.delete("all")
        mid, h_scale = 300, 50
        w_scale = 1200 / STEPS

        # Target Baseline (OMEGA)
        target_y = mid - (from_q16(FX_OMEGA) * h_scale)
        self.canvas.create_line(0, target_y, 1200, target_y, fill="#1e293b", dash=(4,4))

        for c in self.cores:
            pts_p1 = [(i * w_scale, mid - (from_q16(v) * h_scale)) for i, v in enumerate(c.hist_p1)]
            pts_p2 = [(i * w_scale, mid - (from_q16(v) * h_scale)) for i, v in enumerate(c.hist_p2)]
            
            if len(pts_p1) > 2:
                self.canvas.create_line(pts_p1, fill="#450a0a", width=1) # Reactive
                self.canvas.create_line(pts_p2, fill="#0ea5e9", width=2) # Adaptive

        # Telemetry HUD
        p1_val = from_q16(self.cores[0].p1_theta)
        p2_val = from_q16(self.cores[0].p2_theta)
        alpha_val = from_q16(self.cores[0].p2_alpha)
        
        telemetry = (
            f"TIME STEP: {self.t}/{STEPS}\n"
            f"REACTIVE PATH VALUE: {p1_val:.4f}\n"
            f"ADAPTIVE PATH VALUE: {p2_val:.4f}\n"
            f"ADAPTIVE GAIN (ALPHA): {alpha_val:.5f}"
        )
        self.canvas.create_text(30, 500, anchor="nw", fill="#94a3b8", font=("Consolas", 11), text=telemetry)

if __name__ == "__main__":
    root = tk.Tk()
    SystemDashboard(root)
    root.mainloop()