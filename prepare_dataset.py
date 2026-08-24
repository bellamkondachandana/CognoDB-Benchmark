import gzip
import io
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
url = "https://snap.stanford.edu/data/wiki-Vote.txt.gz"
raw = DATA / "wiki-Vote.txt.gz"
out = DATA / "edges.csv"

print("Downloading:", url)
urllib.request.urlretrieve(url, raw)

count = 0
with gzip.open(raw, "rt", encoding="utf-8") as src, out.open("w", encoding="utf-8") as dst:
    dst.write("source,target\n")
    for line in src:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            continue
        dst.write(f"{parts[0]},{parts[1]}\n")
        count += 1

print(f"Wrote {count:,} relationships to {out}")
if count < 100_000:
    raise SystemExit("Dataset has fewer than 100,000 relationships; stop rather than silently changing the benchmark.")
