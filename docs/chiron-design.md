# Chiron — the learning engine (design of record)

Status: historical initial design. Chiron is now canonical in its own repository; the 2026-08-31
source gate passes, while the v6 study pilot remains not ready pending H2, B0, and the B10
prerequisite chain. See `docs/audits/recursion-v2-mvp-chiron-pilot-2026-08-31.md`.
Read `ANCHOR.md` first. Named for the centaur who tutored the Greek heroes.

## Purpose
Interactive learning engine that puts Lucas *ahead* of his peers in Berkeley's **5-series**
("Physics for Physicists" — the honors majors track: Kleppner/Purcell rigor, proof-heavy, brutal
problem sets). Goal (ANCHOR): arrive at lecture already stuck on the material — lecture as
*resolution*, not first contact.

## The load-bearing design decision: TWO frontends
Telegram and a learning surface are opposite jobs — do not force both through Telegram.
- **Telegram = the Recursion *supervisor's* control surface** (status, approvals, executive
  decisions, "how's my learning going"). Low-bandwidth, async. Correct for supervision.
- **Chiron = a dedicated *learning* web app.** Canvas-first: rendered math, figures/plots,
  embedded or linked interactive models, AI explanation woven in, a tutor dialogue *inside* the
  canvas. A chat window can't *instill* — teaching physics needs a canvas.

**Two frontends, one brain:** Chiron's mastery map is part of the ledger, so the supervisor READS
it and nudges via Telegram ("Lagrangian: introduced, not applied; lecture in 12 days") while the
actual learning happens in Chiron's app.

## MVP scope (decided): curate + link + explain + track
**Do NOT hand-build simulations** (hard, inaccurate, and blows the Berkeley timeline). Reuse the
world's best existing interactive models — **PhET, Desmos, GeoGebra, Falstad, 3Blue1Brown/manim** —
and layer Chiron's value on top: **sequencing, sourcing, connecting, assessing, explaining**, with
the mastery memory underneath. Custom-build only the few visualizations that genuinely don't exist.
Emphasis: **AI explanation, testing, and curriculum.**

## Its own memory — the mastery map (what makes it a tutor, not a chatbot)
Per concept, track the five stages explicitly + always know where Lucas stands:
**introduce → instill → explore → apply → explain.** Plus: what he's solved, what he tested well on,
which re-explanations he got right. The "explain" stage (re-derive/teach it back — the Feynman
effect) is the real mastery gate.

## Curriculum principle: proven pedagogy + desirable difficulty (grounded, not vibes)
- **Proven:** retrieval practice (testing *as* learning), spaced repetition, interleaving,
  worked→faded→independent examples, self-explanation.
- **Difficult/frontier:** Bjork's *desirable difficulties* — productive struggle at the edge, the
  hardest problems, deep cross-connections (the part that builds a differentiated brain).
- The 5-stage ladder already encodes this; build the spine on it. "Actively simulate my
  understanding" = the **apply + explore** stages (predict, manipulate a model, get feedback).

## Content grounding + the high-stakes guardrail
- Ground problems in **real known-solution sets**; generate *sequencing*, not problems, unless asked.
- **Don't hand solutions before a genuine attempt** exists in the log; hints escalate in stages.
- **Never false-positive mastery.** Re-explanation graded against canonical, with **confidence
  flags**; run dimensional-analysis + limiting-case checks on any derivation. ANCHOR: *confident
  wrong physics is the worst possible output.*

## Courses + texts (5-series, honors)
Entire lower-division: **Mechanics, E&M, eventually Thermodynamics.** Canonical honors texts as the
known-solution source:
- **Mechanics (5A):** Kleppner & Kolenkow + **Morin** (Morin's problems = the difficulty engine).
- **E&M (5B):** Purcell & Morin.
- **Thermo (5C):** Blundell & Blundell (or Kittel).
- ⚠ Confirm against the actual assigned syllabus before finalizing the spine.

## Time budget (the real constraint)
~**7–8 focused hrs/day TOTAL**, shared across learning *and* all project dev — this is ANCHOR's
"review throughput" as a number. Rough split: ~3 hrs deep physics (Chiron, foreground), ~3–4 hrs
project *decisions + review* (the loop executes; Lucas adjudicates), buffer. Autonomous project work
runs in the background (costs review time, not hands) — that's what lets learning + many projects fit
one day.

## Timeline
Berkeley starts **2026-08-26**. Learning starts THIS WEEK — the curriculum spine + tutor loop
(explain→test→re-explain→track) need no app; start concept 1 immediately, app MVP built in parallel
over ~2 weeks. Don't gate learning on the build.

## Open decisions (for the build session)
1. **Hosting** — Next.js web app on Railway / Vercel / Cloudflare Pages? (reuse the GS stack muscle?)
2. **Entry point** — start at foundations (build the rigor floor) vs enter at the current edge
   (gap-map flags "Lagrangian mechanics — not started")?
3. **Mastery store** — structured files in `recursion/state/chiron/` vs a DB? (start simple.)

## First session moves
1. Confirm texts/syllabus + entry point.
2. Draft the 5A Mechanics spine into `recursion/curriculum/` (5-stage ladder over the concept order).
3. Seed the mastery map. Start concept 1 — learning begins before the app exists.
