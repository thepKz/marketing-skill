# FIELD Marketing Creative Studio

Local campaign compiler powered by the `marketing-creative-director` and `marketing-one-page-studio` skill contracts. It turns a product brief into three creative lanes, provider-ready image prompts, a channel manifest, Brand DNA, a one-page website sequence, and adaptive pre-flight QA.

## Run locally

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite. No API key is required because the studio compiles campaign artifacts locally; it does not render images or publish campaigns.

## Verify

```powershell
npm run lint
npm run build
```

Exports include Markdown, a JSON payload matching `marketing-one-page-studio/assets/one-page-schema.json`, and a CSV asset manifest.
