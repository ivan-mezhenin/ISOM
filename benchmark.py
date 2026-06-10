#!/usr/bin/env python3
"""Benchmark: C vs Python hypergraph isomorphism checker.
   Honest tests with real numbers."""
import subprocess, time, sys, os, statistics

C_BIN = os.path.join("ISOM_C", "isom")
PY_MAIN = os.path.join("ISOM_PYTHON", "main.py")

def run_c(g1, g2):
    if len(g1) > 100000:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hg') as f1, \
             tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.hg') as f2:
            f1.write(g1); f2.write(g2)
            p1, p2 = f1.name, f2.name
        r = subprocess.run([C_BIN, "@" + p1, "@" + p2], capture_output=True, text=True, timeout=600)
        os.unlink(p1); os.unlink(p2)
    else:
        r = subprocess.run([C_BIN, g1, g2], capture_output=True, text=True, timeout=600)
    return r.stdout.strip().split('\n')[0]

def run_py(g1, g2):
    r = subprocess.run([sys.executable, PY_MAIN, g1, g2], capture_output=True, text=True, timeout=600)
    return r.stdout.strip()

def measure(runner, g1, g2, warmup=2, runs=10):
    for _ in range(warmup):
        runner(g1, g2)
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        res = runner(g1, g2)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)
    mean = statistics.mean(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean, std, res

# Basic tests: both C and Python give correct result
BASIC = [
    ("Изоморфные, переименование",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "P1(a5,a6,a7)&P1(a8,a5,a6)&P1(a6,a7,a5)",
     "ISOMORPHIC"),
    ("Неизоморфные, цепь vs звезда",
     "P1(a0,a1)&P1(a1,a2)&P1(a2,a3)",
     "P1(a0,a1)&P1(a0,a2)&P1(a0,a3)",
     "NOT ISOMORPHIC"),
    ("Изоморфные, сложные (19 рёбер)",
     "P1(a1,a3,a2)&P1(a2,a1,a5)&P1(a2,a5,a8)&P1(a2,a1,a8)&P1(a3,a4,a1)&"
     "P1(a3,a5,a1)&P1(a3,a9,a4)&P1(a3,a9,a5)&P1(a3,a9,a1)&P1(a5,a2,a3)&"
     "P1(a5,a2,a4)&P1(a5,a3,a10)&P1(a5,a4,a10)&P1(a5,a10,a2)&P1(a8,a2,a10)&"
     "P1(a9,a10,a3)&P1(a10,a5,a9)&P1(a10,a8,a5)&P1(a10,a8,a9)",
     "P1(a1,a4,a2)&P1(a2,a1,a6)&P1(a2,a6,a3)&P1(a2,a1,a3)&P1(a3,a2,a8)&"
     "P1(a4,a5,a1)&P1(a4,a6,a1)&P1(a4,a7,a5)&P1(a4,a7,a6)&P1(a4,a7,a1)&"
     "P1(a6,a2,a5)&P1(a6,a2,a4)&P1(a6,a5,a8)&P1(a6,a4,a8)&P1(a6,a8,a2)&"
     "P1(a7,a8,a4)&P1(a8,a3,a6)&P1(a8,a6,a7)&P1(a8,a3,a7)",
     "ISOMORPHIC"),
    ("Неизоморфные, разная арность",
     "P1(a1,a2,a3)",
     "P1(a4,a5)",
     "NOT ISOMORPHIC"),
    ("Изоморфные, одинаковые графы",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "P1(a1,a2,a3)&P1(a4,a1,a2)&P1(a2,a3,a1)",
     "ISOMORPHIC"),
]

# Python bugs: crash or wrong answer
BUGS = [
    ("Python crash: цепь",
     "P1(a,b)&P1(b,c)",
     "P1(a,b)&P1(a,c)",
     "NOT ISOMORPHIC"),
    ("Python crash: повторы",
     "P1(a,b)&P1(a,b)",
     "P1(a,b)&P1(a,b)",
     "ISOMORPHIC"),
    ("Python неверный ответ: 12 аргументов",
     "&".join(f"P1(a{i*3+1},a{i*3+2},a{i*3+3})" for i in range(4)),
     "&".join(f"P1(b{i*3+1},b{i*3+2},b{i*3+3})" for i in range(4)),
     "ISOMORPHIC"),
]

# C scalability tests (isomorphic, all unique args)
def make_pair(N, arity=2):
    a = [f"a{i}" for i in range(1, N*arity+1)]
    b = [f"b{i}" for i in range(1, N*arity+1)]
    pname = f"P{arity}"
    def edge(lst, offset):
        return pname + "(" + ",".join(lst[offset+j] for j in range(arity)) + ")"
    g1 = "&".join(edge(a, i*arity) for i in range(N))
    g2 = "&".join(edge(b, i*arity) for i in range(N))
    return g1, g2

SCALE = [(N, 2) + make_pair(N, 2) for N in [100, 1000, 5000, 10000]]
SCALE += [(N, 4) + make_pair(N, 4) for N in [100, 1000, 5000, 10000]]

def main():
    print("=" * 70)
    print("Benchmark: C vs Python")
    print("Machine: MacBook Air (Apple M4, 16 GB)")
    print("=" * 70)
    print()

    # Compile C
    print("Compiling C...", end=" ", flush=True)
    r = subprocess.run(["make", "-C", "ISOM_C", "clean", "all"], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED")
        sys.exit(1)
    print("OK\n")

    # ── Basic tests ──
    print("--- Базовые тесты (C vs Python) ---\n")
    h = f"{'Сценарий':<30} {'Ожидается':<18} {'C (мс)':<22} {'Python (мс)':<22} {'Ускорение':<8}"
    print(h)
    print("-" * len(h))
    basic_results = []
    for name, g1, g2, exp in BASIC:
        c_mean, c_std, c_res = measure(run_c, g1, g2)
        py_mean, py_std, py_res = measure(run_py, g1, g2)
        speedup = py_mean / c_mean if c_mean > 0 else float('inf')
        c_v = "✓" if c_res == exp else f"✗({c_res})"
        py_v = "✓" if py_res == exp else f"✗({py_res})"
        c_str = f"{c_mean:.2f} ± {c_std:.2f}"
        py_str = f"{py_mean:.2f} ± {py_std:.2f}"
        print(f"{name:<30} {exp:<18} {c_str:<22} {py_str:<22} {speedup:<7.1f}x  C:{c_v} Py:{py_v}")
        basic_results.append((name, c_mean, py_mean, speedup, c_v, py_v))
    print()

    avg_speedup = statistics.mean([r[3] for r in basic_results])
    print(f"Среднее время C: {statistics.mean([r[1] for r in basic_results]):.2f} мс, "
          f"Python: {statistics.mean([r[2] for r in basic_results]):.2f} мс")
    print(f"Среднее ускорение: {avg_speedup:.1f}x")
    print()

    # ── Python bugs ──
    print("--- Ошибки Python-реализации ---\n")
    for name, g1, g2, exp in BUGS:
        c_mean, c_std, c_res = measure(run_c, g1, g2)
        c_v = "✓" if c_res == exp else f"✗({c_res})"
        try:
            py_res = run_py(g1, g2)
            py_status = f"Результат: {py_res} (ожидалось {exp})"
        except Exception as e:
            py_status = f"Ошибка: {type(e).__name__}"
        print(f"  {name}")
        print(f"    C: {c_mean:.2f} ± {c_std:.2f} мс {c_v}")
        print(f"    Python: {py_status}")
    print()

    # ── C scalability ──
    print("--- Масштабирование C (только C) ---\n")
    print(f"{'Рёбер':<10} {'Арность':<10} {'Время (мс)':<30} {'Результат':<15}")
    print("-" * 65)
    for N, arity, g1, g2 in SCALE:
        for _ in range(2):
            subprocess.run([C_BIN, g1, g2], capture_output=True, timeout=600)
        times = []
        for _ in range(5):
            t0 = time.perf_counter()
            r = subprocess.run([C_BIN, g1, g2], capture_output=True, text=True, timeout=600)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000)
        mean = statistics.mean(times)
        std = statistics.stdev(times)
        res = r.stdout.strip().split("\n")[0]
        print(f"{N:<10} {arity:<10} {mean:<10.2f} ± {std:<8.2f}      {res:<15}")
    print()

if __name__ == '__main__':
    main()
