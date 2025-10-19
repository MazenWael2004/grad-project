import torch
print("CUDA available:", torch.cuda.is_available())
print("MPS available (Apple):", hasattr(torch.backends, "mps") and torch.backends.mps.is_available())
print("XPU available (Intel):", hasattr(torch, "xpu") and torch.xpu.is_available())