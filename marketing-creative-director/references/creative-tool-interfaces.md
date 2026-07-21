# Creative Tool Interfaces

Use this reference for campaign landing pages and products that expose text-to-image or image-edit workflows.

## Interface principle

Organize the interface around creative decisions and recoverability, not around a giant prompt box. A user should always understand:

- What is being created or changed.
- Which references control identity, product, style, and composition.
- What is locked.
- What will vary.
- What the tool is doing now.
- How to compare, revise, and export without losing work.

## Text-to-image workspace

Use this durable structure:

1. **Brief rail**: purpose, audience, channel, ratio, campaign lane.
2. **Reference dock**: product, person, brand, composition, and mood inputs with visible priority.
3. **Prompt composer**: structured sections that can collapse into a raw prompt view.
4. **Constraint controls**: lock list, copy-safe area, negative constraints, fidelity level.
5. **Canvas**: large output area with generation state and direct selection.
6. **Variant strip**: labeled variants showing which axes changed.
7. **Inspector**: prompt record, seed/settings when available, dimensions, source lineage.
8. **History**: non-destructive generations, branches, favorites, and restore.
9. **Export**: channel crops, format, quality, naming, and rights note.

Do not hide essential state inside tooltips. Do not make every control a card. Use panels, rails, dividers, tabs, and spatial grouping according to task frequency.

## Image-edit workspace

Prioritize precision and before/after trust:

1. Canvas with zoom, pan, mask, and region selection.
2. Side-by-side, split, flicker, or overlay comparison.
3. Visible `Change`, `Lock`, `Match`, and `Reject` sections.
4. Layer or edit history with reversible steps.
5. Reference priority and identity/product fidelity controls.
6. Local regenerate and mask refinement.
7. Full-resolution artifact inspection.
8. Export with crop variants and metadata.

Never make a local edit trigger an unexplained full-image regeneration. Warn before an operation may alter locked identity or product details.

## Campaign planning workspace

Map the campaign system visibly:

- Brief and assumptions.
- Audience tension and message ladder.
- Concept lanes with comparison criteria.
- Asset matrix by funnel stage and channel.
- Shot list and prompt records.
- Review status, comments, and approval.
- Experiment hypotheses and results.

A useful visual relationship is `campaign -> lane -> asset -> variant -> export`. Preserve this lineage in navigation and filenames.

## Marketing landing-page craft

- Carry the ad promise into the first viewport.
- Use real imagery when the brief implies product, people, fashion, beauty, food, travel, or physical space.
- Make typography, imagery, color, and motion express one named campaign idea.
- Vary section rhythm; do not repeat icon-heading-text cards.
- Use purposeful first-load motion or none. Avoid uniform fade-on-scroll scaffolding.
- Design mobile and desktop compositions independently where the imagery requires it.
- Verify text contrast, responsive overflow, loading behavior, keyboard access, and reduced motion.

## Anti-template interface rules

Reject:

- Generic purple-blue AI gradients.
- Decorative grid backgrounds unrelated to a canvas or measurement surface.
- Glass panels everywhere.
- Huge rounded cards nested inside rounded cards.
- Identical feature-card grids.
- Gradient text, random glowing orbs, and meaningless 3D blobs.
- One tiny uppercase eyebrow above every section.
- A dark theme selected only because the product uses AI.

Choose a physical scene before choosing the theme: who uses the tool, where, under what light, during what kind of creative work. Let that scene determine density, contrast, color commitment, and motion.

## Critical states

Design and verify:

- Empty project and first generation.
- Missing or low-quality reference.
- Prompt conflict with lock list.
- Generation queue, progress, cancel, and retry.
- Partial failure or unavailable provider.
- Content or policy rejection with actionable recovery.
- No acceptable variants.
- Unsaved edits or branching conflict.
- Export mismatch, low resolution, or unsupported ratio.
- Mobile review and approval flow.

