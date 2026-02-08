import random
import tkinter as tk

# ========== MASTER CONFIGURATION ==========
SEEDS = [42, 7, 101, 2026, 99]  # 5x Master Seeds
STEPS = 400
LR = 0.12
DECAY = 0.985
TRUE_MEAN = 3.5
NOISE_SIGMA = 1.2

# ========== LAMBDA CALCULUS CORE ==========
# Path A: Naive Drift (Reactive)
λ_drift = lambda θ, grad: θ - (LR * grad)

# Path B: Adaptive Gain (Predictive/Damped)
λ_gain = lambda state, grad: (
    state[0] - (LR * state[1] * grad),  # Theta update
    max(0.005, state[1] * DECAY)        # Alpha decay
)

# ========== LEARNING MACHINE INSTANCE ==========
class LearningMachine:
    def __init__(self, seed):
        random.seed(seed)
        self.stream = [random.gauss(TRUE_MEAN, NOISE_SIGMA) for _ in range(STEPS)]
        self.state_a = 0.0
        self.state_b = (0.0, 1.0)  # (Theta, Alpha)
        self.hist_a = []
        self.hist_b = []

    def transition(self, t):
        sample = self.stream[t]
        # Path A raw drift
        self.state_a = λ_drift(self.state_a, self.state_a - sample)
        # Path B adaptive gain (needs Path A signal)
        self.state_b = λ_gain(self.state_b, self.state_a - sample)
        # Store history
        self.hist_a.append(self.state_a)
        self.hist_b.append(self.state_b[0])

# ========== VISUALIZATION ==========
class FinalPopout:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual-Path Lambda: 5-Instance Adaptive Learning")
        self.canvas = tk.Canvas(root, width=1000, height=600, bg="#020617", highlightthickness=0)
        self.canvas.pack()

        # Create learning instances
        self.machines = [LearningMachine(s) for s in SEEDS]
        self.t = 0
        self.animate()

    def animate(self):
        if self.t < STEPS:
            for m in self.machines:
                m.transition(self.t)
            self.draw()
            self.t += 1
            self.root.after(15, self.animate)

    def draw(self):
        self.canvas.delete("all")
        mid, scale = 300, 50

        # Ground Truth Line
        horizon_y = mid - (TRUE_MEAN * scale)
        self.canvas.create_line(0, horizon_y, 1000, horizon_y, fill="#1e293b", width=1)

        # Draw all instances
        for m in self.machines:
            pts_a = [(i * (1000/STEPS), mid - (v * scale)) for i, v in enumerate(m.hist_a)]
            pts_b = [(i * (1000/STEPS), mid - (v * scale)) for i, v in enumerate(m.hist_b)]
            if len(pts_a) > 2:
                # Path A: Muted Red Drift
                self.canvas.create_line(pts_a, fill="#451a21", width=1, stipple="gray50")
                # Path B: Blue Adaptive Gain
                self.canvas.create_line(pts_b, fill="#0ea5e9", width=2)

        # Real-time Metrics HUD
        avg_a = sum(m.state_a for m in self.machines) / len(self.machines)
        avg_b = sum(m.state_b[0] for m in self.machines) / len(self.machines)
        avg_alpha = sum(m.state_b[1] for m in self.machines) / len(self.machines)

        hud_text = (
            f"STEP: {self.t}/{STEPS} | TARGET: {TRUE_MEAN}\n"
            f"PATH A (Drift) AVG: {avg_a:.3f} | ERROR: {abs(avg_a-TRUE_MEAN):.4f}\n"
            f"PATH B (Gain)  AVG: {avg_b:.3f} | ERROR: {abs(avg_b-TRUE_MEAN):.4f}\n"
            f"MEAN SENSITIVITY (α): {avg_alpha:.4f}"
        )
        self.canvas.create_text(20, 530, anchor="nw", fill="#94a3b8", font=("Consolas", 11), text=hud_text)

# ========== RUN SIMULATION ==========
if __name__ == "__main__":
    root = tk.Tk()
    FinalPopout(root)
    root.mainloop()
