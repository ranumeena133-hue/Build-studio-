#!/usr/bin/env bash
# HindiAI Coder - full pipeline: data → train → evaluate
# Usage: bash run_all.sh
set -e
cd "$(dirname "$0")/.."
PY=".venv/bin/python"
[ -x "$PY" ] || PY="python3"

echo "=== 1/3 Dataset ==="
$PY studio-hindi-ai/data/build_dataset.py --synth 3000

echo "=== 2/3 Train (is machine par ~3.5h) ==="
OMP_NUM_THREADS=2 $PY -u studio-hindi-ai/model/train.py \
  --preset tiny --epochs 8 --batch 16 --block 384 \
  --lr 8e-4 --warmup 200 --log-every 50 --eval-every 500 \
  --save-every 1000 --vocab 6390

echo "=== 3/3 Evaluate ==="
$PY studio-hindi-ai/model/evaluate.py --n 60

echo "DONE. Web app ke liye: $PY studio-hindi-ai/app/server.py"
