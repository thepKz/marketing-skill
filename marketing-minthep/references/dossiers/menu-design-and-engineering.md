# Menu Design and Menu Engineering

## Scope

Menu engineering as an analytical method (Kasavana & Smith matrix, exact arithmetic, VND worked example), an
evidence audit of menu psychology that separates supported findings from folklore and from numbers that appear
to have been invented by vendor blogs, plus information architecture, typography, print/production specs,
delivery-platform merchandising, Vietnamese F&B conventions, three fully specified menu directions for a
single-dish bún bò shop, and how to express all of it inside a text-to-image prompt.
All external facts carry an inline source. Physics, optics and arithmetic do not.

---

# PART 1 — MENU ENGINEERING AS AN ANALYTICAL METHOD

## 1.1 What the method actually is

Menu engineering was introduced in 1982 by Michael L. Kasavana and Donald I. Smith in *Menu Engineering: A
Practical Guide to Menu Analysis* (source: https://en.wikipedia.org/wiki/Menu_engineering, retrieved
2026-07-29). It plots every menu line on two axes and nothing else:

| Axis | Name | What it measures | What it deliberately ignores |
|---|---|---|---|
| Vertical | Popularity / menu mix % | Units sold of item ÷ total units sold | Revenue, price, ticket size |
| Horizontal | Contribution margin (CM) in currency | Selling price − plate food cost | Labour, rent, prep time, waste, %-margin |

The method is a *cash* method, not a percentage method. This is the single most important thing to understand
about it: a 12% food-cost drink and a 44% food-cost bowl of bún bò can both be correct, because the bowl throws
off 26,000 VND of cash and the drink throws off 2,300 VND. A food-cost-percentage view would tell you to sell
more tea. That is the whole reason Kasavana & Smith exists.

## 1.2 The exact arithmetic

```
Plate cost (item food cost)   = sum of costed ingredient weights per portion, incl. garnish + side + sauce
Contribution margin (CM)      = selling price − plate cost                          [in currency, not %]
Total CM for an item          = item CM × units sold
Menu total CM                 = Σ (item CM × units sold)
Menu mix % (MM%) for an item  = (units sold of item ÷ total units sold) × 100

Popularity threshold          = (1 ÷ number of menu items) × 0.70
                              (source: https://www.getmeez.com/blog/menu-engineering-matrix,
                               retrieved 2026-07-29)

Average CM (Kasavana & Smith) = Menu total CM ÷ total units sold           ← WEIGHTED
Average CM (many blogs 2020s) = Σ(item CM) ÷ number of items               ← SIMPLE / UNWEIGHTED
```

Classification: an item is HIGH popularity if `MM% > popularity threshold`, HIGH profitability if
`item CM ≥ average CM`.

| MM% | CM | Quadrant |
|---|---|---|
| High | High | **Star** |
| High | Low | **Plowhorse** |
| Low | High | **Puzzle** |
| Low | Low | **Dog** |

## 1.3 Why 0.70, and what the multiplier really does

On a 10-item menu a perfectly even distribution would give each item 10%. Almost no real menu is even, so a
10% bar would classify most of the menu as unpopular. The 0.70 factor lowers the bar to 7% so the threshold
reflects realistic dispersion rather than a mathematical fiction (source:
https://www.getmeez.com/blog/menu-engineering-matrix, retrieved 2026-07-29). The 2022 DETUROPE application of
the model to a Hungarian restaurant menu uses the same rule — 70% of the average menu-mix percentage
(source: https://www.deturope.eu/pdfs/det/2022/01/06.pdf, retrieved 2026-07-29).

Consequence you must state to the user: **0.70 is a convention, not a law.** It is a sensitivity dial.

| Multiplier | Effect | Use when |
|---|---|---|
| 0.50 | Very forgiving; almost everything is "popular" | Long tail menu, >30 items, you only want to find true Dogs |
| **0.70** | Standard | Default. Use unless you have a reason |
| 0.85 | Strict | Short menu (≤8 items), you want to force ranking |
| 1.00 | Pure average | Only when sales really are near-uniform (set menus, fixed combos) |

## 1.4 The disagreement practitioners never flag: weighted vs simple average CM

Kasavana & Smith's original model computes the CM axis as **total weighted contribution margin ÷ total units
sold** (source: https://digitalcommons.fiu.edu/cgi/viewcontent.cgi?article=1453&context=hospitalityreview via
search result, retrieved 2026-07-29 — the FIU *Hospitality Review* "Menu Analysis: A Review of Techniques and
Approaches" is the review that documents this; the PDF returned 403 on direct fetch, so the formula is
confirmed from the indexed abstract text, not the full paper).

A large share of 2020s restaurant-software blogs instead take the **unweighted mean of item CMs** (source:
https://www.getmeez.com/blog/menu-engineering-matrix, retrieved 2026-07-29 — worked example: item CMs of
$6…$15 summed to $105 and divided by 10 items = $10.50 threshold).

These are not the same number and they move in opposite directions:

- **Weighted** average is pulled DOWN by high-volume, low-CM lines (tea, rice, bread). Result: more food items
  land in the "high CM" half, fewer Dogs.
- **Simple** average is pulled UP by low-volume, high-CM lines (one expensive set menu nobody orders). Result:
  more items land in the "low CM" half, more Dogs.

Rule for this skill: **use weighted (Kasavana & Smith original) and say which you used.** If you switch method
mid-analysis, items change quadrant with no change in the business. Always print the threshold value next to
the table.

## 1.5 The scope trap: what goes into the matrix

More items flip quadrant from *matrix scope* than from *threshold multiplier*. Rules:

| Line type | Put in the same matrix as mains? | Correct treatment |
|---|---|---|
| Mains / bowls | Yes | This is the matrix |
| Add-ons that cannot be ordered alone (thêm chả, thêm giò) | **No** | Attach rate = add-on units ÷ bowls sold |
| Drinks | **No** — separate matrix | Attach rate + CM per bowl-occasion |
| Desserts | **No** — separate matrix | Attach rate |
| Combos / sets | Only if the components are decremented, else double counting | Model as its own line with its own plate cost |
| Off-menu / staff meal / delivery-only SKU | No | Separate channel P&L |

Why: menu mix % has *total units sold* in the denominator. A 3,000 VND glass of iced tea attached to 88% of
bowls inflates the denominator and deflates the weighted average CM, which silently reclassifies real food
items. Section 1.6 demonstrates this with a flip.

## 1.6 Worked example — 9-line bún bò shop, HCMC, one month

Assumptions (stated so the user can replace them): ~180 bowls/day, 6:00–13:00, 30 days.
Price band is realistic: bún bò in HCMC observed at 25,000–70,000 VND/bowl, with one shop at 35,000 for
*tô thường* and 60,000 for *tô đặc biệt* (source: https://vinwonders.com/vi/wonderpedia/news/bun-bo-hue-ngon-o-sai-gon/
and https://ghiensaigon.com/bun-bo-binh-thanh/, retrieved 2026-07-29).

### Step 1 — raw table

| # | Item | Price VND | Plate cost VND | CM VND | Units/mo |
|---|---|---:|---:|---:|---:|
| 1 | Bún bò thường | 45,000 | 19,000 | 26,000 | 2,340 |
| 2 | Bún bò đặc biệt | 65,000 | 30,500 | 34,500 | 1,120 |
| 3 | Bún bò chay | 42,000 | 13,000 | 29,000 | 160 |
| 4 | Bún bò tô nhỏ | 35,000 | 15,500 | 19,500 | 410 |
| 5 | Thêm chả cua (add-on) | 15,000 | 6,500 | 8,500 | 880 |
| 6 | Thêm giò heo (add-on) | 20,000 | 11,000 | 9,000 | 520 |
| 7 | Trà đá / trà nóng | 3,000 | 700 | 2,300 | 2,900 |
| 8 | Nước sâm / nước mía | 15,000 | 4,500 | 10,500 | 640 |
| 9 | Bánh flan | 12,000 | 4,000 | 8,000 | 300 |

Total units = 9,270. Menu total CM = **140,065,000 VND/month**.

### Step 2 — the WRONG matrix (everything in one pot, 9 items)

Popularity threshold = (1 ÷ 9) × 0.70 = **7.78%**
Weighted average CM = 140,065,000 ÷ 9,270 = **15,110 VND**
(Simple average would be 147,300 ÷ 9 = 16,367 VND — 8.3% higher bar, for the same business.)

| # | Item | MM% | CM VND | Quadrant |
|---|---|---:|---:|---|
| 1 | Bún bò thường | 25.24 | 26,000 | Star |
| 2 | Bún bò đặc biệt | 12.08 | 34,500 | Star |
| 3 | Bún bò chay | 1.73 | 29,000 | Puzzle |
| 4 | Bún bò tô nhỏ | 4.42 | 19,500 | **Puzzle** |
| 5 | Thêm chả cua | 9.49 | 8,500 | Plowhorse |
| 6 | Thêm giò heo | 5.61 | 9,000 | Dog |
| 7 | Trà đá | 31.28 | 2,300 | Plowhorse |
| 8 | Nước sâm/mía | 6.90 | 10,500 | Dog |
| 9 | Bánh flan | 3.24 | 8,000 | Dog |

### Step 3 — the RIGHT matrix (food-only, items 1–6 → then split add-ons out)

Food-only, 6 items, total units 5,430:
Popularity threshold = (1 ÷ 6) × 0.70 = **11.67%**
Food-only menu CM = 124,275,000 → weighted average CM = 124,275,000 ÷ 5,430 = **22,887 VND**

| # | Item | MM% | CM VND | Quadrant |
|---|---|---:|---:|---|
| 1 | Bún bò thường | 43.09 | 26,000 | Star |
| 2 | Bún bò đặc biệt | 20.63 | 34,500 | Star |
| 3 | Bún bò chay | 2.95 | 29,000 | Puzzle |
| 4 | Bún bò tô nhỏ | 7.55 | 19,500 | **Dog** ← flipped from Puzzle |
| 5 | Thêm chả cua | 16.21 | 8,500 | Plowhorse |
| 6 | Thêm giò heo | 9.58 | 9,000 | Dog |

**The flip is the lesson.** *Tô nhỏ* looked like a Puzzle (worth promoting) only because 2,900 glasses of
3,000 VND tea dragged the average CM from 22,887 down to 15,110. On the correct food-only matrix it is a Dog
and the correct move is to delete it or re-price it, not to promote it.

### Step 4 — the metrics that beat "average CM per unit"

```
Bowls sold (customer occasions) = 2,340 + 1,120 + 160 + 410 = 4,030
CM per bowl-occasion            = 140,065,000 ÷ 4,030 = 34,756 VND   ← the real KPI
Attach rate, chả cua            = 880 ÷ 4,030 = 21.8%
Attach rate, giò heo            = 520 ÷ 4,030 = 12.9%
Attach rate, any drink          = (2,900 + 640) ÷ 4,030 = 87.8%
Attach rate, dessert            = 300 ÷ 4,030 =  7.4%
Average add-on spend per bowl   = (8,500×880 + 9,000×520) ÷ 4,030 = 3,017 VND
```

### Step 5 — the decision-changing arithmetic

Two candidate +2,000 VND price moves, same nominal increase:

| Move | ΔCM/month | Per bowl-occasion | Customer visibility |
|---|---:|---:|---|
| Trà đá 3,000 → 5,000 (87.8% attach, 2,900 units) | +5,800,000 | +1,439 VND (+4.1%) | Low — nobody price-shops iced tea |
| Bún bò thường 45,000 → 47,000 (2,340 units) | +4,680,000 | +1,161 VND (+3.3%) | High — this is the headline price |

**The invisible 2,000 VND on the 88%-attach drink out-earns the visible 2,000 VND on the hero bowl and costs
less goodwill.** This is the kind of output the skill should produce instead of "raise prices carefully."

## 1.7 What to DO with each quadrant — specific moves, not adjectives

| Quadrant | Diagnosis | Do this | Do NOT |
|---|---|---|---|
| **Star** | High MM%, high CM | Lock the spec (gram weights, broth Brix, meat cut, bowl size). Photograph it. Put it first in its category. Test a +3–5% price rise on the *highest-CM* Star only, and watch MM% for 14 days; abandon if MM% drops more than 10% relative. Never discount it. | Never run it as a promo item; never let a new cook improvise it |
| **Plowhorse** | High MM%, low CM | 1) Attack plate cost first: re-portion to the nearest 5g, re-spec the cheapest 20% of ingredients by cost, cut garnish waste. 2) Then bundle it into a set where the set CM ≥ average CM. 3) Then raise price in the smallest local increment (VN: 2,000–5,000 VND). 4) Move it *off* the first line of the category so a Star takes primacy. | Do not raise price before fixing yield — a Plowhorse is the item most likely to have a price-elastic crowd |
| **Puzzle** | Low MM%, high CM | 1) Re-name with a concrete sensory/provenance detail (see §2.7 caveats). 2) Move to position 1 or last in its category (primacy/recency, §2.5). 3) Make it the stated default: "Lần đầu ăn? Gọi món này." 4) Add a decoy tier above it (§2.4). 5) Server script: one sentence, spoken at order-taking. If MM% has not crossed the threshold after 30 days at 2 interventions, demote to Dog. | Do not simply add a photo and call it done; do not lower the price (that destroys the only reason it is a Puzzle) |
| **Dog** | Low MM%, low CM | Delete, unless it is one of: (a) a dietary gate — the only veg/child/no-pork option, without which a whole table walks; (b) a prep by-product with near-zero marginal cost; (c) a required item for a platform/category listing. If kept for reason (a), re-price to at least average CM and accept low MM%. | Do not keep a Dog "for variety". Each extra line costs prep, storage, waste, print area, and comparability |

## 1.8 Known limitations of the method (say these out loud)

1. **Ignores labour and prep time.** A 34,500 VND CM bowl needing 4 minutes of assembly at peak may be worse
   than a 26,000 VND bowl needing 90 seconds. Fix: add a third column, CM per minute of station time, and
   re-rank Stars by it.
2. **Ignores substitution.** Deleting a Dog does not delete its revenue; some of it migrates. There is a
   published extension addressing exactly this — "Menu engineering re-engineered: Accounting for menu item
   substitutes in pricing and menu placement decisions" (source:
   https://www.sciencedirect.com/science/article/abs/pii/S0278431920300566, retrieved 2026-07-29;
   abstract-level only, full text not accessed — [UNVERIFIED: exact model specification]).
3. **Ignores the guest's basket.** A Dog that reliably brings a group of four is not a Dog.
4. **Needs ≥30 days and ≥100 units per line** before a quadrant call is trustworthy. Below that, MM% is noise.
5. **Cannibalisation by portion tiers**: three sizes of the same dish are not three items. Model tiers as one
   item with a mix, plus a separate "tier mix" analysis.
6. **Alternative frameworks exist** and disagree: Miller's food-cost-% matrix, Pavesic's cost/margin analysis
   (weighted food-cost % × CM), Uman, and Hayes–Huffman goal-value analysis are all reviewed in the FIU
   *Hospitality Review* menu-analysis review (source:
   https://digitalcommons.fiu.edu/cgi/viewcontent.cgi?article=1453&context=hospitalityreview, retrieved
   2026-07-29 — [UNVERIFIED: individual formulas, PDF returned 403; do not state Pavesic's exact axes without
   re-checking]). The practical point: Miller's %-based method and Kasavana & Smith's cash method will
   classify the same item differently, and the cash method is the correct one for pricing decisions.

---

# PART 2 — MENU PSYCHOLOGY: AN EVIDENCE AUDIT

## 2.0 Grading scale used below

| Grade | Meaning |
|---|---|
| **A** | Multiple studies or a meta-analysis; effect direction stable |
| **B** | One peer-reviewed primary study with a real behavioural measure (checks, orders, eye-tracking) |
| **C** | Mechanism is well-established in general psychology, but no restaurant-specific primary study found |
| **D** | Actively disconfirmed by primary research; still repeated by the industry |
| **E** | A specific number circulating in vendor marketing with no traceable primary source. Treat as fabricated until proven otherwise |

## 2.1 Master audit table

| Claim as usually stated | Grade | What the primary evidence actually is |
|---|---|---|
| Removing the currency symbol raises spend | **B** | Numeral-only prices ("20") produced significantly higher checks than "$20" or "twenty dollars": +$5.55, ≈8%, at one upscale-casual lunch service. No difference between the symbol and the spelled-out word (source: https://news.cornell.edu/stories/2009/12/beware-menus-dont-use-dollar-signs, retrieved 2026-07-29) |
| Never use a right-aligned price column or dotted leaders | **C** | Practitioner consensus, near-universal in menu-design writing. **No primary experiment found isolating column alignment or leader dots.** The "8%" figure repeatedly attached to this rule is borrowed from the currency-symbol study above, which did not manipulate alignment |
| 9-endings signal value; 0-endings signal quality | **B** | Quick-service menus were perceived as more value-oriented with "9" endings; fine-dining menus as higher quality with "0" endings (source: https://journals.sagepub.com/doi/10.1177/0010880401421003, retrieved 2026-07-29) |
| Price presentation changes perceived quality and value, and differs by segment | **B** | Parsa & Njite, *Journal of Hospitality & Tourism Research* 28(3):263–280, 2004 (source: https://www.researchgate.net/publication/247752613_Psychobiology_of_Price_Presentation_An_Experimental_Analysis_of_Restaurant_Menus, retrieved 2026-07-29) |
| "Parsa & Njite found anchoring lifts check value 6.8%" | **E** | This figure appears in a supplier blog (source: https://laneequipment.com/resources/blog/decoy-dishes-and-anchor-pricing-menu-engineering-psychology-explained, retrieved 2026-07-29). It is **not** in the abstract of the 2004 paper. Do not use |
| A decoy option pushes guests to the pricier bundle | **A/B** | Bujisic, Bujisic, Parsa, Bilgihan & Li, *International Hospitality Review* 40(1):145–158; N = 463 across four studies. Restaurant-bundle results: pilot 65% → 95.1%; Study 2 44.7% → 71.4%; Study 3 82% → 93.1% bundle/premium selection with a dominated mid option present. Larger price gaps produced stronger effects (source: https://www.emerald.com/ihr/article/doi/10.1108/IHR-04-2024-0023/1249855/Anchoring-decisions-the-role-of-decoy-pricing-in, retrieved 2026-07-29). [Publication year returned as 2026 by the fetch — verify before printing a year] |
| First/last item in a list sells more | **A** | Items at the beginning or end of a category list were **up to twice as popular** as the same items placed mid-list, in a lab study and a real-restaurant study (source: https://www.cambridge.org/core/journals/judgment-and-decision-making/article/nudge-to-nobesity-ii-menu-positions-influence-food-orders/8CBE6FB7505ECCD31C09157A74007EC9, retrieved 2026-07-29) |
| Position effect depends on layout axis | **B** | Middle options preferred in a **horizontal** display; edge options preferred in a **vertical** display. Held for food and beverage, and for both even and odd option counts. Kim, Hwang, Park, Lee & Park, *Cornell Hospitality Quarterly* 60(2), 2019 (source: https://journals.sagepub.com/doi/abs/10.1177/1938965518778234, retrieved 2026-07-29) |
| The "golden triangle" / "sweet spot" | **D** | Eye-tracking found guests read menus **sequentially, like a book**, with no statistically significant sweet spot; one region behaved as a *sour spot* (restaurant info + salads). Yang, *International Journal of Hospitality Management* 31(3), 2012 (sources: https://www.eurekalert.org/news-releases/829582 and https://www.sciencedirect.com/science/article/abs/pii/S0278431911002015, retrieved 2026-07-29). Yang called the golden triangle "a bad rumor that just kept perpetuating" and said the industry had been "piggybacking off past research" (source: https://www.restaurant-hospitality.com/how/menu-engineering-gets-makeover, retrieved 2026-07-29) |
| The golden triangle came from a 1987 Gallup study | **C** | Attributed in secondary coverage (source: https://www.kyivworkshop.com/blogs/news/superior-techniques-for-creating-menus, retrieved 2026-07-29). [UNVERIFIED — original Gallup report not located. Do not cite as if primary] |
| Price bracketing (wide spread pulls guests up) | **C** | Widely described as anchoring/compromise-effect in practice (source: https://www.tastingtable.com/1677131/meaning-of-bracketing-at-restaurant-spending-more-money/, retrieved 2026-07-29). **No restaurant-specific primary study found.** The nearest real evidence is the decoy paper above, which is bundle-level, not spread-level |
| Wine lists sorted ascending by price push guests to cheaper wines | **B** | Ordering wine menus by ascending price led consumers to choose lower-priced wines more often; sorting by sensory description shifted variety choice and made guests use descriptions, food-match and award info (source: https://www.researchgate.net/publication/267547451_How_does_item_order_and_other_information_impact_wine_menu_choice, retrieved 2026-07-29 — abstract level) |
| Descriptive labels raise sales 27% | **B-with-a-red-flag** | See §2.7. The number is real in the paper, the paper is not retracted, but the senior author was found by Cornell to have committed academic misconduct and has 18 retractions |
| More than 7 items per category overwhelms guests | **C→B** | The "7" is a consultant heuristic (source: https://www.mentalfloss.com/article/63443/8-psychological-tricks-restaurant-menus, retrieved 2026-07-29). The nearest primary support is Johns, Edwards & Hartwell, "Menu Choice: Satisfaction or Overload?", *Journal of Culinary Science & Technology* 11(3), 2013, reported ideal ≈ **6 choices for quick service, 7–10 for fine dining** (source: https://www.tandfonline.com/doi/abs/10.1080/15428052.2013.798564, retrieved 2026-07-29 — [UNVERIFIED: sample size and statistics; full text not accessed]) |
| Choice overload is a robust law | **D** | Meta-analysis of 63 conditions / 50 experiments / N = 5,036 found a **mean effect size of virtually zero** with large between-study variance (source: https://academic.oup.com/jcr/article-abstract/37/3/409/1827647, retrieved 2026-07-29) |
| Choice overload happens under specific conditions | **A** | 99 observations, N = 7,202, four moderators: **choice set complexity, decision task difficulty, preference uncertainty, decision goal**. Chernev, Böckenholt & Goodman, *Journal of Consumer Psychology* 25:333–358 (source: https://myscp.onlinelibrary.wiley.com/doi/abs/10.1016/j.jcps.2014.08.002, retrieved 2026-07-29) |
| Photos raise item sales ~30% | **E** | Traced only to consultant/vendor content. Do not use |
| "Cornell's 2014 study found +6.5% sales per item with photos" | **E** | Appears on an AI menu-photo vendor site (source: https://www.menuphotoai.com/guides/food-photography-science-research, retrieved 2026-07-29). No such Cornell study located. Treat as fabricated |
| Photos raise attention and purchase intention | **B (café context)** | Kim et al., *International Journal of Tourism Research*, 2025, eye-tracking on café menus: photographs give vivid sensory cues, increase attention and purchase intention (source: https://onlinelibrary.wiley.com/doi/full/10.1002/jtr.70133, retrieved 2026-07-29 — paywalled at 402; abstract-level only, **no effect sizes verified**) |
| Colour changes where the eye lands first | **B (weak)** | Gaze plots suggested colour shifted the *first 10 seconds*: centre-first in the colour version, top-left-first in the non-colour version; heat maps showed middle and upper-left viewed most regardless. Smith, Guliuzo, Benedict & Chaparro, 2019 (source: https://journals.sagepub.com/doi/10.1177/1071181319631347, retrieved 2026-07-29) |
| Guests prefer paper menus to QR | **B** | Technomic survey, n = 1,000, May 2022: 88% prefer paper at sit-down restaurants; 66% dislike pulling out a phone on sitting down; 55% find QR menus hard to read/browse; 50% say QR lessens the experience; 67% agree QR is more sanitary (source: https://www.restaurantbusinessonline.com/technology/customers-really-dont-qr-code-menus via indexed content, retrieved 2026-07-29 — page returned 403 on direct fetch) |
| "78% favour QR menus" / "67% prefer scanning" | **E** | Both appear only in QR-menu vendor blogs with no named instrument (source: https://www.menutiger.com/blog/qr-code-menu-forecast, retrieved 2026-07-29). Contradicts the traceable Technomic figure. Do not use |

## 2.2 Price presentation — what to actually do, and where it breaks in VND

The verified mechanism is *salience of the pain of paying*: "references to dollars, in words or symbol,
reminds people of the 'pain of paying'" (source:
https://news.cornell.edu/stories/2009/12/beware-menus-dont-use-dollar-signs, retrieved 2026-07-29).

Everything below inherits that mechanism, but **the study was conducted in USD with a prefix "$" at one
upscale-casual lunch service.** Vietnamese prices carry a *suffix* ("đ", "VNĐ", "k") and are written in
thousands. The mechanism plausibly transfers; the specific format has not been tested in VND.
[UNVERIFIED — no VND price-format experiment located. Do not tell a user "removing đ will raise your check 8%".]

| Format | Reads as | Risk | Use for |
|---|---|---|---|
| `45.000đ` | Default Vietnamese retail | None; zero lift | Local quán, delivery apps, anything price-led |
| `45.000` | Slightly designed | None | Modern casual, chains |
| `45k` | Casual, young, street | Reads cheap; wrong for premium | Street food, bubble tea, late-night |
| `45` + header "Đơn vị: 1.000đ" | Editorial / restrained | Older or first-time guests can misread; must have the unit note **above the first price on every panel**, not once on a cover | Premium/editorial only |
| `Bốn mươi lăm nghìn` | Precious, hard to scan | Do not use. The USD study found spelled-out prices performed no better than the symbol | Never |

Layout rules, with honest grading:

| Rule | Grade | When it matters most | When to ignore it |
|---|---|---|---|
| Price as plain text at the end of the description, same size and weight as the item name | C | Price spread within a category > 2.0× | Spread < 1.5× (a bún bò shop at 35–65k is 1.86×; borderline) |
| No dotted leaders | C | Always — they add ink, cost legibility, and serve no reader need | Never worth keeping |
| No right-aligned price column | C | Wide-spread menus, upsell-driven menus | **A narrow-spread quán menu.** Local guests *expect* a scannable price column and it reduces order-taking friction. Removing it to chase an 8% figure from a different market is cargo-culting |
| Price never larger or bolder than the dish name | C | Always | Never — an oversized price is the loudest signal that the menu is about money |
| Never repeat the currency unit on every line | C | Always | Delivery platforms render currency for you |

## 2.3 Charm vs round pricing in a restaurant

Verified split: `9`-endings → value perception in quick service; `0`-endings → quality perception in fine
dining (source: https://journals.sagepub.com/doi/10.1177/0010880401421003, retrieved 2026-07-29). Managers'
own beliefs about price endings were studied separately in *Cornell Hospitality Quarterly* (Schindler, Parsa &
Naipaul, 2011, source: https://doi.org/10.1177/1938965511421168, retrieved 2026-07-29 — [UNVERIFIED: findings,
abstract not accessed]).

In VND the "ending" is the **thousands digit**, not the units digit. Observed real ladders sit on 5,000 steps
(35 / 40 / 45 / 50 / 55 / 60 / 65) — see the pricing observed in §1.6 sources.

| VND ending | Reads as | Segment fit |
|---|---|---|
| `x5.000`, `x0.000` | Normal, honest, local | Quán, casual, premium — the default |
| `x9.000` (49.000, 59.000) | Promotional, chain, imported tactic | Fast-casual chains, delivery-only, LTO |
| `x8.000` (48.000) | "Calculated" — reads like a spreadsheet leaked | Avoid |
| `x2.000`, `x7.000` | Reads like a cost pass-through | Avoid on the hero item; acceptable on add-ons |
| Any non-multiple of 1,000 | Cash-handling failure | Never — VN street trade rounds to 1,000, often 5,000 |

Decision rule: **premium and editorial menus round to 0 or 5; promotional and chain menus may use 9; nothing
uses 8.**

## 2.4 Decoys and anchors — the one high-confidence lever

The strongest restaurant-specific finding in this dossier. Add a **dominated** option (clearly worse value at
a nearby price) and selection of the target option rises sharply: 44.7% → 71.4% in the cleanest of the three
restaurant studies (source: https://www.emerald.com/ihr/article/doi/10.1108/IHR-04-2024-0023/1249855/Anchoring-decisions-the-role-of-decoy-pricing-in,
retrieved 2026-07-29). Effect strengthened as the price gap widened.

Construction recipe for a 3-tier portion ladder:

```
Tier 1 (entry / reference)  = P1
Tier 2 (DECOY, dominated)   = P1 + Δ1, adds little visible value    ← must look poor value
Tier 3 (TARGET)             = P1 + Δ1 + Δ2, where Δ2 ≤ Δ1 and the added value is obvious
Design constraint: (value added T2→T3) / (Δ2) must visibly exceed (value added T1→T2) / (Δ1)
```

Bún bò instance, real prices:

| Tier | Item | Price | What you get | Role |
|---|---|---:|---|---|
| 1 | Bún bò thường | 45,000 | nạm + chả | Reference |
| 2 | Bún bò thêm chả | 55,000 | + 1 viên chả cua | **Decoy** — +10,000 for one item |
| 3 | Bún bò đặc biệt | 65,000 | + chả cua + giò heo + huyết + mọc | **Target** — +10,000 for four items |

Ethical line for this skill: a decoy must be a **real, orderable, honestly described item**. Do not invent a
phantom tier, do not list an item you will not serve, do not misdescribe portions. The mechanism works because
the comparison is true, not because the guest is deceived.

## 2.5 Sequencing and position — what actually holds

1. **Guests read sequentially, top to bottom, like a book** (Yang 2012). Therefore *reading order is layout
   order*. There is no hidden hot zone to exploit.
2. **Primacy and recency are the real effects.** First and last in a category list can be up to 2× the
   mid-list rate (Dayan & Bar-Hillel 2011). Practical: each category has exactly two premium slots — line 1
   and the final line.
3. **The axis flips the effect.** Vertical list → edges win. Horizontal row (menu board, tab strip, app
   carousel) → **middle** wins (Kim et al. 2019). This is decision-changing for menu boards and delivery-app
   category strips, where the layout is horizontal.
4. **Ascending price order pushes guests down-market** (wine-list finding). Do not sort a category by
   ascending price unless you want the cheapest item.

Placement decision table:

| Layout | Where the target item goes | Where the Dog/decoy goes |
|---|---|---|
| Vertical list, printed | Line 1, or the final line | Positions 3–4 of 6 (mid-list) |
| Horizontal row (board, app strip, table tent) | Centre position | Far left / far right |
| Two-page spread | Top of the left page (reading start), and last line of the right page | Middle of the right page (Yang's "sour spot" region) |
| Category order on a page | First category = highest-CM category | Low-CM categories last |
| Sort within a category | By CM descending, or by narrative (light → rich) | Never by ascending price |

## 2.6 Item count and choice overload — the honest version

Three facts that must be stated together:

- **Choice overload is not a general law.** Mean effect ≈ zero across 63 conditions (Scheibehenne, Greifeneder
  & Todd 2010).
- **It is real under four conditions**: set complexity, task difficulty, preference uncertainty, weak decision
  goal (Chernev, Böckenholt & Goodman 2015).
- **Hick's law is logarithmic**: `RT = a + b·log₂(n + 1)`. Going from 4 to 8 options adds
  `b·(log₂9 − log₂5) = 0.85b`. Going from 8 to 17 adds the *same* 0.85b. The marginal cost of an extra item
  falls as the list grows. Item count alone is a weak lever.
- **Miller's "7±2" does not apply to menus.** Miller (1956) measured immediate serial recall of chunks from
  *memory*; Cowan's later work revised the figure to ≈4. A menu is *visible* — there is no recall load. Anyone
  who justifies "7 items per category" with Miller is misapplying the source. The defensible number comes from
  Johns et al. 2013: ≈6 for quick service, 7–10 for fine dining.

Therefore the operational rule is **not** "cut items". It is: *make the four moderators go away.*

| Moderator | Menu lever | Concrete spec |
|---|---|---|
| Choice set complexity | One axis of difference per category | Portion tiers differ only by toppings; do not also vary noodle type, broth and spice in the same tier ladder |
| Decision task difficulty | Remove time pressure | Wall board readable from the queue; QR menu browsable before seating; A-board with the 3-line core menu at the door |
| Preference uncertainty | A stated default | One line per category marked "Nên gọi / Recommended" — exactly one, never three |
| Weak decision goal | A first-visit path | "Lần đầu đến? → Bún bò thường + trà đá — 48.000" as a named set |

Item-count decision table:

| Situation | Lines per category | Total lines | Rationale |
|---|---:|---:|---|
| Single-dish specialist (bún bò shop) | 3–4 bowls | 8–12 incl. drinks/add-ons | Tier ladder + decoy needs exactly 3; a 4th is the dietary gate |
| Quick service / fast-casual | 5–6 | 15–25 | Johns et al. QSR figure |
| Casual dining | 6–8 | 30–45 | |
| Fine dining à la carte | 5–7 | 18–25 | Johns et al. fine-dining figure, lower bound |
| Delivery-platform listing | 4–8 per category | 20–35 | Scroll depth, not overload, is the constraint (§6) |
| Tourist-facing | 6–10 with photos | 25–40 | Unfamiliarity raises preference uncertainty; more visual anchors help |

## 2.7 Descriptive naming — the effect size and the reason to distrust it

The widely-cited numbers: descriptively labelled items sold **27% more** than the same items with plain names
over a six-week study; guests rated them higher on quality and value; 56% chose the descriptively labelled
item (source: https://journals.sagepub.com/doi/10.1177/0010880401426008 and
https://www.academia.edu/14160365/Descriptive_Menu_Labels_Effect_on_Sales, retrieved 2026-07-29 —
Wansink, Painter & van Ittersum, *Cornell Hotel and Restaurant Administration Quarterly* 42(6), 2001).

Why the skill must caveat this every single time it is used:

- The paper itself **is not retracted** as of retrieval (source:
  https://journals.sagepub.com/doi/10.1177/0010880401426008, retrieved 2026-07-29).
- But the senior author was found by a Cornell faculty committee to have committed academic misconduct,
  including "misreporting of research data, problematic statistical techniques, failure to properly document
  and preserve research results, and inappropriate authorship", resigned in 2018, and has **18 retractions**
  in the Retraction Watch database (sources:
  https://www.science.org/content/article/cornell-nutrition-scientist-resigns-after-retractions-and-research-misconduct-finding
  and https://retractionwatch.com/2022/05/31/cornell-food-marketing-researcher-who-retired-after-misconduct-finding-is-publishing-again/,
  retrieved 2026-07-29).
- **No independent replication of the 27% figure was located.** [UNVERIFIED — needs a pre-registered
  replication before the number is quoted to a client.]

How to phrase it in output: *"Descriptive naming is standard practice and the direction of effect is
plausible; the frequently quoted +27% comes from a 2001 paper whose senior author was later found to have
committed research misconduct, so treat the size of the effect as unknown."*

What to do regardless of effect size — because these are truthful information, not tricks:

| Naming move | Spec | Bún bò example |
|---|---|---|
| Sensory | One texture + one temperature/heat word, ≤4 words added | "nước dùng đậm, cay vừa" |
| Provenance | Named place or supplier, only if true | "sả và ớt bột Huế" |
| Ingredient specificity | Cut, part, or grade, only if true | "nạm bò, giò heo khoanh, chả cua tự làm" |
| Process | The step that costs you time | "hầm xương 8 tiếng" |
| Nostalgic / family | Only if the person exists | "công thức của mẹ" — never invent a grandmother |
| Portion truth | Grams or count | "2 viên chả cua" not "nhiều chả" |

Hard limits: **≤ 14 Vietnamese words / ≤ 90 characters per description** on a printed line (measured against
the 32-character item-name budget in §4.4), and **zero unverifiable claims**. If the user cannot confirm
"8-hour broth", the line does not ship.

## 2.8 Dietary and spice markers

| Marker | Spec | Why |
|---|---|---|
| Spice | 3 levels max, one glyph repeated: `◦ / ◦◦ / ◦◦◦` or a chilli icon ×1–3, with a legend once per panel | More than 3 levels is unenforceable in a kitchen |
| Vegetarian | Vietnamese `chay` is the load-bearing word — clearer than a leaf icon to local guests. Use word + icon for tourists | `chay` in Vietnam usually implies no allium for Buddhist guests; if your dish uses onion/garlic, label it `thuần chay (có hành/tỏi)` or you will get complaints |
| No pork / no beef | Explicit word, not an icon | Religious and dietary requirement; icons are ambiguous |
| Allergens | List the big ones in plain words in a footer: đậu phộng, hải sản, mè, sữa, gluten | No verified Vietnamese regulation mandates allergen disclosure on *restaurant menus* — the labelling regime (Decree 43/2017/ND-CP, amended by Decree 111/2021/ND-CP) targets prepackaged goods (source: https://www.lexology.com/library/detail.aspx?g=4bcf1a55-7511-485a-b285-75d82488eb1a, retrieved 2026-07-29). [UNVERIFIED — needs a Vietnamese food-law check before making a compliance claim] |
| Calories / nutrition | Do not add unless the user has lab or software-derived values | Invented numbers are a liability |
