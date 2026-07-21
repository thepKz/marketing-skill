---
name: "FIELD Marketing Creative Studio"
description: "A tactile creative control room that turns product truth into campaign material."
colors:
  cobalt-instrument: "oklch(0.52 0.16 247.4)"
  cobalt-signal: "oklch(0.742 0.14 247.4)"
  safety-orange: "oklch(0.68 0.19 42)"
  true-white: "oklch(1 0 0)"
  flight-deck-ink: "oklch(0.16 0.025 255)"
  cool-surface: "oklch(0.965 0.009 247)"
  muted-instrument: "oklch(0.43 0.027 250)"
  success: "oklch(0.54 0.14 154)"
  error: "oklch(0.55 0.20 27)"
typography:
  display:
    fontFamily: "Archivo Black, sans-serif"
    fontSize: "clamp(3.2rem, 6.6vw, 6rem)"
    fontWeight: 400
    lineHeight: 0.93
    letterSpacing: "-0.04em"
  body:
    fontFamily: "Manrope, sans-serif"
    fontSize: "1rem"
    fontWeight: 500
    lineHeight: 1.65
  label:
    fontFamily: "Fragment Mono, monospace"
    fontSize: "0.68rem"
    fontWeight: 700
    lineHeight: 1.4
    letterSpacing: "0.08em"
rounded:
  control: "4px"
  surface: "6px"
  soft: "10px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "18px"
  lg: "30px"
  xl: "72px"
components:
  button-primary:
    backgroundColor: "{colors.cobalt-instrument}"
    textColor: "{colors.true-white}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 20px"
    height: "48px"
  button-ghost:
    backgroundColor: "{colors.true-white}"
    textColor: "{colors.flight-deck-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "0 20px"
    height: "48px"
  input:
    backgroundColor: "{colors.true-white}"
    textColor: "{colors.flight-deck-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "12px 13px"
  tab-active:
    backgroundColor: "{colors.cobalt-instrument}"
    textColor: "{colors.true-white}"
    typography: "{typography.label}"
    height: "48px"
---

# Design System: FIELD Marketing Creative Studio

## Overview

**Creative North Star: "The Marked-Up Flight Deck"**

FIELD feels like a creative director's working surface placed inside a precise instrument panel. Its structure is exposed: borders, seams, ledgers, statuses, prompt records, and production lineage remain visible. Softness comes from generous spacing, real photography, and readable body type rather than rounded shells or glass effects.

The page uses soft brutalism with disciplined asymmetry. Cobalt behaves as an active instrument signal, safety orange marks intervention, and true white prevents the palette from collapsing into generic AI fog. The system explicitly rejects generic purple-blue AI SaaS, soft glass dashboards, equal-card landing pages, prompt-box demos with no workflow, over-retouched beauty advertising, and chaotic neo-brutalist collage.

**Key Characteristics:**

- Exposed structural seams and ruled ledgers.
- One dominant visual decision per scene.
- Cobalt for active state; orange for intervention.
- Real images and artifacts instead of decorative blobs.
- Mechanical motion with immediate reduced-motion fallbacks.

## Colors

The palette is a flight deck at dawn: true white working light, blue instruments, orange intervention marks, and near-black structural ink.

### Primary

- **Cobalt Instrument**: Primary actions, selected tabs, active channels, and major status surfaces.
- **Cobalt Signal**: Loading scans, secondary indicators, and tonal ramps; never a decorative glow.

### Secondary

- **Safety Orange**: Intervention, departure-lane emphasis, physical seams, and high-value hover states.

### Neutral

- **True White**: Main work surface and high-contrast copy field.
- **Flight Deck Ink**: Body text, full borders, dark production surfaces, and structural contrast.
- **Cool Surface**: Form rail, quiet sections, and grouped utility areas.
- **Muted Instrument**: Secondary text that remains readable against true white.

**The Instrument Rule.** Cobalt marks something active, selected, or operational. It is never spread as atmospheric fog.

**The Orange Tape Rule.** Safety orange appears as a purposeful mark or state transition, not a universal accent.

## Typography

**Display Font:** Archivo Black (sans-serif fallback)
**Body Font:** Manrope (sans-serif fallback)
**Label/Mono Font:** Fragment Mono (monospace fallback)

**Character:** Archivo Black creates compressed poster-like decisions. Manrope keeps long operational copy calm. Fragment Mono exposes metadata, state, lineage, and control labels without turning the entire product into a terminal costume.

### Hierarchy

- **Display** (400, fluid 3.2rem-6rem, 0.93): Hero promises and selected campaign statements only.
- **Headline** (400, fluid 2rem-4.2rem, 1): Section decisions and output modes.
- **Title** (700, 1rem-1.4rem, 1.25): Component and lane titles.
- **Body** (500, 1rem, 1.65): Explanations, prompts, and form guidance with a 65-75ch ceiling.
- **Label** (700, 0.68rem, 0.08em, uppercase): State, route, provider, field, and export metadata.

**The Compression Rule.** Display type can be loud but never exceed three intentional lines on desktop or four on mobile.

## Elevation

FIELD is flat by default. Depth comes from tonal changes, full borders, overlap, crop, and occasional hard offset shadows. Wide ambient shadows and glass elevation are prohibited.

### Shadow Vocabulary

- **Pressed Offset** (`4px 4px 0 var(--line)`): Primary button hover and tactile confirmation.
- **Selected Offset** (`6px 6px 0 var(--line)`): Lane-card hover only.

**The Honest Depth Rule.** A surface moves because it is interactive or selected, never because every container needs decoration.

## Components

### Buttons

- **Shape:** Hard-soft control corner (4px), full 2px structural border.
- **Primary:** Cobalt fill, white label, 48px minimum height.
- **Hover / Focus:** Translate by -3px with a hard 4px offset; focus uses a 3px cobalt ring.
- **Ghost:** White at rest; safety-orange fill on hover.

### Chips

- **Style:** Square channel labels with 1px full borders; no pill shape.
- **State:** White unselected, cobalt selected, visible keyboard focus.

### Cards / Containers

- **Corner Style:** 0-6px depending on whether the surface is structural or interactive.
- **Background:** True white, cool surface, cobalt, or safety orange according to role.
- **Shadow Strategy:** Flat at rest; hard offset only on interactive lane surfaces.
- **Border:** Full structural border. Colored side stripes are forbidden.
- **Internal Padding:** 18-30px for tools, 42-88px for major scenes.

### Inputs / Fields

- **Style:** White field, 1px flight-deck border, 4px corner, label above control.
- **Focus:** Cobalt border plus a restrained 4px offset field shadow.
- **Error / Disabled:** Error includes text and border; disabled preserves the user's content and lowers contrast without hiding it.

### Navigation

- **Style:** Stable 62px ruled rail with Archivo brand mark and Fragment Mono links.
- **States:** Underline hover, explicit focus ring, no floating pill navigation.
- **Mobile:** Collapse optional links while preserving brand and system state.

### Campaign Lane

Lane surfaces expose index, idea, visual grammar, hero, and risk. The recommended lane receives a cobalt field; neighboring lanes remain white and shift position to create controlled asymmetry.

## Do's and Don'ts

### Do:

- **Do** expose assumptions, locks, provider, asset lineage, and rejection reasons.
- **Do** use true white and near-black as architectural surfaces while cobalt and orange carry operational meaning.
- **Do** recompose the tool into a stable single column below 900px.
- **Do** use real photography, product references, prompt records, tables, diagrams, and process lines as visual proof.
- **Do** design loading, validation, empty, success, copy, download, keyboard, and reduced-motion states.

### Don't:

- **Don't** resemble "generic purple-blue AI SaaS" or use cobalt as atmospheric fog.
- **Don't** build "soft glass dashboards" or decorative glass cards.
- **Don't** use "equal-card landing pages" or nested card grids.
- **Don't** ship a "prompt-box demo with no workflow"; every prompt connects to a lane, asset, QA, and export.
- **Don't** use "over-retouched beauty advertising" as proof of human realism.
- **Don't** create "chaotic neo-brutalist collage" without a stable reading path.
- **Don't** use gradient text, decorative grid backgrounds, random orbs, repeated section eyebrows, or 32px card radii.
