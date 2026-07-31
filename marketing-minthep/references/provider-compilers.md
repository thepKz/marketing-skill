# Provider Compilers

Keep one provider-neutral master prompt. Compile only the execution layer. Provider features and parameters change; verify current official documentation before production.

Model IDs here were verified on 2026-07-29 — see `api-image-orchestration.md` for the source URLs
and the re-verification rule.

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

## GPT Image 2

Best fit: direct generation/editing, same-prompt variants, natural-language art direction, multiple reference roles, and conversational iteration.

- Use labeled sections and complete sentences.
- Repeat edit invariants in every edit pass.
- Quote exact text verbatim and inspect every character.
- Separate required locks from desired style.
- Iterate with one targeted change.
- Use Image API `images.generate` or `images.edit` for direct stateless work.
- Use the Responses API image-generation tool for conversational generate/edit flows.
- Omit `input_fidelity` for `gpt-image-2`; image inputs are always processed at high fidelity.
- For four or five text-only same-prompt variants, use `n=4` or `n=5`. For reference-sensitive variants, branch independent calls from the same original inputs unless live edit documentation confirms the desired multi-output behavior.

Output form: structured prompt without provider shorthand.

## Nano Banana 2 Lite

Best fit: low-cost, low-latency drafts with zero or one reference and no sequential consistency requirement.

- Model: `gemini-3.1-flash-lite-image`.
- Keep the prompt direct and the reference set small.
- Do not choose it for multiple-character consistency or complex multi-turn editing.

Output form: canonical prompt, role-labeled inputs, aspect ratio, and draft-resolution request.

## Nano Banana 2

Best fit: several reference images, character or object consistency, general image generation/editing, and high-volume production.

- Model: `gemini-3.1-flash-image`.
- Send images with explicit roles rather than an unlabeled pile.
- Keep exploration variants as independent interactions from the same canonical reference set.
- Use `previous_interaction_id` only to refine the selected output.
- Set `response_format` for image MIME type, aspect ratio, and image size.

Output form: canonical prompt, ordered image inputs, response format, and one named delta per interaction.

## Nano Banana Pro

Best fit: premium art direction, brand consistency, localization, complex layouts, accurate text, and 2K/4K production.

- Model: `gemini-3-pro-image`.
- Prefer it when precision matters more than speed or cost.
- Keep exact text isolated and verify every character.
- Use the same branch-and-refine discipline as Nano Banana 2.

Output form: production prompt, ordered reference roles, response format, text locks, and finishing checklist.

## Midjourney

Best fit: visual exploration, mood, composition variation, and concept lanes.

- Compress the master prompt into ordered visual phrases.
- Put subject, scene, composition, and material before mood adjectives.
- There is no negative-prompt field. Exclusions go through parameter syntax that has changed between versions, so return them as a reject checklist for the person reviewing the render rather than as prompt text.
- Append current aspect-ratio and style controls only after checking live syntax. `--cref` and `--cw` are V6-only, `--oref` and `--ow` V7-only, and neither works on the current default version - see `prompt-grammar.md`.
- Rendered text needs double quotation marks; single quotes and apostrophes do not trigger text at all, and the documented range is the standard Latin alphabet, which leaves Vietnamese diacritics untested.
- Do not rely on Midjourney for exact packaging text or identity-critical edits without verified workflows.

Output form: compact single-line prompt plus a separate lock and caveat note.

## Flux

Best fit: controlled photorealism, local or hosted workflows, and pipelines that expose model-specific reference or guidance controls.

- Use literal subject and spatial descriptions.
- Describe camera and light physically.
- Avoid overlong poetic clauses.
- Keep text requirements exact and isolated.
- Record model/version because Flux variants differ materially.
- FLUX.2 documents no negative-prompt support. Express an exclusion as what should occupy that part of the frame instead, and keep the rejection criteria out of the prompt.

Output form: concise positive prompt, a reject checklist that is explicitly not part of the prompt, and implementation notes.

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
3. Negative constraints, as a negative prompt only where the provider documents that field, and otherwise as a reject checklist labelled as not part of the prompt. Five of the nine families here have no such field, and sending exclusions to them as prompt text puts the thing you are excluding into the prompt.
4. Required inputs and locks.
5. Provider-specific caveats.
6. Manual finishing steps.

Use `scripts/compile_prompt.py` for deterministic adaptation of a JSON brief, then `scripts/check_prompt_grammar.py --prompt-file … --provider …` on what it emits. `prompt-grammar.md` and `data/prompt-grammar.csv` carry the URL behind every capability claim on this page, plus the eleven questions no provider answers.
