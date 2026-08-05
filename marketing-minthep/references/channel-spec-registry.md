# Channel Specification Registry

One shoot, exported once, posted everywhere. That is how almost every small-business asset in Vietnam gets made, and it is where the money leaks: Facebook Feed takes a 1:1 still and crops the price off the bottom, the Reel beside it went out at a size Instagram recommends against, and the six-second bumper somebody cut at eight seconds was never going to be accepted at all. None of that is a taste argument. Each one is a published number the exporter did not know about.

This unit is that set of numbers, read off the vendor pages rather than remembered, plus a script that compares a finished file against them.

- `data/channel-specs.csv` — 28 placements across Meta, LinkedIn, TikTok, Google Ads, YouTube and Google Merchant, each row stamped with the URL it came off and the date somebody read it.
- `scripts/check_channel_spec.py` — one asset against one placement, or against every registered placement at once.

## What the earlier version of this file got wrong

It said things like "commonly recommends 2:3", "guidance includes 1200x627", "video supports multiple ratios". Read that back and you can hear what it was: a memory of specs, dressed as a citation. Every hedge in it marked a number nobody had actually looked up, and hedged numbers are worse than no numbers, because they get used.

It also carried Pinterest, LinkedIn and Amazon, then removed all three with the argument that a small local shop does not advertise on LinkedIn. Pinterest and Amazon remain out of scope until a real route needs them. LinkedIn is back because the skill now serves founders, B2B work, agencies and professional services as well as local commerce; removing a channel from a general marketing system because one example business would not use it was a routing error.

## Three states, and why an empty cell is not one of them

Reading vendor pages in one sitting turns up something the hedged version had no way to express. A page can tell you three different things about a limit, and they are not interchangeable:

A **number**. Facebook Feed video caps at 4GB. That is a requirement; break it and the upload is refused.

A **stated absence**. Facebook Reels video documents no maximum length, in those words. TikTok Spark Ads document no restriction on ratio, resolution, file type, duration, bitrate or file size, because the ad *is* an existing organic post rather than an upload. Knowing a limit does not exist is a fact worth having.

**Silence**. Four Meta placements — Facebook Reels image, Instagram Feed image, Instagram Reels image, Facebook Stories video — publish a recommended size and a copy budget and then carry no technical-requirements block at all. No file ceiling. No minimum width. Nothing on tolerance.

That third state is the dangerous one, because silence reads as permission and it is not. The uploader still refuses something. The figure simply is not published, so the only honest answer is *go and find out*, and a table that wrote `0` or left the cell blank would be inventing an answer instead. So the CSV spells all three out:

| token | meaning |
| --- | --- |
| a value | the page publishes this figure |
| `unlimited` | the page states there is no limit |
| `undocumented` | the page publishes no such figure |
| `not-applicable` | the field does not exist here — no headline slot, no duration on a still |
| `per-placement` | not ratio-driven; the page tabulates exact pixel sizes instead |

`check_channel_spec.py` never returns `passed` against `undocumented`; it returns `review`, and it names the page you have to go and read.

## Requirement against recommendation

Meta publishes copy budgets under *Đề xuất về văn bản* and pixel floors under *Yêu cầu kỹ thuật*. One is advice and the other is enforcement, and a tool that failed your ad for a 46-character Instagram Reels caption would be lying to you about who rejects what.

So the script has two failure grades. `failed` means a documented requirement is broken: the upload is refused, or the crop is taken out of your hands. `review` means either the page publishes nothing, or it publishes a recommendation this asset sits outside.

A 200-character caption against a 125-character budget will publish and then truncate on a phone, which puts the ellipsis wherever the layout wants it rather than after a finished thought. Worth fixing, not worth blocking.

## Using it

Check one asset against one placement:

```bash
python scripts/check_channel_spec.py --placement meta-facebook-feed-video \
  --width 1080 --height 1920 --duration 0:42 --file-size 180MB --format mp4 \
  --primary-text "Com tam suon nuong than hoa, 45.000d, giao trong 20 phut"
```

The more useful question is the other way round. You have one file and a week of posting to fill, so ask where it can go untouched:

```bash
python scripts/check_channel_spec.py --survey \
  --width 1080 --height 1920 --duration 22 --file-size 30MB --format mp4
```

Read the resulting pass, fail and review groups as a posting schedule rather than as a score. A new
platform row changes the counts without changing the decision logic, which is why this reference no
longer hardcodes a survey total. Also useful:

- `--list-placements` — every key with its ratio, its floors, its ceilings and the date somebody last read the page it came from.
- `--show KEY` — one row in full, caveat included.
- `--output-format json` — for wiring into a pipeline.

Exit codes follow the rest of the toolkit: 0 clear, 2 a broken requirement, 3 needs a human.

## Rows that carry a warning as well as a number

Half the value of the sweep was in the exceptions, and those live in the `caveat` column rather than in prose here. Four worth knowing before you plan a shoot:

**Instagram Feed wants a different ratio for the still and the video.** 4:5 for the image, 9:16 for the video, on the same surface. One master cannot satisfy both, which is the real reason a still and a cut of the same shoot need separate exports rather than a resize.

**Instagram Reels changes its minimum width at thirty seconds.** 250 px under, 500 px at thirty and over. The table records the looser figure, so a 30-second cut can clear that row and still be refused. Cross the boundary and the rules move under you.

**Facebook Stories tolerates a third of what Feed does.** Three per cent on Feed, one per cent on Stories. The same slightly-off export is legal on one and cropped on the other.

**Google Merchant's 500x500 floor takes effect on 2027-01-31.** It is announced rather than enforced today, so a feed that passes now fails then, with no change on your side.

## Four surfaces with no row, and what each one returned

The domestic platforms are the ones this user needs most and the ones whose specs are hardest to cite. Every attempt is recorded here because a gap somebody documented is worth more than a gap somebody filled from memory. Checked 2026-07-31:

- **Shopee** — the Shopee Uni help article cited by an earlier version of this unit now returns 404 (`Tiếc quá, trang này hiện không tồn tại`). The site is a Vue bundle served from a CDN with no server-side rendering, and its education API answers `403 {"errcode":2,"message":"token not found"}` without a session. `robots.txt` disallows only `/account/`, so reading `/edu/` was permitted; it simply is not readable without an account.
- **TikTok Shop Vietnam university** — `401`.
- **Zalo developer documentation** — a single-page shell; the content arrives by script after load.
- **Lazada University** — the same shape.

Reverse-engineering an internal API to reach a help page was available and was not done. A number obtained that way has no citable source, which puts it in the same class as the hedged figures this rewrite exists to remove.

If you have a seller account on any of the four, the fastest honest path is to read the spec panel in the upload flow itself and add the row with that URL and today's date.

## Ninety days

`STALE_AFTER_DAYS = 90` in the script. It is not a vendor figure, because none of them publishes one. It is a bet, and the bet has already been settled once: the Shopee article above was cited from a live read and was gone within months.

Past ninety days the freshness gate returns `review` on every check against that row and names the page to re-read. Nothing in the row is wrong at that point, and nothing in it is confirmed either.

Re-read a row sooner than that when the placement or objective changes — Meta's URLs are keyed by both, and the specs differ across them — or the moment an upload is rejected against a spec this table says it should have passed.

## Export QA, after the numbers check out

Clearing the table is the floor, not the finish.

Recompose rather than crop. A 4:5 built by trimming a 9:16 has its subject in the wrong third and reads as a mistake even when nobody can say why.

Keep the load-bearing content out of the interface. Product, face, logo, subtitles, disclosure and call to action all need to sit clear of the platform's own furniture. TikTok publishes downloadable overlay files for exactly this, and its safe zone shifts with dimension, caption length and any extra format in play, so there is no single margin to memorise.

Check it at the size people see. Thumbnail, real display size, dark mode where it applies, and on a slow connection. In email, check it with images blocked, because a meaningful share of recipients will see it that way whether they chose to or not.

Keep the master and note every derivative against it. The reason is dull and it is the one that bites: six weeks later something needs a 4:5 and nobody can find the file that was not already 9:16.
