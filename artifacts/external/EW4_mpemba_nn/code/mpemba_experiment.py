"""
M-EXT4 — Mpemba Effect in NN Parameter Dynamics
Pilot & Confirmatory Experiment Code

Protocol: M-EXT4-MPEMBA-v1
Preregistration: PREREG.md (locked)
"""

import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, Subset
import time
from pathlib import Path

# ========== Configuration ==========

class Config:
    """Experiment configuration (immutable, from prereg)"""
    # Architecture
    input_dim = 784  # MNIST flattened
    hidden_dim = 128
    output_dim = 10
    
    # Training
    lr = 0.01
    batch_size = 128
    max_steps = 5000
    monitor_every = 10
    
    # Hot/Cold construction
    sigma_hot_factor = 2.0  # σ_hot = 2.0 * H_e
    sigma_cold_factor = 0.3  # σ_cold = 0.3 * H_e
    
    # Target definition
    target_epsilon_factor = 0.1  # ε = 0.1 * D(θ_rand, θ*)
    convergence_threshold = 0.01  # Train loss < 0.01 for θ* convergence
    
    # Calibration set size (for KL distance)
    calib_size = 1000
    
    # Multi-modality exclusion (C9)
    final_loss_diff_threshold = 0.05
    
    # Sharpness monitoring (C8)
    sharpness_every = 100
    lanczos_iters = 50


# ========== Model ==========

class MLP2Layer(nn.Module):
    """2-layer MLP as specified in prereg"""
    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x):
        x = x.view(x.size(0), -1)  # Flatten
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# ========== Distance Metrics ==========

def compute_distance_L2(theta, theta_star, model_template):
    """Parameter-space L2 distance (V2 formulation)"""
    dist = 0.0
    for (name, p), (_, p_star) in zip(model_template.named_parameters(), theta_star.items()):
        dist += torch.sum((p - p_star) ** 2).item()
    return np.sqrt(dist)


def compute_distance_KL(model, model_star, data_loader, device='cpu'):
    """KL-based distance (V1 formulation)
    D_KL(θ, θ*) = E_x [ KL( p(y|x,θ*) || p(y|x,θ) ) ]
    """
    model.eval()
    model_star.eval()
    kl_sum = 0.0
    count = 0
    
    with torch.no_grad():
        for x, _ in data_loader:
            x = x.to(device)
            logits_star = model_star(x)
            logits = model(x)
            
            p_star = F.softmax(logits_star, dim=-1)
            log_p = F.log_softmax(logits, dim=-1)
            
            # KL(p* || p) = sum_i p*_i log(p*_i / p_i) = sum_i p*_i (log p*_i - log p_i)
            kl = torch.sum(p_star * (F.log_softmax(logits_star, dim=-1) - log_p), dim=-1)
            kl_sum += torch.sum(kl).item()
            count += x.size(0)
    
    model.train()
    model_star.train()
    return kl_sum / count if count > 0 else 0.0


def compute_loss(model, data_loader, device='cpu'):
    """Compute average cross-entropy loss"""
    model.eval()
    loss_sum = 0.0
    count = 0
    
    with torch.no_grad():
        for x, y in data_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = F.cross_entropy(logits, y, reduction='sum')
            loss_sum += loss.item()
            count += x.size(0)
    
    model.train()
    return loss_sum / count if count > 0 else 0.0


def compute_accuracy(model, data_loader, device='cpu'):
    """Compute classification accuracy"""
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for x, y in data_loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            pred = torch.argmax(logits, dim=-1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    
    model.train()
    return correct / total if total > 0 else 0.0


def estimate_he(model):
    """Estimate H_e: mean of Kaiming init scales"""
    scales = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() >= 2:
            fan_in = param.shape[1]
            scale = np.sqrt(2.0 / fan_in)
            scales.append(scale)
    return np.mean(scales) if scales else 0.1


# ========== Initialization ==========

def init_reference_model(config, device='cpu'):
    """Initialize reference model θ_ref with Kaiming uniform"""
    model = MLP2Layer(config.input_dim, config.hidden_dim, config.output_dim).to(device)
    for name, param in model.named_parameters():
        if 'weight' in name:
            nn.init.kaiming_uniform_(param, a=np.sqrt(5))
        elif 'bias' in name:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(model.fc1.weight if 'fc1' in name else model.fc2.weight)
            bound = 1 / np.sqrt(fan_in)
            nn.init.uniform_(param, -bound, bound)
    return model


def perturb_parameters(model_star, sigma, seed, device='cpu'):
    """Perturb θ* with Gaussian noise: θ ~ N(θ*, σ^2 I)"""
    rng = np.random.default_rng(seed)
    model = MLP2Layer(Config.input_dim, Config.hidden_dim, Config.output_dim).to(device)
    
    with torch.no_grad():
        for (name, p), (_, p_star) in zip(model.named_parameters(), model_star.named_parameters()):
            noise = torch.from_numpy(rng.normal(0, sigma, p.shape)).float().to(device)
            p.copy_(p_star + noise)
    
    return model


# ========== Training ==========

def train_step(model, optimizer, x, y, device='cpu'):
    """Single SGD step"""
    x, y = x.to(device), y.to(device)
    optimizer.zero_grad()
    logits = model(x)
    loss = F.cross_entropy(logits, y)
    loss.backward()
    optimizer.step()
    return loss.item()


def train_to_convergence(model, train_loader, config, device='cpu', max_steps=10000):
    """Train reference model to convergence (θ_ref)"""
    optimizer = torch.optim.SGD(model.parameters(), lr=config.lr)
    
    for step in range(max_steps):
        for x, y in train_loader:
            loss = train_step(model, optimizer, x, y, device)
            
            if step % 100 == 0:
                avg_loss = compute_loss(model, train_loader, device)
                print(f"  Step {step}, Loss: {avg_loss:.4f}")
                if avg_loss < config.convergence_threshold:
                    print(f"  Converged at step {step}")
                    return step
    
    print(f"  Max steps {max_steps} reached")
    return max_steps


# ========== Experiment Runner ==========

class MpembaExperiment:
    """Single hot-vs-cold experiment run"""
    
    def __init__(self, config, theta_star_state, he_scale, 
                 seed_hot, seed_cold, seed_batch,
                 train_loader, test_loader, calib_loader,
                 device='cpu'):
        self.config = config
        self.device = device
        self.he_scale = he_scale
        
        # Seeds
        self.seed_hot = seed_hot
        self.seed_cold = seed_cold
        self.seed_batch = seed_batch
        
        # Data loaders
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.calib_loader = calib_loader
        
        # Theta star (reference)
        self.model_star = MLP2Layer(config.input_dim, config.hidden_dim, config.output_dim).to(device)
        self.model_star.load_state_dict(theta_star_state)
        self.model_star.eval()
        
        # Hot & Cold models
        sigma_hot = config.sigma_hot_factor * he_scale
        sigma_cold = config.sigma_cold_factor * he_scale
        
        self.model_hot = perturb_parameters(self.model_star, sigma_hot, seed_hot, device)
        self.model_cold = perturb_parameters(self.model_star, sigma_cold, seed_cold, device)
        
        # Check initial condition: D_hot(0) > D_cold(0)
        d_hot_0 = self.compute_distance_hot()
        d_cold_0 = self.compute_distance_cold()
        
        if d_hot_0 <= d_cold_0:
            print(f"WARNING: Initial condition violated: D_hot={d_hot_0:.4f} <= D_cold={d_cold_0:.4f}")
            self.valid_initial_condition = False
        else:
            self.valid_initial_condition = True
            print(f"Initial condition OK: D_hot={d_hot_0:.4f} > D_cold={d_cold_0:.4f}")
        
        # Target epsilon
        model_rand = init_reference_model(config, device)
        d_rand = compute_distance_KL(model_rand, self.model_star, calib_loader, device)
        self.target_epsilon = config.target_epsilon_factor * d_rand
        print(f"Target epsilon: {self.target_epsilon:.4f} (10% of random-init distance {d_rand:.4f})")
        
        # Optimizers
        self.opt_hot = torch.optim.SGD(self.model_hot.parameters(), lr=config.lr)
        self.opt_cold = torch.optim.SGD(self.model_cold.parameters(), lr=config.lr)
        
        # Trajectory storage
        self.history = {
            'step': [],
            'd_hot_train': [],
            'd_cold_train': [],
            'd_hot_test': [],
            'd_cold_test': [],
            'loss_hot_train': [],
            'loss_cold_train': [],
            'loss_hot_test': [],
            'loss_cold_test': [],
        }
        
        self.tau_hot_test = None
        self.tau_cold_test = None
    
    def compute_distance_hot(self, use_test=False):
        """Compute distance D(θ_hot, θ*) — KL-based (V1)"""
        loader = self.test_loader if use_test else self.calib_loader
        return compute_distance_KL(self.model_hot, self.model_star, loader, self.device)
    
    def compute_distance_cold(self, use_test=False):
        """Compute distance D(θ_cold, θ*) — KL-based (V1)"""
        loader = self.test_loader if use_test else self.calib_loader
        return compute_distance_KL(self.model_cold, self.model_star, loader, self.device)
    
    def run(self):
        """Run training for T_max steps, monitor distances"""
        if not self.valid_initial_condition:
            print("Skipping run due to invalid initial condition")
            return None
        
        print(f"\nStarting training for {self.config.max_steps} steps...")
        
        # Prepare batches (same order for hot and cold)
        torch.manual_seed(self.seed_batch)
        batch_iter = iter(self.train_loader)
        
        for step in range(self.config.max_steps):
            # Get batch (same for hot and cold)
            try:
                x, y = next(batch_iter)
            except StopIteration:
                batch_iter = iter(self.train_loader)
                x, y = next(batch_iter)
            
            # Train step
            train_step(self.model_hot, self.opt_hot, x, y, self.device)
            train_step(self.model_cold, self.opt_cold, x, y, self.device)
            
            # Monitor
            if step % self.config.monitor_every == 0:
                d_hot_train = self.compute_distance_hot(use_test=False)
                d_cold_train = self.compute_distance_cold(use_test=False)
                d_hot_test = self.compute_distance_hot(use_test=True)
                d_cold_test = self.compute_distance_cold(use_test=True)
                
                loss_hot_train = compute_loss(self.model_hot, self.train_loader, self.device)
                loss_cold_train = compute_loss(self.model_cold, self.train_loader, self.device)
                loss_hot_test = compute_loss(self.model_hot, self.test_loader, self.device)
                loss_cold_test = compute_loss(self.model_cold, self.test_loader, self.device)
                
                self.history['step'].append(step)
                self.history['d_hot_train'].append(d_hot_train)
                self.history['d_cold_train'].append(d_cold_train)
                self.history['d_hot_test'].append(d_hot_test)
                self.history['d_cold_test'].append(d_cold_test)
                self.history['loss_hot_train'].append(loss_hot_train)
                self.history['loss_cold_train'].append(loss_cold_train)
                self.history['loss_hot_test'].append(loss_hot_test)
                self.history['loss_cold_test'].append(loss_cold_test)
                
                # Check first-passage (test set)
                if self.tau_hot_test is None and d_hot_test < self.target_epsilon:
                    self.tau_hot_test = step
                    print(f"  Hot reached target at step {step} (D_test={d_hot_test:.4f})")
                
                if self.tau_cold_test is None and d_cold_test < self.target_epsilon:
                    self.tau_cold_test = step
                    print(f"  Cold reached target at step {step} (D_test={d_cold_test:.4f})")
                
                if step % 100 == 0:
                    print(f"Step {step}: D_hot_test={d_hot_test:.4f}, D_cold_test={d_cold_test:.4f}, "
                          f"L_hot_test={loss_hot_test:.4f}, L_cold_test={loss_cold_test:.4f}")
        
        # Final check
        print(f"\nFinal step {self.config.max_steps}:")
        print(f"  τ_hot_test = {self.tau_hot_test}")
        print(f"  τ_cold_test = {self.tau_cold_test}")
        print(f"  Hot wins: {self.tau_hot_test < self.tau_cold_test if self.tau_hot_test and self.tau_cold_test else 'N/A'}")
        
        # Check C9 (multi-modality)
        final_loss_hot = self.history['loss_hot_train'][-1]
        final_loss_cold = self.history['loss_cold_train'][-1]
        final_loss_diff = abs(final_loss_hot - final_loss_cold)
        
        if final_loss_diff > self.config.final_loss_diff_threshold:
            print(f"WARNING: Final loss difference {final_loss_diff:.4f} > threshold {self.config.final_loss_diff_threshold:.4f} (C9 exclusion)")
            self.excluded_c9 = True
        else:
            self.excluded_c9 = False
        
        return {
            'seed_hot': self.seed_hot,
            'seed_cold': self.seed_cold,
            'seed_batch': self.seed_batch,
            'tau_hot_test': self.tau_hot_test,
            'tau_cold_test': self.tau_cold_test,
            'hot_wins': self.tau_hot_test < self.tau_cold_test if (self.tau_hot_test and self.tau_cold_test) else None,
            'excluded_c9': self.excluded_c9,
            'history': self.history,
        }


# ========== Main Entry Point ==========

def prepare_mnist_data(config, device='cpu'):
    """Load MNIST and prepare data loaders"""
    try:
        from torchvision import datasets, transforms
    except ImportError:
        print("ERROR: torchvision not installed. Install with: pip install torchvision")
        return None, None, None
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST normalization
    ])
    
    train_dataset = datasets.MNIST('/tmp/mnist', train=True, download=True, transform=transform)
    test_dataset = datasets.MNIST('/tmp/mnist', train=False, download=True, transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=False)
    
    # Calibration set: 1000 random samples from train
    calib_indices = np.random.choice(len(train_dataset), config.calib_size, replace=False)
    calib_subset = Subset(train_dataset, calib_indices)
    calib_loader = DataLoader(calib_subset, batch_size=config.batch_size, shuffle=False)
    
    return train_loader, test_loader, calib_loader


def run_pilot(config, output_dir, device='cpu'):
    """Run pilot experiment (5 seed pairs)"""
    print("="*80)
    print("M-EXT4 MPEMBA PILOT EXPERIMENT")
    print("="*80)
    
    # Load data
    train_loader, test_loader, calib_loader = prepare_mnist_data(config, device)
    if train_loader is None:
        return None
    
    # Step 1: Train reference model θ*
    print("\n[1] Training reference model θ*...")
    model_ref = init_reference_model(config, device)
    train_to_convergence(model_ref, train_loader, config, device, max_steps=10000)
    theta_star_state = model_ref.state_dict()
    
    # Estimate H_e
    he_scale = estimate_he(model_ref)
    print(f"\nEstimated H_e scale: {he_scale:.4f}")
    
    # Step 2: Run 5 pilot seed pairs
    pilot_seeds = [
        (42, 43, 100),
        (142, 143, 200),
        (242, 243, 300),
        (342, 343, 400),
        (442, 443, 500),
    ]
    
    results = []
    
    for i, (seed_hot, seed_cold, seed_batch) in enumerate(pilot_seeds):
        print(f"\n{'='*80}")
        print(f"PILOT RUN {i+1}/5: seeds=(hot={seed_hot}, cold={seed_cold}, batch={seed_batch})")
        print(f"{'='*80}")
        
        exp = MpembaExperiment(
            config, theta_star_state, he_scale,
            seed_hot, seed_cold, seed_batch,
            train_loader, test_loader, calib_loader,
            device
        )
        
        result = exp.run()
        if result:
            results.append(result)
    
    # Step 3: Aggregate pilot results
    print(f"\n{'='*80}")
    print("PILOT SUMMARY")
    print(f"{'='*80}")
    
    n_valid = len([r for r in results if not r['excluded_c9']])
    n_wins = len([r for r in results if r['hot_wins'] == True])
    
    print(f"Valid runs: {n_valid}/5")
    print(f"Hot wins: {n_wins}/5")
    print(f"\nDecision:")
    if n_wins >= 3:
        print("  ✓ Proceed to confirmatory (≥3/5 wins)")
        decision = "PROCEED"
    else:
        print("  ✗ Effect too weak or absent, REJECT hypothesis")
        decision = "REJECT"
    
    # Save results
    output_path = Path(output_dir) / "pilot_results.json"
    with open(output_path, 'w') as f:
        json.dump({
            'config': vars(config),
            'he_scale': he_scale,
            'pilot_seeds': pilot_seeds,
            'results': results,
            'summary': {
                'n_valid': n_valid,
                'n_wins': n_wins,
                'decision': decision
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    return decision


if __name__ == '__main__':
    import sys
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    config = Config()
    output_dir = "/workspace/artifacts/external/EW4_mpemba_nn/results"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--confirmatory':
        print("ERROR: Confirmatory run requires sealed holdout unsealing. Use pilot first.")
        sys.exit(1)
    
    # Default: run pilot
    decision = run_pilot(config, output_dir, device)
    
    if decision == "PROCEED":
        print("\n✓ Pilot complete. Next: unseal SEALED_HOLDOUT.json and run confirmatory.")
    else:
        print("\n✗ Hypothesis REJECTED based on pilot. No confirmatory needed.")
