# Creative Evaluation

Score only after critical gates pass. A beautiful asset with product drift, false claims, identity errors, or rights risk is a rejection, not a low score.

## Critical gates

Reject immediately when any is true:

- Product, logo, label, closure, color, identity, or required text materially drifts.
- Human anatomy, hands, face, age presentation, or body becomes implausible.
- Light, perspective, scale, contact shadow, reflection, or material physics fails visibly.
- The asset invents a claim, statistic, testimonial, certification, ingredient, price, or legal proof.
- Consent, source rights, celebrity, trademark, or close-imitation risk is unresolved.
- Essential copy or product is outside a required crop or platform-safe region.

## 100-point rubric

| Dimension | Points | What earns the score |
|---|---:|---|
| Strategy | 20 | Clear behavior change, message ladder, proof, and objective fit |
| Fidelity | 20 | Product, identity, text, material, and reference locks hold |
| Distinction | 20 | Ownable idea, category-reflex rejection, memorable visual grammar |
| Craft | 20 | Composition, hierarchy, camera, light, anatomy, physics, typography |
| Channel | 10 | Native format, first-frame behavior, safe zones, crop, CTA continuity |
| Rights and claims | 10 | Supported claims, consent, source lineage, no close imitation |

## Score interpretation

- `90-100`: production candidate after final export inspection.
- `80-89`: strong; fix named weaknesses before release.
- `70-79`: promising concept with execution or proof gaps.
- `50-69`: revise the idea or rebuild the asset.
- `<50`: reject.

No score overrides a critical gate.

## Selection procedure

1. Review outputs anonymously when possible.
2. Reject critical failures.
3. Score against the same brief and channel.
4. Record concrete evidence for every deduction.
5. Select one primary and one learning variant.
6. Preserve rejection labels for future prompt improvements.

## Rejection labels

- `STRATEGY`: no meaningful campaign idea.
- `FIDELITY`: product or identity drift.
- `ANATOMY`: human detail failure.
- `PHYSICS`: light, material, scale, or perspective failure.
- `HIERARCHY`: unclear message or thumbnail failure.
- `CROP`: unsafe composition.
- `CLAIM`: unsupported or invented proof.
- `GENERIC`: category reflex or AI-template aesthetic.
- `OFF-BRAND`: conflicts with Brand DNA.
- `RIGHTS`: consent, source, trademark, or imitation risk.

Use `scripts/score_creative.py` with `assets/templates/creative-evaluation.json` for a repeatable record.

