# disciplan

A study system for an exam period: a daily plan, one study document per module, self-test trainers, and one build script that merges it all into a single offline page. Plain Python 3 (standard library only) and vanilla HTML/CSS/JS.

This repo holds the engine and three made-up demo modules (`KAF` coffee machine, `RAD` bike workshop, `GAR` garden planning). No real course material.

## Build

```bash
python build.py                      # → klausuren.html
python module/KAF/trainer/build.py   # rebuild one trainer
python check.py                      # lint; check.py <K> --plan also checks the day plan
```

## Layout

```
disciplan/
├── build.py                 merges module/<K>/<K>.html into klausuren.html
├── klausuren_data.py        MODULES, DAYS (day plan), TEXT — demo data here
├── check.py  patch.py  restyle.py  theme.py
├── trainer-style.css  trainer-kopf.js  trainer-blatt.js  trainer-rail.js
├── module/KAF  RAD  GAR     demo study documents and trainers
├── prompts/add-module.md    preset prompt for adding a module
├── CLAUDE.md                rules for Claude sessions (analysis modes, document structure, drill mode)
├── docs/readme-standard/    README standard and templates
├── docs/study-cockpit-notes.md   notes and open points from the showcase draft
└── examples/source/         the original study-system README and its images, as a finished example
```

## Add a module

See [prompts/add-module.md](prompts/add-module.md).

## Known open points

- `build.py` still has the dates of the first run hard-coded (plan view starts 2026-08-28, countdown to 2026-09-01, two localStorage migrations). These should move into `klausuren_data.py`.
