"""
SCALE-UP PATH — Claude-level takkar dene ke liye
==================================================
Is sandbox (2 CPU, 4GB RAM, no GPU) par sirf chhota model train ho sakta hai.
Claude/Claude-Code level coding AI banane ke liye ye script Google Colab
(free T4/A100) ya kisi bhi GPU par chalayen.

Kya karta hai:
  1. Qwen2.5-Coder-1.5B (ya 7B) ko le leta hai — ye pehle se strong coding model hai
  2. Aapka Hindi coding dataset (jo is repo me hai) par LoRA fine-tune karta hai
  3. Result: ek Hindi-samajhne wala coding model jo Qwen pe based hai

Kaise chalayen:
  1. google.colab.com kholen -> New notebook (GPU runtime)
  2. Ye file upload karke uska content paste kar dein
  3. Run karein (1.5B par T4 par ~2-4 ghante, 7B par A100 par ~6-10 ghante)
  4. Save hua adapter HF Space par deploy karein -> free hosting
"""
import json
import os

# pip install -q transformers datasets peft accelerate bitsandbytes
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"  # 7B ke liye: "Qwen/Qwen2.5-Coder-7B-Instruct"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
OUTPUT_DIR = "hindi-coder-lora"


def load_pairs():
    pairs = []
    for f in os.listdir(os.path.join(DATA_DIR, "seeds")):
        if f.endswith(".json"):
            for p in json.load(open(os.path.join(DATA_DIR, "seeds", f), encoding="utf-8")):
                pairs.append((p["q"], p["code"]))
    # agar synthetic jsonl present ho (build_dataset.py se bana sakte ho)
    synth = os.path.join(DATA_DIR, "docs_train.jsonl")
    if os.path.exists(synth):
        for line in open(synth, encoding="utf-8"):
            d = json.loads(line)
            pairs.append((d["q"], d["code"]))
    return pairs


def chat_template(q, code):
    """Qwen chat format me prompt+answer"""
    return (
        f"<|im_start|>user\n{q}<|im_end|>\n"
        f"<|im_start|>assistant\n```python\n{code}\n```<|im_end|>\n"
    )


def main():
    pairs = load_pairs()
    print(f"pairs: {len(pairs)}")
    texts = [chat_template(q, c) for q, c in pairs]
    ds = Dataset.from_dict({"text": texts})

    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    tok.pad_token = tok.eos_token

    def collate(batch):
        enc = tok([b["text"] for b in batch], padding=True, truncation=True, max_length=512)
        return enc

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16, device_map="auto"
    )
    model = prepare_model_for_kbit_training(model)
    lora = LoraConfig(
        r=32, lora_alpha=64, lora_dropout=0.05, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    args = TrainingArguments(
        OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        warmup_steps=50,
        logging_steps=10,
        save_strategy="epoch",
        fp16=False, bf16=True,
        optim="paged_adamw_8bit",
        report_to="none",
    )
    from transformers import Trainer
    trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collate)
    trainer.train()
    model.save_pretrained(os.path.join(OUTPUT_DIR, "final"))
    tok.save_pretrained(os.path.join(OUTPUT_DIR, "final"))
    print("DONE ->", OUTPUT_DIR)
    print("Ab HF Spaces par 'Qwen/Qwen2.5-Coder-1.5B-Instruct' + ye adapter deploy karein")


if __name__ == "__main__":
    main()
