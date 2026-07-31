# Virtual Person System

## Contents

- What the job actually is
- Why the option menu was deleted
- The parameter sheet
- Locked identity against campaign styling
- Reproducing the same person
- Using a real face as a reference
- Makeup
- Douyin as a capture grammar
- Identity bible
- Generation sequence
- QA

## What the job actually is

A recurring fictional model, AI creator, brand face, campaign character or product demonstrator.

The requirement is not one good image. It is the same person in fifty posts across two years, because
that is the only thing that turns a generated face into an asset. A beautiful face that arrives slightly
different every month is a stock photo budget with extra steps: nobody recognises it, so it accumulates
nothing. So the whole system here is built around one question - can this person be rendered again
tomorrow - and everything that does not serve that question was removed.

## Why the option menu was deleted

This document used to open with four face codes, four build codes, four pose codes and seven makeup
codes. `F1` was "soft romantic: warm, polished, inviting". `B1` was "slender light-frame: long visual
lines, narrow healthy frame".

Feed that vocabulary to this skill's own gate and it comes back:

```
# specificity check - language en, verdict failed
3 sentences, 41 words, 0 checkable things (none).
| fact-floor  | failed | 0 checkable        | >= 3    |
| brand-swap  | failed | 100% of sentences carry nothing checkable (3 of 3) | <= 50% |
```

A menu that fails the gate the same skill ships to clients is a mood board, not a specification. And the
deeper problem is not the score. It is that an adjective survives no round trip: the person who writes
"slender", the person who prompts with it and the model that renders it are holding three different
pictures, and there is no way to find out until the images disagree. `7.5 head units, shoulders 2.1 head
widths, shoulder-to-waist 1.3` is held identically by all three, and can be diffed when a render drifts.

The codes are gone. `data/person-parameters.csv` replaced them.

## The parameter sheet

Thirty-one axes in `data/person-parameters.csv`, one row each, grouped `face`, `build`, `pose`,
`camera`. Every row carries a unit, an input domain, a neutral value, what the axis controls, how it
fails when it is wrong, the phrasing to put in a prompt, and where the term comes from.

Three conventions matter more than the contents:

**Faces are ratios, not features.** `face-length-to-width` at 1.40, `bigonial-to-bizygomatic` at 0.78,
`interpupillary-to-face-width` at 0.46, `canthal-tilt` at +4 degrees. Ratios survive being resized to a
40px avatar, which is where most of a brand face is actually seen, and they are what a viewer registers
as resemblance before they can name a single feature. A sheet that specifies eyes, nose and mouth
separately gets three plausible features and a jointly wrong face.

**Builds are head units, not sizes.** `stature-head-units` at 7.5, `shoulder-width-head-units` at 2.1.
No centimetres and no clothing size, so the sheet works at any crop and in any market. This also
defends against a specific drift: fashion illustration convention runs to 8.5 or 9 heads and image
models have absorbed it, so an unspecified full-body frame elongates below the waist and stops matching
the half-body frames.

**An input domain is not a norm.** The `input_domain` column is the range the script accepts. It is not
a claim about how faces or bodies are distributed in any population, and it is not a range of preferred
values. Inventing population statistics here would be the exact failure the rest of this skill exists to
catch. Where a term is standard anatomy or standard photographic practice the `term_grade` column says
so and `source` says where to verify it; where the axis is this skill's own construction, `term_grade`
is `house-axis` and says nothing more.

## Locked identity against campaign styling

Seventeen axes are `locked` and fourteen are `styling`.

Locked is the person: face ratios, build ratios, posture signature, and one named distinguishing mark.
Styling is the campaign: weight distribution, counter-rotation, torso rotation, head tilt, chin
elevation, gaze, hands, focal length, subject distance, camera height.

The split is the whole point. Mixing them produces the specific failure that ends a virtual brand face -
a character whose jaw changes when the lipstick does, because the sheet never said which of the two was
allowed to move. `vermilion-ratio` is locked precisely because an overlined lip is a makeup decision:
lock the bare mouth, and let the makeup row restyle it.

`distinguishing-asymmetry` deserves its own note. Exactly one named mark, with a side: a mole two
centimetres above the left jaw, a right brow sitting marginally lower. A perfectly symmetric face is the
strongest single tell of generated imagery, and it is also unownable, because it is the average of the
training set. It belongs to nobody and resembles everybody.

## Reproducing the same person

The locked block is canonicalised, sorted and hashed to a `person_id` and a derived seed. Same locked
values, same id, on any machine, in whatever order the flags were typed.

```
python scripts/plan_virtual_person.py --list-axes
python scripts/plan_virtual_person.py --set stature-head-units=7.4 canthal-tilt=6 \
    bigonial-to-bizygomatic=0.74 --makeup kr-crying-eye --purpose "skincare brand face"
python scripts/plan_virtual_person.py --verify sheet.json
python scripts/plan_virtual_person.py --drift before.json after.json
```

Exit codes: 0 clean, 1 usage error, 2 a locked axis moved or a value is out of domain, 3 the sheet is
mostly neutral defaults.

`--verify` recomputes the id from a saved sheet and fails if it moved. `--drift` names the axes that
changed between two sheets. That pair is what makes a drifting character debuggable: when the renders
stop looking like the person, the answer is a named axis and two values, not another guess at the
prompt.

Two limits worth stating before anyone relies on this.

An axis left at its neutral default still hashes, so the person is still reproducible - but a neutral
default is not a decision, it is a value nobody chose, and it is an axis this character shares with
every other character built from the same table. The report counts them for that reason. A sheet with
thirteen of seventeen locked axes at neutral is graded `review`, not `passed`.

And the seed reproduces a person inside one model at one version. No provider guarantees determinism
across versions. The sheet is what survives a version change; the seed is not.

## Using a real face as a reference

The request comes up constantly, usually as "take this photo and make someone similar". Two reasons to
answer it with a parameter sheet instead, and neither is a rule.

It does not reproduce. A reference image gets you one output that resembles the reference. It does not
get you the same person next month, because there is nothing written down to check the next render
against, and "looks like the photo" is not a check anybody can run. The sheet is the check.

It does not become yours. A face derived from an identifiable person carries that person's likeness
rights into every ad it appears in, and those rights usually do not sit with whoever posted the photo -
on an idol image they sit with the agency and the photographer. The commercial asset is a face nobody
else can claim, and a derived face is the one thing that cannot be.

What to do instead: read the reference the way `reference-reading.md` says to read anything - measure the
frame, do not keep the file - and turn what you measured into axis values. Ratios are not protectable;
a specific person's face is. `reference-observations.csv` is where the measurement lands.

Never build a face by averaging named public figures. Translate references into separate
non-identifying values and add at least one original distinguishing mark.

## Makeup

Makeup is not re-specified here. `data/makeup-looks.csv` carries 47 looks across thirteen families,
each with a `discriminator` column separating it from the look it gets confused with, and
`makeup-art-direction.md` carries the contract. `--makeup` takes a `look_id` from that table and is
validated against it.

The seven `M1` to `M7` lane codes are gone. They were bare strings that never touched the table on disk,
which meant the makeup vocabulary in this document and the makeup unit in the same skill could drift
apart indefinitely and nothing would notice.

Treat makeup as surface styling only. It sits on the anatomy the locked axes define and never changes
it.

## Douyin as a capture grammar

Treat `Douyin` as a makeup and capture grammar, not an ethnicity or an identity instruction. The
contract lives in `makeup-looks.csv` under `cn-douyin`, with `kr-crying-eye`, `kr-aegyo-sal` and
`jp-igari` as the looks it is most often confused with and the discriminator for each.

The capture half is axis values, not adjectives: frontal or three-quarter beauty crop is
`torso-rotation` at 0 to 30, `camera-height` level with the eyes, `focal-length` at 85 with
`subject-distance` around 2.5.

Reject oversized generated eyes, painted under-eye bags, white crescent stickers, duplicated lower
lashes, poreless skin, a pinched nose, an extreme V-line jaw, or childlike age presentation.

## Identity bible

1. The parameter sheet, saved as JSON, with its `person_id` recorded.
2. Neutral head reference: front, left three-quarter, right three-quarter, profile.
3. Neutral full-body reference, simple fitted clothing, `subject-distance` stated so the frame is not
   carrying lens distortion into the anatomy.
4. Expression sheet: neutral, small smile, focused, surprised, campaign-specific.
5. A makeup-off baseline, when makeup will vary across campaigns.
6. The lock list, the freedom list and the reject list - which the `lock_class` column already is.

Camera angle and wardrobe change apparent proportions. Do not write lens distortion into the locked
axes; that is what `focal-length` and `subject-distance` are for, and they are styling.

## Generation sequence

1. `scripts/plan_virtual_person.py --list-axes`, then set the axes that matter to this brand.
2. Read the `left_at_neutral_default` count. Anything above half the locked axes means the character is
   mostly the table's average, and the verdict says `review` for that reason.
3. Save the sheet. Record the `person_id`.
4. Generate the neutral identity sheet before any high-styling campaign image.
5. Branch campaign variants by changing styling axes only. The `person_id` must not move.
6. `--verify` before every campaign, so a changed locked axis is caught here rather than in the render.

## QA

Reject when:

- The person resembles a named public figure strongly enough to imply copying or endorsement.
- `--verify` fails, or `--drift` names a moved locked axis that nobody decided to move.
- Locked axes hold but the renders still disagree, which means an axis the sheet does not cover is
  carrying identity. Name it and add the row.
- A slender build becomes unhealthy, anatomically impossible, or childlike. No emaciation, no protruding
  bones, no implausible waist, no weight number, and never a claim that one build is more attractive.
- Makeup changes eye, nose, jaw or lip anatomy instead of sitting on it.
- Full-body perspective contradicts the sheet's head-unit values.
- The person is attractive only through pore erasure, extreme symmetry, or generic beauty-filter traits.
- The subject is anything other than a fictional adult. The script refuses a minor before it parses
  anything else.
