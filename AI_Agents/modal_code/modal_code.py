import json
from typing import Any

import aiohttp
import modal

vllm_image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm")
    .env(
        {
        "HF_XET_HIGH_PERFORMANCE": "1",
        "VLLM_LOG_STATS_INTERVAL": "1",
        }
    )
)
MODEL_NAME = "google/gemma-4-26B-A4B-it"
MODEL_REVISION = "47b6801b24d15ff9bcd8c96dfaea0be9ed3a0301"

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)

vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)
FAST_BOOT = True

SPECULATIVE_MODEL_NAME = "google/gemma-4-26B-A4B-it-assistant"
SPECULATIVE_MODEL_REVISION = "f188f476dc11dd5bb3014dc861529d316bce49d3"

app = modal.App("vllm-inference")

N_GPU = 1

MINUTES = 60 # 60 seconds

VLLM_PORT =8000


@app.function(
    image=vllm_image,
    gpu=f"A10:{N_GPU}",
    scaledown_window=15 * MINUTES,
    timeout=10 * MINUTES,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol
    },
)

@modal.concurrent(max_inputs=100)

@modal.web_server(port=VLLM_PORT,startup_timeout=10 * MINUTES)
def serve():
    import json
    import subprocess
    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--revision",
        MODEL_REVISION,
        "--served-model-name",
        MODEL_NAME,
        "llm",
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--uvicorn-log-level=info",
        "--async-scheduling",
    ]

    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    cmd += ["--tensor-parallel-size", str(N_GPU)]

    cmd += [
        "--limit-mm-per-prompt",
        f"'{json.dumps({'image': 0, 'video': 0, 'audio': 0})}'",
        "--enable-auto-tool-choice",
        "--reasoning-parser gemma4",
        "--tool-call-parser gemma4",
    ]

    cmd += [
        "--speculative-config",
        f"'{json.dumps({'model': SPECULATIVE_MODEL_NAME, 'revision': SPECULATIVE_MODEL_REVISION, 'num_speculative_tokens': 4})}'",
    ]

    print(*cmd)

    subprocess.Popen(" ".join(cmd), shell=True)