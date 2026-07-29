# Marketing-Minthep

[🇬🇧 English](README.md) · **🇻🇳 Tiếng Việt**

Một skill marketing all-in-one cho Claude Code và GPT/Codex. Nó biến một brief chưa hoàn chỉnh — kể cả câu *"tôi không biết gì về marketing"* — thành một hệ thống có thể sản xuất và đo lường được: định vị, offer, content, campaign, ảnh sản phẩm, thiết kế menu và bố cục, chuỗi shot video, và một hợp đồng đo lường.

Một lần gọi, nhiều workbench. Skill chỉ nạp phần kiến thức mà công việc hiện tại cần, thay vì đổ toàn bộ marketing vào một prompt khổng lồ.

```text
$marketing-minthep
```

## Mục lục

- [Skill tạo ra gì](#skill-tạo-ra-gì) · [Cách nó quyết định](#cách-nó-quyết-định) · [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Năm phần thường gây khó hiểu](#năm-phần-thường-gây-khó-hiểu) — copywriting, edit ảnh, xây campaign, màu sắc, bố cục
- [Output mẫu](#output-mẫu) · [Thư viện reference](#thư-viện-reference) · [Cổng chống AI-slop](#cổng-chống-ai-slop)
- [Cấu trúc repo](#cấu-trúc-repo) · [Kiểm tra](#kiểm-tra) · [Những gì skill không làm](#những-gì-skill-không-làm)

## Skill tạo ra gì

Sáu pipeline, mỗi pipeline có hợp đồng deliverable cố định:

| Pipeline | Deliverable | Output tiêu biểu |
|---|---|---|
| `plan-from-zero` | 16 | Bằng chứng thị trường, audience, định vị, offer, message ladder, copy pack, lịch, ngân sách và đo lường |
| `deep-research` | 9 | Tách câu hỏi, phân tầng nguồn, phép tính sizing, đối chiếu ba nguồn, độ tin cậy, source map |
| `image-from-reference` | 10 | Role map cho reference, locks/freedoms/rejects, chọn provider, 4–5 nhánh có kiểm soát, QA |
| `design-render` | 9 | Các hướng thiết kế, hệ đã chọn, menu/wireframe/key visual render thật, handoff in ấn và export |
| `video-campaign` | 9 | Shot list mang continuity, prompt từng shot, âm thanh, edit plan, cutdown theo nền tảng |
| `optimize-iterate` | 7 | Lineage của asset, log thử nghiệm, read-out, đề xuất test kế tiếp |

Mười một workbench nằm rải trên các pipeline đó: strategy và offer, campaign và launch, content và phân phối, commerce và merchandising, paid media, PR, sales enablement, creator và UGC, lifecycle và retention, visual production, measurement.

Các nhóm sản phẩm đã có playbook riêng và yêu cầu proof riêng: beauty, fashion, food & beverage, điện tử, đồ gia dụng, trang sức/luxury, SaaS, dịch vụ địa phương, giáo dục, hospitality.

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

Mỗi phần có một dossier chuyên sâu và một lệnh tạo ra artefact thật.

### Copywriting

Thang là `tension → promise → mechanism → proof → action`, và nó là một cái thang vì không được bỏ bậc: promise mà không có mechanism thì chỉ là slogan, mechanism mà không có proof thì chỉ là một lời khẳng định. Đọc [`references/copywriting.md`](marketing-minthep/references/copywriting.md) cho copy pack theo kênh, và [`references/dossiers/copywriting-deep.md`](marketing-minthep/references/dossiers/copywriting-deep.md) cho craft ở mức từng câu — cụ thể thay vì xếp tính từ, cái phản đối phải tự nêu trước khi người đọc nêu, và vì sao "chất lượng cao" không phải một lợi ích.

### Edit ảnh

Edit không phải generate. Đường đi là: soi ảnh gốc, dựng **lock map**, gọi một năng lực edit thật, rồi so kết quả với các lock. Trên ảnh người thật, edit makeup chỉ đổi pigment và finish trên bề mặt; head shape, hình học và khoảng cách mắt, mí, mũi, môi, xương hàm, chin, tai, hairline, tone da, tuổi thể hiện, độ bất đối xứng, biểu cảm và hướng nhìn đều bị khóa. Edit outfit chỉ đổi trang phục. Nếu không có năng lực edit thật, skill trả về một prompt edit chạy được kèm chỉ dẫn mask chính xác, và nói thẳng là chưa render gì. Xem [`references/image-editing.md`](marketing-minthep/references/image-editing.md).

### Xây campaign

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "..."
```

Brief tách hai thứ trước đây cùng in ra `TBD`: **UNKNOWN** là chưa ai nói và kế hoạch bị chặn đến khi có câu trả lời; **TBD** là việc của mình, chỉ chưa quyết. Asset xen kẽ giữa các kênh và mang một funnel stage, thay vì là tích Descartes của kênh nhân định dạng — đó là một phép nhân, không phải một kế hoạch. Xem [`references/campaign-systems.md`](marketing-minthep/references/campaign-systems.md).

### Màu sắc

Palette được dựng, không phải được chọn. Dossier [`references/dossiers/colour-science-and-harmony.md`](marketing-minthep/references/dossiers/colour-science-and-harmony.md) nói về độ sáng cảm nhận so với trực giác đọc mã hex, tỉ lệ tương phản còn sống nổi trên màn hình điện thoại giữa nắng, khác biệt giữa một màu thương hiệu và một accent chỉ xuất hiện đúng một lần, và chuyện gì xảy ra với palette khi sang CMYK. `references/composition-light-color.md` nối nó với camera, ánh sáng và grade.

### Bố cục

```powershell
python marketing-minthep/scripts/plan_design_options.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json
python marketing-minthep/scripts/render_mockup.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json --output out.svg --html-output out.html
```

Bộ render đo chữ rồi dòng chữ chảy theo phép đo đó. Không có gì được đặt theo một phân số của chiều cao canvas — cách cũ đó đã tạo ra dấu tiếng Việt cắt xuyên dòng kicker và một tiêu đề bị vẽ chồng dưới ảnh hero. Copy không vừa chỗ sẽ báo lỗi thay vì bị cắt âm thầm, vì một mockup lặng lẽ xóa hai phần ba câu vẫn trông như đã hoàn thiện, và đó chính là chỗ nguy hiểm. Dossier: [`layout-wireframe-typography.md`](marketing-minthep/references/dossiers/layout-wireframe-typography.md), [`composition-and-layout-vision.md`](marketing-minthep/references/dossiers/composition-and-layout-vision.md), [`menu-design-and-engineering.md`](marketing-minthep/references/dossiers/menu-design-and-engineering.md).

## Output mẫu

Ba hướng menu cho cùng một quán bún bò, do `render_mockup.py` render từ spec trong `assets/examples/bun-bo/` — không API, không công cụ thiết kế:

| Modern street | Heritage craft | Quiet editorial |
|---|---|---|
| [SVG](docs/assets/generated/bun-bo-menu-modern-street.svg) | [SVG](docs/assets/generated/bun-bo-menu-heritage-craft.svg) | [SVG](docs/assets/generated/bun-bo-menu-quiet-editorial.svg) |

Các hướng ảnh do `compile_prompt.py` biên dịch rồi render qua provider:

| Packshot | Key visual | Beauty campaign | Fashion look |
|---|---|---|---|
| <img src="docs/assets/generated/minthep-serum-packshot.png" width="180"> | <img src="docs/assets/generated/minthep-serum-key-visual.png" width="180"> | <img src="docs/assets/generated/minthep-beauty-campaign.png" width="180"> | <img src="docs/assets/generated/minthep-fashion-look.png" width="180"> |

Shot video đến từ `plan_video_sequence.py`, công cụ mang continuity đi tiếp: mỗi shot thừa hưởng trạng thái nhân vật, trang phục, hướng sáng, lens và grade của shot trước, nên prompt 4 không thể nói ngược prompt 3.

```powershell
python marketing-minthep/scripts/plan_video_sequence.py --input marketing-minthep/assets/examples/bun-bo/video-sequence.json --format prompts
```

## Thư viện reference

20 ảnh reference trong `docs/assets/references/`, ghi nguồn ở `ATTRIBUTION.txt`, phủ makeup macro, grid biểu cảm, candid action, full-body với negative space, pose editorial và nhiều điều kiện sáng. Chúng tồn tại để được tách thành các thuộc tính có thể chuyển hóa — `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, `texture` — chứ không bao giờ để sao chép. Dùng chúng không hàm ý endorsement và không tự cấp quyền tái sử dụng cho campaign.

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
  SKILL.md                  điểm vào, dưới 150 dòng
  references/               45 file chủ đề, mỗi file dưới 150 dòng
    dossiers/               14 dossier craft chuyên sâu + index
  scripts/                  19 công cụ + bộ test
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

93 test. `evaluate_workbench.py` chạy lại các routing case trong `assets/evals/`. `.github/workflows/deploy-pages.yml` kiểm tra cấu trúc, planner, manifest builder, unit test và biên dịch Python, rồi deploy `docs/` lên GitHub Pages.

## Những gì skill không làm

- Bịa claim, thành phần, thông số, giá, review, khách hàng, số liệu, chứng nhận, cue scarcity hay endorsement.
- Sao chép danh tính celebrity, phong cách của một living artist, một campaign, một tấm ảnh hay một layout đặc trưng. Reference được tách thành thuộc tính, hoặc không dùng.
- Làm gầy hay đổi hình thể một người thật trong ảnh edit.
- Trình bày một bao bì do AI tạo như ảnh chụp sản phẩm thật khi không có reference chính xác.
- Tự publish, liên hệ báo chí hay creator, mua ads, hay đổi campaign đang chạy. Những việc đó cần ủy quyền riêng.
- Gọi một prompt là ảnh, một storyboard là video, hay một kế hoạch là kết quả.

## Giới hạn vận hành

Spec nền tảng thay đổi; phải kiểm tra nguồn chính thức live trước khi export hoặc upload. Kết quả ảnh phụ thuộc provider, reference hợp lệ và năng lực render thực có tại thời điểm đó. Claim về PR, pháp lý, sức khỏe, tài chính, so sánh và các ngành bị quản lý cần bằng chứng và phê duyệt của chủ sở hữu. Skill này lập kế hoạch và tạo artefact; publishing, media buying, outreach và deployment vẫn là việc của bạn.
