# Guide

How to use disciplan for your own exam period. The [README](README.md) shows what the tool is; this page is the detail behind "Use it yourself".

**Contents:** [Quick start](#quick-start) · [Dates and the day plan](#dates-and-the-day-plan) · [Add a module](#add-a-module) · [Trainers are optional](#trainers-are-optional) · [Modes and sources](#modes-and-sources) · [The scripts](#the-scripts) · [Module colours](#module-colours) · [Repository layout](#repository-layout) · [Known limits](#known-limits)

---

## Quick start

Needs Python 3 and nothing else (standard library only).

```bash
python scripts/build.py        # merges module/<K>/<K>.html into klausuren.html
python scripts/check.py        # text lint: code blocks, dead anchors, dark-mode clashes
python scripts/check.py KAF --plan   # one module, plus checks of the day plan
```

Open `klausuren.html` in a browser. It is one self-contained file and works offline from the file system. Progress (ticked steps) is saved in the browser's `localStorage`.

## Dates and the day plan

Everything you would edit lives in `klausuren_data.py`:

| Name | What it holds |
|---|---|
| `MODULES` | one entry per module: `k` (short name = folder name), `name`, `d` and `t` (exam date and time), `v` (attempt), `typ` (`PF` required / `WP` elective), `prof`, `mode`, `desc`, `col` (module colour), and `trainer=dict(file=..., was=...)` only if the module has a trainer |
| `PLAN_START` | first day of the running plan view; everything before it goes to the archive |
| `PREP_END` | target date of the "days of preparation left" counter, usually the day before the first exam |
| `DAYS` | the day plan: per day a list of blocks `(module, minutes, type, text, anchor, steps, reminders)` and a day type (`""`, `"deadline"`, `"klausur"`) |
| `TEXT` | the overview texts (title, plan intro, strategy, time windows) |

Block types: **L** read · **U** practise · **D** from memory · **T** test, cold · **W** repeat · **O** organisation · **V** optional (falls below the end-of-day line first).

The principle behind the plan is *objectives instead of hours*: every block is a checkable state ("the state diagram works from memory"), not a time budget. The arrow on a block jumps to the anchor in the study document.

After editing `klausuren_data.py`, run `python scripts/build.py` again.

## Add a module

Put the old exams in `module/<K>/altklausuren/` and the lecture material in `module/<K>/quellen/`, then paste the prompt from [`prompts/add-module.md`](prompts/add-module.md) into Claude Code in the repo root. Fill in only the `+` lines (module, exam date, material). Claude analyses first, proposes the mode and the files, and **waits for your ok** before it creates anything.

By hand, for a module `MATH`:

1. Create `module/MATH/` with `altklausuren/` and `quellen/`, and fill them.
2. Write `module/MATH/README.md` in the six-part structure from [`CLAUDE.md`](CLAUDE.md). Mode: "NOCH NICHT ANALYSIERT" for now.
3. Analyse the old exams as `CLAUDE.md` → *MODULE ANALYSIS* describes, pick the mode, decide the artefacts (at most three `.md` files, one of them `fehler-log.md`), update the README.
4. Write the study document `module/MATH/MATH.html` in the six parts. Copy the `<head>`, CSS and sidebar from `module/KAF/KAF.html` so `build.py` picks it up unchanged.
5. Register it in `klausuren_data.py`: a `dict(k="MATH", name=..., d="YYYY-MM-DD", t="HH:MM", v=1, typ="PF", prof=..., mode=..., desc=..., col="#...")` in `MODULES`, in exam-date order. **A module folder that is not in `MODULES` is ignored by the build.**
6. Optional trainer, see below.
7. `python scripts/build.py`, then `python scripts/check.py MATH`.

## Trainers are optional

A module needs a trainer only when self-testing in the exam's own formats pays off. `GAR` in the demo has none, and the cockpit handles that (no trainer button).

A trainer is one HTML file, built from three parts in `module/<K>/trainer/`:

| Part | What it is |
|---|---|
| `shell.html` | the app: layout, question types, progress |
| `data/` | the question banks (`*.js` or `*.json`) |
| `build.py` | injects the data into the shell and writes `module/<K>/<K>-Trainer.html` |

To add one: copy `module/KAF/trainer/` (first generation) or `module/RAD/trainer/` (second generation, with simulations) to `module/<K>/trainer/`, replace `data/`, fix the output name and file lists in its `build.py`, replace every KAF/RAD-specific text in `shell.html`, then run `python module/<K>/trainer/build.py`. Add `trainer=dict(file="module/<K>/<K>-Trainer.html", was="...")` to the module's entry in `MODULES`.

The shared look of the trainers is in [`assets/trainer/`](assets/trainer/): `trainer-style.css` plus the three `trainer-*.js` add-ons. `python scripts/restyle.py <shell.html>` injects them into a shell; afterwards rebuild that trainer. Each module gets its own accent colour there (`PALETTEN` in `scripts/restyle.py`).

## Modes and sources

A module's mode stays *unresolved* until its old exams are analysed: question types across years, drift in the newest exam, points per type, share of the lecture the exams touch. With fewer than three years of exams there is no guess.

- **ALTKLAUSUR-DRIVEN**: the old exams and their corrections *are* the material, `quellen/` only closes gaps.
- **STOFF-DRIVEN**: built from the learning objectives plus whatever exams exist.
- **MIXED**: a recurring core plus new questions each year, with the split named.

Order of trust: official solutions → old exams and their corrections → lecture material → own notes. The full rulebook (analysis, file limits, drill mode) is [`CLAUDE.md`](CLAUDE.md).

## The scripts

| Script | What it does |
|---|---|
| `scripts/build.py` | merges all module study documents into `klausuren.html`: scopes each module's CSS to `#m-<K>`, namespaces IDs, rewrites links between modules and to trainers |
| `scripts/check.py` | text checks instead of screenshots: code blocks, dead anchors, dark-mode clashes; `--plan` checks the day plan against the built cockpit |
| `scripts/patch.py` | applies edits to a HTML file as data (a list of operations), all or nothing |
| `scripts/restyle.py` | gives a trainer shell the shared look from `assets/trainer/` |
| `scripts/theme.py` | adds the Auto / Light / Dark switch to a page without rewriting its CSS |
| `scripts/make_diagram.py` | draws the demo state diagram for KAF |
| `scripts/make_readme_assets.py` | draws the README images into `docs/images/`; `--shots` re-shoots the demo screenshots (needs Playwright) |

All of them run from the repo root and need only the standard library, except `--shots`.

## Module colours

Each module has one colour, set with `col` in `MODULES`. It shows up as the chip on the cockpit card, the dot in the sidebar and the filter chips of the day plan. For a trainer, use the same colour in its palette (`PALETTEN` in `scripts/restyle.py`, or the `:root` block in its `shell.html`). The demo uses violet (KAF), teal (RAD) and green (GAR).

## Repository layout

```
disciplan/
├── README.md, GUIDE.md, CLAUDE.md
├── klausuren_data.py      modules, dates, day plan, overview texts
├── klausuren.html         the cockpit (generated, do not edit)
├── scripts/               build, check, patch, restyle, theme, image tools
├── assets/trainer/        shared trainer look: CSS and JS
├── module/<K>/            <K>.html, <K>-Trainer.html, trainer/, README.md, fehler-log.md
├── prompts/               add-module.md
├── docs/                  MY-EXAM-PERIOD.md, readme-standard/, images/
└── examples/source/       the original README of my real exam period, as a finished example
```

A real module folder also has `altklausuren/`, `quellen/` and up to two more `.md` artefacts. They are not in this repo because they are course material.

## Known limits

- `scripts/build.py` still carries four `localStorage` migrations from my own first run (keys `kl-recut…`, `kl-split…`). They only matter if you reuse a browser profile that ran the old plan.
- Trainers are two generations of the same idea, not one engine.
- `restyle.py --alle` is untested on the second-generation shell and rewrites it: pass the shell you mean instead.
