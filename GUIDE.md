# Guide: use disciplan yourself

You need Python 3 (standard library only) and a browser. Nothing else is installed.

## 1 · First build

```bash
python scripts/build.py      # → klausuren.html
python scripts/check.py      # optional lint; scripts/check.py <K> --plan also checks the day plan
```

Open `klausuren.html` from disk. You see the three fictional demo modules (KAF, RAD, GAR), a day plan and the strategy tab. Each demo module has a study document (`module/<K>/<K>.html`), KAF and RAD also a trainer (`module/<K>/<K>-Trainer.html`). Rebuild one trainer with `python module/KAF/trainer/build.py`.

## 2 · Set your dates

`scripts/build.py` contains no dates. Everything date-related lives in `PLAN` in `klausuren_data.py`:

```python
PLAN = dict(
  start="2026-08-28",       # first day of the running plan view; earlier days become the archive
  countdown="2026-09-01",   # end of preparation: "days of preparation left" counts down to it
  store="kl-demo",          # localStorage key for ticked goals
  migrations=[],            # see below; empty unless you re-cut the plan
)
```

| Key | What it controls | Note |
|---|---|---|
| `start` | The week grid of the running plan, the "goals since …" counter, the archive boundary (the day before `start`) | Use the first day of your own plan, `YYYY-MM-DD` |
| `countdown` | The "days of preparation left" counter | Usually the day before your first exam |
| `store` | The browser key your ticks are saved under | Change it and progress starts empty. Use one key per exam period |
| `migrations` | One-time resets of ticks after the plan changed | Leave `[]` at the start |

The exam dates of the modules are in `MODULES` (`d="YYYY-MM-DD"`), the day plan in `DAYS`. After a change, run `python scripts/build.py` again.

### Migrations (only when you re-cut a running plan)

Ticks are stored per day index and position (`"47_0"` = day 47, block 0). If you insert or remove blocks in a day that already has ticks, old ticks point at different goals. A migration fixes that once per browser:

```python
migrations=[
  dict(key="kl-recut-1", value="1",    # marker in localStorage; a new value runs it again
       days=[24, None],                # delete ticks of day indexes 24 … end (None = open end)
       steps=False,                    # True also clears the step ticks of those days
       tick=[]),                       # optional: re-tick keys afterwards, e.g. ["47_0"]
]
```

Give every re-cut a new `key` (or `value`), otherwise browsers that already ran it skip it.

## 3 · Replace the demo with your modules

1. Put the old exams in `module/<K>/altklausuren/` and the lecture material in `module/<K>/quellen/`.
2. Open Claude Code in the repo root and paste [prompts/add-module.md](prompts/add-module.md) with your module filled in. It analyses first, proposes a mode and waits for your ok before it creates anything. The rules it follows are in [CLAUDE.md](CLAUDE.md).
3. Delete the demo modules when you no longer need them: remove their folders and their entries in `MODULES` and `DAYS` in `klausuren_data.py`. A folder that isn't in `MODULES` is ignored by `scripts/build.py`.
4. `python scripts/build.py`, then `python scripts/check.py <K>`.

A trainer is optional: GAR has none. Give each module a colour with `col` and `dcol` (light and dark) in its `MODULES` entry. The cockpit uses it for the module card, the sidebar and the plan chips; a trainer takes its colour from `PALETTEN` in `scripts/restyle.py`.

## 4 · Drill

Tell Claude `drill <K>`. It reads the module's `README.md` and `fehler-log.md`, asks **one** question and stops. After your answer it grades strictly, names the exact gap, appends it to `fehler-log.md` and moves on. Details in `CLAUDE.md` → DRILL MODE.

## What the demo does not include

The per-module `README.md` and `fehler-log.md` are not part of the demo modules. They belong to your own modules and are created by the add-module prompt.
