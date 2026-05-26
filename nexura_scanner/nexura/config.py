import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "gguf_models"
REPORTS_DIR = BASE_DIR / "reports"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

LLAMA_MODEL_PATH = os.getenv("NEXURA_MODEL", str(MODELS_DIR / "qwen2.5-7b-instruct-q4_k_m.gguf"))
LLAMA_N_CTX = int(os.getenv("NEXURA_CTX_SIZE", "4096"))
LLAMA_N_THREADS = int(os.getenv("NEXURA_THREADS", "4"))
LLAMA_N_GPU_LAYERS = int(os.getenv("NEXURA_GPU_LAYERS", "0"))
LLAMA_TEMP = float(os.getenv("NEXURA_TEMP", "0.1"))
LLAMA_MAX_TOKENS = int(os.getenv("NEXURA_MAX_TOKENS", "2048"))

WEB_HOST = os.getenv("NEXURA_WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("NEXURA_WEB_PORT", "8080"))

TIMEOUT = int(os.getenv("NEXURA_TIMEOUT", "300"))
