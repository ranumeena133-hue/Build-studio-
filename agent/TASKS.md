# TASKS.md — agent ko kya-kya bol sakte ho (task JSON spec)

Phone par `bhai` yehi files khaata hai: `tasks/*.json` (repo me main likhta hoon,
phone `bhai sync` / `bhai watch` se uthaata hai).

## Shape

```json
{
  "id": "0042-clean",
  "title": "Downloads safe cleanup",
  "confirm": "MERGE",
  "steps": [
    { "op": "delete", "glob": "**/*.tmp", "root": "Download" }
  ]
}
```

* `id` — ek baar per task apply hota hai (duplicate se bachne ke liye). Dobara chalane ke liye `bhai run <id> --force`.
* `confirm` — do to phone par terminal me woh exact word type karna padega, warna task skip.
  Main bhaari/nukli kaam par yeh lagata hoon.
* `steps` — order-wise chalti hain. Ek step fail ho to bhi aage chalti hain (report me `err` dikhega).

## Paths

Step me jo bhi path do, woh **shared storage ke relative** hote hain:

| aap likho | matlab |
|---|---|
| `DCIM/Camera/x.jpg` | `/sdcard/DCIM/Camera/x.jpg` |
| `Download/` | `/sdcard/Download/` |
| `~/scripts/x.sh` | Termux home |
| `/data/data/com.termux/...` | absolute |

Folders ke liye aage `/` lagao (`Download/BuildStudio/`) to `mkdir` folder bana dega.

**Safety:** likhna/move/delete sirf `/sdcard`, `$HOME`, `~/.bhai`, `/tmp`, repo ke andar allowed hai.
Baaki sab par step error karta hai: `Safety: outside allowed roots`.
`delete` kabhi hard-delete nahi karta — `~/.bhai/trash/<time>/` me jata hai (recover ho jata hai).
Sirf `"force": true` ke saath permanent hota hai.

## Ops (sabhi me opt.: `glob`+`root` se bulk, `--dry` se preview)

| op | fields | kya karta hai |
|---|---|---|
| `note` | `text` | report me line |
| `sh` | `cmd`, `timeout`, `show` | Termux shell command (stdout captured) |
| `mkdir` | `path` | folder (trailing `/` = folder) |
| `write` | `path`, `content` \| `content_b64`, `crlf` | file banaao/overwrite |
| `append` | `path`, `content` | end me jodo |
| `touch` | `path` | khali file / timestamp |
| `replace` | `path`\|`glob`, `find`, `with`, `regex`, `count` | text substitute |
| `replace` | `lines:true`, `find:"7"`, `with:".."`, `delete_lines` | line-number edit |
| `copy` | `path`/`glob`, `to` | copy (`to` dir ho to naam bachaata hai) |
| `move` | `path`, `to` | move/rename |
| `rename` | `glob`, `pattern` | bulk rename: `{n} {name} {ext} {extd} {date} {time} {size}` |
| `delete` | `path`/`glob`, `force` | trash (ya force = permanent) |
| `extract` | `path` (.zip/.tar\*), `to` | unpack |
| `compress` | `path`, `to` | zip banaao |
| `link` | `path`, `to` | symlink |
| `chmod` | `path`, `mode` | e.g. `"755"` |
| `up` | `paths:[...]` ya `glob` | file staging → main edit kar sakta hoon |
| `download` | `url`, `to` | curl (net chahiye) |

Bulk example:

```json
{ "op": "rename", "root": "DCIM/Camera", "glob": "**/IMG_*.jpg", "pattern": "{date}-{n}{extd}" }
```

## Puri loop (do transport)

1. **Zero-setup (default):** main `tasks/*.json` ya `storage/file` commit karta hoon →
   tum phone par `bhai sync` (ya `bhai watch` chhoda hua) → apply → `bhai report` → tum
   report ka text mujhe chat me paste. **Koi token nahi, koi app nahi.**
2. **Optional full-auto:** `bhai auth <fine-grained PAT>` (Contents: Read&write, sirf yeh repo)
   → `bhai up <file> -g` seedha repo me push, receipts/reports apne aap aa jaate hain.

## Ek din ka pattern

```
bhai watch                 # ek Termux session me chhodo (har 30s)
```
phir chat me bolo — *"mera Downloads folder sort kar de, 1 saal purane screenshots trash kar de"* —
main task file bana dunga, 30 second me phone par lag jayegi, aur report me dikhega kya hua.

Kuch galat lage to: `bhai log 60`, `ls -R ~/.bhai/trash`, `bhai doctor`.
