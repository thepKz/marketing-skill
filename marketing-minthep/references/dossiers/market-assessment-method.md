# Market Assessment Method

## Scope

An executable method for assessing a market for one small business, producing a written assessment where every number is traceable to a stated assumption or a cited source. Covers honest sizing (TAM/SAM/SOM, top-down and bottom-up with full arithmetic), demand evidence and its biases, competitive structure, customer evidence, segmentation and beachhead, category timing, pricing and unit-economics floors, risk scan, and a strict output contract. Two running examples: one bún bò restaurant in Da Nang, Vietnam, and a DTC skincare serum sold in Vietnam. Excludes: brand strategy, creative execution, media buying mechanics (other reference files).

---

## 0. The failure mode this file exists to prevent

CB Insights' post-mortem analysis is the most-cited number in this space: 42% of failed startups shared "no market need", ahead of "ran out of cash" (29%) and "outcompeted" (19%), based on 110+ founder post-mortems 2014–2021, later extended with 431 VC-backed shutdowns since 2023 (source: https://segmentos.io/blog/why-startups-fail, retrieved 2026-07-29). Treat the 42% as directional only: it is a self-selected sample of VC-backed failures with founder-narrative bias, and it says nothing about the base rate for a noodle shop. [UNVERIFIED - the primary CB Insights report page was not retrieved; needs a direct cbinsights.com citation and the exact sample definition before quoting the figure in client-facing work.]

The operational lesson is not "markets fail" but this: **the information needed to avoid the failure almost always existed before the money was spent, and was not gathered because gathering it is boring and citing a market report is fast.** Everything below is the boring version.

Three rules that govern the whole method:

1. **No number without a chain.** Every figure is either measured, cited, or derived from figures that are. A number with no chain is deleted, not softened.
2. **No point estimate without a range in the same sentence.** "About VND 34bn" is a lie. "VND 34bn (range 15–62bn), driven by breakfast-out share and occasion share" is an estimate.
3. **Bottom-up is the answer; top-down is the sanity check.** Never the reverse. Investors and lenders discount top-down on sight because it cannot be falsified.

---

## 1. TAM / SAM / SOM: the definitions people actually get wrong

| Term | Correct definition | The discriminating test | Common wrong version |
|---|---|---|---|
| TAM | Annual revenue if you served 100% of everyone with the need, in every geography, with unlimited capacity, at your price | "Would a buyer here physically be able to buy from anyone offering this?" | Industry revenue from a syndicated report, unfiltered |
| SAM | The subset of TAM you could serve **with your current business model, geography, channel, language, price point and legal permissions** | "If they wanted to buy today, could I actually take their money?" | A fixed % of TAM (e.g. "SAM is 10% of TAM") |
| SOM | The subset of SAM you can win in a stated window (usually 12 months), constrained by capacity, capital, acquisition engine and competition | "Is this number the *lower* of my capacity ceiling and my defensible share?" | TAM × 1% |
| Beachhead SAM | The one segment where you can be #1 within 12–24 months | Aulet's three tests (see §8) | "Our first target market" with no exit criteria |

Definitions of TAM/SAM/SOM above are consistent with mainstream practitioner usage (source: https://hginsights.com/blog/tam-sam-som-the-complete-guide-to-market-sizing/, retrieved 2026-07-29; source: https://sea.ub-speeda.com/asean-insights/resource-center/market-sizing/, retrieved 2026-07-29).

### The eight named errors

| # | Error | Why it is fatal | Fix |
|---|---|---|---|
| E1 | **Vanity TAM** — citing the parent category ("the $1.88bn Vietnam skincare market") as your TAM | It is a narrative, not a constraint; it produces no decision | Filter for the sub-category, buyer, geography and channel you actually serve, and show each filter's multiplier |
| E2 | **SAM as a fixed % of TAM** | Invents the answer instead of deriving it | Derive SAM from reachability filters, each with its own source |
| E3 | **The 1% fallacy** — "we only need 1%" | 1% of a large market is frequently a top-5 position. In Vietnam e-commerce, 1% of the VND 429.7tn 2025 platform GMV is VND 4.3tn — larger than most listed Vietnamese retailers | Convert your claimed share into an implied competitive rank and state it |
| E4 | **GMV/revenue confusion** | A marketplace's GMV is 10–30x its revenue at a 3–10% take rate. Retail value is typically 2–3x ex-factory value | Label every figure: GMV, retail value, net revenue, or ex-factory |
| E5 | **Units drift** | Mixing bowls, orders, customers and households in one chain | Write the unit next to every number in the chain; the units must cancel |
| E6 | **Administrative-boundary error** | Using a political unit as a trade area. Da Nang City, after the 1 July 2025 merger with Quang Nam, has 3,065,628 people over 11,859.59 km² and 94 commune-level units (source: https://thuviennhadat.vn/phap-ly-nha-dat/dan-so-thanh-pho-da-nang-sau-sap-nhap-la-bao-nhieu-theo-nghi-quyet-202-686112.html, retrieved 2026-07-29, citing Resolution 202/2025/QH15 of 12 June 2025). A noodle shop's real catchment is ~7 km². Using 3.07m instead of ~85,000 is a **36x error** | Define the trade area geometrically or by travel time, never by administrative name |
| E7 | **Stacked wallet** | Your TAM plus everyone else's TAMs for the same wallet exceeds household income | Run the wallet-share check (§4) |
| E8 | **Currency/vintage drift** | A 2022 USD figure restated in 2026 VND with no FX date | State year, currency, FX rate and FX date on every converted figure |

### The units ladder (write this in the assessment)

```
population (people)
  × filter (dimensionless)        -> reachable people
  × occasions per person per year -> occasions/year
  × share of occasions you serve  -> your occasions/year
  × average ticket (VND/occasion) -> VND/year
```

If a step does not change the unit or is dimensionless, say so. Any chain where the units do not resolve to VND/year is broken.

---

## 2. Top-down vs bottom-up, with full arithmetic

### 2.1 The bottom-up build (the only chain you defend)

```
1. Universe        : population of the defined geography            [source: census / statistical office]
2. Reachable pool  : × eligibility filters (age, income, behaviour) [source or stated assumption + range]
3. Frequency       : × purchase occasions per person per period     [survey / observation / analogue]
4. Your share      : × share of those occasions you can win         [derived from competitor census, NOT assumed]
5. Ticket          : × average revenue per occasion                 [observed competitor prices]
= revenue per period
6. Constrain       : SOM = MIN(capacity ceiling, defensible share)  [both computed, take the lower]
```

Step 6 is the step nobody does. It is the difference between an assessment and a pitch.

### 2.2 Worked example A — one bún bò shop, urban Da Nang

**Verified inputs**

| Input | Value | Source |
|---|---|---|
| Da Nang City population (post-merger) | 3,065,628 over 11,859.59 km²; 94 commune-level units (23 wards, 70 communes, 1 special zone) | https://thuviennhadat.vn/phap-ly-nha-dat/dan-so-thanh-pho-da-nang-sau-sap-nhap-la-bao-nhieu-theo-nghi-quyet-202-686112.html, retrieved 2026-07-29 |
| Vietnam F&B outlets 2025 | 329,500 (+2.0% vs 2024); industry revenue VND 726,500bn (+5.5%); 2026 forecast 333,600 outlets / VND ~760,000bn (+4.6%) | https://ipos.vn/thong-cao-bao-chi-ipos-vn-va-nestle-professional-cong-bo-bao-cao-thi-truong-kinh-doanh-am-thuc-tai-viet-nam-nam-2025/, retrieved 2026-07-29 (published 2026-04-08; n=3,001 owners + 3,045 diners) |
| Bún bò bowl prices, Hue shops | VND 15,000–60,000/bowl across 7 named shops; typical band 25,000–35,000 | https://danangbest.com/bun-bo-hue-huong-vi-mien-trung-thom-ngon-va-hap-dan.html, retrieved 2026-07-29 (page updated 2026-03-11) |
| Urban per-capita income, Vietnam 2025 | VND 7.4m/month urban vs 5.2m rural; national VND 6.0m (+10.9%); survey n=46,995 households | https://dtinews.dantri.com.vn/vietnam-today/hanoi-tops-nation-in-monthly-per-capita-income-20260714090606170.htm, retrieved 2026-07-29 |
| Region I minimum wage from 2026-01-01 (incl. Da Nang) | VND 5,310,000/month; VND 25,500/hour (Decree 293/2025/ND-CP of 2025-11-10) | https://www.vietnam-briefing.com/news/vietnams-new-minimum-wage-january-1-2026.html/, retrieved 2026-07-29 |
| Food-delivery app concentration, Vietnam | ShopeeFood 48% and GrabFood 48% of sales, beFood 4%; market ~US$2.1bn in 2025 (+19%) | https://e.vnexpress.net/news/business/data-speaks/shopeefood-and-grabfood-dominate-vietnam-s-food-delivery-market-with-90-share-4911896.html and https://vir.com.vn/vietnamese-spend-21-billion-on-food-delivery-apps-in-2025-145787.html, retrieved 2026-07-29 |

**Top-down attempt (and why it lies)**

```
Vietnam F&B revenue 2025                       VND 726,500,000,000,000
× Da Nang share of national population
  (3,065,628 / 102,300,000 = 3.00%)            VND  21,795,000,000,000
× noodle-soup breakfast share of F&B  (assume 8%)   VND 1,743,600,000,000
× bún bò share of noodle soup         (assume 25%)  VND   435,900,000,000
× "we only need 1%"                                 VND     4,359,000,000  (= VND 363m/month)
```
Vietnam's 2025 population of 102.3 million is per the National Statistics Office as reported (source: https://www.nso.gov.vn/en/data-and-statistics/2026/01/socio-economic-situation-in-the-fourth-quarter-and-2025/, retrieved 2026-07-29).

Result: VND 363m/month revenue for a single shop, i.e. ~8,000 bowls at VND 45,000 → **269 bowls/day, every day.** Sounds almost plausible, which is what makes it dangerous. But the number is unfalsifiable: the 8% and 25% are invented, and "1%" secretly assumes this one shop takes 1% of bún bò spending across 11,860 km². There are, by census, ~18 bún bò shops within 1.5 km of the site alone. The top-down number cannot tell you whether the shop works. Discard as a decision input; keep only as a magnitude check.

**Bottom-up build**

| Step | Value | Basis / confidence |
|---|---|---|
| 1. Trade area | 1.5 km radius = π×1.5² = **7.07 km²** | Breakfast noodle catchment: walk + 3-min motorbike. Assumed; validate by asking 30 diners their origin |
| 2. Trade-area population | 7.07 × 12,000/km² = **84,840 → 85,000 people** | Density band 8,000–20,000/km² for a Da Nang inner ward. [UNVERIFIED - needs ward-level population from the ward People's Committee or census tabulation. Base 12,000] |
| 3. Eat breakfast away from home ≥1×/week | 85,000 × 45% = **38,250 people** | Assumed 45% (band 35–60%). Directionally supported: Vietnamese food-away-from-home is rising structurally (source: https://www.tandfonline.com/doi/full/10.1080/09581596.2025.2598702, retrieved 2026-07-29), while iPOS reports 2025 consumers reduced frequency but raised spend per visit |
| 4. Breakfast-out occasions per such person per week | × 3.5 = **133,875 occasions/week** | Assumed 3.5 (band 2.5–4.5). Test with a 7-day diary from 30 people |
| 5. Share of breakfast-out occasions that are bún bò | × 11% = **14,726 occasions/week** | Assumed 11% (band 7–15%). Cross-check: bún bò signage = 18 of ~160 breakfast outlets counted in the trade area = 11.3%. Signage share is a real proxy |
| 6. Annualise | × 52 = **765,750 occasions/year** | |
| 7. Average ticket | × VND 45,000 (bowl 38,000 + drink/side attach 7,000) | Bowl price from observed 25,000–35,000 (2025 Hue/Da Nang mass band) uplifted for 2026 Da Nang urban; attach rate assumed 100% at VND 7,000 |
| **= Trade-area SAM** | **VND 34,458,750,000 → VND 34bn/year** (round to 2 s.f.) | ≈ US$1.3m at VND 26,000/USD [UNVERIFIED - use live FX on the day of writing] |

**SOM: compute both ceilings, take the lower**

*Capacity ceiling*
```
seats                                   24
breakfast service window            5.0 h  (05:30–10:30)
average dwell                        18 min -> 3.33 turns/seat/hour
theoretical covers = 24 × 5 × 3.33 =   400 covers/day
× realistic utilisation 55%         =  220 covers/day   (peak is 45 min, not 5 h)
+ delivery uplift 18%               =  260 covers/day
× 26 trading days/month             = 6,760 covers/month
× 12                                = 81,120 covers/year
capacity revenue = 81,120 × 45,000  = VND 3.65bn/year
```
Delivery uplift of 18% is assumed (band 10–25%); the channel exists and is concentrated — ShopeeFood and GrabFood hold 48% each of Vietnam food delivery, so a two-app listing reaches ~96% of app demand.

*Defensible-share ceiling*
```
bún bò occasions in trade area/year      765,750
fair share with 18 competitors = 1/18   = 5.56%  -> 42,569 covers/year
capacity implies                         81,120 / 765,750 = 10.6% = 1.9× fair share
```
Claiming 1.9× fair share requires a named reason (best broth, only air-conditioned option, only shop open past 11:00, only one on the school-run corner). Absent proof, cap at 1.3× fair share = 7.2% → **55,140 covers/year**.

```
SOM = MIN(81,120 ; 55,140) = 55,140 covers/year
    = 4,595 covers/month = 177 covers/day
    = VND 2.48bn/year  (55,140 × 45,000)
```

**Reconciliation**

| Method | Answer | Ratio to bottom-up |
|---|---|---|
| Top-down "1% of category" | VND 4.36bn/year | 1.76× |
| Bottom-up SOM (share-capped) | VND 2.48bn/year | 1.00× |
| Bottom-up capacity ceiling | VND 3.65bn/year | 1.47× |
| Bottom-up trade-area SAM | VND 34bn/year | 13.7× |

Report as: **SOM VND 2.5bn/year (range 1.4–3.6bn)**, where the low case is share-capped at fair share (VND 1.92bn) with a 25% lower ticket, and the high case is the capacity ceiling. The top-down figure exceeds the defensible bottom-up by 1.8× — inside the tolerable band (§4, check 5), so the model is not obviously broken, but the top-down must not be quoted.

### 2.3 Worked example B — DTC skincare serum, Vietnam

**Verified inputs**

| Input | Value | Source |
|---|---|---|
| Vietnam skin care market 2025 | US$1.88bn 2025 → US$2.81bn 2032, CAGR 5.93% | https://www.inkwoodresearch.com/reports/vietnam-skin-care-market-size/, retrieved 2026-07-29 |
| Vietnam skin care market (alternative) | ~US$1.20bn in 2024, CAGR 9.50% 2025–2034 → ~US$2.97bn by 2034 | https://www.researchandmarkets.com/reports/6113009/vietnam-skin-care-products-market, retrieved 2026-07-29 |
| Vietnam Beauty & Personal Care **total** | US$2.79bn in 2025, CAGR 3.26% 2025–2030 | https://www.statista.com/outlook/cmo/beauty-personal-care/vietnam, retrieved 2026-07-29 |
| Vietnam e-commerce 2025 (Shopee, TikTok Shop, Lazada, Tiki) | GMV VND 429.7tn (+34.75%); units 3,941.6m (+15.23%); active shops 601,800 (2024: 650,000; −7.43%); Shopee 56.04% share (from 64%), TikTok Shop 41.31% (from 29%); Shop Mall = 2.12% of shops but 32.6% of Shopee+TikTok revenue | https://metric.vn/insights/thi-truong-tmdt-viet-nam-nam-2025-nhung-chuyen-dich-dang-chu-y/, retrieved 2026-07-29 (published 2026-01-14) |
| DTC beauty benchmarks | Avg CAC US$61; gross margin 60–70%; repurchase rate 25–30%; brands US$5–75m revenue | https://commercecatalyst.ai/benchmarks/, retrieved 2026-07-29 (aggregates First Page Sage, Finaloop 800+ DTC P&Ls, MobiLoud, inBeat) |
| Meta CPM, SEA proxies | Singapore US$7.21, Malaysia US$5.39, Philippines US$3.40. **Vietnam not listed** | https://lebesgue.io/facebook-ads/facebook-cpm-by-country, retrieved 2026-07-29 |

> **Note the units trap in the Metric figures:** Vietnamese number formatting writes 601.8 nghìn (thousand) and 3.941,6 triệu (million). English summaries of this report have rendered "601.8 million shops" and "36,000 trillion VND per month", both impossible. Always re-derive: VND 429.7tn / 12 = VND 35.8tn/month. If a cited figure fails a division test, the citation is mis-transcribed, not the market.

**Top-down attempt**
```
Vietnam skin care 2025                        US$1,880,000,000
× serum sub-category share (assume 12%)       US$  225,600,000
× "1% capture"                                US$    2,256,000  (= VND ~58.7bn/year)
```

**Bottom-up build**

| Step | Value | Basis / confidence |
|---|---|---|
| 1. Vietnam population 2025 | 102,300,000 | NSO, as reported (see §2.2) |
| 2. Female | × 50.2% = 51,354,600 | [UNVERIFIED - needs NSO sex ratio table] |
| 3. Age 22–40 | × 27% = 13,865,742 | [UNVERIFIED - needs NSO age pyramid] |
| 4. Urban | × 40% = 5,546,297 | [UNVERIFIED - needs NSO urbanisation rate] |
| 5. Buys skincare online | × 55% = 3,050,463 | Assumed (band 40–70%). Supported directionally: 601,800 active shops and VND 429.7tn platform GMV imply near-universal urban platform usage |
| 6. Can absorb a VND 450,000 serum | × 45% = 1,372,708 | VND 450,000 = 6.1% of urban monthly per-capita income (VND 7.4m). This is a considered purchase, not impulse. Assumed top 45% by income (band 30–60%) |
| **SAM (people)** | **≈ 1.37m (range 0.7–2.4m)** | |
| 7. Units per year per buyer | × 2.2 | 30 ml at 2 pumps/day lasts 8–12 weeks → 4.3–6.5 units for a perfect adherer; real adherence is far lower. Anchored to reported DTC beauty purchase frequency of ~2.7 orders/year (source: https://commercecatalyst.ai/benchmarks/, retrieved 2026-07-29), discounted for a single-SKU brand. Band 1.5–3.0 |
| 8. AOV | × VND 520,000 | Unit price 450,000 + bundle attach. Sanity check: reported DTC beauty AOV ~US$66 ≈ VND 1.72m; Vietnam AOV at 30% of that tracks the income gap (urban VND 7.4m/month vs US median). PASS |
| **= SAM (money)** | **VND 1,570bn/year ≈ US$60m** | 1.372m × 2.2 × 520,000 = VND 1,570,378,000,000 |

*Cross-check against top-down:* serum sub-category at 10–15% of a US$1.2–1.88bn skincare market = US$120–282m. My SAM of US$60m is 21–50% of that. Since SAM is restricted to urban, online, 22–40, female, top-45%-income buyers, 21–50% is plausible. **PASS.**

**SOM: derive from the acquisition engine, never from a percentage**

```
media budget                          VND 400,000,000/month = 4,800,000,000/year
CPM (Vietnam)                         VND 78,000 /1,000 impressions  (≈US$3.00)
   [UNVERIFIED - no published Vietnam Meta CPM found; proxied below Philippines US$3.40]
impressions = 4.8bn / 78,000 × 1,000  = 61,538,462
× CTR 1.2%                            =    738,462 clicks   (implied CPC ≈ VND 6,500 / US$0.25)
× landing CVR 1.6%                    =     11,815 first orders
CAC = 4,800,000,000 / 11,815          = VND 406,300  (≈US$15.6)
```
*CAC sanity check:* reported DTC beauty CAC benchmarks cluster US$25–120 with a US$61 average in US/EU markets. US$15.6 sits below that floor. Media cost differences make it directionally possible, but this is the single most fragile number in the model and must be labelled Assumed, not Sourced.

```
repurchase rate 27%  (band 25–30%, sourced)
repeat orders per repeater 1.4
orders year 1 = 11,815 × (1 + 0.27 × 1.4) = 11,815 × 1.378 = 16,281
revenue year 1 = 16,281 × 520,000        = VND 8,466,120,000 -> VND 8.5bn (US$326k)
SOM as % of SAM = 8.5 / 1,570            = 0.54%
```

**Reconciliation**

| Method | Year-1 revenue | Ratio |
|---|---|---|
| Top-down "1% of serum sub-category" | VND 58.7bn (US$2.26m) | **6.9×** |
| Bottom-up, acquisition-derived | VND 8.5bn (US$326k) | 1.00× |

The top-down overstates by 6.9×. **Ratio > 3× is a hard fail (§4, check 5).** The assessment must say so explicitly and discard the top-down number.

### 2.4 The two-report contradiction (use this in every assessment)

Statista puts Vietnam **Beauty & Personal Care in total** at US$2.79bn for 2025. Inkwood puts Vietnam **skin care alone** at US$1.88bn for 2025 — 67% of the parent category. Skin care is not 67% of beauty & personal care in any market; typical shares run 25–40%. A third report puts skincare at US$1.20bn for 2024. **At least one of these numbers is unusable, and you cannot tell which.**

Correct handling: pick one, name it, state the range across sources, and state what breaks if you picked wrong. **Never average syndicated market sizes** — averaging two incompatible methodologies produces a number that belongs to neither.

---

## 3. Uncertainty as a range, not a fake number

### 3.1 Construction rules

1. Give every driver a **low / base / high**. Low and high are the 10th and 90th percentile of what you would bet on, not the worst and best conceivable.
2. Compute the base case as base × base × … .
3. **Do not** compute the range by multiplying all lows and all highs. In a 5-driver chain with ±30% each, that gives 0.7⁵ = 0.17× to 1.3⁵ = 3.71× — a 22× spread that is theatre, because it assumes all five errors point the same way.
4. Instead: rank drivers by **uncertainty width**, vary only the top two or three, hold the rest at base.
5. Round to **2 significant figures**. `VND 34,458,750,000` claims 8-digit precision from a guessed density. Write `VND 34bn`.
6. Every point estimate carries its range in the same sentence, plus the named driver responsible.

### 3.2 The counter-intuitive rule about sensitivity

In a purely multiplicative chain, **every driver has identical sensitivity** — a ±30% move in any one moves the answer ±30%. So sensitivity analysis is useless for prioritisation. Prioritise by *uncertainty width* instead:

| Driver (bún bò SAM) | Base | Plausible band | Width (high/low) | Measurable? | Measurement cost | Priority |
|---|---|---|---|---|---|---|
| Bún bò share of breakfast-out occasions | 11% | 7–15% | 2.14× | Yes — signage census + 100 intercepts | 1 day, ~VND 1m | **1** |
| Breakfast-out share of population | 45% | 35–60% | 1.71× | Yes — 100 door intercepts | 1 day | **2** |
| Occasions/person/week | 3.5 | 2.5–4.5 | 1.80× | Yes — 7-day diary, n=30 | 1 week, ~VND 3m | 3 |
| Trade-area density | 12,000/km² | 8,000–20,000 | 2.50× | Yes — ward statistics office, free | 2 hours | **0 (do first, free)** |
| Ticket | 45,000 | 35,000–55,000 | 1.57× | Yes — menu census, free | 3 hours | 0 (free) |

Rule: **do the free measurements first, then buy the widest remaining band.** After the free ward-population and menu census, the range collapses from ~7× to ~2.8×, which is enough to make a lease decision.

### 3.3 Reporting template

```
SOM year 1: VND 2.5bn (range 1.4–3.6bn).
Low case  = fair-share capture (5.6%) at ticket VND 38,000.
High case = physical capacity ceiling at 55% utilisation.
Dominant uncertainty: bún bò share of breakfast-out occasions (7–15%).
Single measurement that most narrows this: 100 door-intercept interviews at 06:30–08:30
  on the target street over 3 weekdays. Cost ~VND 1m, 1 day. Would cut the range to ~1.6×.
```

---

## 4. Sanity checks that catch a nonsense TAM

Run all ten. Record PASS / FAIL / N/A in the assessment. Any FAIL blocks publication of the number.

| # | Check | Formula | Threshold | Worked |
|---|---|---|---|---|
| 1 | **Per-capita reality** | TAM ÷ population of geography ÷ 12 = VND/person/month | Must be < 8% of per-capita monthly income for one product category; < 2% for one dish/SKU | A claimed VND 500bn bún bò TAM in an 85,000-person trade area = VND 490,000/person/month = 6.6% of urban income (VND 7.4m) on one dish. **FAIL.** The VND 34bn figure = VND 33,300/person/month = 0.45%. **PASS** |
| 2 | **Wallet stacking** | Σ(your TAM + adjacent TAMs on the same wallet) vs household disposable income | Sum must be < 100% of income | Breakfast + lunch + coffee + delivery fees + groceries must fit inside VND 7.4m/person/month |
| 3 | **Capacity of supply** | TAM ÷ revenue per outlet per year = implied outlets | Implied outlets must be ≤ observed outlets | VND 34bn ÷ VND 2.5bn = 13.6 outlets implied vs 18 counted. **PASS** (and tells you the average competitor is smaller than your plan) |
| 4 | **Transaction absurdity** | TAM ÷ ticket ÷ 365 ÷ outlets = transactions/outlet/day | Must be ≤ physical capacity | VND 34bn ÷ 45,000 ÷ 365 ÷ 18 = 115 bowls/shop/day. Plausible for a 20-seat shop. **PASS** |
| 5 | **Method ratio** | bottom-up SOM ÷ top-down SOM | 0.33–3.0 tolerable; outside = one model is wrong; > 1.0 with SOM vs industry TAM = always an error | Bún bò: 2.48/4.36 = 0.57 **PASS**. Serum: 8.5/58.7 = 0.14 **FAIL — discard top-down** |
| 6 | **Source internal consistency** | sub-category ÷ parent category from different reports | Sub-category > 50% of parent is a red flag | Skin care US$1.88bn vs BPC US$2.79bn = 67%. **FAIL — sources mutually impossible** |
| 7 | **Units audit** | Label every figure GMV / retail value / net revenue / ex-factory / units | No unlabelled figure survives | Metric's VND 429.7tn is platform GMV, not seller net revenue |
| 8 | **Growth plausibility** | category growth ÷ nominal GDP growth | > 3× for > 3 years requires a named mechanism | VN e-commerce +34.75% in 2025 has one: TikTok Shop 29% → 41.31% share shift (content-to-commerce). Named. **PASS** |
| 9 | **Vintage & FX** | Every converted figure carries year, currency, rate, rate date | No exceptions | US$1.88bn (2025) at [live rate, dated] — not a 2022 rate |
| 10 | **Stranger reproduction** | Hand your assumption table to someone who has not seen the model | They must reproduce the number in < 10 minutes | If not reproducible, it is not defensible |

**Bonus check for service businesses:** TAM ÷ (revenue per practitioner per year) = implied practitioners. If that exceeds the number of people employed in the occupation in that geography, the TAM is impossible.

---

## 5. Demand evidence: five weak signals, their biases, and how to triangulate

No single online signal measures demand. Each measures a *proxy* with a known, directional bias. The method is to collect three, correct each for its bias, and accept the estimate only if they converge.

### 5.1 Signal reference table

| Signal | What you actually pull | Native unit | Direction of bias | Correction | Confidence cap |
|---|---|---|---|---|---|
| **Search volume** | Google Keyword Planner monthly volume; Google Trends 0–100 index | searches/month (bucketed) | **Overstates** for discovery-driven categories; **massively understates** habitual local purchase (nobody googles their daily breakfast) | Split query intent (local / recipe / tourist / brand); never use for habitual categories | Sourced at best; Assumed if bucket width > 3× |
| **Marketplace listings** | Count of active listings for the exact product type, with filters set to the geography | listings | Overstates supplier count (duplicates, dropshippers, virtual brands); understates demand | Deduplicate by seller; check "sold" counters | Sourced for supply, never for demand |
| **Review counts** | Reviews per listing, per competitor | reviews | Reflects *lifetime cumulative* sales, not current run-rate; review rate varies 1%→10% by category | Use for **ranking** competitors only, where the bias is roughly constant across the set | Assumed |
| **Delivery-app category depth** | Number of listings in the category within the delivery radius; displayed order counts / rating counts | listings + lifetime orders | Delivery is only 10–25% of a breakfast shop's volume; virtual brands inflate counts | Multiply delivery volume by 4–10× to get total; deduplicate kitchen addresses | Triangulated |
| **Social hashtag / sound volume** | Post counts and view counts per hashtag; sound usage counts | posts, views | Measures *creator supply*, not consumer demand; bot and re-upload inflation; view ≠ 3 seconds of attention | Use ratio of comments-with-purchase-intent to views, not raw views | Assumed |
| **Job postings** | Count of postings for the role that only exists if the demand exists (e.g. "nhân viên bếp bún", "livestream host", "cosmetics QA") | postings | Lags demand by 1–2 quarters; skews to firms large enough to post formally | Best used as a **direction** indicator and for competitor expansion detection, not level | Sourced for direction |

### 5.2 Search volume: what the numbers actually are

- **Google Keyword Planner is bucketed.** Without an active Ads campaign you get **7 order-of-magnitude ranges**: 0–10, 10–100, 100–1K, 1K–10K, 10K–100K, 100K–1M, 1M+. With an active campaign you get roughly **60 discrete predetermined values**: 10, 20, 30, 40, 50, 70, 90, 110, 140, 170, 210, 260, 320, 390, 480, 590, 720, 880, 1000, 1300, 1600, 1900, 2400, 2900, 3600, 4400, 5400, 6600, 8100, 9900, 12100, 14800, 18100, 22200, 27100, 33100, 40500, 49500, 60500, 74000, 90500, 110000, 135000, 165000, 201000, 246000, 301000, 368000, 450000, 550000, 673000, 823000, 1000000, 1220000, 1500000, 1830000, 2740000, 5000000, 7480000 — from an analysis of 60 million keywords (source: https://www.authoritas.com/blog/understanding-googles-search-volume-buckets-a-deep-dive-into-how-search-volumes-really-work, retrieved 2026-07-29). A displayed "1,600" means *the bucket labelled 1,600*, and moving buckets at the high end takes an 18–23% real change. **Treat every KP number as a bucket label, and state the bucket edges.**
- **Google Trends is not volume.** It is a 0–100 index of a term's share of all searches in that geography and window, computed from a **sample**, with deliberate small random fluctuations added — most visible on low-volume queries — and Google itself states it "is not a perfect mirror of search activity" and should be "one data point among others" (source: https://support.google.com/trends/answer/4365533, retrieved 2026-07-29). You may compare terms to each other; you may not convert the index to searches.
- **Search-to-click decay is real but often irrelevant.** 68.01% of US Google searches ended without a click in January–April 2026, up from 60.45% in 2024, measured on Similarweb's desktop+mobile clickstream panel; AI Overviews appear on 20%+ of searches and cut CTR by nearly 60% when present; AI Mode accounted for only 0.34% of searches in that window (source: https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/, retrieved 2026-07-29). **But for a physical local business, the "click" is often a tap inside Maps and the outcome is a visit, so do not decay local intent for zero-click — count searches as intent events instead.** No equivalent Vietnam-specific zero-click measurement was found. [UNVERIFIED - needs a Vietnam or SEA clickstream source before applying the 68% figure outside the US.]

**Tool cost, if the client asks (verified from vendor pricing pages):** Ahrefs Starter US$29/mo, Lite US$129/mo (US$107.76/mo annual), Standard US$249/mo, Advanced US$449/mo, Enterprise from US$1,499/mo; a free tier exists (source: https://ahrefs.com/pricing, retrieved 2026-07-29). Semrush SEO US$139/mo (US$117.33 annual), Starter US$199/mo, Pro+ US$299/mo, Advanced US$549/mo, with 500–5,000 tracked keywords/day and a 7-day free trial (source: https://www.semrush.com/pricing/, retrieved 2026-07-29). Google Keyword Planner is free with an Ads account, and gives ~60-value buckets once a campaign is active — which is usually the cheapest path to usable data for a small business.

### 5.3 Review counts: the multiplier is folklore

The widely-repeated claim is that "1–2% of Amazon buyers leave a review", attributed to Amazon. Reported ranges in circulation: 1–2%, 1–3%, 3–10%, 4–5% for electronics, ~1% for budget beauty (source: https://tracefuse.ai/blog/what-percent-of-amazon-customers-leave-reviews/, retrieved 2026-07-29). **A 1%→10% spread in the review rate is a 10× spread in any sales estimate derived from review counts.** Therefore:

- **Never** use `reviews × multiplier` as a primary demand estimator.
- **Do** use review counts to rank competitors, because the platform's review-prompting behaviour is roughly constant across sellers on the same platform.
- **Do** use *review velocity* (reviews added in the last 90 days, read from review dates) as a run-rate proxy — it removes the lifetime-accumulation bias, which is the larger error.
- Platform-specific distortion: Shopee's coin/voucher review incentives inflate 5-star volume, so pooled star averages across Shopee and Google Maps are meaningless. Report per platform, never pooled.

### 5.4 Triangulation protocol (worked, on bún bò weekly demand)

**Rule:** accept the bottom-up estimate when **at least two independent signals land within ±40%** of it. Report the range as [min, max] of the surviving estimates. If the spread across signals exceeds **3×**, publish no point estimate — publish the range plus the one measurement that would collapse it.

*Bottom-up estimate to test: 14,726 bún bò occasions/week in the 1.5 km trade area (§2.2).*

**Signal 1 — Search (weak for habitual categories).**
```
"bún bò đà nẵng" KP bucket                  1,600/month   (bucket edges: 1,600 exactly, adjacent 1,300 / 1,900)
× local-intent share (excl. recipe/tourism)     60%  ->  960 intent events/month, whole city
× search->visit conversion (band 25–50%, base 35%)  ->  336 visits/month, whole city
÷ search-covered share of occasions (band 3–8%, base 5%)  -> 6,720 occasions/month city-wide
= 1,551 occasions/week for ALL of Da Nang
```
This is **~10% of the bottom-up figure for a single 7 km² trade area**, i.e. off by two orders of magnitude. **Conclusion: reject search as an estimator for habitual local food.** Keep it only for the awareness read (§9.2). This is not a failure of the method — it is the method working: the signal disqualified itself.

**Signal 2 — Delivery-app category depth.**
```
bún bò listings on ShopeeFood + GrabFood within 3 km       41 listings
- deduplicate by kitchen address / identical menu photos  -> 29 distinct kitchens
median displayed lifetime orders per listing                1,200
assume median listing age 30 months -> 40 orders/month/kitchen
delivery volume in trade area (scale 29 kitchens -> the 1.5 km subset ~18)
   18 × 40 = 720 delivery orders/month = 166/week
delivery = 18% of total volume (band 10–25%)
-> total = 166 / 0.18 = 922 ... per KITCHEN-set? No: 166/0.18 = 922 occasions/week
```
922/week is **6% of the bottom-up figure** — also far too low, because displayed order counters on Vietnamese delivery apps are frequently capped, hidden, or reset. **Downgrade to "supply census only".** What it *does* tell you reliably: 29 distinct bún bò kitchens compete for delivery in 3 km, and delivery is a crowded, low-differentiation channel.

**Signal 3 — Physical census (strongest for local).**
```
weekday 06:30–08:30 ride of the 1.5 km radius, 3 separate mornings
shops with bún bò signage                        18
mean occupied stools at 07:15                    14
mean dwell                                       18 min -> 3.33 turns/stool/hour
peak-hour covers = 18 × 14 × 3.33             =  840 covers/hour
peak hour as share of daily volume (band 25–35%, base 30%)
daily covers = 840 / 0.30                     =  2,800 covers/day
weekly (7 days, weekend −20%)                 =  2,800 × 6.6 = 18,480 covers/week
```
18,480 vs bottom-up 14,726 = **+25%. Within ±40%. PASS.**

**Verdict:**
```
Surviving estimates: bottom-up 14,726/week ; physical census 18,480/week
Reported: 15,000–18,500 bún bò occasions/week in the 1.5 km trade area
          (point estimate 16,600, ±12%)
Rejected: search (understates habitual demand by ~10×), delivery-app order counters
          (platform display artefacts)
Confidence: Triangulated
Next measurement to narrow: repeat the census on 3 more mornings incl. one rainy day,
          and 100 door intercepts to fix the peak-hour share. Cost ~VND 1m, 2 days.
```

**The general lesson to encode in the skill:** for **habitual, local, low-ticket** purchases, physical observation beats every digital signal. For **considered, searched, national** purchases (the serum), search and marketplace signals dominate and physical census is impossible. Choose the signal set from the purchase type, not from what is convenient.

### 5.5 Signal choice by purchase type

| Purchase type | Primary signal | Secondary | Reject |
|---|---|---|---|
| Habitual, local, low-ticket (breakfast, coffee, laundry) | Physical census at the occasion hour | Delivery-app supply census; Maps review velocity | Search volume; hashtag views |
| Considered, local, high-ticket (dentistry, driving school, aircon install) | Search volume + Maps review velocity | Job postings of competitors; price-list scraping | Hashtag views |
| Considered, national, shipped (serum, supplement, gadget) | Marketplace listing + review velocity | Search volume; affiliate/livestream frequency | Physical census |
| Impulse, social-discovered (novelty food, trend beauty) | Hashtag/sound velocity **change rate**, not level | Marketplace new-listing rate | Search volume (lags the trend) |
| B2B services | Job postings; procurement/tender notices | LinkedIn headcount change of target accounts; search for the problem phrase | Hashtag views; consumer reviews |

---

## 6. Competitive analysis with teeth

### 6.1 Build the competitor set in four rings (plus the do-nothing row)

| Ring | Definition | Bún bò shop, Da Nang | DTC serum, Vietnam | How many to include |
|---|---|---|---|---|
| **R1 Direct** | Same product, same occasion, same trade area/channel | 18 bún bò shops within 1.5 km | Vietnamese-brand serums in the VND 350–650k band on Shopee/TikTok Shop | All, if ≤ 20; else the 12 nearest + 8 highest-review-velocity |
| **R2 Indirect** | Different product, same occasion | Mì quảng, phở, bánh mì, xôi, cháo, bún chả cá shops in the same radius (~140 outlets) | Imported K-beauty serums, ampoules, essences at any price | Top 8 by observed traffic/GMV |
| **R3 Substitute** | Different behaviour that satisfies the same job | Instant noodles at home; office pantry; skipping breakfast; company canteen | Dermatologist visit; clinic treatment; a cheaper 3-step routine; sunscreen only | Name every one; quantify the top 3 |
| **R4 Do-nothing** | The status quo, treated as a competitor with a row of its own | "Same shop I've gone to for 6 years" — habit, zero switching cost, known outcome | "My current routine works well enough" — VND 0 incremental cost, zero risk | Always exactly one row |

**The do-nothing row is mandatory and must be filled like any competitor:** its price is 0 incremental, its switching cost is 0, its risk is 0, and its performance is "the customer's current state". You beat it only when push + pull exceed anxiety + habit (§7.2). Assessments that omit it systematically overestimate capture, because they implicitly assume everyone in the market is shopping. Most are not.

### 6.2 The census method: how to actually count competitors

Counting is where assessments are won. Do not "research the competitive landscape"; execute a census with a stated frame.

**For a local business**
1. Draw the trade area (radius or 8-minute ride isochrone). State it.
2. Google Maps: search the category term + the ward name; pan the map at a fixed zoom; record every pin. Then repeat with 3 Vietnamese synonyms (bún bò / bún bò Huế / bún bò giò heo) — Maps returns different sets per synonym.
3. Physically ride every street in the radius once. **Expect Maps to miss 25–45% of informal outlets** (cart, pavement, home-front operations with no listing). This gap is the single most common cause of understated competitive intensity in local assessments. [Practitioner estimate — no published measurement found. UNVERIFIED, but the direction is certain: Maps under-counts unregistered outlets.]
4. Cross-check with the two delivery apps (ShopeeFood, GrabFood) — they capture some shops Maps misses and vice versa.
5. Record per outlet: name, coordinates, opening hours, seat count, price of the flagship item, delivery-app presence, Google rating and review count, review count added in last 90 days, air-con y/n, parking capacity, signage condition.

**For a marketplace product**
1. Fix the frame: platform + category path + price band + shipping-from filter. State it.
2. Capture the first 100 listings by "best selling" and the first 100 by "newest". The gap between those two lists tells you the entrant rate.
3. Deduplicate by seller ID, then by identical product photos (white-label detection).
4. Record per listing: price, "sold" counter, review count, review count in last 90 days, Shop Mall status, discount depth, bundle structure, ingredient/claim wording, main-image composition.
5. Check the Meta Ads Library and Google Ads Transparency Center for the same brands — a listing with no ads and high sales is organically/affiliate driven, which is a different opponent from a paid-media brand.

### 6.3 Comparison matrix: use axes that predict switching, not axes that are easy

Most competitor matrices compare features nobody switches over. Build the axis list from the customer evidence (§7) and keep only axes that satisfy all three: **(a) observable by a stranger in under 10 minutes, (b) actually varies across the set, (c) appeared in switching stories or 1–2★ reviews.**

Axis-selection test, applied:

| Candidate axis | Observable? | Varies? | In switching evidence? | Keep? |
|---|---|---|---|---|
| Bowl price | Yes | Yes (25k–99k) | Yes — "quá đắt cho một tô bún" | **Keep** |
| Time from order to bowl | Yes (stopwatch) | Yes (2–11 min) | Yes — "chờ lâu, trễ giờ làm" | **Keep** |
| Opening hours end time | Yes | Yes (10:00–22:00) | Yes — "đến muộn thì hết" | **Keep** |
| Seating comfort (air-con + stool vs chair + toilet) | Yes | Yes | Yes — "nóng, ngồi ghế nhựa thấp" | **Keep** |
| Broth "authenticity" | No (subjective) | — | Yes but unmeasurable | Drop as an axis; handle as a claim needing proof |
| Number of menu items | Yes | Yes | No | **Drop** |
| Instagram follower count | Yes | Yes | No | **Drop** |
| Years in business | Yes | Yes | Weakly (trust) | Keep as a tiebreak column only |

The output is a matrix with 4–6 kept axes, all competitors as rows, and — critically — **the do-nothing row and your own planned position** as rows too.

### 6.4 Price-ladder mapping

A price ladder is the observed price distribution of the category in *your* frame, with the rungs named by what buyers get at each rung. Build it from the census, never from intuition.

**Bún bò, Da Nang/Hue observed (source: https://danangbest.com/bun-bo-hue-huong-vi-mien-trung-thom-ngon-va-hap-dan.html, retrieved 2026-07-29, page updated 2026-03-11; plus reported Da Nang shop prices of VND 25,000–35,000 in 2025 and VND 99,000 at Madame Lân)**

| Rung | VND/bowl | What the buyer gets | Observed examples | Site format |
|---|---|---|---|---|
| Floor | 15,000–25,000 | Small bowl, pavement stool, 2–4 h window, cash only | O Cương–Chú Điệp 15–30k; Bà Tuyết 25–35k | Cart / home-front |
| Mass | 25,000–40,000 | Standard bowl, plastic stool, morning-only | Mệ Kéo 25–35k; Bún Hẻm 30–35k | Shopfront, 15–30 seats |
| Comfort | 40,000–65,000 | Fan or air-con, chairs, tables, all-day, delivery-listed | Mệ Kéo special up to 60k; Bà Gái 20–50k | Shopfront + delivery |
| Premium | 65,000–99,000+ | Air-con restaurant, tourist-facing, service, English menu | Madame Lân ~99k (2025, up from ~65k in 2019) | Restaurant |

Two things this immediately gives you: the **mass band is compressed** (25–40k, a 1.6× spread) which signals mature price competition (§6.7), and the **40–65k comfort rung is thinly occupied in residential wards** — a positioning gap, provided customer evidence supports willingness to pay for comfort.

**DTC serum, Vietnam — build the same table from a 100-listing capture.** Rungs typically resolve to: white-label floor (VND 99–199k), local brand mass (VND 250–450k), local premium / clinical-claim (VND 450–800k), imported K-beauty (VND 600–1,500k), Western prestige (VND 1,500k+). [UNVERIFIED - these bands are illustrative; capture live Shopee/TikTok Shop listings and replace with observed prices before use.]

**Ladder discipline:** you must state which rung you are entering, which rung you are stealing from, and what physically changes about the product/experience to justify the rung. Entering a rung with a product built for the rung below is the most common cause of a stalled launch.

### 6.5 Positioning map built from measured attributes

Do not draw the `premium ↔ traditional` 2×2 that every deck contains. Construct it:

1. From §6.3, take the kept axes (4–6).
2. Score every competitor on every axis from census data. Use real units where possible (VND, minutes, seats) and 0–3 ordinals only where necessary (comfort = air-con 1 + chairs-not-stools 1 + clean toilet 1).
3. Compute the **variance** of each axis across the set. Keep the two highest-variance axes that are also in the switching evidence. Those are your map axes.
4. Plot all competitors. Plot the do-nothing option at the origin of "effort" if relevant.
5. Identify empty regions. **An empty region is only an opportunity if customer evidence shows demand there.** Empty regions are usually empty because nobody wants them.
6. State the test: "if the comfort-at-mid-price quadrant is real, then ≥25% of intercepted diners will say they would pay VND 55,000 for an air-conditioned bún bò with seated tables at 07:00. Measure before signing the lease."

Worked axes for the bún bò set: **X = price per bowl (25k–99k observed, variance high); Y = comfort index 0–3 (variance high).** Result: a dense cluster at (25–40k, comfort 0–1), a thin tail at (65–99k, comfort 3), and a near-empty region at (45–60k, comfort 2). That region is the hypothesis.

### 6.6 Porter's five forces, applied — not recited

Porter's framework originates in "How Competitive Forces Shape Strategy", *Harvard Business Review* 57(2), March–April 1979, pp. 137–145 (source: https://hbr.org/1979/03/how-competitive-forces-shape-strategy, retrieved 2026-07-29). The textbook recitation is useless for a small business. Score each force 1–5 with an **observable** behind it, and end each row with a "so what" that changes an action.

**A. Single bún bò shop, urban Da Nang**

| Force | Score | Observable evidence | So what (the action it changes) |
|---|---|---|---|
| Rivalry among existing | **5** | 18 direct shops in 1.5 km; mass price band compressed to 25–40k; Vietnam F&B outlets +2.0% to 329,500 in 2025 while industry revenue rose only 5.5% → revenue per outlet grew ~3.4%, below the 2025 income growth of 10.9%, i.e. the average outlet is losing ground (iPOS 2025; NSO/HLSS 2025) | Do not enter on price. The only viable edges are a signature the customer can name, speed, and hours nobody else covers |
| Supplier power | **3** | Beef shank/bone is commodity but shock-prone. iPOS 2025 records that the Canfoco canned-food incident changed product choices for 54.45% of surveyed consumers and African swine fever affected 41.77% — supply shocks reach consumers fast | Dual-source beef; then convert the risk into an asset by publishing provenance, which the census shows no competitor does |
| Buyer power | **4** | Zero switching cost; 18 alternatives within a 5-minute walk; total price transparency (prices are painted on the wall) | Buyer power is neutralised only by habit. Engineer a morning routine: fixed opening minute, remembered order, 10th-bowl card |
| Threat of new entry | **5** | Entry capital is a pot, a cart and a pavement; household-business registration is cheap and fast | Barriers must be built, not found: recipe consistency under staff turnover, a lease you control, and a review moat (review velocity, §5.3) |
| Substitutes | **5** | R2+R3: ~140 non-bún-bò breakfast outlets in radius, plus home instant noodles, canteens, and skipping breakfast | The real competitive set is "what a Da Nang office worker eats at 07:10", not "bún bò shops". Position against the occasion, not the dish |
| **Net** | **4.4/5 — structurally unattractive** | | Only two defensible plays: (a) micro-catchment monopoly — be unambiguously best within 400 m; (b) own an occasion nobody serves (post-21:00, office bulk delivery, tourist-facing with English). Say this plainly; an assessment that calls this an "attractive market" is lying |

**B. DTC skincare serum, Vietnam**

| Force | Score | Observable evidence | So what |
|---|---|---|---|
| Rivalry | **5** | 601,800 active shops across the 4 platforms in 2025; Shop Mall stores are only 2.12% of shops on Shopee+TikTok Shop but take 32.6% of their revenue → the platform routes revenue to verified/branded stores, leaving ~67% of GMV to 97.9% of sellers (Metric 2025) | Achieving Shop Mall / official-store status is worth more than any single creative asset. Budget for it in month 1 |
| Supplier power | **2** | Contract manufacturers are plentiful; power sits in MOQ and lead time, not price | Negotiate a 1,500-unit first run even at worse unit cost, to avoid working-capital lock before demand is proven |
| Buyer power | **4** | One-tap price comparison; voucher stacking normalised; unit growth (+15.23%) far below revenue growth (+34.75%) in 2025, i.e. buyers traded up but remain price-aware (Metric 2025) | Do not discount into the mass rung. Compete on bundle construction and on a claim you can substantiate |
| New entry | **5** | A white-label serum can be listed within weeks; active-shop count is falling (−7.43%) *while* revenue rises, which is churn, not scarcity | Assume your differentiation will be copied in one quarter. The durable asset is the customer list and the content engine, not the formula |
| Substitutes | **4** | Existing routine; imported K-beauty; clinic treatment; sunscreen-only minimalism | Position against the *routine slot*, not against other serums |
| **Platform power (sixth force — add it)** | **5** | TikTok Shop went 29% → 41.31% of platform revenue in one year while Shopee fell 64% → 56.04%; ShopeeFood+GrabFood hold 96% of food delivery. When two platforms hold > 90% of a channel they set your take rate, your discoverability and your access to the customer | Cap single-platform revenue at 60% by month 12; build one owned channel (Zalo/email list) from order one. Treat an algorithm change as a named risk with a leading indicator |
| **Net** | **4.2/5 — enterable only with conditions** | | Enter only with (a) a substantiable mechanism claim, (b) an acquisition asset that survives an algorithm change, (c) AOV high enough to absorb platform fees + CAC (see §10.4, where at VND 450k single-unit it does not) |

**Why the sixth force matters:** Porter's 1979 framework predates marketplaces that simultaneously act as channel, competitor (own-brand), landlord (fees), and regulator (policy). For any business whose demand arrives through a platform, model platform power as a first-class force with its own row, score and mitigation. This is a deliberate departure from the textbook and should be labelled as such in client work.

### 6.7 Reading competitive intensity from observable signals

Score each; ≥5 signals in the "high" column means the market is intensity-constrained and marketing spend will underperform.

| Signal | Low intensity | High intensity | Where to observe |
|---|---|---|---|
| Discount depth | < 10% of listings discounted | > 50% discounted, avg depth > 25% | Platform category page, or wall/menu signage |
| Price spread, top 20 | > 2.5× (max/min) | < 1.6× | Census price column |
| New-entrant rate | < 1/quarter | > 1/month | Maps new pins; platform "newest" listing sort |
| Distinct advertisers on the head term | < 5 | > 15 | Meta Ads Library search; Google Ads Transparency Center |
| Ad creative half-life | same creative live > 90 days | rotated < 21 days | Meta Ads Library "started running" dates |
| Exits in last 24 months | none | multiple | Local news; platform delistings. VN food delivery: Baemin exited Dec 2023, Gojek/GoFood Sep 2024, Loship end-2024 |
| Seller count trend vs revenue trend | both rising | sellers falling while revenue rises (shakeout) | Metric 2025: shops −7.43%, GMV +34.75% |
| Top-2 concentration | < 40% | > 85% | Market reports. ShopeeFood + GrabFood = 96% |
| Review velocity of leaders | flat | accelerating on the top 3 only | Census, 90-day review counts |
| Job postings by competitors | none | multiple, incl. "livestream host", "performance marketer" | Job boards; competitor Facebook pages |

Both running examples score high on 7+ signals. That is a finding, and it belongs in the decision summary — not buried on page 9.

---

## 7. Customer evidence

### 7.1 The switch interview (Jobs-to-be-Done)

Interview people who **recently switched** — bought, cancelled, or moved from one option to another in the last 90 days — and walk the decision backwards in forensic detail. Recency matters because memory of the trigger decays fast.

**Recruit:** 8–12 recent switchers per segment; stop when two consecutive interviews produce no new codes (saturation). Include at least 2 people who considered you and chose something else, and 2 who chose do-nothing. Interviews run 35–50 minutes. Record and transcribe verbatim; paraphrase destroys the language capture (§7.4).

**Timeline structure — six beats, walked in reverse then replayed forward**

| Beat | What you are looking for | Question that opens it |
|---|---|---|
| 6. First use / outcome | Whether the job got done, and what they told others | "Walk me through the first time you actually used it. What happened?" |
| 5. Purchase moment | The final trigger, who was present, what almost stopped it | "Where were you when you actually paid? What was the last thing you checked?" |
| 4. Active looking | Shortlist, comparison criteria, information sources | "What did you compare it against? What did you type in?" |
| 3. Passive looking | The idea sitting dormant; what re-activated it | "How long between first thinking about it and doing something? What kept it alive?" |
| 2. First thought | The originating event, in date and place | "Take me back to the first time you thought 'this has to change'. What happened that day?" |
| 1. Prior state | The old solution and what it was actually doing for them | "What were you doing before? What was fine about it?" |
| Replay | Verify the sequence and dates; catch reordering | "Let me read the timeline back — did I get the order right?" |

**Hard rules:** never ask "what features do you want"; never ask a hypothetical ("would you buy…"); never let them speak in general terms ("I usually…") — push to a single dated instance ("the last time — what day was it?").

### 7.2 The four forces of progress, with elicitation and scoring

The four forces are the push of the current situation, the pull of the new solution, the anxiety of the new solution, and the habit of the present; a switch happens only when push + pull exceed anxiety + habit (source: https://jobstobedone.org/the-four-forces/, retrieved 2026-07-29; framework attributed to Bob Moesta and Chris Spiek).

| Force | Definition (as published) | Elicitation questions | Score 1–5 | What it maps to in the output |
|---|---|---|---|---|
| **Push** | "The problem with the current situation… the friction, frustration, or broken moment that makes someone start looking" | "What was the last straw?" / "What did it cost you the last time it went wrong?" | Rate by whether they name a dated incident (4–5) or only a vague dissatisfaction (1–2) | The problem asset: headline, opening frame of a video |
| **Pull** | "The magnetism of the new way… the vision of progress the customer can imagine for themselves" | "When you imagined it working, what did you picture yourself doing?" | Rate by specificity of the imagined outcome | The outcome asset: the after-state, the promise |
| **Anxiety** | "The fear of the unknown: 'What if it doesn't work? What if I look foolish?'" | "What nearly stopped you?" / "What did you check last before paying?" | Rate by how many distinct anxieties they name unprompted | The proof asset: guarantee, ingredient list, patch test, before/after, return policy |
| **Habit** | "The comfortable inertia of what people already know and do" | "What did you have to stop doing?" / "Who else was used to the old way?" | Rate by how many other people/routines were disrupted | The transition asset: "add one step", migration help, keep-your-old-thing framing |

**Scoring output (bún bò, n=11 switchers):**
```
Push    3.8  ("cũ đổi chủ, nước lèo nhạt hẳn" — a dated, specific degradation event, cited by 7/11)
Pull    2.4  (vague: "nghe nói ngon")
Anxiety 3.1  ("sợ dở mà vẫn phải trả tiền"; "sợ đông, trễ giờ làm")
Habit   4.2  (9/11 had used the same shop >2 years; 6/11 go with the same colleague)
Net = (3.8 + 2.4) − (3.1 + 4.2) = −1.1  -> switching does NOT happen spontaneously
```
Interpretation with a concrete action: because habit dominates, acquisition cannot rely on being better; it must rely on a **habit-breaking event** (a new shop opening moment, a free-first-bowl for the building next door, a lunchtime slot where the incumbent is closed) and on **anxiety reduction** (visible price, visible kitchen, a "not good? don't pay" guarantee). Copy that only argues quality will fail. This is the kind of conclusion the four forces exist to produce; a four-forces diagram with no numbers and no action is decoration.

### 7.3 Review mining as a systematic method

**Where to mine**

| Business type | Primary | Secondary | Unfiltered |
|---|---|---|---|
| Local F&B, Vietnam | Google Maps reviews; ShopeeFood + GrabFood reviews | Facebook page reviews and comment threads | TikTok comment sections on videos tagged to the shop; local Facebook groups ("Ăn gì ở Đà Nẵng") |
| DTC skincare, Vietnam | Shopee product reviews + Q&A; TikTok Shop reviews | Retailer product pages (Hasaki, Guardian); Lazada | Facebook skincare groups; Reddit r/AsianBeauty (English-language signal, different buyer) |

**Sampling protocol (the part everyone skips)**
1. **Frame:** all reviews for the top N=8 competitors in the trade area/frame, last 18 months. State N, the window, and the platforms.
2. **Stratify by rating, do not take the most recent:** up to 40 five-star, 40 one-and-two-star, and 40 three-star per competitor. **Three-star reviews carry the highest diagnostic density and are the most systematically under-read** — they contain the trade-off the customer accepted.
3. **Minimum viable sample:** ≥150 coded reviews total and ≥25 per competitor, or the finding is labelled low-confidence and cannot support a recommendation.
4. **Codebook:** open-code the first 30 reviews, then close the codebook at **8–14 codes**. More than 14 codes cannot be applied consistently by one analyst.
5. **Reliability test:** re-code 20 reviews after a 24-hour gap. If your own agreement with yourself is < 80%, the codebook is too vague — merge codes and repeat.
6. **Quantify** each code: n mentions, % of coded reviews, % of 1–2★ reviews, verbatim exemplar, and competitor skew (which competitor over-indexes).
7. **Rank** by frequency × valence intensity, not frequency alone. A code appearing in 12% of reviews with furious language outranks one in 30% with mild language.

**Worked output (illustrative structure, bún bò, 168 coded reviews across 8 shops)**

| Code | n | % of coded | % of 1–2★ | Verbatim exemplar | Skew |
|---|---|---|---|---|---|
| Broth too sweet / MSG-forward | 34 | 20.2% | 41% | "nước lèo ngọt đường, không ra vị bún bò" | Shops C, F |
| Wait too long at peak | 28 | 16.7% | 33% | "chờ 15 phút, trễ giờ làm" | Shops A, B |
| Portion shrank / price rose | 21 | 12.5% | 29% | "lên giá mà tô nhỏ lại" | Shops B, E |
| Hot / no fan / cramped | 19 | 11.3% | 22% | "nóng quá, ngồi không nổi" | Shops D, G |
| Sold out before 09:00 | 14 | 8.3% | 10% | "đến 8h30 là hết" | Shop A |
| Delivery arrived cold / spilled | 13 | 7.7% | 31% | "ship tới nguội, nước tràn hết" | Shops C, H |
| Consistent for years (positive) | 24 | 14.3% | 0% | "10 năm vẫn một vị" | Shop A |
| Owner remembers my order (positive) | 15 | 8.9% | 0% | "cô chủ nhớ mình không hành" | Shops A, E |

Note the two positives: **consistency** and **being remembered** are the moat the incumbents actually have — which is the same conclusion the four-forces habit score reached. Two independent methods converging is what "Triangulated" confidence means.

**Biases to state explicitly, every time**
- Reviews over-represent the extremes; the modal satisfied customer never writes.
- Delivery failures are over-represented because the platform prompts a review at the failure moment.
- Shopee's coin/voucher incentives inflate 5★ volume; Google Maps reviews in Da Nang skew tourist and English-language. **Report per platform, never pooled.**
- Review rate varies 1–10% by category (§5.3), so review counts measure attention, not sales.
- Recency: weight the last 12 months more heavily; an 18-month-old complaint may already be fixed. Always check whether the complaint recurs in the most recent 90 days before acting on it.

### 7.4 The language-capture rule

**Every customer-facing phrase in the eventual copy must be traceable to a verbatim in the evidence file, or be flagged as invented.** Maintain a verbatim bank with source, date, platform and rating.

| Invented marketing phrasing | Verbatim from evidence | Use |
|---|---|---|
| "authentic traditional broth" | "nước lèo đậm vị sả và ruốc, không ngọt đường" | Headline; and it doubles as a product spec |
| "fast service" | "gọi là có, 3 phút có tô, kịp giờ làm" | Ad body; and it sets an operational target of ≤3 min |
| "advanced brightening complex" | "da mình xỉn, chụp ảnh phải kéo sáng" | Problem-aware ad opening |
| "clinically inspired formula" | "sợ dùng đồ mạnh xong da bong tróc" | Anxiety asset — drives the patch-test panel, not a claim |

Note the second-order benefit: verbatims frequently contain a **measurable operational target** ("3 phút") that a generic phrase does not. Language capture improves the operation, not just the copy.

### 7.5 Pain/gain map that drives copy

Four columns, one row per code from §7.3, ranked. Nothing enters the copy that is not on this map.

| Pain (verbatim) | Frequency | Gain the customer names | Proof we can actually show | Asset it becomes |
|---|---|---|---|---|
| "nước lèo ngọt đường" | 20.2% | broth that tastes of lemongrass and shrimp paste, not sugar | published recipe ratio; no-MSG statement we can stand behind; open kitchen | Hero video: broth being built, 25s |
| "chờ 15 phút, trễ giờ làm" | 16.7% | out the door in under 8 minutes | stopwatch guarantee posted on the wall; measured median service time | On-wall promise + ad line |
| "lên giá mà tô nhỏ lại" | 12.5% | knowing what I get for what I pay | photographed portion with weight in grams on the menu | Menu photo set |
| "nóng quá" | 11.3% | sit down comfortably for 10 minutes | air-con + seated tables (the §6.5 gap) | Interior still, 07:10 light |
| "đến 8h30 là hết" | 8.3% | still available when I arrive late | stated daily quantity and a "still serving" status | Zalo/status post asset |

**Rule:** a pain with no showable proof does not become an asset. It becomes an operations task first.

<!--PART4-->


