# study-cockpit

*Draft README (public copy). Items marked [CHECK] are open questions; this file must not be published while any remain.*

> Build tooling and a quiz engine that turned eight separate exam-prep documents into one offline study cockpit, used for an exam phase of 8 exams in 25 days (September 2026).

---

## The problem

- **One document per module, eight different designs.** Each module had its own HTML document with its own CSS, IDs and scripts. Opening eight files and keeping a daily plan in your head doesn't scale when the exams are about two days apart.
- **Self-testing kept breaking down.** Practice needed to happen in the exam's own formats (multiple choice, numeric answers, ordering, matching, cloze, computed tasks), and the explanation had to come right when an answer was wrong.
- **Content that can't be published.** The documents are built on course material. So the question for this repo is: how do you publish the *system* without the *content*?

## What it does

- **One cockpit file.** `build.py` combines every `module/<K>/<K>.html` into a single `klausuren.html`. It has a sidebar, a countdown, a module grid, a daily plan, a timeline, a strategy tab, Ctrl-K search, a dark/light toggle and print.
- **A daily plan of checkable steps.** Each day lists blocks; each block lists steps with a minute budget and a "↗" link that jumps to the exact anchor in the study document. The principle is *objectives instead of hours*: "three hours of studying" is not progress, "convolution works from cold" is. Ticks are saved in `localStorage`. When the plan was re-cut, versioned migrations reset only the affected days.
- **Trainer apps (one per module).** Each is a single HTML file built from `shell.html` plus data files.
  - **Question types:** `single`, `multi`, `num`, `text`, `order`, `match`, `gap`, `begriff` (flashcard) and `gen`.
  - **Parametric generators (`gen`):** fresh numbers every time, a worked solution, and a note on what changes and where the typical errors are.
  - **Sheet mode:** a whole chapter on one page, including an exam-sheet variant.
  - **Progress header:** shows how far you are, with a jump to open tasks.
- **A second-generation trainer** (the newest one). A dashboard start page sorts topics weakest first. A three-column review page shows the correction on the left, the question in the middle and the variants on the right. There are timed two-part exam simulations with a checklist and export, a searchable cheat-sheet panel, and an English toggle for explanations.
- **Theme tooling.** `theme.py` adds an Auto / Light / Dark switch to every page without rewriting any CSS. `restyle.py` gives all trainers one design with a per-module accent colour.
- **Quality tooling.** `check.py` runs text checks instead of screenshots. `patch.py` applies edits as data, all-or-nothing.

## How it's built

**Stack.** Plain Python 3 (standard library only) and vanilla HTML/CSS/JS. There are no frameworks and no build dependencies. Every output is a single self-contained HTML file that works offline from the file system.

**`build.py`: combining documents without touching them**
- **CSS scoping.** Each module's CSS is scoped to `#m-<K>` by a small CSS walker that recurses into `@media`, `@supports` and `@layer`, and leaves `@keyframes`, `@page` and `@font-face` alone.
- **Dark mode.** Each module's `@media (prefers-color-scheme: dark)` block is rewritten to `html[data-t=dark] #m-<K>`, so the cockpit's toggle wins over the OS setting.
- **ID namespacing.** All IDs and in-page anchors are prefixed per module, and ID selectors in the module CSS follow. JavaScript isn't rewritten textually, which breaks on dynamic IDs. Instead, `document.getElementById` is routed through a per-module helper that adds the prefix at runtime.
- **Link rewriting.** Links between modules become in-app routes, and links to trainer apps are rebased.
- **Adding a module:** create `module/<K>/<K>.html` and it's picked up on the next build.

**`theme.py`.** At runtime it collects the dark-mode media rules from the CSSOM and sets their condition to `all` (always dark) or `not all` (never dark). Auto restores the original. The CSS stays untouched, so `build.py` still sees what it expects. One `localStorage` key is shared by every page.

**Trainer engine**
- **Build.** `trainer/build.py` inlines `data/*.js` (or `*.json`) into `shell.html` at a `/*__DATA__*/` marker and prints what it included.
- **Data checks.** `check.js` validates every data file: unique IDs, a solution index inside the options, single vs. multi consistency, and missing explanations or "what changes" notes.
- **Browser test.** `e2e.js` drives the built app in Chromium with Playwright, runs named UI checks, and collects any page or console errors.

**`restyle.py`.** It replaces each trainer's `<style>` with the shared `trainer-style.css`, applies a per-module palette (light and dark values), moves the action bar from the window bottom into the question card, and injects the shared add-ons (`trainer-kopf.js`, `trainer-blatt.js`, `trainer-rail.js`). It's idempotent.

**`check.py`.** It checks, without a browser:
- dead anchors;
- code blocks that don't parse as Python (`ast.parse`);
- `<pre>` lines wider than the measured column (118 chars);
- class names that collide with the shell's unscoped CSS;
- dark-mode rules that set `background` without `color`;
- with `--plan`: dead plan anchors and minute sums that don't add up.

**`patch.py`.** Edits are a list of operations (`replace`, `before`, `after`, `between`, `css`, `cssdark`). Anchors match regardless of entity or literal spelling (`&#8212;` = `—`). The file is written only if **every** operation matches exactly once, with a `.bak-patch` backup.

## How I worked with AI

The documents, trainers and tools were built in Claude sessions (Cowork / Claude Code), steered by a project `CLAUDE.md` and module READMEs that recorded each change and its reason. [CHECK] Confirm how you want to describe the split between what you wrote and what the AI wrote.

**My decisions (recorded as mine in the files)**
- **Learning material, not reference works.** Every study document follows a fixed six-part structure (orientation → foundations from zero → procedures with *why* → graded exercises with hidden solutions → tactics → sources). This came from my criticism that the earlier versions assumed the material was already understood.
- **Judgement, not obedience.** The AI had to argue against my plan when it saw a better one, test my assumptions about each exam against the old exams, and flag anything that optimised for the *feeling* of preparation.
- **Didactic rules:**
  - don't mix topics while learning; connect them afterwards with arrows;
  - link text and exercises both ways;
  - name the concrete practice source, not a unit number;
  - no second explanation after first use (a counter-question instead, as exam simulation).
- **Filing:** nothing is deleted; old versions go to a dated archive with a manifest.

**What the AI did (per the READMEs and logs)**
- Analysed old exams per module (task types across years, point distribution) and proposed a study mode with a confidence level.
- Built and rebuilt the documents, the plan, the trainers and the tooling; checked documents line by line against model solutions (one pass found 14 factual errors).
- Turned its own recurring failures into tools. Entity mix-ups had caused about five full script rewrites, which led to `patch.py`. Slow screenshot checking and leaking CSS led to `check.py`.

**Working rules that kept the cost down:** collect changes, build once and check once; use screenshots only for truly visual questions; when something fails, fix only the failing operation.

## What I'd do next

These are open points from the project files, phrased as next steps. [CHECK] Confirm which you actually want to list.

- **Move `MODULES` / `DAYS` out of `build.py`** into a data file, so the engine is publishable as-is (the cleanup report says the same).
- **Clear the 16 existing `check.py` findings** (mostly dark-mode `.warn` rules).
- **Make `restyle.py --alle` safe** for the newer trainer shell. Right now it would also pick it up, and that's untested.
- **Unify the two trainer generations** into one engine with pluggable modes.

## Repo layout (proposed)

```
study-cockpit/
├── build.py            engine; reads data/plan.json + module/*/
├── theme.py  restyle.py  check.py  patch.py
├── trainer-style.css  trainer-kopf.js  trainer-blatt.js  trainer-rail.js
├── module/DEMO1/ DEMO2/     demo documents + demo trainer data
├── data/plan.json           demo plan
└── docs/screenshots/        taken from the demo build
```
