# Rewrite human — one draft, worked end to end

A coffee roaster's About-us paragraph, the kind produced by asking a model for "professional
marketing copy". Every sentence is grammatical. The paragraph says nothing a buyer can check.

## Run it

```bash
python ../../../scripts/rewrite_human.py --check 01-draft-vi.md
python ../../../scripts/rewrite_human.py --check 02-rewrite-vi.md
python ../../../scripts/rewrite_human.py --check 03-transcreation-en.md
```

The first exits non-zero and names six blocking failures. The other two exit zero.

| File | What it is |
|---|---|
| `01-draft-vi.md` | The draft as received. Four sentences, no checkable fact |
| `02-rewrite-vi.md` | The rewrite. Same product, facts supplied from the shop |
| `03-transcreation-en.md` | English built from the same facts, not translated from the Vietnamese |

## What the numbers showed

The draft measured CV 0.10 against a target of 0.45 — four sentences within a syllable or two of
each other, which is the flatness a reread cannot see. It also had no landing beat at all: every
claim arrived mid-sentence, so nothing landed. Four calques fired, including `một trong những
đơn vị hàng đầu` and `chất lượng cao`.

Both were symptoms of the same thing. The draft had nothing to say, so no sentence had a reason
to be short and no claim had a place to land. Rhythm could not have been fixed first. The facts
came from the shop — batch size, roast date on the bag, the price, the seven-day swap — and the
cadence followed from where those facts needed a beat.

Note the length. The rewrite carries seven checkable facts and is barely longer than the draft
that carried none.

## Why the English is not a translation

The Vietnamese middle paragraph is three sentences; the English is four. `Không thấy ngày rang
thì đừng mua, của ai cũng vậy` became two sentences in English, because English wants the
aside to stand on its own — `No date, no sale. That goes for anyone's beans, not just ours.`

That is the test. If the sentence count had survived intact, the words were translated and the
decisions behind them were thrown away. Prices, the roast mechanism and the swap window match
exactly. Rhythm and sentence boundaries do not, and should not.


---

# 01 — Draft (VI)

Chúng tôi tự hào là một trong những đơn vị hàng đầu trong lĩnh vực cung cấp cà phê rang xay tại Việt Nam. Với đội ngũ nhân viên giàu kinh nghiệm và nhiệt huyết, chúng tôi cam kết mang đến cho quý khách hàng những sản phẩm chất lượng cao nhất. Sản phẩm của chúng tôi được sản xuất theo quy trình khép kín, đảm bảo vệ sinh an toàn thực phẩm. Hãy liên hệ với chúng tôi ngay hôm nay để được tư vấn miễn phí và nhận được những ưu đãi hấp dẫn nhất.


---

# 02 — Rewrite (VI)

Cà phê rang tại xưởng ở Gò Vấp, giao trong ngày cho quán trong bán kính 8km.

Robusta Đắk Lắk, rang theo mẻ 12kg rồi đóng túi van một chiều ngay khi vừa nguội, nên túi bạn mở ra tuần này là mẻ rang tuần này chứ không phải hàng tồn kho từ tháng trước. Ngày rang in dưới đáy túi. Không thấy ngày rang thì đừng mua, của ai cũng vậy.

195.000đ/kg. Từ 5kg còn 175.000đ. Uống không hợp gu thì đổi mẻ khác trong 7 ngày, mở túi rồi vẫn đổi.

Gọi 0938 xxx xxx, gửi mẫu 200g miễn phí.


---

# 03 — Transcreation (EN)

We roast in Go Vap and deliver the same day, anywhere inside 8km.

Dak Lak robusta, roasted in 12kg batches and bagged with a one-way valve the moment it cools, so the bag you open on Tuesday was roasted this week rather than sitting in a warehouse since March. The roast date is stamped on the base. No date, no sale. That goes for anyone's beans, not just ours.

195,000d a kilo. 175,000d from five kilos up. If it is not your taste, swap it for another batch within seven days, opened bag and all.

Call 0938 xxx xxx and we will send 200g free.
