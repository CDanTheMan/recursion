# Chiron — Product Contract

**Version:** v1 · **Status:** current · **Last-verified:** 2026-08-06

> One short, versioned definition of *the first usable Chiron experience*. This file is the
> task-definition layer: every Chiron feature task is scoped against THIS document so the build
> arm extends the product instead of reinventing it. (Root cause it fixes: two separate tasks
> both "add a landing page" — the arm had no contract telling it what already exists or what the
> product is for.) The `state/roadmaps/chiron.md` checklist is the ordered BUILD queue; this file
> is WHY. When they disagree, this file wins and the roadmap is corrected.

## 1. What Chiron is

Chiron is a fast, minimal, **static** learning site that helps people **get ahead of the
5-series** — the Claude 5 model family (Fable 5, Sonnet 5, and the wider 5-series). It is
content-first: a visitor arrives, understands what is new, and reads short practical lessons on
using the new models. (The name is the tutor-centaur; the product is a tutor for the 5-series.)

- **Audience:** developers and power users who want to understand and adopt the Claude 5 models.
- **Tagline (shipped, authoritative):** "Get ahead of the 5-series."
- **Shape:** a small Next.js static site (no backend). Home → Learn → About.

## 2. The first usable experience (the v1 bar)

A first-time visitor can, with no account and no setup:

1. Land on **Home** — a hero (name + one-line pitch) and a single primary CTA, "Start learning".
2. Follow the CTA to **/learn** — an index of **real lesson cards** (title + one-line summary),
   each opening a short lesson page with actual 5-series content.
3. Read **/about** — what Chiron is and who it is for.
4. Move between Home / Learn / About via a **shared header/nav** on every page.

**Usable = a first-time visitor understands what Chiron is and can read at least 3 real lessons
about the 5-series.** Until real lessons exist, /learn is a scaffold, not the product.

## 3. In scope for v1

- Home (hero + pitch + CTA)  ·  /learn index with real lesson cards  ·  per-lesson pages
- /about  ·  a shared header/nav component  ·  a clean static `next build`
- Responsive layout + baseline accessibility (semantic headings, focusable links, contrast)

## 4. Non-goals for v1 (do NOT build these; a task that adds one is out of contract)

- No auth, accounts, or user state  ·  no backend, database, or API routes
- No CMS / admin UI  ·  no interactive quizzes, playground, or live model calls
- No analytics / tracking  ·  no i18n  ·  no design-system dependency (inline styles are fine)
- Lesson content is static (TSX/MDX committed to the repo), not fetched at runtime.

## 5. Acceptance philosophy

`npm run build` proves it COMPILES, not that it WORKS. The Chiron lane graduates to autonomous
continuation only once acceptance is **browser-level** (the built page renders and the key
elements are present) — see the Chiron-hardening plan, Phase B. Until then, tasks are scoped by
this contract and reviewed before merge.

## 6. Open — confirm with Lucas (not to be invented by the loop)

- **Curriculum:** which specific 5-series topics the first lessons cover, and in what order.
- **Visual direction / branding** beyond the current minimal black-on-white.
- **Domain / deployment target.**

These are product decisions. The loop may build the STRUCTURE (routes, cards, nav) against this
contract, but must ESCALATE (not guess) the lesson CONTENT and branding.

## 7. Versioning

This contract is versioned. A change to scope, the v1 bar, or non-goals bumps the version and the
date, and notes what changed. v1 (2026-08-06): initial contract, documenting the shipped tagline
+ the roadmap-implied structure.
