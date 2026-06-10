#!/usr/bin/env python3
"""Benchmark: compare C vs Python hypergraph isomorphism checkers."""

import subprocess
import time
import sys
import os
import statistics

TESTS = [
    ("3l 2a ISO simple",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "P1(a5,a6,a7)&P1(a8,a5,a6)&P1(a6,a7,a5)",
     "ISOMORPHIC"),

    ("3l 2a NOT ISO chain",
     "P1(a0,a1)&P1(a1,a2)&P1(a2,a3)",
     "P1(a0,a1)&P1(a0,a2)&P1(a0,a3)",
     "NOT ISOMORPHIC"),

    ("19l 3a ISO",
     "P1(a1,a3,a2)&P1(a2,a1,a5)&P1(a2,a5,a8)&P1(a2,a1,a8)&P1(a3,a4,a1)&"
     "P1(a3,a5,a1)&P1(a3,a9,a4)&P1(a3,a9,a5)&P1(a3,a9,a1)&P1(a5,a2,a3)&"
     "P1(a5,a2,a4)&P1(a5,a3,a10)&P1(a5,a4,a10)&P1(a5,a10,a2)&P1(a8,a2,a10)&"
     "P1(a9,a10,a3)&P1(a10,a5,a9)&P1(a10,a8,a5)&P1(a10,a8,a9)",
     "P1(a1,a4,a2)&P1(a2,a1,a6)&P1(a2,a6,a3)&P1(a2,a1,a3)&P1(a3,a2,a8)&"
     "P1(a4,a5,a1)&P1(a4,a6,a1)&P1(a4,a7,a5)&P1(a4,a7,a6)&P1(a4,a7,a1)&"
     "P1(a6,a2,a5)&P1(a6,a2,a4)&P1(a6,a5,a8)&P1(a6,a4,a8)&P1(a6,a8,a2)&"
     "P1(a7,a8,a4)&P1(a8,a3,a6)&P1(a8,a6,a7)&P1(a8,a3,a7)",
     "ISOMORPHIC"),

    ("3l 2a same graph",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "ISOMORPHIC"),

    ("2l 2a arity mismatch",
     "P1(a1,a2,a3)",
     "P1(a4,a5)",
     "NOT ISOMORPHIC"),
]

C_DIR = os.path.join(os.path.dirname(__file__), "ISOM_C")
PY_DIR = os.path.join(os.path.dirname(__file__), "ISOM_PYTHON")
C_BIN = os.path.join(C_DIR, "isom")
PY_MAIN = os.path.join(PY_DIR, "main.py")


def run_c(g1, g2):
    result = subprocess.run(
        [C_BIN, g1, g2],
        capture_output=True, text=True, timeout=600
    )
    return result.stdout.strip().split('\n')[0]


def run_py(g1, g2):
    result = subprocess.run(
        [sys.executable, PY_MAIN, g1, g2],
        capture_output=True, text=True, timeout=600
    )
    return result.stdout.strip()


def measure(runner_fn, g1, g2, warmup_runs=2, bench_runs=10):
    for _ in range(warmup_runs):
        runner_fn(g1, g2)
    times = []
    for _ in range(bench_runs):
        t0 = time.perf_counter()
        res = runner_fn(g1, g2)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    mean = statistics.mean(times)
    stdev = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean, stdev, times, res


def fmt_num(x):
    return f"{x:.2f}"


def main():
    print("=" * 80)
    print("Hypergraph Isomorphism Benchmark: C vs Python")
    print("=" * 80)
    print()

    print("Compiling C...", end=" ", flush=True)
    ret = subprocess.run(["make", "-C", C_DIR, "clean", "all"],
                         capture_output=True, text=True)
    if ret.returncode != 0:
        print("FAILED")
        print(ret.stderr)
        sys.exit(1)
    print("OK\n")

    header = f"{'Test':<25} {'Result':<15} {'C (ms)':<22} {'Python (ms)':<22} {'Speedup':<10}"
    print(header)
    print("-" * len(header))

    all_correct = True

    for name, g1, g2, expected in TESTS:
        c_mean, c_std, c_times, c_res = measure(run_c, g1, g2)
        py_mean, py_std, py_times, py_res = measure(run_py, g1, g2)

        speedup = py_mean / c_mean if c_mean > 0 else float('inf')
        correct = (c_res == expected and py_res == expected)
        if not correct:
            all_correct = False

        ck = "✓" if c_res == expected else f"✗({c_res})"
        pk = "✓" if py_res == expected else f"✗({py_res})"

        c_col = f"{fmt_num(c_mean)} ± {fmt_num(c_std)}"
        py_col = f"{fmt_num(py_mean)} ± {fmt_num(py_std)}"
        print(f"{name:<25} {expected:<15} {c_col:<22} {py_col:<22} {speedup:<8.1f}x  C:{ck} Py:{pk}")
        print(f"  C:  " + " ".join(f"{t:>6.2f}" for t in c_times))
        print(f"  Py: " + " ".join(f"{t:>6.2f}" for t in py_times))
        print()

    print(f"{'All tests correct!' if all_correct else 'SOME TESTS FAILED!'}")
    print("Done.")


if __name__ == '__main__':
    main()
