# GPT Image 2 and Nano Banana Orchestration

## Contents

- Routing summary
- GPT Image 2
- Nano Banana family
- Four-to-five variant execution
- Provider-neutral request contract
- Current sources

## Routing summary

| Need | Preferred route |
|---|---|
| Direct text-to-image, one prompt, one or several same-prompt variants | GPT Image 2 Image API |
| Direct reference-image generation or image edit | GPT Image 2 Image API edits |
| Conversational generate/edit with iterative context | OpenAI Responses API image-generation tool |
| Several references and character/object consistency | Nano Banana 2 (`gemini-3.1-flash-image`) |
| Complex brand layout, localization, precise text, premium 2K/4K | Nano Banana Pro (`gemini-3-pro-image`) |
| Lowest latency/cost, few references, no sequential edit dependency | Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`) |
| Legacy Gemini image integration only | Nano Banana (`gemini-2.5-flash-image`); prefer migration for new work |

Run `scripts/plan_image_generation.py` rather than selecting from taste alone.

## GPT Image 2

### Direct Image API

Use `gpt-image-2` with:

- `images.generate` for new images.
- `images.edit` for editing or generating from one or more reference images.
- `n` for multiple images from the same generation prompt; official generation documentation allows multiple images in one request and the API reference currently documents `1-10`.
- `quality`: `low`, `medium`, `high`, or `auto`.
- `size`: standard sizes or supported `WIDTHxHEIGHT` values. Verify the live API constraints before executing arbitrary or 4K dimensions.
- `output_format` and compression where supported.

For `gpt-image-2`, do not send `input_fidelity`; official guidance states all image inputs are processed at high fidelity and the parameter cannot be changed.

Use direct Image API when the flow is stateless and the application already owns the prompt, references, variants, and output files.

### Responses API

Use the image-generation tool when the user wants a conversational editing session or a multi-step agentic flow.

- Provide input images as URL, Base64 data URL, or Files API IDs.
- Use `action: auto` to let the system choose generate/edit, `generate` to force a new image, or `edit` only when an image exists in context.
- Continue with `previous_response_id` or retained image-generation outputs/image IDs.
- Expect the mainline model to revise the prompt; preserve the revised prompt in lineage when available.
- Streaming can return partial images for responsive UI feedback.

Branch exploration variants from the same original response state. Do not mutate one variant into the next.

## Nano Banana family

Nano Banana is Google's name for Gemini native image generation.

### Nano Banana 2 Lite

- Model: `gemini-3.1-flash-lite-image`.
- Optimize for speed, scale, and low cost.
- Do not select for multiple-reference-heavy or sequential editing workflows.
- Use for drafts, thumbnails, and simple single-reference exploration.

### Nano Banana 2

- Model: `gemini-3.1-flash-image`.
- Default Google route for general image generation and editing.
- Prefer when multiple reference images and consistency matter.
- Official guidance documents support for up to 14 total reference images, with model-specific character/object fidelity limits; keep the set smaller and role-labeled unless the task truly needs more.
- Supports multi-turn editing with `previous_interaction_id`.
- Supports response controls including aspect ratio and image size.

### Nano Banana Pro

- Model: `gemini-3-pro-image`.
- Use for professional asset production, complex art direction, stronger world knowledge, localization, brand consistency, layout, and precise text.
- Supports 1K, 2K, and 4K output where documented.
- Select when quality and control outweigh latency or cost.

### Google interaction behavior

- Send text and image inputs together through the Gemini interaction.
- Use `response_format` for image-only or interleaved text/image output, MIME type, aspect ratio, and image size.
- Use `previous_interaction_id` only after choosing a direction for refinement.
- Google Batch API is for non-interactive large jobs and may take up to 24 hours; do not use it for an interactive request for four or five images.

## Four-to-five variant execution

### GPT Image 2

If there are no reference images and all variants share one prompt, use one Image API generation request with `n=4` or `n=5`, then label outputs after inspection.

If reference images, masks, or identity-sensitive edits are involved, verify the live edit endpoint's multi-output behavior. When uncertain, issue independent edit calls from the same originals so every variant has identical input state.

### Nano Banana

Issue four or five independent interactions using:

- The same reference set.
- The same lock list.
- The same ratio and resolution.
- One controlled prompt delta per interaction.

Do not use `previous_interaction_id` across exploration variants because this turns exploration into sequential drift. After selection, use it to refine the winning variant.

## Provider-neutral request contract

```json
{
  "reference_images": [
    {"id": "image-1", "role": "composition+lighting"},
    {"id": "image-2", "role": "styling+pose"}
  ],
  "reference_intent": "style-only",
  "operation": "generate",
  "variant_count": 4,
  "same_prompt_variants": false,
  "needs_character_consistency": false,
  "complex_layout_or_text": false,
  "multi_turn": true,
  "latency_priority": "balanced",
  "output": {"aspect_ratio": "4:5", "resolution": "2K"}
}
```

Store provider, model, API surface, request count, reference roles, canonical prompt, per-variant delta, output ID, revised prompt where available, selected result, and rejection reasons.

## Current sources

Checked 2026-07-22:

- OpenAI image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI create-image API reference: https://developers.openai.com/api/reference/resources/images/methods/generate
- Google Gemini native image generation: https://ai.google.dev/gemini-api/docs/image-generation
- Google Gemini model catalog: https://ai.google.dev/gemini-api/docs/models

Provider parameters, quotas, pricing, and preview/stable labels can change. Re-check official docs before executing production API calls.
