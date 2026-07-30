#!/usr/bin/env python3
"""Call an OpenAI-compatible image API to generate or edit a real file.

This is the one script in the skill that can produce an actual image instead of a
prompt. It is optional by design: every other pipeline works from prompts and SVG
reference sheets alone, per `references/api-image-orchestration.md`. Configure
`MINTHEP_IMAGE_BASE`, `MINTHEP_IMAGE_KEY`, and `MINTHEP_IMAGE_MODEL` in the repository's
`.env` (already gitignored) to use it; leave them unset and every other pipeline still
runs. The key is read from the environment and is never printed, logged, or included in
an error message - only request shape and response status are ever emitted.

Endpoints follow the OpenAI Images API shape: POST {base}/v1/images/generations for a
new image, POST {base}/v1/images/edits (multipart) for an edit or reference-driven
generation. Never send `input_fidelity`; official guidance says every input image is
processed at high fidelity and the parameter cannot be changed.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json, use_utf8_stdout  # noqa: E402
from _env import get as env_get  # noqa: E402

MODES = ("generate", "edit")
QUALITIES = ("low", "medium", "high", "auto")


def _redact_url(base: str, path: str) -> str:
    return base.rstrip("/") + path


def _read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt
    raise ValueError("Provide --prompt or --prompt-file.")


def _build_generate_request(args: argparse.Namespace, model: str, prompt: str) -> dict:
    body = {"model": model, "prompt": prompt, "n": args.n}
    if args.size:
        body["size"] = args.size
    if args.quality:
        body["quality"] = args.quality
    if args.output_format:
        body["output_format"] = args.output_format
    return body


def _multipart_body(fields: list[tuple[str, str]], files: list[tuple[str, Path]]) -> tuple[bytes, str]:
    boundary = "minthep-image-boundary-7f3c9a"
    parts: list[bytes] = []
    for name, value in fields:
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8")
        )
    for name, path in files:
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        parts.append(
            (
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; "
                f"filename=\"{path.name}\"\r\nContent-Type: {content_type}\r\n\r\n"
            ).encode("utf-8")
        )
        parts.append(path.read_bytes())
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _build_edit_request(args: argparse.Namespace, model: str, prompt: str) -> tuple[bytes, str]:
    fields = [("model", model), ("prompt", prompt), ("n", str(args.n))]
    if args.size:
        fields.append(("size", args.size))
    if args.quality:
        fields.append(("quality", args.quality))
    if args.output_format:
        fields.append(("output_format", args.output_format))
    image_field = "image" if len(args.input) == 1 else "image[]"
    files = [(image_field, Path(p)) for p in args.input]
    if args.mask:
        files.append(("mask", Path(args.mask)))
    return _multipart_body(fields, files)


def _save_images(data: list[dict], output: str | None, output_dir: str | None, output_format: str) -> list[str]:
    saved: list[str] = []
    ext = output_format or "png"
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(data):
        if output and index == 0:
            target = Path(output)
        elif output_dir:
            target = Path(output_dir) / f"image-{index + 1:02d}.{ext}"
        else:
            target = Path(f"image-{index + 1:02d}.{ext}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if "b64_json" in item:
            target.write_bytes(base64.b64decode(item["b64_json"]))
        elif "url" in item:
            with urllib.request.urlopen(item["url"]) as response:  # noqa: S310
                target.write_bytes(response.read())
        else:
            continue
        saved.append(str(target))
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=MODES, default="generate")
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument("--input", action="append", default=[], help="Reference image path; repeat for several. Required for --mode edit.")
    parser.add_argument("--mask")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--size")
    parser.add_argument("--quality", choices=QUALITIES, default="auto")
    parser.add_argument("--output-format", default="png")
    parser.add_argument("--output")
    parser.add_argument("--output-dir")
    parser.add_argument("--base")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true", help="Build the request and print its shape; makes no network call and needs no key.")
    args = parser.parse_args()

    use_utf8_stdout()

    if args.mode == "edit" and not args.input:
        print("error: --mode edit requires at least one --input image", file=sys.stderr)
        return 1

    try:
        prompt = _read_prompt(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    base = args.base or env_get("MINTHEP_IMAGE_BASE")
    model = args.model or env_get("MINTHEP_IMAGE_MODEL")
    key = env_get("MINTHEP_IMAGE_KEY")

    if not base or not model:
        print(
            "error: MINTHEP_IMAGE_BASE and MINTHEP_IMAGE_MODEL are not configured. "
            "Set them in .env, or pass --base/--model, or use --dry-run.",
            file=sys.stderr,
        )
        return 1

    path = "/v1/images/generations" if args.mode == "generate" else "/v1/images/edits"
    url = _redact_url(base, path)

    if args.dry_run:
        summary = {
            "method": "POST",
            "url": url,
            "authorization": "Bearer ***" if key else "(none configured)",
            "mode": args.mode,
            "model": model,
            "prompt_preview": prompt[:120],
            "n": args.n,
            "size": args.size,
            "quality": args.quality,
            "output_format": args.output_format,
            "inputs": list(args.input),
        }
        emit_json(summary)
        return 0

    if not key:
        print("error: MINTHEP_IMAGE_KEY is not configured. Set it in .env or pass --dry-run.", file=sys.stderr)
        return 1

    headers = {"Authorization": f"Bearer {key}"}
    if args.mode == "generate":
        body = json.dumps(_build_generate_request(args, model, prompt)).encode("utf-8")
        headers["Content-Type"] = "application/json"
    else:
        body, content_type = _build_edit_request(args, model, prompt)
        headers["Content-Type"] = content_type

    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        print(f"error: {exc.code} {exc.reason}\n{detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"error: could not reach {base}: {exc.reason}", file=sys.stderr)
        return 1

    saved = _save_images(payload.get("data", []), args.output, args.output_dir, args.output_format)
    emit_json({"mode": args.mode, "model": model, "count": len(saved), "files": saved})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
