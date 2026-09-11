"""
Train the Hindi Coder mini-GPT on the built dataset (CPU).
Usage: python train.py --preset small --epochs 8 --batch 8 --block 192
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from net import MiniGPT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
CKPT = os.path.join(os.path.dirname(HERE), "checkpoints")

PRESETS = {
    # name: (n_layer, n_embd, n_head)  -> ~params
    "tiny":  (6, 256, 4),    # ~6.5M
    "small": (8, 320, 5),    # ~13M
    "base":  (10, 384, 6),   # ~23M
}


def get_batch(data, block_size, batch_size):
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([data[i:i + block_size] for i in ix])
    y = torch.stack([data[i + 1:i + block_size + 1] for i in ix])
    return x, y  # data is a torch tensor


def load_tensor(path):
    return torch.from_numpy(np.fromfile(path, dtype=np.int32)).long()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="small", choices=list(PRESETS))
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--block", type=int, default=192)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--grad-clip", type=float, default=1.0)
    ap.add_argument("--log-every", type=int, default=25)
    ap.add_argument("--eval-every", type=int, default=200)
    ap.add_argument("--save-every", type=int, default=500)
    ap.add_argument("--vocab", type=int, default=16384)
    ap.add_argument("--threads", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(CKPT, exist_ok=True)
    if args.threads:
        torch.set_num_threads(args.threads)
    else:
        torch.set_num_threads(min(2, os.cpu_count()))

    n_layer, n_embd, n_head = PRESETS[args.preset]
    cfg = dict(n_layer=n_layer, n_embd=n_embd, n_head=n_head,
               vocab_size=args.vocab, block_size=args.block, dropout=0.0)
    n_params = sum(p.numel() for p in MiniGPT(cfg).parameters())
    print(f"[train] preset={args.preset} params={n_params/1e6:.1f}M "
          f"batch={args.batch} block={args.block} epochs={args.epochs}", flush=True)

    train_data = load_tensor(os.path.join(DATA, "train.bin"))
    dev_data = load_tensor(os.path.join(DATA, "dev.bin"))
    print(f"[train] train tokens={len(train_data):,} dev tokens={len(dev_data):,}", flush=True)

    model = MiniGPT(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.wd, betas=(0.9, 0.95))

    steps_per_epoch = max(1, int(len(train_data) / (args.batch * args.block)))
    total_steps = steps_per_epoch * args.epochs
    print(f"[train] steps/epoch~{steps_per_epoch} total_steps={total_steps}", flush=True)

    def lr_at(step):
        if step < args.warmup:
            return args.lr * (step + 1) / args.warmup
        prog = (step - args.warmup) / max(1, total_steps - args.warmup)
        return args.lr * 0.5 * (1 + math.cos(math.pi * min(prog, 1.0)))

    log_path = os.path.join(CKPT, "train_log.jsonl")
    logf = open(log_path, "a")
    best_dev = float("inf")
    t0 = time.time()
    step = 0
    tokens_seen = 0

    for epoch in range(args.epochs):
        model.train()
        for it in range(steps_per_epoch):
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            x, y = get_batch(train_data, args.block, args.batch)
            logits, loss = model(x, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            tokens_seen += args.batch * args.block

            if step % args.log_every == 0:
                dt = time.time() - t0
                tok_s = tokens_seen / dt
                print(f"[step {step}/{total_steps}] epoch={epoch+1} loss={loss.item():.4f} "
                      f"lr={g['lr']:.2e} tok/s={tok_s:,.0f} elapsed={dt/60:.1f}m", flush=True)
                logf.write(json.dumps({"step": step, "epoch": epoch + 1,
                                       "loss": loss.item(), "lr": g["lr"],
                                       "tok_per_s": tok_s,
                                       "t": time.time()}) + "\n")
                logf.flush()

            if step % args.eval_every == 0:
                model.eval()
                with torch.no_grad():
                    dev_losses = []
                    for _ in range(10):
                        x, y = get_batch(dev_data, args.block, args.batch)
                        _, dl = model(x, y)
                        dev_losses.append(dl.item())
                dev_loss = float(np.mean(dev_losses))
                ppl = math.exp(min(dev_loss, 20))
                print(f"[eval] dev_loss={dev_loss:.4f} ppl={ppl:.1f}", flush=True)
                logf.write(json.dumps({"step": step, "type": "dev",
                                       "loss": dev_loss}) + "\n")
                logf.flush()
                if dev_loss < best_dev:
                    best_dev = dev_loss
                    model.save(os.path.join(CKPT, "best.pt"))
                    print("[eval] saved best.pt", flush=True)
                model.train()

            if step % args.save_every == 0:
                model.save(os.path.join(CKPT, f"step_{step}.pt"))

    model.save(os.path.join(CKPT, "final.pt"))
    logf.close()
    print(f"[train] DONE in {(time.time()-t0)/60:.1f} min. checkpoints in {CKPT}", flush=True)


if __name__ == "__main__":
    main()
