---
name: marketing-minthep
description: "Autonomous marketing system: market research, positioning, offer, copywriting, branding imagery from a reference photo, menu and wireframe design, video. Writes bilingual VI/EN deliverables to disk."
---

# Marketing-Minthep for Claude

Read `../../../marketing-minthep/SKILL.md` completely and follow it as the canonical skill.

Resolve every referenced file, script, template, registry, dossier, and asset relative to `../../../marketing-minthep/`, not relative to this adapter directory.

Apply these runtime rules:

1. Use Claude's available web, filesystem, shell, subagent, and image capabilities. Never pretend an unavailable tool exists, and never claim a result it did not produce.
2. Preserve the canonical pipeline routing, truth, rights, identity-lock, QA, and provider-selection rules.
3. Filesystem tools are normally available here, so a broad plan or production request must create a run workspace with `scripts/start_workbench.py` and pass `scripts/run_status.py --strict` before being reported complete.
4. When research subagents are available, delegate independent evidence tracks, then verify their citations yourself before synthesising.
5. When rendering is unavailable, return executable prompts and state plainly that no image was rendered.
6. Never copy a celebrity identity into an original subject or imply endorsement.
7. For authorized makeup or outfit edits, preserve the exact person and reject face or body drift.

This adapter contains no duplicated marketing knowledge. Update the canonical skill only.
