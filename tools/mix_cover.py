"""把转换后的人声与伴奏合成一首歌。

- 转换人声为单声道，伴奏为立体声；人声居中，伴奏原样
- 人声按「原始人声」的 RMS 做等响匹配，保证和 UVR 分离时相同的音量配比
- 输出 wav，可用 ffmpeg 再压 mp3

用法:
    python mix_cover.py 原始人声.wav 转换人声.wav 伴奏.wav 输出.wav [--vocal-db 0]
"""

import argparse
import sys

import numpy as np
import soundfile as sf


def load(path):
    x, sr = sf.read(path, always_2d=False)
    return x.astype(np.float32), sr


def to_mono(x):
    return x.mean(axis=1) if x.ndim > 1 else x


def rms(x):
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


def fit(x, n):
    if len(x) >= n:
        return x[:n]
    pad = np.zeros((n - len(x),) + x.shape[1:], dtype=x.dtype)
    return np.concatenate([x, pad])


def main() -> int:
    ap = argparse.ArgumentParser(description="人声 + 伴奏混音")
    ap.add_argument("src_vocal", help="原始人声（用于等响匹配）")
    ap.add_argument("conv_vocal", help="转换后的人声")
    ap.add_argument("music", help="伴奏")
    ap.add_argument("out", help="输出 wav")
    ap.add_argument("--vocal-db", type=float, default=0.0, help="人声额外增益 dB，默认 0")
    args = ap.parse_args()

    sv, sr = load(args.src_vocal)
    cv, sr2 = load(args.conv_vocal)
    mu, sr3 = load(args.music)
    if not (sr == sr2 == sr3):
        print(f"采样率不一致: {sr} / {sr2} / {sr3}")
        return 2

    sv, cv = to_mono(sv), to_mono(cv)
    n = min(len(sv), len(cv), len(mu))
    sv, cv, mu = fit(sv, n), fit(cv, n), fit(mu, n)

    gain = rms(sv) / rms(cv) * (10 ** (args.vocal_db / 20))
    cv = cv * gain

    if mu.ndim == 1:
        mu = np.stack([mu, mu], axis=1)
    left = mu[:, 0] + cv
    right = mu[:, 1] + cv
    out = np.stack([left, right], axis=1)

    peak = float(np.max(np.abs(out)))
    if peak > 0.98:
        out *= 0.98 / peak
    sf.write(args.out, out, sr)

    print(f"混音完成: {args.out}")
    print(f"  时长 {n/sr:.1f}s | 人声增益 {20*np.log10(gain):+.2f} dB (额外 {args.vocal_db:+.1f} dB)")
    print(f"  人声 RMS {rms(sv):.4f} -> 匹配后 {rms(cv):.4f} | 伴奏 RMS {rms(mu):.4f}")
    print(f"  峰值 {peak:.3f}" + ("（已衰减到 0.98）" if peak > 0.98 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
