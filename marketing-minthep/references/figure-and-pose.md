# Figure and Pose Construction

How to build a pose that reads as a person standing there, and how to say it in numbers a render can be
checked against. The axes are rows in `data/person-parameters.csv`; this document is why they are the
axes and where each one comes from.

## Contents

- The one thing to take from this document
- Three masses, three planes
- Weight: the engaged leg
- Counter-rotation, and its sign
- Line of action against central axis against midline
- Open and closed
- Negative space is a measuring tool
- Hands
- Head angle needs a datum
- Distance, not lens
- What has no source
- Reject list

## The one thing to take from this document

A pose is not a shape you pick. It is a set of relationships between four things - the three body masses,
the ground, the viewing axis and the frame - and every one of those relationships can be stated as a
number. The reason to bother stating them is not rigour for its own sake. It is that "confident, natural
pose" produces a different image every time it is prompted and there is no way to find out why, while
`weight-distribution 70, hip-shoulder-counter-rotation +12, torso-rotation 30, line-of-action C` produces
a render you can hold up against four values and say which one the model ignored.

## Three masses, three planes

Bridgman's model, and the most useful single idea in the source material: the figure is three masses that
do not change shape - head, chest, pelvis - plus limbs. The masses are unchanging; only their relations
to each other change, and those relations are limited to three planes. Bent forward and back. Twisted.
Tilted.

Two consequences worth having.

Almost invariably all three are present at once, to different degrees. So a pose specified in one plane
only - "turned to the side" - is underspecified by two thirds, and the model fills the other two from its
own prior, which is what makes generated poses look subtly stiff even when the described part is right.

And: the masses are balanced symmetrically over each other rarely in life, and in action never. This is
the structural version of the symmetry rule that `distinguishing-asymmetry` enforces on the face. It is
not an aesthetic preference. A symmetric arrangement of the three masses is a description of a body not
doing anything.

Source: Bridgman, *Constructive Anatomy*, 1920, https://archive.org/details/constructiveanat00briduoft

## Weight: the engaged leg

Contrapposto, in its own vocabulary: the **engaged leg** bears the weight and is straight or very
slightly bent; the **free leg** is relaxed and slightly bent. That is the whole mechanism, and
`weight-distribution` is the number - 50 is even, 95 is almost entirely on one leg, 70 is the ordinary
standing asymmetry.

The working cue that makes it checkable in a finished render, from life-model teaching rather than art
history: the weight-bearing side compresses, so the shoulder and hip on that side sit **closer together**
than on the free side. That is a comparison you can make on the image, left against right, without
measuring anything absolutely.

Sources: https://en.wikipedia.org/wiki/Contrapposto and
https://lifemodelssociety.org/2021/08/04/common-art-life-modelling-terms/

## Counter-rotation, and its sign

The relation is reciprocal, and the sign is the part usually got wrong. In the frontal plane: right hip
higher means right shoulder **lower**. In the axial plane: shoulders and arms twist off the axis of the
hips and legs.

`hip-shoulder-counter-rotation` runs −25 to +25 degrees and its sign is what carries this. A pose where
the hip and shoulder rise together on the same side is the tell of a figure that was described rather
than constructed - it is what happens when the whole torso is tilted as one block, which is exactly the
mistake the three-mass model exists to prevent.

Conventionally dated to the Kritios Boy, about 480 BCE, which is worth knowing only because it makes the
point that this is a two-and-a-half-thousand-year-old solved problem being re-broken by prompt vagueness.

## Line of action against central axis against midline

Three different things that get used interchangeably, and separating them is what makes torso twist
sayable:

- **Central axis** - the internal line through a form, joint to joint.
- **Midline** - same alignment, but on the surface: the sternum from the front, the vertebral column from
  the back. This is the one you can actually see in a photograph, so this is what `torso-rotation` is
  read off.
- **Line of action** - the directional movement of the whole figure within the pose. More organic than
  the central axis and at times not following it at all. It indicates a sweeping alignment rather than a
  joint-by-joint one.

A strong directional alignment of torso, limbs and head is what creates the illusion of movement in a
stationary figure. That is the entire job of `line-of-action`, and its four values - straight, C, S,
reverse-S - are named curves rather than degrees because the axis is a shape, not a magnitude.

The S-curve is the stronger case: it involves more of the body than contrapposto does, and it guides the
eye through the image to the subject at the end of the curve. Which means it is a composition decision as
much as a pose decision, and it is the reason a full-body frame with a described-but-unstated line of
action tends to put the eye nowhere.

Sources: Winslow, *Classic Human Anatomy in Motion*,
https://doctorlib.org/anatomy/classic-human-anatomy-motion/12.html and
https://en.wikipedia.org/wiki/S-curve_(art)

## Open and closed

Open pose: arms spread wide, head up. Closed pose: shrunken, curled or compact, limbs often crossing one
another, sometimes the face hidden.

`pose-openness` is a two-value axis and it is stated first, before any other pose axis, because it
decides how much silhouette the frame gets at all. Closed is not a mistake - it is how you get intimacy,
protection, self-containment. But choosing it means accepting that crossing limbs and a possibly hidden
face have to be resolved some other way, by light separation or by colour, and that is a decision to make
deliberately rather than discover in the render.

Source: https://lifemodelssociety.org/2021/08/04/common-art-life-modelling-terms/

## Negative space is a measuring tool

The spaces between the arms and the body, or the legs and the ground or chair. The reason it appears on
the parameter sheet as `arm-torso-negative-space` in head units, with a floor of 0.25, is not that gaps
look nicer. It is that negative space is **used for correcting proportions**: the shape of the gap is
easier to judge than the limb bounding it, so an arm that has merged into the torso has taken the
proportion check away with it.

Bridgman gives the structural reason the merge happens: masses of about the same size or proportion are
conceived not as masses but as **one mass**. His prescribed fix is wedging one into another - overlapping
them at an angle so the sizes stop matching - which is a more useful instruction than "leave a gap",
because it works in the cases where there is no room for a gap.

## Hands

The two things worth stating, because hands are where generated figures fail most visibly:

**Scale.** A hand is as long as the face. This is larger than nearly everyone estimates, which is why
`hand-length-to-face` is on the locked block with a neutral of 1.00 - unstated, hands arrive small.

**Structure.** Two masses, the hand proper and the thumb. The knuckles lie on one arc concentric around
the base of the thumb, with the second knuckle largest and highest. The fingers move as a fan about the
middle finger, because the palmar interossei collect toward it and the dorsal interossei spread away from
it - not as five independent sticks, which is precisely how a bad generated hand reads.

And the diagnosis behind `hand-height` and `hand-articulation`: the instruction sources describe small
hands as a **budget failure, not a care failure**. In fast studies there is too little time to suggest
smaller forms such as hands, and the prescribed fix is to give them their own construction time.
Generation has the same economy - the hand is the last form resolved and the first degraded - so the fix
transfers: state the hand as its own subject with its own values, or give it an object to close around so
the failure is removed rather than hoped past.

Sources: Bridgman as above; https://en.wikipedia.org/wiki/Body_proportions for hand length;
https://doctorlib.org/anatomy/classic-human-anatomy-motion/11.html for the time-budget claim.

## Head angle needs a datum

`head-tilt` and `chin-elevation` were the two weakest rows on the sheet until this: an angle is not a
number without a reference plane, and "degrees from level" begs the question of what is level.

The datum is the **Frankfort horizontal plane** - superior external auditory canal to inferior
infraorbital rim. In a photograph, approximated as superior tragus to the junction of lower eyelid and
cheek. Head position in clinical facial photography is standardised against this plane, not against the
frame, which is what makes pitch reportable across images shot at different camera heights.

The related measurable is the **mentocervical angle**, across the transition from chin to neck, reported
at 80 to 95 degrees. Landmarks: menton, the lowest point of the chin; pogonion, the most anterior point
in profile; the cervical point. Useful because a raised chin and a lengthened neck are usually specified
as one wish and are two different axes.

Source: Facial Analysis, ENT Secrets ch 60, https://clinicalpub.com/facial-analysis/

## Distance, not lens

The load-bearing correction, and it invalidates most of what is said about portrait lenses:
**perspective changes are caused by distance, not by the lens.** Two photographs taken from the same
distance show identical perspective geometry whatever focal length was used. The lens changes the crop;
the distance changes the face.

So `subject-distance` is the axis that controls how the face is shaped and `focal-length` only controls
how much of the scene comes with it. Getting this backwards is why "shot on 85mm" fails to fix a face
that looks wrong - the fix is standing further back.

The measured result behind it: one face photographed simultaneously at 45cm and 135cm through a
half-silvered mirror, normalised on interocular separation, warp modelled from 115 labelled landmarks.
Closer distance makes the nose relatively larger and the ears smaller, and the face width-to-height ratio
smaller, t(17)=11.16, p<0.001. Observers could not judge the actual distance, so the cue operates
implicitly - which is the mechanism by which a too-close portrait reads as *off* rather than as *close*.

Anchors for `focal-length`: about 50mm is the geometrically correct focal length for prints of 35cm and
larger; the median of 3,930 Flickr SLR photographs was 68mm in 35mm-equivalent terms; 85 to 135mm is the
conventional portrait band. Preferred viewing distance is set by picture size, not by the focal length
used - it changed only about 20 percent across a 614 percent change in projection distance. Small screens
therefore need longer focal lengths for the same fidelity, which is the case that actually matters here,
since the output is a phone feed.

`camera-height` is film convention, not measurement, and is labelled as such on the sheet: high angle
small or vulnerable, low angle powerful or threatening, eye level little to no psychological effect. No
measured effect sizes were obtained for these.

Sources: https://en.wikipedia.org/wiki/Perspective_distortion; Cooper, Piazza and Banks 2012, *Journal of
Vision* 12(5):8, https://jov.arvojournals.org/article.aspx?articleid=2192052; Bryan, Perona and Adolphs
2012, *PLOS ONE*,
https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0045301;
https://en.wikipedia.org/wiki/Camera_angle citing Ascher and Pincus, *The Filmmaker's Handbook* p214.

## What has no source

Recorded because a skill that gates other people's claims has to record its own failures to source
things. Each of these was searched for in teaching and reference material and came back with nothing
citable:

- **Tangency**, as a named composition fault. Every ranked result was a content-marketing tip list citing
  nothing. `tangency-check` is therefore graded `house-axis`, not `photographic-standard`. The structural
  substitute above - two masses of similar size merging into one - covers the same failure and is sourced.
- **Cropping at the joints.** Same outcome. The sourced material names the accepted framings - full
  length, half length, head and shoulders, head only - without prohibiting anything between them.
- **The rule of vertical fifths**, **Loomis's internal head-construction ratios**, **Hogarth's head
  units**, and named **hand-posing conventions**. Not found in citable form.
- **Gonion and zygion** as skeletal landmark names. The Wikipedia craniofacial-anthropometry entry
  redirects to a history of scientific racism and carries no landmark list, so it was not used as a
  source. FISWG expresses cheek width as a relative descriptor instead, and that is both safer and better
  practice, which is why `bigonial-to-bizygomatic` is graded `house-axis`.
- **Population ranges** for canthal tilt, vermilion ratio, neck length in head units, shoulder width in
  head units, and gaze offset. The `input_domain` values for those rows are accepted ranges only.

One axis does have a real measured distribution, and it is the only one: `shoulder-to-hip` lateral width
ratio, Hughes and Gallup 2003 - men 1.18, SD 0.071, observed range 1.03 to 1.40; women 1.03, SD 0.066,
range 0.90 to 1.22. Treat it as the reference case for what a sourced anthropometric claim looks like,
and treat every other row's domain as what it says it is.

Finally, FISWG's own caveat, which applies to this whole document: photoanthropometry should not be used
for identification. The vocabulary is borrowed here to *describe* a fictional person consistently, never
to identify a real one.

## Reject list

- A pose stated in one plane only. Say bend, twist and tilt, or accept the model's prior for two of them.
- Hip and shoulder rising together on the same side.
- A full-body frame with no stated line of action.
- An arm merged into the torso with no wedging and no gap, so the proportion check is gone.
- Hands smaller than the face, five fingers splayed to full length, or a hand with no stated structure in
  a frame where it is visible.
- Chin elevation or head tilt given as an angle with no datum.
- A face shape fixed by changing focal length rather than subject distance.
- Camera-angle psychology quoted as a finding rather than as film convention.
