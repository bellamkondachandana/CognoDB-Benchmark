# CognoDB Cloud Benchmark

This repository is a reproducible benchmark harness for the WEXA AI take-home assignment.

## Important
The benchmark must use the **same dataset, logical workloads, client machine and region** as closely as possible for every database. Do not invent or manually enter benchmark numbers. Run the scripts and commit the generated results.

## Databases
- CognoDB Cloud
- Neo4j
- Memgraph
- FalkorDB
- ArangoDB

## Required measurements
1. Data loading: nodes/sec, relationships/sec, total load time
2. Traversals: 1-hop, 2-hop, 3-hop p50/p95 latency
3. Lookups: point lookup and indexed/filtered lookup p50/p95
4. Aggregation: p50/p95
5. Mixed workload: concurrent read/write throughput
6. Footprint: observable resource/instance information

## Setup

### 1. Create a virtual environment
```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure secrets
Copy `.env.example` to `.env` and fill in the credentials for the databases you actually run.

**Never commit `.env`.**

### 4. Dataset
Download a public graph dataset containing at least 100,000 relationships. Put the edge list at:

`data/edges.csv`

The CSV must have:
```text
source,target
```

Update the dataset name, source URL, node count and relationship count in `config.yaml`.

### 5. Run
```bash
python benchmark.py
```

The script writes:
- `results/raw_results.csv`
- `results/summary.csv`

## Methodology
- Warm up before measurements.
- Read workloads use 100 iterations by default.
- Report p50 and p95, not only averages.
- Use the same logical queries and randomly selected start nodes.
- Record failures, timeouts, throttling and unavailable metrics honestly.
- Do not compare a free tier with a paid tier unless the resource limits are documented and the methodology explains the difference.

## Results
After running the benchmark, paste the generated summary tables into this README. Do not create results by estimation.

## Suggested final README sections
- Objective
- Database selection
- Instance/resource specifications
- Dataset and exact source
- Loading methodology
- Query methodology
- Warm-up and repetitions
- Results matrix
- Charts
- Analysis
- Caveats
- Reproduction instructions

## Security
Connection strings and passwords must come from environment variables. They must never be committed to GitHub.
