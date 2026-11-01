"""Service health check for KleeVoice.

Checks the TTS API (port 9880) and optionally the ASR API (port 9001).
Bypasses HTTP(S)_PROXY so localhost probes never go through a system proxy.

Usage:
    python status_all.py            # check 9880 (and 9001 if ASR is used)
    python status_all.py --tts 9880
"""
import argparse
import json
import sys
import urllib.request
from urllib.request import ProxyHandler, Request, build_opener

OPENER = build_opener(ProxyHandler({}))  # no proxy for localhost


def probe(url, timeout=6):
    try:
        with OPENER.open(Request(url, headers={"User-Agent": "KleeVoice/1.0"}), timeout=timeout) as r:
            body = r.read(200).decode("utf-8", "ignore")
            return r.status, body
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def check(name, url, expect=None):
    status, body = probe(url)
    if status is None:
        print(f"  [DOWN] {name:<18} {url}\n         {body[:120]}")
        return False
    ok = status == 200 and (expect is None or expect in body)
    tag = "UP  " if ok else "WARN"
    print(f"  [{tag}] {name:<18} {url} -> {status} {body[:60]!r}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--tts", type=int, default=9880)
    ap.add_argument("--asr", type=int, default=9001)
    ap.add_argument("--no-asr", action="store_true", help="skip ASR check")
    args = ap.parse_args()

    print("KleeVoice status")
    ok = check("TTS", f"http://{args.host}:{args.tts}/docs")
    if not args.no_asr:
        check("ASR (optional)", f"http://{args.host}:{args.asr}/health", expect="ok")
    print()
    print("TTS is ready." if ok else "TTS is not responding - run start_tts.cmd")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
