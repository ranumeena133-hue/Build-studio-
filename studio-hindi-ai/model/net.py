"""Mini GPT (nanoGPT-style) in pure PyTorch. Weights tied between embedding and LM head."""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        assert cfg["n_embd"] % cfg["n_head"] == 0
        self.n_head = cfg["n_head"]
        self.n_embd = cfg["n_embd"]
        self.head_dim = cfg["n_embd"] // cfg["n_head"]
        self.c_attn = nn.Linear(cfg["n_embd"], 3 * cfg["n_embd"])
        self.c_proj = nn.Linear(cfg["n_embd"], cfg["n_embd"])
        self.attn_drop = nn.Dropout(cfg["dropout"])
        self.resid_drop = nn.Dropout(cfg["dropout"])

    def forward(self, x):
        B, T, C = x.size()
        q, k, v = self.c_attn(x).split(C, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        att = att.masked_fill(
            torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1),
            float("-inf"),
        )
        att = F.softmax(att, dim=-1)
        att = self.attn_drop(att)
        y = (att @ v).transpose(1, 2).contiguous().view(B, T, C)
        return self.resid_drop(self.c_proj(y))


class MLP(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.c_fc = nn.Linear(cfg["n_embd"], 4 * cfg["n_embd"])
        self.c_proj = nn.Linear(4 * cfg["n_embd"], cfg["n_embd"])
        self.drop = nn.Dropout(cfg["dropout"])

    def forward(self, x):
        return self.drop(self.c_proj(F.gelu(self.c_fc(x))))


class Block(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg["n_embd"])
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg["n_embd"])
        self.mlp = MLP(cfg)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x


class MiniGPT(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.transformer = nn.ModuleDict(
            dict(
                wte=nn.Embedding(cfg["vocab_size"], cfg["n_embd"]),
                wpe=nn.Embedding(cfg["block_size"], cfg["n_embd"]),
                h=nn.ModuleList([Block(cfg) for _ in range(cfg["n_layer"])]),
                ln_f=nn.LayerNorm(cfg["n_embd"]),
            )
        )
        self.drop = nn.Dropout(cfg["dropout"])

    def forward(self, idx, targets=None):
        B, T = idx.size()
        assert T <= self.cfg["block_size"]
        pos = torch.arange(T, device=idx.device)
        x = self.drop(self.transformer.wte(idx) + self.transformer.wpe(pos))
        for block in self.transformer.h:
            x = block(x)
        x = self.transformer.ln_f(x)
        # tied LM head: embedding matrix transposed as the output projection
        logits = F.linear(x, self.transformer.wte.weight)  # [B,T,C] -> [B,T,V]
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=0.8, top_k=40, eos_id=1,
                 stop_ids=(1,), repeat_penalty=1.0):
        """idx: [1, T] -> returns [1, T+new]"""
        self.eval()
        out = idx
        for _ in range(max_new_tokens):
            logits, _ = self(out)
            logits = logits[:, -1, :] / temperature
            if repeat_penalty != 1.0:
                # light repetition penalty
                seen = torch.unique(out[0])
                logits[0, seen] = torch.where(
                    logits[0, seen] > 0,
                    logits[0, seen] / repeat_penalty,
                    logits[0, seen] * repeat_penalty,
                )
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")
            probs = F.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)
            out = torch.cat((out, next_id), dim=1)
            if (next_id.item() in stop_ids) and (len(stop_ids) > 1 or next_id.item() == eos_id):
                break
        return out

    def save(self, path):
        torch.save({"model": self.state_dict(), "cfg": self.cfg}, path)

    @classmethod
    def load(cls, path, device="cpu"):
        d = torch.load(path, map_location=device, weights_only=False)
        model = cls(d["cfg"])
        model.load_state_dict(d["model"])
        model.to(device)
        model.eval()
        return model
