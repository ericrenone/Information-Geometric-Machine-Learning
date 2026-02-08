import random
import tkinter as tk

# ========== Q16.16 FIXED-POINT ENGINE ==========
SHIFT = 16
ONE = 1 << SHIFT
PRECISION = 1.0 / ONE

def to_q(f): return int(f * ONE)
def from_q(q): return q * PRECISION
def mul_q(a, b): return (a * b) >> SHIFT

# ========== MASTER CONFIGURATION ==========
MASTER_SEED = 42
STEPS = 400
# Hyperparameters in Q-format
Q_LR = to_q(0.12)
Q_DECAY = to_q(0.985)
Q_TRUE_MEAN = to_q(3.5)
Q_NOISE_SIGMA = to_q(1.2)

# ========== THE LAMBDA CALCULUS CORE (FIXED-POINT) ==========
# Path A: Naive Q-Drift
λ_drift = lambda q_θ, q_grad: q_θ - mul_q(Q_LR, q_grad)

# Path B: Adaptive Q-Gain (q_theta, q_alpha)
λ_gain = lambda state, q_grad: (
    state[0] - mul_q(mul_q(Q_LR, state[1]), q_grad), 
    max(to_q(0.005), mul_q(state[1], Q_DECAY))
)

class QLearningMachine:
    def __init__(self, seed):
        random.seed(seed)
        self.q_state_a = to_q(0.0)
        self.q_state_b = (to_q(0.0), ONE) # (θ, α=1.0)
        self.history_a, self.history_b = [], []

    def step(self):
        # GPT-style data generation
        sample = random.gauss(from_q(Q_TRUE_MEAN), from_q(Q_NOISE_SIGMA))
        q_sample = to_q(sample)
        
        # Calculate Gradients (Error Signals)
        q_grad_a = self.q_state_a - q_sample
        q_grad_b = self.q_state_b[0] - q_sample
        
        # Atomic Lambda Transitions
        self.q_state_a = λ_drift(self.q_state_a, q_grad_a)
        self.q_state_b = λ_gain(self.q_state_b, q_grad_b)
        
        self.history_a.append(from_q(self.q_state_a))
        self.history_b.append(from_q(self.q_state_b[0]))

class ProdVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Q16.16 Fixed-Point Lambda Learning [Seed: {MASTER_SEED}]")
        self.canvas = tk.Canvas(root, width=1000, height=500, bg="#020617")
        self.canvas.pack()
        
        self.machine = QLearningMachine(MASTER_SEED)
        self.t = 0
        self.animate()

    def animate(self):
        if self.t < STEPS:
            self.machine.step()
            self.draw()
            self.t += 1
            self.root.after(10, self.animate)

    def draw(self):
        self.canvas.delete("all")
        m, scale = 250, 50
        
        # Ground Truth
        ty = m - (from_q(Q_TRUE_MEAN) * scale)
        self.canvas.create_line(0, ty, 1000, ty, fill="#1e293b", width=1)
        
        # Paths
        for hist, col, stp in [(self.machine.history_a, "#f43f5e", "gray50"), 
                               (self.machine.history_b, "#0ea5e9", None)]:
            pts = [(i * (1000/STEPS), m - (v * scale)) for i, v in enumerate(hist)]
            if len(pts) > 2:
                self.canvas.create_line(pts, fill=col, width=2, stipple=stp)

        # Production HUD
        self.canvas.create_text(20, 480, anchor="sw", fill="#94a3b8", font=("Consolas", 10),
            text=f"Q16.16 DOMAIN | STEP: {self.t} | GAIN (α): {from_q(self.machine.q_state_b[1]):.4f}")

if __name__ == "__main__":
    root = tk.Tk()
    ProdVisualizer(root)
    root.mainloop()