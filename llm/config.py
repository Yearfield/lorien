from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LLMConfig:
    enabled: bool
    model_path: str | None
    n_threads: int
    n_ctx: int
    n_gpu_layers: int
    temperature: float
    top_p: float
    max_tokens: int
    seed: int | None
    # Efficiency & control
    concurrency: int
    cache_ttl_s: int
    triage_max_chars: int
    actions_max_chars: int
    rate_limit_rps: float  # per-process crude limiter

def _env_bool(key: str, default: bool=False) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in {"1","true","yes","on"}

def load_llm_config() -> LLMConfig:
    enabled = _env_bool("LLM_ENABLED", False)
    model_path = os.environ.get("LLM_MODEL_PATH")
    n_threads = int(os.environ.get("LLM_N_THREADS", max(1, (os.cpu_count() or 4) // 2)))
    n_ctx = int(os.environ.get("LLM_N_CTX", "2048"))  # conservative
    n_gpu_layers = int(os.environ.get("LLM_N_GPU_LAYERS", "0"))  # 0 = CPU only
    temperature = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
    top_p = float(os.environ.get("LLM_TOP_P", "0.95"))
    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", "160"))   # short, efficient
    seed = int(os.environ["LLM_SEED"]) if os.environ.get("LLM_SEED") else None

    if model_path:
        model_path = str(Path(model_path).expanduser().resolve())

    concurrency = int(os.environ.get("LLM_CONCURRENCY", "1"))   # serialize by default
    cache_ttl_s = int(os.environ.get("LLM_CACHE_TTL_S", "300")) # 5 min
    triage_max_chars = int(os.environ.get("LLM_TRIAGE_MAX_CHARS", "160"))
    actions_max_chars = int(os.environ.get("LLM_ACTIONS_MAX_CHARS", "200"))
    rate_limit_rps = float(os.environ.get("LLM_RATE_LIMIT_RPS", "1.0"))  # 1 req/sec

    return LLMConfig(
        enabled, model_path, n_threads, n_ctx, n_gpu_layers, temperature, top_p,
        max_tokens, seed, concurrency, cache_ttl_s, triage_max_chars, actions_max_chars, rate_limit_rps
    )
