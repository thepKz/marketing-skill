# Prompt Grammar

What each image model family actually documents about the prompt you send it, with the URL beside
every claim and an explicit record where the answer does not exist. Sixty-nine rows in
`data/prompt-grammar.csv`, eleven of them recording that no primary source was found. Thirty-two are
read by `scripts/check_prompt_grammar.py`, which turns them into gates.

## The one thing to take from this document

The prompt-listicle genre treats every provider as the same machine with different adjectives. The
documentation does not. Four rules cover almost everything:

- **Position matters only where an encoder truncates.** Front-loading is real on a CLIP-only
  pipeline, where token 78 is not weighted less but absent. On a model carrying a T5 encoder it is
  mostly superstition.
- **A negative prompt is an architectural feature, not a phrasing style.** It exists where
  classifier-free guidance is exposed. Where guidance was distilled away, no wording brings it back.
- **Character consistency is documented as reference-image conditioning, never as prompt wording**,
  and every provider that documents it also says it is not guaranteed.
- **In-image text is a documented limitation on one provider, a required syntax on another, a
  numeric budget on exactly one, and a separately indemnified surface on a fourth.**

```
python scripts/check_prompt_grammar.py --list-families
python scripts/check_prompt_grammar.py --prompt-file runs/x/prompt.txt --provider flux
python scripts/check_prompt_grammar.py --provider midjourney --recurring-person --needs-reproducible
```

Exit codes: 0 consistent with the documentation, 2 a request the provider will accept and quietly
not honour, 3 depends on something the provider does not publish. That third code is most of the
table, and it is the honest answer rather than a soft pass.

## Contents

- Token windows and character limits are different failures
- Negative prompts, by provider
- In-image text
- Character consistency, and the only numbers anybody publishes
- Seeds, and what reproducibility costs
- Ownership and likeness
- Nine things the internet gets wrong
- What has no source
- Reject list

## Token windows and character limits are different failures

Overrun an encoder window and the tail of the prompt disappears with no error. Overrun an API
character limit and the request is rejected. One is silent and one is loud, so the script gates them
separately.

| Family | Window | Kind |
|---|---|---|
| Stable Diffusion 1.x / XL | 77 tokens | Silent truncation, CLIP |
| Stable Diffusion 3 / 3.5 | 256 tokens on the T5 branch, 77 still applying to CLIP | Silent truncation |
| GPT image models | 32,000 characters | Request rejected |
| dall-e-3 / dall-e-2 | 4,000 / 1,000 characters | Request rejected, both models removed from the API |
| Midjourney, FLUX, Imagen, Gemini, Firefly, Ideogram | Nothing published | Unknown |

Two notes on that table. The 32,000-character figure lives on the API reference and not on the
prompting guide, and the first pass at this table recorded "no limit published" because it read only
the guide - which is why every row carries the URL that answered it rather than the provider's name.
And 32,000 characters is not a budget to fill; it is a validation ceiling roughly a hundred times
past any prompt worth writing.

The one published encoder finding worth quoting: dropping the T5-XXL encoder from SD3 costs a 38
percent win rate on written text specifically, and much less on general prompt following. That is the
only number connecting an encoder to a capability anywhere in this survey, and it is why typography
quality is an architecture question before it is a wording question.

Two providers rewrite the prompt before it runs. Through the Responses API image tool, the mainline
model revises the prompt automatically; on Imagen, `ENABLE_PROMPT_REWRITING` defaults to true. Both
matter for one-variable iteration: with rewriting on, a prompt A/B compares two rewrites rather than
two prompts. Turn it off, or call the images endpoint directly, before concluding a wording change
did anything.

## Negative prompts, by provider

| Family | Field | Detail |
|---|---|---|
| Stable Diffusion, Ideogram, open-weight pipelines | Yes | Ideogram states the positive prompt is always favoured over it |
| Imagen on Vertex | Legacy | Supported on `imagen-3.0-generate-001`, `-fast-generate-001` and `-capability-001`, and documented as not included from `imagen-3.0-generate-002` onward |
| Adobe Firefly | Endpoint-dependent | Live on v3 generate-async and fill-async, unsupported with Custom Models on Image Model 3 and 4, absent from the v4 and Image Model 5 schema |
| Gemini image, GPT image, FLUX.2 | No | FLUX.2 documents the absence explicitly; Gemini recommends semantic negative prompts instead |
| Midjourney | No field | Exclusions go through parameter syntax that has changed between versions |

Where the field does not exist, an exclusion list is not a quieter channel - it is prompt content.
`scripts/compile_prompt.py` used to emit a `NEGATIVE PROMPT` heading to FLUX, which meant a brief
asking for no plastic skin was sending the words *plastic skin* into the prompt. The compiler now
splits the master prompt's `DO NOT` section off for those families and returns it as a reject
checklist for the person looking at the render, with the heading saying so. `check_prompt_grammar.py`
is what found that defect, and it fails the same shape again if it comes back.

Where the field does exist: write nouns and attributes, not negated sentences. `people`, not
`no people`. The field is already negative and negating inside it is a double negative. And never
contradict the positive prompt, because the positive one wins and the contradiction costs
effectiveness.

## In-image text

Google publishes the only number: about 25 characters, up to three short phrases. Everything longer
is a layout job. That budget is documented for Imagen and nowhere transferred to Gemini, so it is not
a Google-wide rule.

OpenAI documents text as a *limitation*, in its own words: the model can still struggle with precise
text placement and clarity. Two more limitations sit beside it and are equally load-bearing for
campaign work - recurring characters and brand elements may drift across generations, and elements
may not land precisely in layout-sensitive compositions. Read together, those three are the vendor
agreeing with the division of labour this skill already uses: generate the scene, then set logo,
headline and legal copy in layout.

Midjourney is the only provider documenting a required *syntax*. Text must be in double quotation
marks; single quotes and apostrophes do not trigger text generation at all. It works best with the
standard Latin alphabet and short phrases, which means Vietnamese diacritics are outside the
documented range - treat them as untested rather than broken. When text fails, the documented
recoveries are Raw mode or a lower `--stylize`.

Gemini's guidance is procedural: generate the text first, then ask for an image containing it. Two
calls, which also gets the copy reviewed before it is baked into a JPEG.

Firefly is where typography becomes a contract question. Text Effects is a separately defined
feature, Adobe's IP indemnification covers output generated from 13 September 2023 onward, and it
expressly does not extend to the letter and character shapes themselves. Generated letterforms are
not covered, so licensed type still gets set in a design tool.

## Character consistency, and the only numbers anybody publishes

Gemini publishes counts, which nothing else in this table does: `gemini-2.5-flash-image` works best
with up to 3 input images, `gemini-3-pro-image` supports 5 at high fidelity and up to 14 in total,
and `gemini-3.1-flash-image` supports character resemblance for up to 4 characters and fidelity for
up to 10 objects in a single workflow. Four is therefore the documented ceiling for recurring people
in one frame. A five-person cast is a compositing job.

Midjourney is the correction that matters most. `--cref` and `--cw` are V6-only, `--oref` and `--ow`
are V7-only, neither functions on the current default V8.2, and `--cref` has been removed from the
Parameter List page entirely. Every character-consistency tutorial in circulation teaches a
parameter that no longer runs. The script fails a recurring person on this family for want of a
documented mechanism, which is not a judgement about the model - it is the absence of a page to
point at.

None of this is prompt wording, which is exactly why `virtual-person-system.md` locks identity in a
numeric parameter sheet hashed to a stable seed rather than in adjectives. Wording is not a
documented consistency mechanism at any provider.

## Seeds, and what reproducibility costs

Imagen publishes the strongest language: `SEED_NUMBER` is any integer from 1 to 2,147,483,647 and
the same seed always produces the same images. That range is why `plan_virtual_person.py` emits its
hash modulo 2^31 - 1. But the same page says the seed requires `addWatermark: false`, so on Vertex
you get reproducibility or the default SynthID watermark, not both. Decide that at pipeline design
time and write down which you chose.

Midjourney documents the opposite of what the parameter is usually sold as: seeds produce similar but
not identical results on current models. OpenAI documents no seed at all - it is absent from the full
parameter list for the images endpoint. Gemini documents none either; the word does not appear on the
page. On those three, reproducibility means keeping the prompt and archiving the file, and a stored
seed is not a substitute for the asset.

## Ownership and likeness

The asymmetry to know before choosing a provider for client work:

- **OpenAI writes it down.** The Terms of Use state that as between you and OpenAI you own the
  Output and assign you all their right, title and interest in it; the help centre adds that OpenAI
  will not claim copyright over API-generated content. An assignment of whatever rights they hold is
  still not a warranty that rights exist, and it is not indemnity.
- **Google does not, where you would look.** No ownership-of-output or commercial-use clause was
  found across the Terms of Service, the retired Generative AI Additional Terms, the generative AI
  use policy, or the Gemini API image documentation. The clause that your content remains yours is
  scoped to content you upload, submit, store, send, receive or share - not to model output. Do not
  paraphrase it as an output-ownership clause.
- **Indemnity sits behind a tier.** Three of the four major providers gate it behind a revenue
  threshold or an enterprise agreement. Read the plan the client is actually on, not the marketing
  page.

On real people, the operative documents are the usage policies rather than the system cards. OpenAI
prohibits use of someone's likeness, including their photorealistic image or voice, without consent
in ways that could confuse authenticity. Google prohibits violating others' rights including
privacy, gives *using personal data or biometrics without legally-required consent* as its example,
and separately prohibits impersonating an individual living or dead without disclosure in order to
deceive. The word biometrics is doing real work there: a face is biometric data, so a real-face
reference is a consent question before it is a craft question. None of these is a substitute for the
publicity and personality rights that apply locally, and several jurisdictions are stricter than the
policies. `claims-proof-ledger.md` is where that question is answered.

Two provider-side controls are worth setting deliberately rather than inheriting. Imagen's
`PERSON_SETTING` defaults differ by model - `allow_all` including minors on Imagen 4 generation
models and `imagen-3.0-capability-001`, `allow_adult` including celebrities on everything else - and
no equivalent parameter is documented on the Gemini API. OpenAI's moderation strictness is a
parameter, `auto` or `low`, which matters for false refusals on beauty and swimwear work; record
which setting produced a delivered asset.

Disclosure is a terms question, not only an ethics one. Google's use policy prohibits
misrepresenting provenance by claiming generated content was created solely by a human in order to
deceive, and the main Terms list misleading others into thinking AI content was human-made as
prohibited conduct. On the provider side, OpenAI now attaches both C2PA metadata and SynthID
watermarks to images from ChatGPT, Codex and the API, and states that the SynthID signal is part of
the image and may persist through some edits. Gemini applies SynthID to all generated images. So the
old assumption - metadata that a platform upload strips - no longer holds: assume the asset is
detectable and disclose on purpose.

## Nine things the internet gets wrong

Each of these is a case where the popular answer is wrong and a vendor page says so.

1. **"Negative prompts don't work on turbo models."** No such restriction exists;
   `sd3.5-large-turbo` and `sd3.5-flash` differ from non-turbo in a `cfg_scale` default of 1 versus
   4. Raise guidance before concluding the field does nothing.
2. **"Firefly removed `negativePrompt`."** It is live on v3 generate-async and fill-async. The real
   caveat is narrower and is about Custom Models and the v4 schema.
3. **"Use `--cref` for character consistency."** V6-only, dead on the current default version,
   removed from the docs.
4. **"Imagen is limited to 128 tokens."** That figure belongs to Parti, a different Google model. No
   token limit is published for any Imagen version.
5. **"Imagen uses T5-XXL."** True only of the 2022 research model. The encoder for Imagen 3, Imagen
   4 and every Gemini image model has never been disclosed.
6. **"The SD3 paper has a 77-versus-256 token ablation."** It does not. Those figures are on the
   SD3.5 model card. Cite the card for the numbers and the paper for the encoder ablation.
7. **"DALL·E 3 is the OpenAI image API."** DALL·E 2 and 3 are deprecated and removed from the API.
   Current: gpt-image-2, gpt-image-1.5, gpt-image-1, gpt-image-1-mini.
8. **"Imagen is Google's image API."** All Imagen models are deprecated with shutdowns beginning 30
   June 2026 and 17 August 2026, in favour of Gemini image models.
9. **"A seed makes output reproducible."** True on Imagen, and only without the watermark.
   Documented as similar-but-not-identical on Midjourney, and undocumented on OpenAI and Gemini.

## What has no source

Recorded rather than filled in with a plausible sentence, because the gap is the finding:

- **Prompt structure or clause ordering on GPT image models.** The guide has no prompting section at
  all; its headings run Overview, Generate Images, Edit Images, Customize Image Output, Limitations,
  Content Moderation, Cost and latency. Every ordering rule circulating for this family is inferred.
- **The text encoder** behind Imagen 3, Imagen 4, any Gemini image model, any OpenAI image model,
  any Midjourney model, or any Firefly model. Without the encoder there is nothing to reason about a
  token window with, which is consistent with none being published.
- **Prompt length** for Midjourney, Firefly, Imagen and Gemini. Gemini's page carries token figures,
  but they are output-token costs per generated image indexed by resolution, not an input limit.
- **Any in-image text guidance for FLUX.** The overview page returned a content-filter block on two
  attempts, so it was not characterised from memory.
- **A character limit or accuracy benchmark for in-image text** from OpenAI, Stability, Midjourney or
  Adobe. Google's 25 characters is the only published number.
- **A dedicated Firefly Text Effects API endpoint.** Text Effects is documented as an app feature.
- **Vertex REST wire parameter names** - `sampleCount`, `sampleImageSize`, `outputOptions`,
  `storageUri`. The REST reference, the edit-images page and the customize pages were removed, and
  `generate-images` no longer contains those strings. Read them off a live successful request rather
  than reconstructing them.
- **Google's position on output ownership and commercial use**, and on whether the SynthID watermark
  may be removed on the Gemini API surface.
- **Whether a Nano Banana model accepts a seed or a person-generation setting.** Neither appears on
  its page; both exist on Vertex, and the two surfaces are not the same product.

One caveat on currency that applies to a whole group of rows: the Vertex generative-AI image pages
carry a banner saying Vertex AI documentation is no longer being updated, and the negative-prompt
page recommends moving endpoints before 30 June 2026 - a date now past. Every Vertex-sourced row here
documents Imagen-on-Vertex, not the current Gemini surface. A frozen page describes the past
accurately and the present only by luck.

## Reject list

- A prompt sent with a negative block to a family that documents no such field.
- A parameter copied from a tutorial without checking it exists on the version being called.
- A rendered headline longer than the provider's published character budget, where one is published.
- A recurring character promised on Midjourney V8.2, or on any provider without a reference image.
- A stored seed offered as a reproducibility guarantee on OpenAI, Gemini or Midjourney.
- A prompt A/B run with provider-side prompt rewriting left on.
- A claim about ownership, likeness or indemnity sourced from a model card rather than the terms.
- Any figure in this area quoted without its URL. Two pages from the same provider answered the
  prompt-length question differently, and only the URL distinguishes them.
