# Build Studio — Termux "bhai" agent

**Bina API, bina server, bina setup ke — Arena chat se apne phone ke storage me badlav.**

Tumhare paas already ek public GitHub repo hai (`Build-studio-`). Yehi bridge hai:

```
  Arena chat (main)                    GitHub repo (public)                Termux (tumhara phone)
  ───────────────                      ────────────────────                ─────────────────────────
  tum bolo: "Downloads clean kar"  ->  tasks/0007-clean.json           ->  bhai sync  /  bhai watch
                                       (commit kar deta hoon)              phone ke /sdcard par apply
                                                                        <-  report likh ke deta hai
  main report padh ke next step   <-   bhai report  (ya paste karo)        (~/.bhai/out/latest.txt)
```

Repo public hai isliye **clone/pull me koi token nahi lagta** — uthana free hai.
Wapas bhejne ke liye bhi kuch nahi chahiye: `bhai report` ka text chat me paste kar do,
ya file attach kar do. Chaaho to ek optional command se push bhi chalu ho jata hai.

## 1 install command (Termux me paste karo)

```bash
git clone --depth 1 -b arena/01a08283-build-studio \
  https://github.com/ranumeena133-hue/Build-studio-.git ~/.bhai/repo \
  && bash ~/.bhai/repo/agent/install.sh
```

`install.sh` sab karta hai: `pkg install git python termux-api`, `~/.bhai` folders,
storage permission check, `bhai` command ko `$PREFIX/bin` me link, config, aur pehla
self-test (`bhai doctor` + `bhai hello`).

> Sirf ek cheez manually karni pad sakti hai (Android permission dialog, script nahi daba sakta):
> `termux-setup-storage` → **Allow** → Termux band karke kholo.

Uske baad:

```bash
bhai hello     # phone par Download/BuildStudio/hello-from-agent.txt banao, khud dekho
bhai sync      # mere naye instructions lao + lagao
bhai watch     # agent mode: har 30s me auto-sync (ek session me chhodo mat)
```

## 2 Commands

| command | kaam |
|---|---|
| `bhai` / `bhai sync` | repo se tasks uthaake apply karo, report banao |
| `bhai watch [sec]` | background agent — har N sec me sync (auto-apply) |
| `bhai up <path>` | apni file/folder staging karo taaki **main edit kar sakun** (`-g` = push bhi) |
| `bhai down` | mere edits original phone location par wapas rakh do (hash se: sirf badle hue) |
| `bhai run <id>` | ek task chalao · `echo '<json>' \| bhai run -` = chat se aaya task directly |
| `bhai ls [dir]` · `bhai find '**/*.mp4'` · `bhai du` | mujhe storage ka naksha dene ke liye |
| `bhai report [--copy]` | paste-ready summary (clipboard, agar termux-api hai) |
| `bhai doctor` | permission / git / network / disk check |
| `bhai config K=V` | REPO_URL, BRANCH, SHARED, MAX_MB, WATCH_SEC, TIMEOUT, NOTIFY |
| `bhai auth <token>` / `bhai auth off` | optional: push-back chalu/band |
| `bhai boot on` | reboot ke baad bhi `watch` apne aap (Termux:Boot app chahiye) |
| `bhai log 60` · `bhai selfupdate` · `bhai uninstall` | debug / update / saaf karna |

Global flags: `--dry` (preview, kuch nahi badlega), `--force` (applied task dobara).

## 3 Security — jo main guarantee deta hoon

* `bhai` phone ke sirf in hisson me likh/move/delete karta hai: `/sdcard`, `$HOME`, `~/.bhai`, `/tmp`, repo clone.
  Path baahir gaya to step turant `Safety: outside allowed roots` pe fail hota hai (symlink-resolve ke baad check).
* `delete` = `~/.bhai/trash/<timestamp>/` me move. Hard-delete sirf `"force": true` par.
* `bhai run x --dry` se har task pehle preview kar lo.
* Kuch bhi destructive ho to main task me `"confirm": "<word>"` dalta hoon — terminal par woh
  word type kiye bina step nahi chalegi.
* Koi server port nahi khulta, koi background network call nahi (sirf `git` us public repo par).
* Token `bhai auth` se set kiya to **sirf tumhare phone** par `~/.bhai/config` me rehta hai, repo me nahi.

## 4 Kaise bolo (examples)

> "Downloads me 50 MB se bade videos `Movies/heavy/` me shift kar de, report bhej"
> "saare screenshots ka naam `2026-09-08-{n}.png` kar de, original copy rakh de"
> "DCIM me duplicate photos dhoondh ke ek list bana de, abhi delete mat kar"
> "mera `.zshrc` theek kar" → `bhai up ~/.zshrc` → main edit → `bhai down`
> `~/storage/shared/Music` me sabhi `.mp3` ke tags folder-name se align karo → `bhai sh '...'` wala step

Main turant `tasks/NNNN-*.json` likh ke commit karunga. Tumhara `bhai watch` use utha lega.

## 5 Files

```
agent/bhai          # pura agent — python3 stdlib only, ~800 lines, koi pip install nahi
agent/install.sh    # one-shot bootstrap (Termux)
agent/TASKS.md      # task JSON ka spec + saare ops
tasks/*.json        # mera inbox: jo phone par karna hai
storage/            # file exchange: tumhari files, mere edits
reports/            # phone ke receipts (push on ho to apne aap aayenge)
```

Phone ka apna state (repo ke baahir, isliye `git reset` se safe):
`~/.bhai/{config, state.json, manifest.json, upload/, out/, trash/, logs/bhai.log}`

## 6 Troubleshooting

| problem | fix |
|---|---|
| `bhai: command not found` | `source ~/.bashrc` (ya naya session) · verify: `ls -l $PREFIX/bin/bhai` |
| `Permission denied` on /sdcard | `termux-setup-storage` → Allow → Termux restart → `bhai doctor` |
| clone/fetch fail | branch delete ho gaya? `bhai config BRANCH=main` · net: `ping github.com` |
| push fail / no token | zarurat nahi — `bhai report` ka text mujhe paste kar do |
| task double-apply? | nahi hoga: `~/.bhai/state.json` me `id` lock hota hai |
| galti se kuch delete ho gaya | `ls ~/.bhai/trash` → `mv` karke wapas |
| Termux background me mar jata hai | Android me Termux ko battery-optimisation se exclude karo, `termux-wake-lock` |
