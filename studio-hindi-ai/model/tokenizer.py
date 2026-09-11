"""
Byte-level BPE tokenizer (GPT-2 style) - self-contained, no external deps.
Handles Devanagari (Hindi) + Python code via UTF-8 byte fallback.

Special tokens:
  0 <BOS>   1 <EOS>   2 <PAD>
bytes occupy ids 3..258, BPE merge tokens start at 259.
"""
import json
import os
import struct
import time
from collections import Counter

BOS, EOS, PAD = 0, 1, 2
BYTE_OFFSET = 3  # byte b -> id b + 3
MERGE_OFFSET = 259  # k-th merge -> id 259 + k


def byte_encode(text: str):
    return [b + BYTE_OFFSET for b in text.encode("utf-8")]


class BPE:
    def __init__(self, itos: dict, rank: dict):
        self.itos = itos          # id -> string
        self.stoi = {s: i for i, s in itos.items()}
        self.rank = rank          # (id, id) -> priority
        self.vocab_size = len(itos)

    # ---------- training ----------
    @classmethod
    def train(cls, corpus, vocab_size=16384, max_merge_len=12, verbose=False):
        t0 = time.time()
        itos = {0: "<BOS>", 1: "<EOS>", 2: "<PAD>"}
        for b in range(256):
            itos[3 + b] = bytes([b]).decode("utf-8", errors="replace")
        rank = {}

        # tokenize corpus into byte-id lists
        token_lists = [byte_encode(t) for t in corpus]
        total = sum(len(x) for x in token_lists)
        if verbose:
            print(f"[bpe] corpus tokens (bytes): {total:,}")

        while len(itos) < vocab_size:
            pair_freqs = Counter()
            for seq in token_lists:
                for a, b in zip(seq, seq[1:]):
                    pair_freqs[(a, b)] += 1
            if not pair_freqs:
                break
            # pick most frequent pair that keeps merged token length bounded
            chosen = None
            for pair, cnt in pair_freqs.most_common():
                if len(itos[pair[0]]) + len(itos[pair[1]]) <= max_merge_len:
                    chosen = pair
                    break
            if chosen is None:
                break
            pair = chosen
            new_id = len(itos)
            # merge: build new sequences
            new_seqs = []
            for seq in token_lists:
                out = []
                i = 0
                while i < len(seq):
                    if i < len(seq) - 1 and (seq[i], seq[i + 1]) == pair:
                        out.append(new_id)
                        i += 2
                    else:
                        out.append(seq[i])
                        i += 1
                new_seqs.append(out)
            token_lists = new_seqs
            # record the string of the merged token
            a_str = itos[pair[0]]
            b_str = itos[pair[1]] if pair[1] < 259 else itos[pair[1]]
            # for merge tokens, reconstruct by decoding via itos
            itos[new_id] = itos[pair[0]] + itos[pair[1]]
            rank[(pair[0], pair[1])] = len(rank)
            if verbose and len(itos) % 2000 == 0:
                print(f"[bpe] vocab={len(itos)}  ({time.time()-t0:.0f}s)")

        return cls(itos=itos, rank=rank)

    # ---------- inference ----------
    def encode(self, text: str):
        seq = byte_encode(text)
        while True:
            pairs = [(self.rank.get((a, b), 10**9), a, b)
                     for a, b in zip(seq, seq[1:])]
            if not pairs:
                break
            best = min(pairs)
            if best[0] >= 10**9:
                break
            new_seq = []
            i = 0
            while i < len(seq):
                if i < len(seq) - 1 and seq[i] == best[1] and seq[i + 1] == best[2]:
                    new_seq.append(259 + best[0])
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1
            seq = new_seq
        return seq

    def decode(self, ids) -> str:
        return "".join(self.itos[i] for i in ids if i in self.itos)

    # ---------- io ----------
    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "itos": {str(k): v for k, v in self.itos.items()},
                "rank": {f"{a},{b}": v for (a, b), v in self.rank.items()},
            }, f)

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        itos = {int(k): v for k, v in d["itos"].items()}
        rank = {tuple(map(int, k.split(","))): v for k, v in d["rank"].items()}
        return cls(itos=itos, rank=rank)


def write_bin(path, ids):
    with open(path, "wb") as f:
        f.write(struct.pack(f"{len(ids)}i", *ids))


def load_bin(path):
    import numpy as np
    return np.memmap(path, dtype="int32", mode="r")
