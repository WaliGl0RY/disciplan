<a name="top"></a>
<p align="center">
  <a href="#top"><img src="docs/images/banner.svg" alt="disciplan. Every day knows what to study." width="100%"></a>
</p>

<p align="center">
  <b>A study system for an exam period</b>: a daily plan, one study document per module, self-test trainers, and one build script that merges it all into a single offline page.<br>
  <sub>Plain Python 3 and vanilla HTML/CSS/JS. Runs from disk.</sub>
</p>

<p align="center">
  <a href="#use"><img src="docs/images/badge-stdlib.svg" alt="Python, stdlib only"></a>
  <a href="GUIDE.md#1--first-build"><img src="docs/images/badge-server.svg" alt="server: none"></a>
  <a href="#demo"><img src="docs/images/badge-demo.svg" alt="3 demo modules"></a>
</p>

<p align="center">
  <a href="#demo"><img src="docs/images/nav-demo.svg" alt="Try the demo"></a>
  <a href="#how"><img src="docs/images/nav-how.svg" alt="How it works"></a>
  <a href="#get"><img src="docs/images/nav-get.svg" alt="What you get"></a>
  <a href="#use"><img src="docs/images/nav-use.svg" alt="Use it yourself"></a>
  <a href="docs/MY-EXAM-PERIOD.md"><img src="docs/images/nav-mine.svg" alt="My exam period"></a>
</p>

<a name="demo"></a>
<p><a href="#demo"><img src="docs/images/strip-demo.svg" alt="Try the demo" width="100%"></a></p>

This repo ships three **fictional** demo modules with the same structure as real ones: a study document, a trainer, a day plan. Build them and open the result (`python scripts/build.py`, then open `klausuren.html`). The real course material I used for my own exams is not in this repo.

<table>
  <tr>
    <td width="33%" align="center" valign="top">
      <a href="module/KAF/KAF.html"><img src="docs/images/card-kaf.svg" alt="KAF, coffee machine technology: study page with a state machine, trainer of the first generation" width="100%"></a><br>
      <a href="module/KAF/KAF.html"><img src="docs/images/btn-study-kaf.svg" alt="KAF study page"></a>
      <a href="module/KAF/KAF-Trainer.html"><img src="docs/images/btn-trainer-kaf.svg" alt="KAF trainer"></a>
    </td>
    <td width="33%" align="center" valign="top">
      <a href="module/RAD/RAD.html"><img src="docs/images/card-rad.svg" alt="RAD, bike workshop: study page with a practical part, trainer of the second generation" width="100%"></a><br>
      <a href="module/RAD/RAD.html"><img src="docs/images/btn-study-rad.svg" alt="RAD study page"></a>
      <a href="module/RAD/RAD-Trainer.html"><img src="docs/images/btn-trainer-rad.svg" alt="RAD trainer"></a>
    </td>
    <td width="33%" align="center" valign="top">
      <a href="module/GAR/GAR.html"><img src="docs/images/card-gar.svg" alt="GAR, garden planning: study page only" width="100%"></a><br>
      <a href="module/GAR/GAR.html"><img src="docs/images/btn-study-gar.svg" alt="GAR study page"></a>
      <a href="GUIDE.md#3--replace-the-demo-with-your-modules"><img src="docs/images/btn-notrainer-gar.svg" alt="GAR has no trainer"></a>
    </td>
  </tr>
</table>

Each module keeps its colour everywhere: here, in the cockpit and in its trainer.

---

<a name="how"></a>
<p><a href="#how"><img src="docs/images/strip-how.svg" alt="How it works" width="100%"></a></p>

<p align="center"><a href="GUIDE.md"><img src="docs/images/how-it-works.svg" alt="Material, Analyse, Build, Plan, Cockpit: five steps from lecture material to one offline page" width="100%"></a></p>

**Material** goes into `module/<K>/` (old exams, slides). **Analyse** decides what the exam rewards and picks a mode per module (rules in [CLAUDE.md](CLAUDE.md)). **Build** writes the study document, the trainer and a `fehler-log.md` for mistakes. **Plan** is typed blocks with steps in `klausuren_data.py`. **Cockpit** is `python scripts/build.py`: one `klausuren.html` for everything.

---

<a name="get"></a>
<p><a href="#get"><img src="docs/images/strip-get.svg" alt="What you get" width="100%"></a></p>

All screens are from the demo modules, in dark mode.

<table>
  <tr>
    <td width="50%" align="center" valign="top"><a href="GUIDE.md#2--set-your-dates"><img src="docs/images/demo/plan-day.png" alt="The day plan: a week, one day with its blocks and the end-of-day line"></a><br><b>Day plan</b><br><sub>a week, typed blocks, one line for "enough"</sub></td>
    <td width="50%" align="center" valign="top"><a href="klausuren_data.py"><img src="docs/images/demo/plan-steps.png" alt="One block opened: its steps, each with a jump into the study document"></a><br><b>Block with steps</b><br><sub>checkable steps, each jumps into the study page</sub></td>
  </tr>
  <tr>
    <td width="50%" align="center" valign="top"><a href="module/KAF/KAF-Trainer.html"><img src="docs/images/demo/trainer-round.png" alt="Trainer round: every option judged with a reason"></a><br><b>Trainer round</b><br><sub>every option gets a reason, not only the right one</sub></td>
    <td width="50%" align="center" valign="top"><a href="module/KAF/KAF.html"><img src="docs/images/demo/study-page.png" alt="Study page: orientation, the one big idea, the exam profile"></a><br><b>Study page</b><br><sub>six parts, from orientation to sources</sub></td>
  </tr>
</table>

Also: a countdown, a search across all modules (Ctrl K), a light/dark switch and print. Progress is saved in the browser.

---

<a name="use"></a>
<p><a href="#use"><img src="docs/images/strip-use.svg" alt="Use it yourself" width="100%"></a></p>

1. **Build it.**
   ```bash
   python scripts/build.py
   ```
2. **Set your dates** in `PLAN` and `MODULES` in `klausuren_data.py`. `scripts/build.py` has none of its own.
3. **Add your modules** with the preset prompt [prompts/add-module.md](prompts/add-module.md). It analyses first and waits for your ok before it creates anything.

The full walkthrough, including what each date setting does, is in [GUIDE.md](GUIDE.md).

**Where things are**

```
disciplan/
├── klausuren_data.py   your settings: dates, modules, day plan. Open it first when you start
├── klausuren.html      the built page. Open it in a browser; scripts/build.py rewrites it
├── GUIDE.md            step by step, including the date settings. Open it when something is unclear
├── CLAUDE.md           the rules Claude follows here. Open it before you change how modules are analysed
├── module/             one folder per module: study page, trainer, your notes. Open it to read or edit a module
├── scripts/            build.py, check.py and the HTML tools. You run them, you rarely edit them
├── assets/trainer/     the CSS and JS all trainers share. Open it to restyle every trainer at once
├── prompts/            add-module.md, the prompt you paste into Claude Code to add a module
├── docs/               my exam period, the README standard and the README images
└── examples/source/    the original screenshots of my real setup; only docs/MY-EXAM-PERIOD.md uses them
```

<table>
  <tr>
    <td>
      <a href="docs/MY-EXAM-PERIOD.md"><img src="docs/images/card-mine.svg" alt="Built for my own exam period: 8 exams in 25 days" width="100%"></a><br>
      <a href="docs/MY-EXAM-PERIOD.md"><img src="docs/images/btn-story.svg" alt="Read the story"></a>
    </td>
  </tr>
</table>

---

<a name="ai"></a>
<p><a href="#ai"><img src="docs/images/strip-ai.svg" alt="How I built it and what the AI did" width="100%"></a></p>

I decided what the system should do, how each module is analysed and what goes into the study documents, and I tested all of it myself while studying for the exams. Claude (Anthropic) was my coding assistant: it helped write the code and the documents under my direction, following the rules in [CLAUDE.md](CLAUDE.md).
