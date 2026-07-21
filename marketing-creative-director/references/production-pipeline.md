# Production Pipeline

## Asset lineage

Preserve this hierarchy:

```text
campaign-id/
  lane-id/
    asset-id/
      source/
      prompts/
      generations/
      edits/
      exports/
      review/
```

Do not replace approved masters silently. Create versioned siblings.

## Naming contract

Use:

```text
{campaign}-{lane}-{channel}-{asset}-{ratio}-{variant}-v{number}.{ext}
```

Example:

```text
barrier-reset-signature-tiktok-hero-9x16-proof-v03.mp4
```

Avoid spaces, vague names such as `final-final`, and provider-generated random filenames in handoff.

## Prompt record

Store:

- Prompt ID, campaign, lane, asset, channel, ratio, and hypothesis.
- Provider and model/version when known.
- Input reference paths and roles.
- Product, identity, text, and claim locks.
- Master prompt and provider-compiled prompt.
- Generation settings available from the provider.
- Selected result, rejected results, and rejection labels.
- Edit passes and exact change scope.
- Approval owner, date, and export status.

## Review states

Use a small state machine:

`draft -> generated -> selected -> editing -> qa -> approved -> exported -> measured`

Allow `rejected` from every state before `approved`. Never label an asset approved when only the prompt was reviewed.

## Export package

Include:

- Approved master.
- Channel-specific exports.
- Copy file and legal copy.
- Prompt record and source references.
- Asset manifest CSV or JSON.
- Rights, consent, usage, and expiration notes.
- QA score and unresolved limitations.

## Channel crop process

1. Start from the selected composition.
2. Recompose for each ratio when hierarchy changes.
3. Protect logo, face, product label, CTA, and UI safe zones.
4. Inspect at actual delivery size and thumbnail size.
5. Add typography after generation when exact text matters.

## Handoff safeguards

- Keep source and export color profiles explicit.
- Preserve full-resolution masters.
- Do not upscale a broken asset and call it production-ready.
- Do not export fake text, temporary labels, watermarks, or debug overlays.
- Record what could not be verified.

Use `scripts/build_asset_manifest.py` and templates under `assets/templates/`.

