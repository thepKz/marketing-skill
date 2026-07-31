# Marketing-Minthep

<p align="right">
  <a href="README.md"><kbd> &nbsp; English &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; <b>Tiếng Việt</b> &nbsp; </kbd></a>
</p>

Một skill marketing all-in-one cho Claude Code và GPT/Codex. Nó biến một brief chưa hoàn chỉnh — kể cả câu *"tôi không biết gì về marketing"* — thành một hệ thống có thể sản xuất và đo lường được: định vị, offer, content, campaign, ảnh sản phẩm, thiết kế menu và bố cục, chuỗi shot video, và một hợp đồng đo lường.

Một lần gọi, nhiều workbench. Skill chỉ nạp phần kiến thức mà công việc hiện tại cần, thay vì đổ toàn bộ marketing vào một prompt khổng lồ.

```text
$marketing-minthep
```

## Mục lục

- [Skill tạo ra gì](#skill-tạo-ra-gì) · [Gọi skill lên thì nó làm gì](#gọi-skill-lên-thì-nó-làm-gì) · [Cách nó quyết định](#cách-nó-quyết-định) · [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Năm phần thường gây khó hiểu](#năm-phần-thường-gây-khó-hiểu) — copywriting, edit ảnh, xây campaign, màu sắc, bố cục
- [Những câu hỏi phía sau các tool còn lại](#những-câu-hỏi-phía-sau-các-tool-còn-lại) — giá và offer, prompt, KPI, người ảo, test, khối lượng việc
- [Output mẫu](#output-mẫu) · [Thư viện reference](#thư-viện-reference) · [Cổng chống AI-slop](#cổng-chống-ai-slop)
- [Cấu trúc repo](#cấu-trúc-repo) · [Kiểm tra](#kiểm-tra) · [Những gì skill không làm](#những-gì-skill-không-làm)

## Skill tạo ra gì

Chín pipeline, mỗi pipeline có hợp đồng deliverable cố định:

| Pipeline | Deliverable | Output tiêu biểu |
|---|---|---|
| `plan-from-zero` | 16 | Bằng chứng thị trường, audience, định vị, offer, message ladder, copy pack, lịch, ngân sách và đo lường |
| `deep-research` | 9 | Tách câu hỏi, phân tầng nguồn, phép tính sizing, đối chiếu ba nguồn, độ tin cậy, source map |
| `image-from-reference` | 10 | Role map cho reference, locks/freedoms/rejects, chọn provider, 4–5 nhánh có kiểm soát, QA |
| `design-render` | 9 | Các hướng thiết kế, hệ đã chọn, menu/wireframe/key visual render thật, handoff in ấn và export |
| `video-campaign` | 9 | Shot list mang continuity, prompt từng shot, âm thanh, edit plan, cutdown theo nền tảng |
| `optimize-iterate` | 7 | Lineage của asset, log thử nghiệm, read-out, đề xuất test kế tiếp |
| `rewrite-human` | 4 | Chẩn đoán một bản nháp bằng số đo, bản viết lại, và đã sửa gì vì sao |
| `score-kpi` | 4 | Định nghĩa chỉ số, trọng số, tỉ lệ hoàn thành, và tỉ lệ đó được tính theo nhánh nào |
| `virtual-model` | 6 | Một người mô tả bằng số, một seed dựng lại đúng người đó, các look trang phục, prompt đã biên dịch |

Ba pipeline cuối ngắn là có chủ đích. Viết lại một đoạn không phải là làm campaign, và bắt người ta mở một kế hoạch mười sáu deliverable để sửa một đoạn văn là cách nhanh nhất để không ai dùng tool nữa.

Mười business job được route bên trong các pipeline đó, định nghĩa ở [`references/marketing-system-router.md`](marketing-minthep/references/marketing-system-router.md): `strategy-offer`, `campaign-launch`, `content-distribution`, `commerce-merchandising`, `pr-communications`, `sales-enablement`, `creator-ugc`, `lifecycle-retention`, `creative-production`, `measurement-optimization`.

Các nhóm sản phẩm đã có playbook riêng và yêu cầu proof riêng: beauty, fashion, food & beverage, điện tử, đồ gia dụng, trang sức/luxury, SaaS, dịch vụ địa phương, giáo dục, hospitality.

## Gọi skill lên thì nó làm gì

Không phải một đoạn chat. Một thư mục. Đây là một lần chạy thật, từ đúng câu mà một chủ shop sẽ gõ ra:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi mở shop mỹ phẩm nhỏ ở Gò Vấp, không biết gì về marketing, muốn có kế hoạch và ảnh sản phẩm đẹp, ngân sách nhỏ" --root .
```

Nó chấm điểm cả chín pipeline theo câu chữ và cho xem điểm — `plan-from-zero` 3 điểm, sát nhất là `deep-research` 1 điểm — rồi ghi ra 34 file. Mười ba deliverable song ngữ Việt và Anh đặt cạnh nhau, một file intake trích nguyên văn câu bạn viết, `claims.csv` và `sources.md` cho những chỗ sau này phải dẫn nguồn, một log quyết định, và một `README.md` mục lục mà đoạn thứ hai của nó là phần đáng đọc nhất:

> Read from the request: horizon **13 weeks** (assumed, not stated); budget **small** (from "ngân sách nhỏ"); product family **beauty** (from "mỹ phẩm"). Correct any of these in `01-intake` first — everything downstream is built on them.

Ba suy luận, mỗi cái ghi kèm cụm từ đã đọc được, và cái không có gì đứng sau thì ghi rõ là do skill tự mặc định. File lịch đã được đặt tên `10-calendar-13w` ngay từ đầu, vì horizon nó nhận là một con số thật chứ không phải chỗ trống.

Bên trong một deliverable, mỗi phần hoặc là hỏi bạn thứ chỉ bạn biết, hoặc là gọi tên đúng câu lệnh giải quyết nó:

```markdown
## CAC ceiling

> WRITE: Derive from contribution margin, repeat rate, and acceptable payback period. Show the calculation.

> RUN: python scripts/price_offer.py --price PRICE --variable-cost COST --repeat-purchases N
> --acquisition-cost CAC — two ceilings, and the report names which one binds. Do not hand-calculate this.
```

Cái marker thứ hai có mặt chính vì lần chạy thử này. Bản đầu tiên bắt chủ shop tự tính trần CAC bằng tay, trong khi script tính đúng chuyện đó nằm không ai dùng ngay trong repo. Giờ có 24 phần mang theo câu lệnh trả lời cho chúng, và dòng đó nằm lại trong file đã hoàn thiện như phần dẫn nguồn cho con số phía trên nó.

Không có file nào tự nhận là đã xong. Mọi file mở ra ở `status=empty`, mọi phần chưa viết là một marker `> WRITE:`, và `run_status.py --strict` đếm cả những phần đó lẫn những phần đã viết đầy mà không bảo vệ được.

## Cách nó quyết định

Scaffold đọc chính câu bạn viết trước khi lập bất cứ kế hoạch nào. `scripts/_signals.py` rút ra bốn dữ kiện từ cách bạn diễn đạt, tiếng Việt hay tiếng Anh, có dấu hay không dấu:

| Signal | Đọc từ | Tác dụng |
|---|---|---|
| Horizon chiến dịch | `"trong 6 tuần"`, `"in 8 weeks"`, `"90 ngày"` | Đặt tên và chia lịch thành các phase cộng lại đúng bằng horizon |
| Áp lực ngân sách | `"ngân sách nhỏ"`, `"tight budget"` | Giới hạn số asset và bỏ những kênh mức đó không với tới, kèm lý do |
| Nhóm sản phẩm | `"bún bò"`, `"serum"`, `"homestay"` | Chọn playbook và yêu cầu proof tương ứng |
| Thị trường | `"Sài Gòn"`, `"Đà Lạt"` | Chuyển sang ngữ cảnh thị trường Việt Nam và chiến thuật một điểm bán |

Cả bốn đều được dán nhãn `inferred` và mang theo đúng cụm từ mà nó đọc được, vì một horizon do bạn nói ra không cùng loại dữ kiện với một horizon do skill mặc định. `01-intake` mở đầu bằng câu yêu cầu của bạn được trích nguyên văn, ngay trên bảng nhãn đó. Sửa một suy luận sai ở đó thì mọi thứ phía sau đi theo.

Dữ kiện được dán nhãn xuyên suốt: `confirmed` (bạn đã nói), `observed` (tìm thấy trong nguồn có dẫn), `inferred` (suy ra từ câu chữ), `unknown`. Một ô `unknown` — nhất là giá bán một đơn vị và biên lợi nhuận — phải được bạn trả lời, hoặc phải có một giả định viết rõ bên cạnh. Nó không bao giờ được điền bằng một con số nghe hợp lý.

Ba độ rộng: `focused` (bộ nhỏ nhất dùng được, mặc định), `system` (strategy nối với kênh và đo lường), `production` (thêm manifest JSON, prompt cho provider, owner, phê duyệt, naming, handoff export). Kế hoạch từ số 0 và deep research bắt đầu ở `system`. Menu, edit ảnh và video tự nâng lên `production` khi request có `render`, `export`, `xuất file`, `MP4` hoặc yêu cầu in.

## Bắt đầu nhanh

Cài vào cả hai CLI, ở mức global:

```powershell
python marketing-minthep/scripts/install_global.py
```

Lệnh này ghi vào `~/.claude/skills/marketing-minthep` và `~/.codex/skills/marketing-minthep`. Repo cũng có adapter mức project ở `.claude/skills/` và `.codex/skills/`; cả hai đều nạp `marketing-minthep/SKILL.md` làm nguồn duy nhất, nên đừng bao giờ sửa nội dung marketing bên trong adapter.

Tạo workspace thật từ một câu:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi không biết marketing, hãy làm kế hoạch từ đầu cho quán bún bò" --root .
```

Campaign brief suy ra hoàn toàn từ câu yêu cầu — horizon, ngân sách, ngành, kênh đều đọc từ đó:

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "Tôi bán bún bò ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng, ngân sách nhỏ"
```

Ghi đè khi bạn biết rõ hơn suy luận của nó:

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --project "Launch" --job campaign-launch --industry beauty --provider gpt-image-2 --channels meta tiktok web
```

Kiểm tra một run trước khi coi là xong:

```powershell
python marketing-minthep/scripts/run_status.py --strict
```

`--strict` báo lỗi cả với deliverable rỗng *và* với deliverable đã điền nhưng không bảo vệ được: số không có nguồn, placeholder còn sót, section mỏng đến mức chỉ là chữ lấp chỗ. Một scaffold không phải một báo cáo, và một file đầy chữ không tự động là một file đứng vững được.

Mỗi run có `_meta/render-capability.json`, khởi điểm ở `not-rendered`. Prompt, storyboard, wireframe SVG và provider plan không bao giờ được gọi là ảnh hay video đã render.

## Năm phần thường gây khó hiểu

Mỗi phần có một dossier chuyên sâu, một bảng tra trong `data/`, và một lệnh tạo ra thứ mình xem được bằng mắt. Tra bảng, đừng nhớ trong đầu: một con số craft nhớ ra là một phỏng đoán, còn một dòng trong bảng là quyết định đã có người viết xuống kèm lý do.

### Copywriting

```powershell
python marketing-minthep/scripts/find_recipe.py --table copy --query "tiêu đề"
```

22 công thức trong `data/copy-formulas.csv`, mỗi cái kèm một ví dụ tiếng Việt và một ví dụ tiếng Anh viết sẵn. Không ví dụ nào chứa số in được — mọi giá, giờ và phần trăm đều là `[slot]`, vì một mẫu mang theo con số trông hợp lý chính là cách một lời khẳng định bịa ra đi tới tay khách. Thang là `tension → promise → mechanism → proof → action`, và nó là một cái thang vì không được bỏ bậc: promise mà không có mechanism thì chỉ là slogan, mechanism mà không có proof thì chỉ là một lời khẳng định. Đọc [`references/copywriting.md`](marketing-minthep/references/copywriting.md) cho copy pack theo kênh, và [`references/dossiers/copywriting-deep.md`](marketing-minthep/references/dossiers/copywriting-deep.md) cho craft ở mức từng câu — cụ thể thay vì xếp tính từ, cái phản đối phải tự nêu trước khi người đọc nêu, và vì sao "chất lượng cao" không phải một lợi ích.

### Edit ảnh

```powershell
python marketing-minthep/scripts/find_recipe.py --query "giao đồ ăn"
python marketing-minthep/scripts/find_recipe.py --brief dish-delivery --palette paper-cobalt
python marketing-minthep/scripts/find_recipe.py --checklist dish-delivery
```

Tìm theo công việc, bằng tiếng Việt hoặc tiếng Anh — không tìm theo tên style. `data/image-recipes.csv` có 39 công việc, trong đó sáu cái thị trường Việt Nam cần mà chưa nơi nào có dòng riêng: xe máy giao hàng, sạp chợ, bố cục Tết, mặt cắt bánh mì, quầy bún, khói than. `--brief` soạn payload cho `compile_prompt.py` và để nguyên `TBD` những gì chỉ chủ hàng biết, kèm lý do; nó không tự bịa `product_truth`. `--checklist` lọc 33 dấu hiệu trong `data/slop-tells.csv` xuống còn những cái áp cho recipe đó, xếp theo mức nặng — checklist đồ uống hỏi về hơi nước đọng, checklist before-after hỏi xem ảnh "after" có phải chỉ là được chiếu sáng đẹp hơn. Mở nó ra trong lúc xem render; đọc lại prompt thì không chứng minh được gì.

Hai sheet nữa giải thích những phần trong brief mà người không làm marketing chưa có từ để gọi. `--sheet lighting` vẽ sáu setup nhìn từ trên xuống thành vị trí đèn, với bóng tính ra từ chỗ đặt key, để "45/45 soft key" thôi là biệt ngữ. `--sheet frames` vẽ năm placement theo đúng tỉ lệ thật và tô những dải bị chiếm — khung story là cái cho thấy vì sao story phải bố cục lại chứ không crop từ post feed.

Edit không phải generate. Đường đi là: soi ảnh gốc, dựng **lock map**, gọi một năng lực edit thật, rồi so kết quả với các lock. Trên ảnh người thật, edit makeup chỉ đổi pigment và finish trên bề mặt; head shape, hình học và khoảng cách mắt, mí, mũi, môi, xương hàm, chin, tai, hairline, tone da, tuổi thể hiện, độ bất đối xứng, biểu cảm và hướng nhìn đều bị khóa. Edit outfit chỉ đổi trang phục. Nếu không có năng lực edit thật, skill trả về một prompt edit chạy được kèm chỉ dẫn mask chính xác, và nói thẳng là chưa render gì. Xem [`references/image-editing.md`](marketing-minthep/references/image-editing.md).

### Xây campaign

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "..."
```

Brief tách hai thứ trước đây cùng in ra `TBD`: **UNKNOWN** là chưa ai nói và kế hoạch bị chặn đến khi có câu trả lời; **TBD** là việc của mình, chỉ chưa quyết. Asset xen kẽ giữa các kênh và mang một funnel stage, thay vì là tích Descartes của kênh nhân định dạng — đó là một phép nhân, không phải một kế hoạch. Xem [`references/campaign-systems.md`](marketing-minthep/references/campaign-systems.md).

### Màu sắc

```powershell
python marketing-minthep/scripts/render_refsheet.py --sheet palettes --output palettes.svg --html-output palettes.html
```

Lệnh đó vẽ cả 20 palette trong `data/palettes.csv` thành vùng màu thật với một cái nút thật trên mỗi cái, và in tỉ lệ tương phản đo được ở dưới. Năm cột cuối của bảng là tính ra, không phải khai ra: hai trong hai mươi accent thật sự không đạt 3:1 so với nền và bị đánh dấu `fill only — too close to the background for text or hairlines`, hữu ích hơn một bộ palette mà cái nào cũng đạt. Palette được dựng, không phải được chọn. Dossier [`references/dossiers/colour-science-and-harmony.md`](marketing-minthep/references/dossiers/colour-science-and-harmony.md) nói về độ sáng cảm nhận so với trực giác đọc mã hex, tỉ lệ tương phản còn sống nổi trên màn hình điện thoại giữa nắng, khác biệt giữa một màu thương hiệu và một accent chỉ xuất hiện đúng một lần, và chuyện gì xảy ra với palette khi sang CMYK. `references/composition-light-color.md` nối nó với camera, ánh sáng và grade.

### Bố cục

```powershell
python marketing-minthep/scripts/plan_design_options.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json
python marketing-minthep/scripts/render_mockup.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json --output out.svg --html-output out.html
python marketing-minthep/scripts/render_social_post.py --input marketing-minthep/assets/examples/bun-bo/post-story.json --output story.svg
python marketing-minthep/scripts/render_refsheet.py --sheet dials --dial margin_ratio --output dials.svg --html-output dials.html
```

Cơ chế là một nhúm con số, và cách trung thực duy nhất để giải thích một con số là cho xem cùng một thứ hai lần với con số đó bị đổi. `data/layout-dials.csv` gọi tên 17 con số — tỉ lệ lề, tỉ lệ tiêu đề, bước dòng món, leading — mỗi cái có min, max, ba giá trị mặc định theo phong cách, nâng lên thì đổi cái gì, và vỡ ở đâu. `--sheet dials` vẽ đúng một menu bún bò bốn món ba lần ở min, mặc định và max, chỉ dial đang xét là dịch chuyển. Đưa cái đó cho người ta xem thay vì mô tả.

```powershell
python marketing-minthep/scripts/find_recipe.py --table ratios --query "reels"
python marketing-minthep/scripts/find_recipe.py --table grids --query "tỉ lệ vàng"
python marketing-minthep/scripts/render_refsheet.py --sheet ratios --output ratios.svg --html-output ratios.html
```

"Có nên dùng tỉ lệ vàng không?" là câu hỏi bố cục hay gặp nhất, và câu trả lời gần như luôn là không — nhưng "không" thì không dùng được, nên hai bảng này trả lời bằng số học chứ không bằng cảm nhận. `data/frame-ratios.csv` có 13 tỉ lệ, khóa theo chỗ tấm ảnh sẽ đi, vì câu hỏi đến dưới dạng *"cho Reels"* hoặc *"in ra giấy A4"*, chưa bao giờ dưới dạng *"9:16"*. `data/composition-grids.csv` xếp hạng bằng chứng cho bảy cái lưới người ta hay tranh nhau, và xếp hạng không hề dễ nghe: xoắn ốc vàng là `myth` — nó xoay, phóng, lật được thành tám hướng, nên trong bất cứ tấm ảnh nào cũng có thứ nằm trên một nhánh nào đó của nó, và một phép thử không thể trượt thì không phải phép thử. Lưới phi là `myth-adjacent`: số học thì đúng, còn cái khác biệt nó đang khẳng định là 38,2% so với 33,3% của chia ba, tức 4,9 điểm phần trăm, tức 53 px trên bề ngang 1080 px. Chia ba là `peer-reviewed-contested` — Amirshahi 2014 thấy điểm chia ba gần như không tương quan với đánh giá thẩm mỹ trên 2.415 tấm, còn Hoh & Zhang 2023 thấy người ta chọn chủ thể ở giữa khi phải chọn một trong hai.

Chỉ `w` và `h` được lưu. Mọi vị trí đều tính ra từ một hàm duy nhất, nên bảng không thể tự mâu thuẫn với chính nó và sheet không thể nói khác bảng. Cái đáng đọc là *khoảng lệch*: trên hình vuông, mắt đối xứng động chính là tâm và cách đường chia ba 180 px; trên 16:9 nó ở 24% và cách 179 px; trên scope nó ở 14,9% và cách 377 px; còn trên 3:2 nó cách 42 px — dưới 5% khung, nên không ai chỉ ra được và lựa chọn đó là rỗng. `--sheet ratios` vẽ cả mười hai tỉ lệ phát hành theo đúng tỉ lệ thật với cả ba lưới đặt lên từng khung, và đó là cách kết quả bất ngờ duy nhất hiện ra bằng mắt: trên giấy A4 theo ISO, đường chia ba màu xám biến mất hẳn dưới đường mắt màu xanh, vì h² = 2w² đặt mắt đúng vào ⅓. Root-2 là tỉ lệ duy nhất mà hai cái lưới là cùng một cái lưới.

Phép đo dừng ở chỗ đo. Nó báo khoảng lệch và không bao giờ nói nên dùng lưới nào, vì 5:4 lệch 5,7% mà vẫn muốn đặt giữa — nó gần vuông. Lời khuyên nằm trong dòng của bảng.

Bộ render đo chữ rồi dòng chữ chảy theo phép đo đó. Không có gì được đặt theo một phân số của chiều cao canvas — cách cũ đó đã tạo ra dấu tiếng Việt cắt xuyên dòng kicker và một tiêu đề bị vẽ chồng dưới ảnh hero. Copy không vừa chỗ sẽ báo lỗi thay vì bị cắt âm thầm, vì một mockup lặng lẽ xóa hai phần ba câu vẫn trông như đã hoàn thiện, và đó chính là chỗ nguy hiểm. Bộ render post thêm một ràng buộc mà menu không có: nền tảng tự vẽ nút của nó lên trên canvas, nên mỗi placement khai báo sẵn những dải nó không được dùng, và một khối chữ chạm vào CTA sẽ báo lỗi kèm số pixel bị lấn. Dossier: [`layout-wireframe-typography.md`](marketing-minthep/references/dossiers/layout-wireframe-typography.md), [`composition-and-layout-vision.md`](marketing-minthep/references/dossiers/composition-and-layout-vision.md), [`menu-design-and-engineering.md`](marketing-minthep/references/dossiers/menu-design-and-engineering.md).

## Những câu hỏi phía sau các tool còn lại

Năm phần ở trên là những gì người ta hỏi thành tiếng. Mấy phần dưới đây là những gì quyết định một kế hoạch có sống sót khi gặp phép tính hay không. Mỗi phần là một câu lệnh, và mỗi câu lệnh trả về một phán quyết — `passed`, `failed`, `skipped` hoặc `review` — chứ không phải một nhận xét.

### "Giảm giá mức này tôi có gánh được không?"

```powershell
python marketing-minthep/scripts/price_offer.py --price 280000 --variable-cost 112000 --discount 0.20
```

> Giảm 20% giá bán làm mất 33% phần đóng góp, không phải 20%. Muốn giữ nguyên lãi gộp thì phải bán 1.50 lần số lượng.

Đó là toàn bộ lý do đơn vị này tồn tại. Giảm 20% không tốn 20%; nó tốn một phần của contribution, và phần đó phụ thuộc vào biên của bạn. Cùng câu lệnh này suy ra ROAS hoà vốn bằng nghịch đảo của tỉ lệ contribution — ở đây là 1.67 — nên một chỉ tiêu ROAS ai đó giao xuống có thể kiểm trước khi nhận, và ra hai trần CAC khi có số lần mua lại, kèm câu trả lời trần nào đang chặn. Chính sách bảo hành đổi trả cũng là một khoản chi phí: đưa tỉ lệ trả hàng dự kiến vào rồi đọc lại contribution. [`references/pricing-and-offers.md`](marketing-minthep/references/pricing-and-offers.md).

### "Provider này có làm đúng thứ prompt tôi viết không?"

```powershell
python marketing-minthep/scripts/check_prompt_grammar.py --prompt-file prompt.txt --provider flux
```

`data/prompt-grammar.csv` có 69 dòng trên tám trục — cửa sổ encoder, negative prompt, chữ trong ảnh, seed, giữ nhân vật nhất quán, quyền sở hữu, quyền hình ảnh — mỗi dòng kèm đúng URL của nhà cung cấp và một cột ghi rõ dòng đó *không* chứng minh được điều gì. Năm trong chín họ mô hình không hề công bố trường negative prompt, nghĩa là gửi cho họ một câu loại trừ chính là đưa thứ cần loại trừ vào trong prompt. Checker tìm ra đúng lỗi đó trong compiler của repo này ngay lần chạy đầu: một brief yêu cầu *không có da nhựa* đang gửi chữ *da nhựa* sang FLUX. Hai loại giới hạn độ dài được giữ riêng có chủ đích, vì cửa sổ encoder âm thầm cắt mất phần đuôi còn giới hạn ký tự của API thì từ chối thẳng request. Mười một câu hỏi không nhà cung cấp nào trả lời được ghi lại thành khoảng trống chứ không điền cho đủ, và [`references/prompt-grammar.md`](marketing-minthep/references/prompt-grammar.md) liệt kê chín điều mà cả cái thể loại "tips viết prompt" trên mạng đang nói sai, trong đó có ba tham số không còn tồn tại ở phiên bản mà người ta vẫn dẫn.

### "Nên báo cáo con số nào, và có thật là đã đạt chưa?"

```powershell
python marketing-minthep/scripts/find_recipe.py --table kpi --query "retention"
python marketing-minthep/scripts/score_kpi.py --input scorecard.json
```

27 chỉ số đo được trong `data/kpi-metrics.csv`, mỗi chỉ số kèm chiều nào là tốt, nó là chỉ số dẫn hay chỉ số trễ, và cách cụ thể mà nó bị lách — vì chỉ số nào cũng có cách đạt được mà thứ bên dưới không hề tốt lên, và nói thẳng cách đó ra là khác biệt giữa một scorecard và một cái chỉ tiêu. Tỉ lệ hoàn thành có bốn nhánh, tuỳ vào cao hơn có tốt hơn không, số 0 có phải là sàn không, và có được vượt chỉ tiêu không; chọn sai nhánh thì con số đổi mà độ hợp lý của nó không đổi. [`references/kpi-scorecards.md`](marketing-minthep/references/kpi-scorecards.md).

### "Test này đủ lớn để nói lên điều gì chưa?"

```powershell
python marketing-minthep/scripts/check_test_readout.py --plan --baseline 0.03 --mde 0.20
```

> Muốn nhìn thấy mức tăng tương đối 20% trên nền 3.00% thì cần 13911 mỗi nhánh, tổng 27822.

Biết được điều này lúc test còn rẻ thì tốt hơn là biết sau hai tuần đổ traffic. `--claim` đi chiều ngược lại, kiểm một bên thắng đã tuyên bố dựa trên khoảng tin cậy thay vì con số điểm: tăng 58% mà p = 0.29 thì không phải là kết quả, và bản đọc nói thẳng chuyện đó trong phán quyết chứ không nhét xuống chú thích.

### "Ảnh sau có còn là đúng người đó không?"

```powershell
python marketing-minthep/scripts/plan_virtual_person.py
```

Tính từ không dựng lại được một khuôn mặt. `data/person-parameters.csv` mô tả một người ảo trên 35 trục đo được, mười chín trục khoá lại làm danh tính, băm thành một seed ổn định để cùng một người render ra hai lần — và bản chạy nói rõ rằng chỉ đúng một nhà cung cấp công bố mức trần giữ nhân vật nhất quán, và mức đó là bốn nhân vật. Đơn vị pose là cùng một nguyên tắc áp cho cơ thể: một dáng được dẫn theo các trục có tên, chứ không tả là *thanh thoát*. Đây là một người được dựng ra, không bao giờ là người thật; skill sẽ không dựng chân dung giống ai từ ảnh mặt của người đó, và [`references/virtual-person-system.md`](marketing-minthep/references/virtual-person-system.md) ghi lại lý do như một lý do, không phải như một điều luật.

### "Bản này đọc có ra giọng người không?"

```powershell
python marketing-minthep/scripts/check_specificity.py --check draft.md
python marketing-minthep/scripts/rewrite_human.py --check draft.md --channel web
python marketing-minthep/scripts/check_address_register.py --check draft.md
```

Đúng thứ tự đó, và thứ tự chính là điểm chính. Sửa nhịp câu sẽ xoá mất chi tiết cụ thể, nên phải đếm số dữ kiện kiểm được trước: dưới ba dữ kiện thì bản nháp đang có vấn đề về nội dung, và từ đó mọi lần sửa nhịp chỉ làm nó đọc mượt hơn trong lúc vẫn không nói gì cả. Câu lệnh thứ ba chỉ dành cho tiếng Việt và giải quyết một chuyện mà style guide tiếng Anh không với tới — bài đang ở ngôi nào, và có giữ nguyên ngôi đó không, vì một trang mở đầu bằng *bạn* rồi kết bằng *quý khách* là đã đổi luôn cái nhìn về người mình đang nói với.

### "Rồi thứ Hai ai làm hết mấy việc này?"

```powershell
python marketing-minthep/scripts/plan_operating_load.py
python marketing-minthep/scripts/plan_composition_set.py --photos 3
```

Mười ba vai, chia ra cái nào chạy một lần và cái nào chạy mỗi tuần, quy ra giờ. Một kế hoạch kênh mà không ai có thời gian chạy thì chỉ là danh sách ước, và đây là file nói ra chuyện đó bằng một con số. Câu lệnh thứ hai trả lời đúng câu đó cho phần hình ảnh: với những tấm ảnh đã có sẵn, bao nhiêu khung mà kế hoạch này giả định là cắt được ra từ đó, và bao nhiêu khung phải chụp thêm.

## Output mẫu

Ba hướng menu cho cùng một quán bún bò, do `render_mockup.py` render từ spec trong `assets/examples/bun-bo/` — không API, không công cụ thiết kế:

| Modern street | Heritage craft | Quiet editorial |
|---|---|---|
| [SVG](docs/assets/generated/bun-bo-menu-modern-street.svg) | [SVG](docs/assets/generated/bun-bo-menu-heritage-craft.svg) | [SVG](docs/assets/generated/bun-bo-menu-quiet-editorial.svg) |

Hai post mẫu cho cùng quán đó, do `render_social_post.py` render. Bản story không phải bản feed bị cắt: nó được dựng lại ở 1080x1920 và để trống 250px trên cùng với 420px dưới cùng cho khung giao diện của ứng dụng, nên nút CTA không thể nằm sau khung trả lời tin.

| Feed 4:5 | Story 9:16 |
|---|---|
| [SVG](docs/assets/generated/bun-bo-post-feed.svg) | [SVG](docs/assets/generated/bun-bo-post-story.svg) |

```powershell
python marketing-minthep/scripts/render_social_post.py --input marketing-minthep/assets/examples/bun-bo/post-feed.json --output post.svg --html-output post.html --caption-output post-caption.md
```

`--caption-output` viết nửa còn lại của một bài đăng — caption, hashtag, alt text, dòng công bố tài trợ. Dòng nào không ai cung cấp thì in ra `UNKNOWN` kèm lý do, vì một caption bịa sai theo đúng cách một cái giá bịa sai: nó trông như đã xong, nên có người đem đăng.

Các hướng ảnh do `compile_prompt.py` biên dịch rồi render qua provider:

| Packshot | Key visual | Beauty campaign | Fashion look |
|---|---|---|---|
| <img src="docs/assets/generated/minthep-serum-packshot.png" width="180"> | <img src="docs/assets/generated/minthep-serum-key-visual.png" width="180"> | <img src="docs/assets/generated/minthep-beauty-campaign.png" width="180"> | <img src="docs/assets/generated/minthep-fashion-look.png" width="180"> |

Shot video đến từ `plan_video_sequence.py`, công cụ mang continuity đi tiếp: mỗi shot thừa hưởng trạng thái nhân vật, trang phục, hướng sáng, lens và grade của shot trước, nên prompt 4 không thể nói ngược prompt 3.

```powershell
python marketing-minthep/scripts/plan_video_sequence.py --input marketing-minthep/assets/examples/bun-bo/video-sequence.json --format prompts
```

## Thư viện reference

Một tấm reference tồn tại để được tách thành các thuộc tính có thể chuyển hóa — `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, `texture` — chứ không bao giờ để sao chép.

```powershell
python marketing-minthep/scripts/find_recipe.py --table axes
python marketing-minthep/scripts/render_refsheet.py --sheet reference --output reference.svg
```

Một nửa tấm ảnh bạn vừa đưa là của người khác: chữ, mặt, dáng, logo. Nửa còn lại không của ai — hình học khung, hướng sáng, đường mắt đi, tỉ lệ crop. `data/reference-axes.csv` chia ra 11 trục và phán quyết từng trục: bốn `keep`, năm `transform`, một `reject`, một `avoid`. `--sheet reference` vẽ cùng một tấm ảnh hai lần — một lần khoanh những phần thuộc về người khác, một lần chỉ còn lưới, hướng sáng và đường mắt đi — nên người không làm marketing vẫn thấy được nửa nào là nửa nào thay vì phải tin. Luật là đổi ít nhất ba trục trước khi dùng một reference; bảng này đổi năm. Nếu kết quả vẫn truy được về một nguồn ngay từ cái nhìn đầu, làm lại.

Còn ba ảnh trong `docs/assets/references/`, giấy phép CC0 và CC BY, kèm tác giả và nguồn trong `ATTRIBUTION.txt`. Mười bảy ảnh đã bị xóa ngày 2026-07-29: đó là ảnh chụp người thật có tên, và giấy phép ghi "bản quyền vẫn thuộc tác giả gốc" — một lời phủ nhận, không phải một sự cho phép. `test_tools.py` làm hỏng cả bộ test nếu có ảnh thứ tư vào đây mà không có dòng giấy phép.

Handbook tĩnh giải thích toàn bộ flow, có nút chuyển VI/EN:

```powershell
python -m http.server 8000 --directory docs
```

## Cổng chống AI-slop

[`references/anti-ai-quality.md`](marketing-minthep/references/anti-ai-quality.md) chạy trước khi giao hàng. Kiểm tra bậc một: có ai đoán được palette, model, prop, ánh sáng và bố cục chỉ từ *nhóm sản phẩm* không? Navy tối và purple glow cho AI software, mặt airbrush và tia nước cho beauty, gradient xanh và cái bắt tay cho corporate, đen với vàng với đá cẩm thạch cho luxury, phòng be và một cái lá xanh cho wellness. Nếu có, cue của nhóm sản phẩm bị thay bằng một mechanism của sản phẩm, một hành vi của audience, hoặc một vật liệu vật lý riêng của brief này.

Kiểm tra bậc hai bắt cửa thoát: sau khi từ chối cái nhìn hiển nhiên của nhóm sản phẩm, tác phẩm có rơi vào một mặc định thời thượng khác — editorial tiết chế chung chung, brutalist utility, maximalist acid graphics — mà không có lý do nào từ brief? Lane thị giác phải được đặt tên và được sản phẩm biện minh, không phải được biện minh bằng sở thích.

## Cấu trúc repo

```
marketing-minthep/
  SKILL.md                  điểm vào và bộ định tuyến, 173 dòng
  references/               61 file chủ đề, mỗi file dưới 150 dòng
    dossiers/               15 dossier craft chuyên sâu + index
  data/                     25 bảng tra: image recipe, palette, layout dial,
                            slop tell, copy formula, translation tell và
                            ngôi xưng, reference axis, frame ratio,
                            composition grid, chỉ số KPI và trọng số, cổng
                            màu, look và chẩn đoán makeup, tham số nhân vật,
                            prompt grammar, bố cục sản phẩm, benchmark,
                            nguồn dữ liệu thị trường, command artifact,
                            các vai marketer Việt Nam
  scripts/                  38 công cụ + bộ test
  assets/
    registries/             pipelines.json, asset-formats.json
    templates/              project-brief.json và khung deliverable
    examples/               input chạy được, gồm case study bún bò
    evals/                  routing case
docs/                       handbook tĩnh, VI/EN, deploy lên GitHub Pages
.claude/skills/  .codex/skills/    adapter mỏng trên cùng một SKILL.md
```

## Kiểm tra

```powershell
python -m unittest discover -s marketing-minthep/scripts -p "test_*.py"
python marketing-minthep/scripts/evaluate_workbench.py
python marketing-minthep/scripts/plan_marketing_system.py --input marketing-minthep/assets/examples/all-in-one-product-request.json
```

368 test, trong đó có test tính lại từng tỉ lệ tương phản trong `data/palettes.csv`, test fail nếu một ví dụ copy chứa số in được, test fail nếu một cờ năng lực dẫn tới dòng nguồn không tồn tại, và test fail nếu một deliverable gọi tên một script không có trong repo. `evaluate_workbench.py` chạy lại các routing case trong `assets/evals/`. `.github/workflows/deploy-pages.yml` kiểm tra cấu trúc, planner, manifest builder, unit test và biên dịch Python, rồi deploy `docs/` lên GitHub Pages.

## Những gì skill không làm

- Bịa claim, thành phần, thông số, giá, review, khách hàng, số liệu, chứng nhận, cue scarcity hay endorsement.
- Sao chép danh tính celebrity, phong cách của một living artist, một campaign, một tấm ảnh hay một layout đặc trưng. Reference được tách thành thuộc tính, hoặc không dùng.
- Làm gầy hay đổi hình thể một người thật trong ảnh edit.
- Trình bày một bao bì do AI tạo như ảnh chụp sản phẩm thật khi không có reference chính xác.
- Tự publish, liên hệ báo chí hay creator, mua ads, hay đổi campaign đang chạy. Những việc đó cần ủy quyền riêng.
- Gọi một prompt là ảnh, một storyboard là video, hay một kế hoạch là kết quả.

## Giới hạn vận hành

Spec nền tảng thay đổi; phải kiểm tra nguồn chính thức live trước khi export hoặc upload. Kết quả ảnh phụ thuộc provider, reference hợp lệ và năng lực render thực có tại thời điểm đó. Claim về PR, pháp lý, sức khỏe, tài chính, so sánh và các ngành bị quản lý cần bằng chứng và phê duyệt của chủ sở hữu. Skill này lập kế hoạch và tạo artefact; publishing, media buying, outreach và deployment vẫn là việc của bạn.

<p align="center">
  <a href="README.md"><kbd> &nbsp; English &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; <b>Tiếng Việt</b> &nbsp; </kbd></a>
</p>
