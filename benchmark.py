import csv
import os
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

random.seed(CFG["benchmark"]["random_seed"])


def percentile(values, p):
    return float(np.percentile(values, p)) if values else None


def measure(fn, iterations):
    values = []
    errors = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        try:
            fn()
            values.append((time.perf_counter() - t0) * 1000)
        except Exception as exc:
            errors.append(type(exc).__name__ + ": " + str(exc))
    return {
        "count": len(values),
        "errors": len(errors),
        "p50_ms": percentile(values, 50),
        "p95_ms": percentile(values, 95),
        "mean_ms": statistics.mean(values) if values else None,
        "error_examples": " | ".join(errors[:3]),
    }


def load_edges():
    path = ROOT / CFG["dataset"]["edges_file"]
    df = pd.read_csv(path)
    s = CFG["dataset"]["source_column"]
    t = CFG["dataset"]["target_column"]
    if s not in df.columns or t not in df.columns:
        raise ValueError(f"Expected columns {s!r} and {t!r} in {path}")
    return df[[s, t]].dropna()


def benchmark_placeholder():
    """
    This deliberately does not fake database results.

    Database-specific adapters should be connected here after credentials
    and provider endpoints are configured. Each adapter should implement:
      - connect()
      - load_edges()
      - one_hop(node)
      - two_hop(node)
      - three_hop(node)
      - point_lookup(node)
      - indexed_lookup(node)
      - aggregation()
      - mixed_read()
      - mixed_write()
    """
    df = load_edges()
    nodes = pd.unique(pd.concat([df.iloc[:, 0], df.iloc[:, 1]], ignore_index=True))
    print(f"Loaded local dataset: {len(nodes)} nodes, {len(df)} relationships")
    print("Next: configure provider adapters and run the real benchmark.")


if __name__ == "__main__":
    benchmark_placeholder()
