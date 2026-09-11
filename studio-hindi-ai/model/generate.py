"""Shared generation helpers for the trained Hindi Coder model."""
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tokenizer import BPE, EOS, BOS  # noqa: E402

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CKPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checkpoints")


def load_model(ckpt_name="best.pt", tok_name="tokenizer.json"):
    import torch
    from net import MiniGPT
    tok = BPE.load(os.path.join(DATA, tok_name))
    path = os.path.join(CKPT, ckpt_name)
    if not os.path.exists(path):
        # fall back
        for alt in ("final.pt", "best.pt"):
            if os.path.exists(os.path.join(CKPT, alt)):
                path = os.path.join(CKPT, alt)
                break
    model = MiniGPT.load(path, device="cpu")
    return model, tok


def format_prompt(q):
    return "प्रश्न: " + q + "\nकोड:\n"


def generate_code(model, tok, q, max_new=350, temperature=0.6, top_k=40, greedy=False):
    ids = [BOS] + tok.encode(format_prompt(q))
    if len(ids) > model.cfg["block_size"] - 8:
        ids = ids[-(model.cfg["block_size"] - 8):]
    x = torch.tensor([ids], dtype=torch.long)
    with torch.no_grad():
        if greedy:
            out = x
            for _ in range(max_new):
                logits, _ = model(out)
                nxt = logits[0, -1].argmax().unsqueeze(0).unsqueeze(0)
                out = torch.cat((out, nxt), dim=1)
                if nxt.item() == EOS:
                    break
        else:
            out = model.generate(x, max_new_tokens=max_new, temperature=temperature,
                                 top_k=top_k, eos_id=EOS)
    text = tok.decode(out[0].tolist())
    # strip prompt prefix
    idx = text.rfind("\nकोड:\n")
    if idx != -1:
        code = text[idx + len("\nकोड:\n"):]
    else:
        code = text
    return code.strip()
