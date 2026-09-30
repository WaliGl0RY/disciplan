# Preset prompt: add a new module

**Before you paste:** put the module's old exams in `module/<K>/altklausuren/` and the
lecture material in `module/<K>/quellen/`. Then open Claude Code in the repo root, fill
in the `<…>` fields on the **green lines** (marked `+`) and paste everything inside the code block.
Everything else stays as it is.

```diff
 Add a new module to the study system.
+ Module: <KÜRZEL> — <full module name>
+ Exam:   <YYYY-MM-DD>, <HH:MM>
+ The material is in module/<KÜRZEL>/altklausuren/ and module/<KÜRZEL>/quellen/.

 1. Read CLAUDE.md completely. As the reference, read the <head> and sidebar of the demo
    module/KAF/KAF.html and the KAF entry in MODULES in klausuren_data.py.
 2. Analyse as CLAUDE.md → MODULE ANALYSIS (a–e) says, from the files, not impressions:
    question types across years, drift in the newest exam, share of the lecture the exams
    touch, points per question type. Fewer than three years: the mode stays UNRESOLVED.
 3. Propose, then STOP: the mode with confidence and the evidence that would flip it; the
    artefacts (max. three .md incl. fehler-log.md: name, content, why this module, how it
    is drilled); whether a trainer is worth it; and ask me for examiner, attempt and
    Pflicht/Wahlpflicht. Create no files before my ok.
 4. After my ok, build:
    - module/<K>/README.md (the six sections from CLAUDE.md), fehler-log.md, the artefacts
    - module/<K>/<K>.html in the six parts (LERNDOKUMENT — Aufbau), reusing the <head>,
      CSS and sidebar of KAF.html so scripts/build.py picks it up unchanged
    - a MODULES entry in klausuren_data.py (k, name, d, t, v, typ, prof, mode, desc;
      trainer=dict(...) only with a trainer), in exam-date order; DAYS only if I ask
    - trainer, only if confirmed: copy module/KAF/trainer/, replace data/, set OUT and the
      file lists in its build.py, replace every KAF-specific text in shell.html (title,
      header, KEY), run scripts/restyle.py on shell.html, then the trainer's build.py
 5. Run python scripts/build.py and python scripts/check.py <K>. Fix the findings for the new module and
    report the files created, the build output, and what is still open.
 Rules: German Fachsprache in module files. At most three .md per module plus README.md.
 No dates in file names. Don't touch other modules.
```
