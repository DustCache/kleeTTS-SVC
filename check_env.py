"""Environment doctor for KleeVoice.

Collects everything needed to diagnose a setup problem, in one copy-pasteable
report. Safe to run: it only reads, never installs or modifies anything.

Usage:
    python check_env.py              # full report
    python check_env.py --role tts   # TTS-focused checks
    python check_env.py --role svc   # SVC-focused checks
    python check_env.py --quiet      # only failures
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OK, BAD, WARN = "[ OK ]", "[FAIL]", "[WARN]"

results: list[tuple[str, str, str]] = []


def add(state: str, name: str, detail: str = "") -> None:
    results.append((state, name, detail))


def exists(rel: str, label: str, min_mb: float = 0.0) -> None:
    path = os.path.join(HERE, rel.replace("/", os.sep))
    if not os.path.exists(path):
        add(BAD, label, f"missing: {rel}")
        return
    if os.path.isdir(path):
        n = sum(1 for _, _, fs in os.walk(path) for f in fs if f != ".gitkeep")
        if n == 0:
            add(BAD, label, f"empty folder: {rel}")
        else:
            add(OK, label, f"{rel}  ({n} files)")
        return
    mb = os.path.getsize(path) / 1048576
    if mb < min_mb:
        add(WARN, label, f"{rel}  only {mb:.1f} MB (expected ~{min_mb:.0f} MB)")
    elif mb < 1:
        add(OK, label, f"{rel}  ({mb * 1024:.0f} KB)")
    else:
        add(OK, label, f"{rel}  ({mb:.1f} MB)")


def section(title: str) -> None:
    print(f"\n--- {title} " + "-" * max(0, 58 - len(title)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", choices=["all", "tts", "svc"], default="all")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    # ---------------- runtime ----------------
    add(OK, "python", f"{sys.version.split()[0]}  ({sys.executable})")
    add(OK, "os", f"{platform.system()} {platform.release()}  {platform.machine()}")

    pyver = sys.version_info
    if pyver[:2] in ((3, 10), (3, 11)):
        add(OK, "python version", "3.10/3.11 - supported")
    elif pyver[:2] == (3, 12):
        add(WARN, "python version", "3.12 - not verified, use 3.10/3.11")
    else:
        add(BAD, "python version", f"{pyver.major}.{pyver.minor} - unsupported")

    # ---------------- torch / cuda ----------------
    try:
        import torch  # noqa: PLC0415

        add(OK, "torch", torch.__version__)
        cuda = torch.cuda.is_available()
        add(OK if cuda else WARN, "cuda available", str(cuda))
        if cuda:
            name = torch.cuda.get_device_name(0)
            cap = ".".join(map(str, torch.cuda.get_device_capability(0)))
            add(OK, "gpu", f"{name}  sm_{cap.replace('.', '')}")
            is_blackwell = cap.startswith("12") or "RTX 50" in name
            torch_cu = (torch.version.cuda or "").replace(".", "")
            if is_blackwell and torch_cu and int(torch_cu) < 128:
                add(BAD, "torch/cuda match",
                    f"RTX 50 needs cu128, got cu{torch.version.cuda} - reinstall torch")
            else:
                add(OK, "torch/cuda match", f"cu{torch.version.cuda}")
    except Exception as exc:  # noqa: BLE001
        add(BAD, "torch", f"import failed: {type(exc).__name__}: {exc}")

    # ---------------- numpy ----------------
    try:
        import numpy  # noqa: PLC0415

        major = int(numpy.__version__.split(".")[0])
        if major >= 2:
            add(BAD, "numpy", f"{numpy.__version__} - GPT-SoVITS needs <2.0 "
                              "(pip install numpy==1.26.4)")
        else:
            add(OK, "numpy", numpy.__version__)
    except Exception as exc:  # noqa: BLE001
        add(BAD, "numpy", f"{type(exc).__name__}: {exc}")

    # ---------------- model files ----------------
    if args.role in ("all", "tts"):
        exists("TTS/GPT_weights_v2/klee-e60.ckpt", "TTS GPT weights", 100)
        exists("TTS/SoVITS_weights_v2/klee_e24_s600.pth", "TTS SoVITS weights", 50)
        exists("TTS/GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
               "TTS BERT (roberta)", 0)
        exists("TTS/GPT_SoVITS/pretrained_models/chinese-hubert-base",
               "TTS HuBERT", 0)
        exists("TTS/GPT_SoVITS/text/G2PWModel", "TTS G2PWModel", 0)
        exists("TTS/data/klee/audio/klee_005.wav", "TTS reference audio", 0)
        exists("TTS/configs/tts_infer_klee.yaml", "TTS config", 0)

    if args.role in ("all", "svc"):
        exists("SVC/exp/reflow-klee/model_108000.pt", "SVC model", 200)
        exists("SVC/exp/reflow-klee/config.yaml", "SVC model config", 0)
        exists("SVC/pretrain/contentvec/checkpoint_best_legacy_500.pt",
               "SVC ContentVec", 100)
        exists("SVC/pretrain/rmvpe/model.pt", "SVC RMVPE", 200)
        exists("SVC/pretrain/pc_nsf_hifigan_44.1k_hop512_128bin_2025.02/model.ckpt",
               "SVC vocoder", 30)

    # ---------------- extra deps ----------------
    if args.role in ("all", "svc"):
        if importlib.util.find_spec("fairseq") is None:
            add(BAD, "fairseq", "not installed - SVC cannot start "
                                "(ddsp/vocoder.py imports it)")
        else:
            try:
                import fairseq  # noqa: PLC0415

                add(OK, "fairseq", getattr(fairseq, "__version__", "?"))
            except Exception as exc:  # noqa: BLE001
                add(BAD, "fairseq", f"installed but import failed: "
                                    f"{type(exc).__name__}: {exc}")

    for mod in ("soundfile", "librosa", "pyworld", "parselmouth", "yaml"):
        if args.role == "tts" and mod in ("pyworld", "parselmouth"):
            continue
        if args.role == "svc" and mod == "yaml":
            continue
        if importlib.util.find_spec(mod) is None:
            add(BAD, f"module {mod}", "not installed")

    # ---------------- report ----------------
    print("=" * 66)
    print(" KleeVoice environment report")
    print("=" * 66)
    for state, heading in ((OK, "OK"), (WARN, "WARNINGS"), (BAD, "FAILURES")):
        rows = [r for r in results if r[0] == state]
        if args.quiet and state == OK:
            continue
        if not rows:
            continue
        section(heading)
        for _, name, detail in rows:
            print(f"  {state} {name:<22} {detail}")

    fails = [r for r in results if r[0] == BAD]
    print("\n" + "=" * 66)
    if fails:
        print(f" {len(fails)} problem(s) found. Fix the [FAIL] lines above.")
        print(" If you need help, copy this whole report into an issue.")
    else:
        print(" No blocking problems found.")
    print("=" * 66)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
