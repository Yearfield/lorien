from __future__ import annotations
import threading, time
from typing import Iterator, Optional, List, Dict, Tuple
from collections import OrderedDict

from .config import load_llm_config
from .safety import safety_gate
from .json_utils import parse_fill_response, clamp

# Global model instance and concurrency control
_MODEL: Optional[object] = None  # Will be Llama instance when available
_MODEL_LOCK = threading.Lock()
_CONCURRENCY = None  # set from config at first load

# very small in-memory cache: key=(root, tuple(nodes), style_triage, style_actions, caps) -> (dt, ac, ts)
_CACHE: "OrderedDict[tuple, tuple[str,str,float]]" = OrderedDict()

SYSTEM_PROMPT = None

def _load_system_prompt() -> str:
    global SYSTEM_PROMPT
    if SYSTEM_PROMPT is None:
        try:
            with open("llm/prompts/system_med_safety.txt", "r", encoding="utf-8") as f:
                SYSTEM_PROMPT = f.read().strip()
        except FileNotFoundError:
            # Fallback system prompt if file doesn't exist
            SYSTEM_PROMPT = """You are a medical triage assistant. Provide guidance only, not diagnosis or treatment.
Never prescribe medications, dosages, or specific treatments.
Focus on triage urgency and next steps for evaluation.
Use clear, concise language appropriate for medical professionals."""
    return SYSTEM_PROMPT

def _get_model():
    global _MODEL, _CONCURRENCY
    cfg = load_llm_config()
    if not cfg.enabled:
        raise RuntimeError("LLM is disabled")
    if not cfg.model_path:
        raise RuntimeError("LLM_MODEL_PATH not set")

    with _MODEL_LOCK:
        if _MODEL is None:
            try:
                # Import llama_cpp here to avoid dependency issues when LLM is disabled
                from llama_cpp import Llama
                _MODEL = Llama(
                    model_path=cfg.model_path,
                    n_ctx=cfg.n_ctx,
                    n_threads=cfg.n_threads,
                    n_gpu_layers=cfg.n_gpu_layers,
                    use_mmap=True,
                    use_mlock=False,
                    seed=cfg.seed if cfg.seed is not None else -1,
                    verbose=False,
                )
                _CONCURRENCY = threading.Semaphore(cfg.concurrency)
            except ImportError:
                raise RuntimeError("llama_cpp not available. Install with: pip install llama-cpp-python")
            except Exception as e:
                raise RuntimeError(f"Failed to load LLM model: {e}")
    return _MODEL

def _rate_limit():
    cfg = load_llm_config()
    delay = 1.0 / max(0.0001, cfg.rate_limit_rps)
    # coarse per-process limiter
    if delay > 0:
        time.sleep(delay)

def _cache_get(key: tuple) -> Tuple[str,str] | None:
    cfg = load_llm_config()
    now = time.time()
    # purge expired entries
    for k in list(_CACHE.keys()):
        if now - _CACHE[k][2] > cfg.cache_ttl_s:
            _CACHE.pop(k, None)
    v = _CACHE.get(key)
    if v:
        # move to end (LRU)
        _CACHE.move_to_end(key)
        return v[0], v[1]
    return None

def _cache_put(key: tuple, dt: str, ac: str) -> None:
    cfg = load_llm_config()
    now = time.time()
    _CACHE[key] = (dt, ac, now)
    # bound cache size (e.g., 128)
    if len(_CACHE) > 128:
        _CACHE.popitem(last=False)

def _build_fill_prompt(root: str, nodes: List[str], style_triage: str, style_actions: str,
                       triage_cap: int, actions_cap: int) -> str:
    """
    Build a tight prompt that requests STRICT JSON only.
    Styles: 'diagnosis-only' | 'short-explanation' | 'none'
            'referral-only' | 'steps' | 'none'
    """
    system = _load_system_prompt()
    path_line = " → ".join([root.strip()] + [n.strip() for n in nodes if n and n.strip()])

    # minimal, grammar-friendly prompt
    return f"""<|system|>
{system}
Return only valid JSON with exactly these keys and string values: "diagnostic_triage", "actions".
Do not include explanations unless requested. Respect character limits.
</|system|>
<|user|>
Symptom path: {path_line}

Output constraints:
- diagnostic_triage: style={style_triage}, max_chars={triage_cap}
- actions: style={style_actions}, max_chars={actions_cap}

Respond as STRICT JSON ONLY, no prose, no markdown, like:
{{"diagnostic_triage":"...", "actions":"..."}}
</|user|>
<|assistant|>
"""

def fill_triage_actions(root: str, nodes: List[str], style_triage: str, style_actions: str) -> Tuple[str, str]:
    cfg = load_llm_config()

    # Safety first
    sr = safety_gate(" ".join([root] + list(nodes or [])))
    if not sr.allowed:
        return ("", "")  # caller can surface refusal; we avoid generating

    # cache
    key = (root.strip(), tuple((n or "").strip() for n in nodes), style_triage, style_actions, cfg.triage_max_chars, cfg.actions_max_chars, cfg.max_tokens)
    cached = _cache_get(key)
    if cached:
        dt, ac = cached
        return clamp(dt, cfg.triage_max_chars), clamp(ac, cfg.actions_max_chars)

    model = _get_model()
    prompt = _build_fill_prompt(root, nodes, style_triage, style_actions, cfg.triage_max_chars, cfg.actions_max_chars)

    _rate_limit()
    with _CONCURRENCY:
        out = model(
            prompt=prompt,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            max_tokens=cfg.max_tokens,
            stop=["</|assistant|>", "</|user|>", "<|user|>", "<|system|>"],
            # Optional: If llama.cpp supports JSON grammar in your version, you can add:
            # grammar="json"   # keep off if version mismatch; we already parse defensively
        )

    text = (out.get("choices", [{}])[0].get("text") or "").strip()
    dt, ac = parse_fill_response(text)

    dt = clamp(dt, cfg.triage_max_chars)
    ac = clamp(ac, cfg.actions_max_chars)
    _cache_put(key, dt, ac)
    return dt, ac
