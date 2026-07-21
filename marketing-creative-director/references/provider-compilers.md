# Provider Compilers

Keep one provider-neutral master prompt. Compile only the execution layer. Provider features and parameters change; verify current official documentation before production.

## Shared source contract

Every provider receives:

- Job and intended asset.
- Reference priority and lock list.
- Subject and action.
- Scene and art direction.
- Composition, crop, and typography-safe region.
- Camera, light, material, and realism.
- Exact text when text rendering is required.
- Negative constraints and rejection criteria.

## OpenAI Images

Best fit: natural-language art direction, image edits, multiple reference roles, conversational iteration, and production prompts with explicit invariants.

- Use labeled sections and complete sentences.
- Repeat edit invariants in every edit pass.
- Quote exact text verbatim and inspect every character.
- Separate required locks from desired style.
- Iterate with one targeted change.

Output form: structured prompt without provider shorthand.

## Midjourney

Best fit: visual exploration, mood, composition variation, and concept lanes.

- Compress the master prompt into ordered visual phrases.
- Put subject, scene, composition, and material before mood adjectives.
- Keep negative constraints short and concrete.
- Append current aspect-ratio and style controls only after checking live syntax.
- Do not rely on Midjourney for exact packaging text or identity-critical edits without verified workflows.

Output form: compact single-line prompt plus a separate lock and caveat note.

## Flux

Best fit: controlled photorealism, local or hosted workflows, and pipelines that expose model-specific reference or guidance controls.

- Use literal subject and spatial descriptions.
- Describe camera and light physically.
- Avoid overlong poetic clauses.
- Keep text requirements exact and isolated.
- Record model/version because Flux variants differ materially.

Output form: concise positive prompt, negative prompt if supported, and implementation notes.

## Ideogram

Best fit: campaign posters, graphic compositions, and assets where rendered headline text matters.

- Put exact text in quotes and state spelling, hierarchy, placement, and casing.
- Reduce competing scene detail when typography is primary.
- Specify whether the asset is poster-led, product-led, or editorial.
- Verify text output manually; never assume perfect legal or packaging copy.

Output form: text-first prompt plus layout and spelling checklist.

## Adobe Firefly

Best fit: commercial design workflows, reference-guided exploration, generative fill, and integration with Adobe editing tools.

- Separate composition reference from style reference.
- Use generative fill for local changes rather than regenerating the entire image.
- Preserve product and identity locks through masks and layer-based edits.
- Carry typography into Illustrator, Photoshop, or InDesign when fidelity matters.

Output form: generation prompt, reference roles, edit mask notes, and finishing instructions.

## Generic fallback

When provider capabilities are unknown:

- Return the full provider-neutral master prompt.
- State required features: image references, editing, masks, exact text, aspect ratio, seed, or identity fidelity.
- Mark unsupported assumptions instead of fabricating parameters.

## Compiler output

Return:

1. Provider and verified capability date.
2. Compiled prompt.
3. Negative constraints.
4. Required inputs and locks.
5. Provider-specific caveats.
6. Manual finishing steps.

Use `scripts/compile_prompt.py` for deterministic adaptation of a JSON brief.

