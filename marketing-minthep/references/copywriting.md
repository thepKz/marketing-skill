# Copywriting System

## Message hierarchy

Build copy in this order:

1. Audience tension or desired progress.
2. Specific promise.
3. Credible mechanism.
4. Proof.
5. Objection resolution.
6. Action and expectation.

Write the clearest true version before creating stylistic variants.

## Titles

The title is not step seven of this list, and writing it last is what produces a title about the work
instead of about the reader. `title-writing.md` owns it, with `data/title-devices.csv` and
`scripts/check_title.py`. Run the check across the whole set of headings rather than one line at a
time: the thing a reader registers as machine-written is repetition across a page, and that is
invisible when you reread each title on its own.

## Copy contract

Capture:

- Audience and awareness level.
- Page or asset job.
- Single message and primary proof.
- Voice traits with concrete examples.
- Terms that must be used or avoided.
- Confirmed claims and prohibited claims.
- CTA and what happens after the action.
- Character, layout, or legal constraints.

## Channel adaptation

### Landing page

- Make the first viewport agree with the traffic source.
- Pair promise with proof or mechanism early.
- Use sections to answer a decision sequence, not to fill a template.
- Keep one dominant action unless the user journey requires a real alternative.

### Social

- Lead with a relevant tension, observation, proof, or unusual specificity.
- Let the body earn the CTA.
- Match native pacing and format while preserving brand voice.

### Email

- Give each email one job.
- Make subject line and opening fulfill the same promise.
- Use plain expectation-setting for transactional or lifecycle content.
- Do not use fake `Re:` prefixes, deceptive urgency, or hidden conditions.

### Paid ads

- Keep the product, benefit, proof, and CTA understandable under fast attention.
- Create variants around one named hypothesis.
- Preserve claim consistency between ad and destination.

### SEO content

Route out to `seo-writing.md`. Three bullets sat here promising a capability the skill advertised in
its own description, which is the worst place to be thin. The unit is ten query intents in
`data/seo-intents.csv` plus `scripts/audit_seo_page.py`, which measures a draft against the intent
you name.

The first of those bullets is now a number. *Satisfy the real query before expanding into brand
narrative* changed no drafts as a sentence; the audit fails a page whose text has not carried every
head term of the query together inside the first hundred and twenty words.

## Editing pass

Run five passes:

1. **Truth**: every claim is supported.
2. **Clarity**: subject, action, and benefit are explicit.
3. **Specificity**: replace category language with mechanism, context, or proof.
4. **Voice**: wording sounds like the brand, not a copy template.
5. **Compression**: remove repetition, throat-clearing, and empty intensifiers.

Delete `revolutionary`, `seamless`, `unlock`, `elevate`, `game-changing`, and `in today's
fast-paced world` outright. No evidence can require them: they are adjectives with no test
attached, which is why every competitor can use the same line. Replace each with the thing that
earned it — `seamless` becomes the number of steps removed, `elevate` becomes the outcome that
changed, `revolutionary` becomes what was impossible before. If nothing can be named, the claim
was empty and the sentence should go, not be softened.

The exception is a phrase the brand already owns in market, where dropping it costs recognition.
That is a brand-guideline decision with a paper trail, not a judgement to make while drafting.
