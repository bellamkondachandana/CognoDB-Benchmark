#!/usr/bin/env bash
set -euo pipefail
python prepare_dataset.py
python benchmark.py
