# 🤖 HindiAI Coder — आपका अपना Hindi Coding AI

> Bhai, ye wala AI hai jo **aapke data par, aapki machine par, scratch se train hua hai** —
> bilkul naya model, Hindi samajh kar Python code likhta hai.

## Kya hai ye?

- **Model:** Mini GPT (nanoGPT-style transformer), **6.5 million parameters**, pure PyTorch
- **Kam:** Hindi (Devanagari) me coding sawaal puchho → Python code milta hai
- **Data:** 78,084 Hindi→Python pairs (~2.27M tokens)
  - 160 hand-written examples (math, strings, lists, dicts, OOP, algorithms, practical)
  - ~78,000 synthetic examples (template-based, function names/values/phrasings vary)
- **Training:** is hi machine par (2 CPU cores, 4GB RAM, **no GPU**) — ~3.5 ghante
- **Tokenizer:** byte-level BPE, 6,390 tokens (Hindi + Python dono cover)

## Pipeline

```
data/seeds/*.json        →  160 hand-written Hindi→code examples
data/build_dataset.py    →  + synthetic templates = 78k pairs
                            → BPE vocab train (6,390 tokens)
                            → train.bin / dev.bin
model/tokenizer.py       →  byte-level BPE (Devanagari + code safe)
model/net.py             →  MiniGPT (tied embeddings, LayerNorm, GELU)
model/train.py           →  AdamW, warmup+cosine LR, grad clip, checkpointing
model/evaluate.py        →  held-out 60 sawal → code generate → run → pass/fail
app/server.py            →  Hindi chat web app (Flask, port 8000)
```

## Chala kaise

```bash
# 1. Environment (pehli baar)
python3 -m venv .venv && .venv/bin/pip install torch numpy flask

# 2. Dataset banao (~7 min)
.venv/bin/python studio-hindi-ai/data/build_dataset.py --synth 3000

# 3. Model train karo (is machine par ~3.5h)
OMP_NUM_THREADS=2 .venv/bin/python studio-hindi-ai/model/train.py \
  --preset tiny --epochs 8 --batch 16 --block 384 \
  --lr 8e-4 --warmup 200 --eval-every 500 --save-every 1000 --vocab 6390

# 4. Evaluate karo (held-out sawal par)
.venv/bin/python studio-hindi-ai/model/evaluate.py --n 60

# 5. Web app (Hindi chat)
.venv/bin/python studio-hindi-ai/app/server.py   # → http://localhost:8000
```

## Natije (Results)

_Training complete hone ke baad ye section `reports/eval_report.md` se update hoga._

| Metric | Value |
|---|---|
| Valid Python | _pending_ |
| Runs without error | _pending_ |
| Output exact match | _pending_ |

## Web app

`app/server.py` chala ke browser me `http://localhost:8000` kholo:
- Hindi me sawaal likho (ya example chip dabao)
- Model code likh deta hai → **Copy** aur **▶ चलाओ** buttons se turant run karo
- Output wahi dikhta hai

## 💪 Claude ko takkar dene ka asli raasta (honest baat)

Is machine par jo ban saka wo **chhota par asli** model hai — scratch se trained, aapke data par.
Claude-Code level ka AI banana GPU + bada model + zyada data maangta hai. **Wo raasta bhi taiyaar hai:**

1. `scaleup/colab_lora_finetune.py` ko **Google Colab** (free GPU) par chalao
2. Ye Qwen2.5-Coder (1.5B/7B) par aapke **same Hindi dataset** se LoRA fine-tune karta hai
3. Result: Claude-Code ke kaarigari ke kareebi ek Hindi-samajhne wala coding model,
   free HF Space par deploy ho sakta hai

Aur aage:
- Zyada real Hindi data (kaggle/HF se HindiCode jaise datasets)
- 7B+ model + A100
- RL from code execution (code chala ke pass/fail se model ko aur sikhao — GRPO/PPO style)

## Files

```
studio-hindi-ai/
├── README.md
├── data/
│   ├── seeds/            # hand-written Hindi examples (6 categories)
│   ├── build_dataset.py  # dataset + BPE builder
│   └── tokenizer.json    # trained BPE vocab (auto-generated)
├── model/
│   ├── tokenizer.py      # byte-level BPE
│   ├── net.py            # MiniGPT
│   ├── generate.py       # inference helpers
│   ├── train.py          # training loop
│   └── evaluate.py       # held-out code execution eval
├── app/
│   ├── server.py         # Hindi chat app (Flask :8000)
│   └── static/index.html
├── scaleup/
│   └── colab_lora_finetune.py  # GPU scale-up script
├── checkpoints/          # model weights (train ke baad)
└── reports/              # train log + eval report
```

## License

MIT — apna banao, apna sikhao, apna use karo. 🙏
