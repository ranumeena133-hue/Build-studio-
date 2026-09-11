"""
Dataset builder: hand-written seed pairs + synthetic template pairs.
Outputs: data/docs_train.jsonl, data/docs_dev.jsonl, data/tokenizer.json, data/train.bin, data/dev.bin
Format per doc:  "प्रश्न: {q}\nकोड:\n{code}"
"""
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PREFIX = "प्रश्न: "
CODE_MARK = "\nकोड:\n"

FUN_NAMES = [
    "calc_total", "compute", "get_result", "solve_it", "do_math", "my_func",
    "process", "helper_fn", "the_answer", "quick_calc", "simple_fn", "make_it",
    "run_calc", "value_fn", "result_fn", "math_tool", "easy_fn", "fast_calc",
    "num_work", "basic_fn", "tool_fn", "do_it", "calc_fn", "get_value",
    "find_it", "work_fn", "num_fn", "total_fn", "avg_fn", "sum_fn",
    "check_fn", "test_fn", "main_fn", "first_fn", "second_fn", "other_fn",
]
VAR2 = [("a", "b"), ("x", "y"), ("n", "m"), ("p", "q"), ("first", "second"),
        ("num1", "num2"), ("val1", "val2"), ("u", "v"), ("i", "j")]
VAR1 = ["n", "x", "num", "val", "number", "value", "a", "i"]
LIST_VARS = ["lst", "arr", "nums", "data", "values", "items", "list1"]
STR_VARS = ["s", "text", "word", "str1", "string", "txt", "line"]


def pick(lst, rng):
    return rng.choice(lst)


# ---------------- template families ----------------

def f_sum2(rng):
    a, b = rng.randint(-30, 30), rng.randint(-30, 30)
    name = pick(FUN_NAMES, rng)
    v1, v2 = pick(VAR2, rng)
    q = pick([
        f"Ek function {name} likho jo do numbers ka sum nikale, jaise {a} aur {b}.",
        f"{name} naam ka function likho jo {v1} aur {v2} ko jodkar return kare. Example: {a}, {b}.",
        f"Function likho jo {a} aur {b} jodkar {a + b} de. Function ka naam {name} ho.",
    ], rng)
    code = (f"def {name}({v1}, {v2}):\n    return {v1} + {v2}\n\n"
            f"print({name}({a}, {b}))  # output: {a + b}")
    return q, code


def f_diff(rng):
    a, b = rng.randint(1, 50), rng.randint(1, 50)
    name = pick(FUN_NAMES, rng)
    v1, v2 = pick(VAR2, rng)
    q = pick([
        f"Ek function {name} likho jo {v1} me se {v2} minus kare. Example: {a} aur {b}.",
        f"Function {name} likho jo do numbers ka difference nikale ({a} - {b} = {a - b}).",
    ], rng)
    code = (f"def {name}({v1}, {v2}):\n    return {v1} - {v2}\n\n"
            f"print({name}({a}, {b}))  # output: {a - b}")
    return q, code


def f_product(rng):
    a, b = rng.randint(1, 20), rng.randint(1, 20)
    name = pick(FUN_NAMES, rng)
    v1, v2 = pick(VAR2, rng)
    q = f"Ek function {name} likho jo do numbers {a} aur {b} ka multiplication nikale."
    code = (f"def {name}({v1}, {v2}):\n    return {v1} * {v2}\n\n"
            f"print({name}({a}, {b}))  # output: {a * b}")
    return q, code


def f_power(rng):
    a = rng.randint(2, 12)
    e = rng.randint(2, 5)
    name = pick(FUN_NAMES, rng)
    q = f"Ek function {name} likho jo base {a} ka power {e} nikale, yaani {a} ki {e} power."
    code = (f"def {name}(base, exp):\n    result = 1\n"
            f"    for _ in range(exp):\n        result *= base\n    return result\n\n"
            f"print({name}({a}, {e}))  # output: {a ** e}")
    return q, code


def f_max2(rng):
    a, b = rng.randint(1, 99), rng.randint(1, 99)
    if a == b:
        b += 1
    name = pick(FUN_NAMES, rng)
    v1, v2 = pick(VAR2, rng)
    big = max(a, b)
    q = f"Ek function {name} likho jo do numbers {a} aur {b} me se bada batae."
    code = (f"def {name}({v1}, {v2}):\n    if {v1} > {v2}:\n        return {v1}\n"
            f"    return {v2}\n\nprint({name}({a}, {b}))  # output: {big}")
    return q, code


def f_avg_list(rng):
    nums = [rng.randint(1, 100) for _ in range(rng.randint(3, 6))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    avg = sum(nums) / len(nums)
    q = f"Ek function {name} likho jo list {nums} ka average nikale."
    code = (f"def {name}({lv}):\n    if not {lv}:\n        return 0\n"
            f"    return sum({lv}) / len({lv})\n\n"
            f"print({name}({nums}))  # output: {avg}")
    return q, code


def f_sum_list(rng):
    nums = [rng.randint(1, 50) for _ in range(rng.randint(3, 6))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    q = f"Ek function {name} likho jo list {nums} ke saare numbers ka sum nikale bina sum() use kiye."
    code = (f"def {name}({lv}):\n    total = 0\n    for x in {lv}:\n"
            f"        total += x\n    return total\n\n"
            f"print({name}({nums}))  # output: {sum(nums)}")
    return q, code


def f_even_odd(rng):
    n = rng.randint(1, 99)
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    ans = "True" if n % 2 == 0 else "False"
    q = f"Ek function {name} likho jo check kare ki {v} even hai ya nahi. Example: {n} ke liye {ans}."
    code = (f"def {name}({v}):\n    return {v} % 2 == 0\n\n"
            f"print({name}({n}))  # output: {ans}")
    return q, code


def f_reverse_str(rng):
    words = ["hindi", "python", "coding", "studio", "namaste", "dost", "sarkar",
             "bharat", "jaldi", "padhai", "khana", "chaap", "naya", "accha"]
    s = pick(words, rng)
    if rng.random() < 0.5:
        s = s.capitalize()
    name = pick(FUN_NAMES, rng)
    v = pick(STR_VARS, rng)
    q = f"Ek function {name} likho jo string \"{' + '.join([chr(34)] * 0)}{s}\" ko reverse kare." if False else \
        f"Ek function {name} likho jo string '{s}' ko ulta (reverse) kare."
    code = (f"def {name}({v}):\n    return {v}[::-1]\n\n"
            f"print({name}('{s}'))  # output: {s[::-1]}")
    return q, code


def f_palindrome(rng):
    words = ["radar", "level", "madam", "racecar", "civic", "rotor", "kayak",
             "anna", "hindi", "python", "dost", "bharat"]
    s = pick(words, rng)
    name = pick(FUN_NAMES, rng)
    v = pick(STR_VARS, rng)
    ans = "True" if s == s[::-1] else "False"
    q = f"Ek function {name} likho jo batae ki '{s}' palindrome hai ya nahi."
    code = (f"def {name}({v}):\n    {v} = {v}.lower()\n    return {v} == {v}[::-1]\n\n"
            f"print({name}('{s}'))  # output: {ans}")
    return q, code


def f_vowels(rng):
    words = ["hello world", "hindi coding", "namaste duniya", "python ki padhai",
             "accha hai", "bharat mata ki jai", "main seekh raha hu", "chai piyo"]
    s = pick(words, rng)
    name = pick(FUN_NAMES, rng)
    v = pick(STR_VARS, rng)
    c = sum(1 for ch in s if ch in "aeiou")
    q = f"Ek function {name} likho jo string '{s}' me kitne vowels hain ye count kare."
    code = (f"def {name}({v}):\n    count = 0\n    for ch in {v}:\n"
            f"        if ch.lower() in \"aeiou\":\n            count += 1\n"
            f"    return count\n\nprint({name}('{s}'))  # output: {c}")
    return q, code


def f_upper(rng):
    words = ["namaste", "hindi", "dost", "python", "coding", "studio"]
    s = pick(words, rng)
    name = pick(FUN_NAMES, rng)
    v = pick(STR_VARS, rng)
    q = f"Ek function {name} likho jo '{s}' ko UPPERCASE me convert kare."
    code = (f"def {name}({v}):\n    result = \"\"\n    for ch in {v}:\n"
            f"        if 97 <= ord(ch) <= 122:\n            result += chr(ord(ch) - 32)\n"
            f"        else:\n            result += ch\n    return result\n\n"
            f"print({name}('{s}'))  # output: {s.upper()}")
    return q, code


def f_words_count(rng):
    s = pick(["main coding seekh raha hu", "aaj accha din hai", "hindi me coding karte ho",
              "kal baazi jaunga", "chalo padhte hai"], rng)
    name = pick(FUN_NAMES, rng)
    v = pick(STR_VARS, rng)
    n = len(s.split())
    q = f"Ek function {name} likho jo string '{s}' me kitne words hain ye batae."
    code = (f"def {name}({v}):\n    words = {v}.split()\n    return len(words)\n\n"
            f"print({name}('{s}'))  # output: {n}")
    return q, code


def f_max_list(rng):
    nums = [rng.randint(1, 100) for _ in range(rng.randint(4, 7))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    q = f"Ek function {name} likho jo list {nums} me sabse bada number nikale."
    code = (f"def {name}({lv}):\n    max_val = {lv}[0]\n    for x in {lv}:\n"
            f"        if x > max_val:\n            max_val = x\n    return max_val\n\n"
            f"print({name}({nums}))  # output: {max(nums)}")
    return q, code


def f_min_list(rng):
    nums = [rng.randint(1, 100) for _ in range(rng.randint(4, 7))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    q = f"Ek function {name} likho jo list {nums} me sabse chhota number nikale."
    code = (f"def {name}({lv}):\n    min_val = {lv}[0]\n    for x in {lv}:\n"
            f"        if x < min_val:\n            min_val = x\n    return min_val\n\n"
            f"print({name}({nums}))  # output: {min(nums)}")
    return q, min(nums), code


def f_evens_list(rng):
    nums = [rng.randint(1, 40) for _ in range(rng.randint(5, 8))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    evens = [x for x in nums if x % 2 == 0]
    q = f"Ek function {name} likho jo list {nums} se saare even numbers nikale."
    code = (f"def {name}({lv}):\n    result = []\n    for x in {lv}:\n"
            f"        if x % 2 == 0:\n            result.append(x)\n    return result\n\n"
            f"print({name}({nums}))  # output: {evens}")
    return q, code, code


def f_double_list(rng):
    nums = [rng.randint(1, 20) for _ in range(rng.randint(3, 5))]
    name = pick(FUN_NAMES, rng)
    lv = pick(LIST_VARS, rng)
    doubled = [x * 2 for x in nums]
    q = f"Ek function {name} likho jo list {nums} ke saare numbers ko double kare."
    code = (f"def {name}({lv}):\n    result = []\n    for x in {lv}:\n"
            f"        result.append(x * 2)\n    return result\n\n"
            f"print({name}({nums}))  # output: {doubled}")
    return q, code


def f_factorial(rng):
    n = rng.randint(3, 9)
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    fact = 1
    for i in range(2, n + 1):
        fact *= i
    q = f"Ek function {name} likho jo {n} ka factorial nikale."
    code = (f"def {name}({v}):\n    if {v} <= 1:\n        return 1\n"
            f"    return {v} * {name}({v} - 1)\n\n"
            f"print({name}({n}))  # output: {fact}")
    return q, code


def f_prime(rng):
    n = rng.choice([7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
                    4, 6, 8, 9, 10, 12, 15, 21, 25, 27, 33, 35, 49])
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    def is_prime(x):
        if x < 2:
            return False
        for i in range(2, int(x ** 0.5) + 1):
            if x % i == 0:
                return False
        return True
    ans = "True" if is_prime(n) else "False"
    q = f"Ek function {name} likho jo batae ki {n} prime number hai ya nahi."
    code = (f"def {name}({v}):\n    if {v} < 2:\n        return False\n"
            f"    for i in range(2, int({v} ** 0.5) + 1):\n"
            f"        if {v} % i == 0:\n            return False\n"
            f"    return True\n\nprint({name}({n}))  # output: {ans}")
    return q, code


def f_gcd(rng):
    a = rng.randint(2, 40) * rng.randint(1, 3)
    b = rng.randint(2, 40)
    def gcd(x, y):
        while y:
            x, y = y, x % y
        return x
    g = gcd(a, b)
    name = pick(FUN_NAMES, rng)
    v1, v2 = pick(VAR2, rng)
    q = f"Ek function {name} likho jo {a} aur {b} ka GCD nikale."
    code = (f"def {name}({v1}, {v2}):\n    while {v2}:\n"
            f"        {v1}, {v2} = {v2}, {v1} % {v2}\n    return {v1}\n\n"
            f"print({name}({a}, {b}))  # output: {g}")
    return q, code


def f_celsius(rng):
    t = rng.randint(-10, 60)
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    ans = round((t * 9 / 5) + 32, 1)
    q = f"Ek function {name} likho jo {t} degree Celsius ko Fahrenheit me convert kare."
    code = (f"def {name}(c):\n    return (c * 9 / 5) + 32\n\n"
            f"print({name}({t}))  # output: {ans}")
    return q, code


def f_rect_area(rng):
    w, h = rng.randint(2, 30), rng.randint(2, 30)
    name = pick(FUN_NAMES, rng)
    q = f"Ek function {name} likho jo rectangle ka area nikale, jiska width {w} aur height {h} ho."
    code = (f"def {name}(width, height):\n    return width * height\n\n"
            f"print({name}({w}, {h}))  # output: {w * h}")
    return q, code


def f_circle_area(rng):
    r = rng.randint(1, 15)
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    ans = round(3.14159 * r * r, 2)
    q = f"Ek function {name} likho jo circle ka area nikale, radius {r} hai."
    code = (f"def {name}({v}):\n    return 3.14159 * {v} * {v}\n\n"
            f"print(round({name}({r}), 2))  # output: {ans}")
    return q, code


def f_two_sum(rng):
    nums = sorted(rng.sample(range(1, 40), rng.randint(4, 6)))
    i = rng.randint(0, len(nums) - 2)
    j = rng.randint(i + 1, len(nums) - 1)
    target = nums[i] + nums[j]
    name = pick(FUN_NAMES, rng)
    q = f"Ek function {name} likho jo list {nums} me aise do numbers dhunde jinka sum {target} ho, aur unke indexes return kare."
    code = (f"def {name}(nums, target):\n    seen = {{}}\n    for i, x in enumerate(nums):\n"
            f"        need = target - x\n        if need in seen:\n"
            f"            return [seen[need], i]\n        seen[x] = i\n    return []\n\n"
            f"print({name}({nums}, {target}))  # output: [0, 1]")
    return q, code


def f_percent(rng):
    part = rng.randint(1, 90)
    whole = part * rng.randint(2, 10)
    name = pick(FUN_NAMES, rng)
    q = f"Ek function {name} likho jo nikale ki {part}, {whole} ka kitna percent hai."
    code = (f"def {name}(part, whole):\n    return (part / whole) * 100\n\n"
            f"print({name}({part}, {whole}))  # output: {part / whole * 100}")
    return q, code


def f_fib(rng):
    n = rng.randint(4, 10)
    a, b, seq = 0, 1, []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    name = pick(FUN_NAMES, rng)
    v = pick(VAR1, rng)
    q = f"Ek function {name} likho jo Fibonacci sequence ke pehle {n} numbers nikale."
    code = (f"def {name}({v}):\n    seq = []\n    x, y = 0, 1\n"
            f"    for _ in range({v}):\n        seq.append(x)\n"
            f"        x, y = y, x + y\n    return seq\n\n"
            f"print({name}({n}))  # output: {seq}")
    return q, code


FAMILIES = [f_sum2, f_diff, f_product, f_power, f_max2, f_avg_list, f_sum_list,
            f_even_odd, f_reverse_str, f_palindrome, f_vowels, f_upper, f_words_count,
            f_max_list, f_min_list, f_evens_list, f_double_list, f_factorial, f_prime,
            f_gcd, f_celsius, f_rect_area, f_circle_area, f_two_sum, f_percent, f_fib]


def build_pairs(seed_ratio=1.0, synth_per_family=900, seed=42):
    rng = random.Random(seed)
    pairs = []
    # seeds (hand-written)
    for fname in sorted(os.listdir(os.path.join(HERE, "seeds"))):
        if fname.endswith(".json"):
            with open(os.path.join(HERE, "seeds", fname), encoding="utf-8") as f:
                for p in json.load(f):
                    pairs.append((p["q"], p["code"]))
    # synthetic
    for fam in FAMILIES:
        for _ in range(synth_per_family):
            out = fam(rng)
            if len(out) == 2:
                pairs.append(out)
            elif len(out) == 3:
                pairs.append((out[0], out[2]))
    return pairs


def to_doc(q, code):
    return PREFIX + q + CODE_MARK + code


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--synth", type=int, default=1500)
    ap.add_argument("--dev-size", type=int, default=600)
    args = ap.parse_args()

    print("[data] building pairs...")
    pairs = build_pairs(synth_per_family=args.synth)
    print(f"[data] total pairs: {len(pairs)}")

    random.Random(1).shuffle(pairs)
    dev = pairs[:args.dev_size]
    train = pairs[args.dev_size:]
    print(f"[data] train: {len(train)}  dev: {len(dev)}")

    with open(os.path.join(HERE, "docs_train.jsonl"), "w", encoding="utf-8") as f:
        for q, c in train:
            f.write(json.dumps({"q": q, "code": c}, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "docs_dev.jsonl"), "w", encoding="utf-8") as f:
        for q, c in dev:
            f.write(json.dumps({"q": q, "code": c}, ensure_ascii=False) + "\n")

    # tokenize
    sys.path.insert(0, os.path.join(ROOT, "model"))
    from tokenizer import BPE, write_bin, BOS, EOS

    docs = [to_doc(q, c) for q, c in train]
    print("[data] training BPE vocab on sample (this can take a while)...")
    tok = BPE.train(docs[:1800], vocab_size=8192, max_merge_len=12, verbose=True)
    tok.save(os.path.join(HERE, "tokenizer.json"))
    print(f"[data] vocab size: {tok.vocab_size}")

    print("[data] tokenizing train...")
    all_ids = []
    n_tok = 0
    lens = []
    for d in docs:
        ids = tok.encode(d)
        all_ids.append(BOS)
        all_ids.extend(ids)
        all_ids.append(EOS)
        n_tok += len(ids)
        lens.append(len(ids))
    lens.sort()
    print(f"[data] train tokens: {n_tok:,}")
    print(f"[data] doc tokens avg={sum(lens)/len(lens):.0f} median={lens[len(lens)//2]} "
          f"p95={lens[int(len(lens)*0.95)]}")
    write_bin(os.path.join(HERE, "train.bin"), all_ids)

    dev_docs = [to_doc(q, c) for q, c in dev]
    dev_ids = []
    for d in dev_docs:
        ids = tok.encode(d)
        dev_ids.append(BOS)
        dev_ids.extend(ids)
        dev_ids.append(EOS)
    print(f"[data] dev tokens: {len(dev_ids):,}")
    write_bin(os.path.join(HERE, "dev.bin"), dev_ids)
    print("[data] DONE")


if __name__ == "__main__":
    main()
