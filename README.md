# Marketing-Minthep

`Marketing-Minthep` là một skill all-in-one dùng được với Claude Code và GPT/Codex, biến brief chưa hoàn chỉnh thành hệ thống marketing có thể sản xuất và đo lường: từ định vị, offer, content, bán hàng, PR đến campaign, hình ảnh sản phẩm, người ảo và production handoff.

Skill được thiết kế theo nguyên tắc **một invocation, nhiều workbench**. Nó chỉ nạp phần kiến thức cần cho công việc hiện tại thay vì đổ toàn bộ marketing vào một prompt khổng lồ.

## Skill làm được gì

| Workbench | Đầu ra điển hình |
|---|---|
| Strategy & offer | Audience, positioning, mechanism, proof, offer, funnel, message ladder |
| Campaign & launch | Big idea, 3 concept lanes, rollout, paid/content/landing matrix, experiment plan |
| Content & distribution | Pillars, SEO topics, editorial briefs, social calendar, repurposing, email |
| Commerce & merchandising | PDP/listing narrative, media sequence, SKU/variant system, catalog, retail assets |
| Paid media | Creative hypotheses, placement matrix, testing hierarchy, naming và measurement contract |
| PR & communications | Newsworthiness, press angle, pitch/release, press kit, Q&A, newsroom assets |
| Sales enablement | One-pager, deck/demo story, case study, proposal, objection handling, follow-up |
| Creator & UGC | Creator criteria, brief, deliverables, disclosure, usage rights, approval và variants |
| Lifecycle & retention | Welcome, nurture, abandonment, post-purchase, win-back, upsell, referral |
| Visual production | Product photography, art key visual, beauty/makeup, image edit, virtual adult person |
| Measurement | Asset lineage, QA, experiment log, reporting, next-test recommendations |

Các loại sản phẩm đã có playbook gồm beauty, fashion, food & beverage, electronics, home, jewelry/luxury, SaaS, dịch vụ, giáo dục và hospitality. Registry hiện bao phủ asset cho PDP, marketplace, catalog, Meta/TikTok/Google, social, web, email, PR, sales, retail, OOH và editorial art.

## Không làm gì

- Không bịa claim, thành phần, thông số, giá, review, khách hàng, số liệu, chứng nhận, scarcity hoặc endorsement.
- Không sao chép danh tính celebrity, living artist, campaign, ảnh hoặc layout đặc trưng; reference chỉ được tách thành thuộc tính có thể chuyển hóa.
- Không tự động làm gầy hoặc đổi cơ thể người thật trong ảnh edit.
- Không coi packaging AI chưa có reference chính xác là hình sản phẩm thật.
- Không tự publish, gửi báo chí, liên hệ creator, mua ads hoặc thay đổi campaign live.

## Quick start

Gọi skill bằng:

```text
$marketing-minthep
```

Repo có hai adapter project-level:

- Claude Code: `.claude/skills/marketing-minthep/SKILL.md`
- GPT/Codex: `.codex/skills/marketing-minthep/SKILL.md`

Hai adapter đều nạp `marketing-minthep/SKILL.md` làm nguồn chính. Không sửa nội dung marketing trực tiếp trong adapter để tránh Claude và GPT cho kết quả lệch nhau.

Input tối thiểu nên có:

1. Sản phẩm/dịch vụ và mục tiêu kinh doanh.
2. Audience hoặc tình huống mua.
3. Kênh, thị trường và thời hạn nếu có.
4. Fact/claim/proof đã xác nhận.
5. Asset/reference hiện có và điều phải giữ hoặc tránh.

Skill sẽ hỏi tối đa ba câu khi thiếu dữ liệu có thể làm thay đổi truth, quyền sử dụng, offer, kiến trúc hoặc chi phí. Các khoảng trống ít rủi ro được ghi rõ là giả định rồi tiếp tục.

### Chọn độ rộng

- `focused`: một workbench và bộ artifact nhỏ nhất có thể dùng ngay; đây là mặc định.
- `system`: nối strategy với các kênh, asset và measurement thật sự phụ thuộc nhau.
- `production`: thêm brief JSON, manifest, provider prompt, owner, approval, naming và export handoff.

Kế hoạch từ số 0 và nghiên cứu sâu mặc định chạy ở `system` để không bỏ sót audience, copy pack, ngân sách và lịch triển khai. Menu, image edit và video sẽ tự nâng lên `production` khi request có `render`, `export`, `xuất file`, `MP4` hoặc yêu cầu in ấn.

### Ví dụ request

Physical product:

```text
Use $marketing-minthep in production mode for this skincare product.
Build the PDP image sequence, Meta/TikTok campaign system, creator brief,
four original image directions, claims ledger, and measurement plan.
```

Beauty hoặc virtual person:

```text
Use $marketing-minthep with my references. Explain four fictional-adult
virtual-person options, including healthy build, makeup and pose. After I choose,
create a consistent identity sheet and four campaign branches without copying celebrity identity.
```

SaaS:

```text
Use $marketing-minthep to launch this B2B SaaS. Produce positioning,
a proof-led landing narrative, LinkedIn content, sales one-pager,
demo story, paid hypotheses and a 30-day measurement plan.
```

Dịch vụ địa phương:

```text
Use $marketing-minthep for a local dental clinic. Build the offer,
Google/Meta asset plan, trust content, review-safe proof system,
lead follow-up flow and a localized production shot list.
```

PR, sales, creator hoặc lifecycle:

```text
Use $marketing-minthep in focused mode for a press launch.
Score newsworthiness and create the angle, pitch, press kit checklist,
Q&A, spokesperson assets and earned-media measurement contract.
```

Để skill tự route một brief rộng:

```powershell
python marketing-minthep/scripts/plan_marketing_system.py --input marketing-minthep/assets/examples/all-in-one-product-request.json
```

Để tạo workspace thật, seed research/provider metadata và nối các pipeline phụ trong cùng một request:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi không biết marketing, hãy làm kế hoạch từ đầu cho quán bún bò" --root .
```

Mỗi run có `_meta/render-capability.json`. File này bắt đầu ở `not-rendered`; chỉ đổi trạng thái sau khi output thật đã được mở và QA. Prompt, storyboard, wireframe SVG và provider plan không được gọi là ảnh/video đã render.

## Image system

Flow chuẩn là `references -> role map -> locks/freedoms/rejects -> provider route -> 4-5 controlled branches -> QA -> winner refinement`.

- GPT Image 2: phù hợp direct generation/edit, multi-turn qua Responses API và nhiều output cùng canonical prompt.
- Nano Banana: phù hợp nhiều reference, consistency, layout/text/localization và refinement theo branch.
- Virtual person luôn là fictional adult, anatomy khỏe mạnh; project có thể ưu tiên `slender-light-frame` nhưng cấm extreme thinness, waist distortion và childlike presentation.
- Makeup được mô tả theo skin, brows, eyes, liner, lashes, blush, facial structure, lips, palette và retouching. Douyin/aegyo-sal là một option, không phải mặc định cho mọi brief.

Các lệnh liên quan:

```powershell
python marketing-minthep/scripts/plan_image_generation.py --input marketing-minthep/assets/examples/reference-image-request.json
python marketing-minthep/scripts/plan_virtual_person.py --input marketing-minthep/assets/examples/virtual-person-request.json
python marketing-minthep/scripts/compile_prompt.py --help
```

## Production tools

```powershell
# Campaign brief đọc từ chính câu yêu cầu: horizon, ngân sách, ngành, kênh đều suy ra từ đó
python marketing-minthep/scripts/scaffold_campaign.py --request "Tôi bán bún bò ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng, ngân sách nhỏ"

# Ghi đè khi bạn biết rõ hơn suy luận của nó
python marketing-minthep/scripts/scaffold_campaign.py --project "Launch" --job campaign-launch --industry beauty --provider gpt-image-2 --channels meta tiktok web

# Tạo manifest từ request hoặc output của planner
python marketing-minthep/scripts/build_asset_manifest.py --input marketing-minthep/assets/examples/all-in-one-product-request.json --format json

# Chấm creative và phân tích performance
python marketing-minthep/scripts/score_creative.py --help
python marketing-minthep/scripts/analyze_performance.py --help
```

## Handbook HTML

Handbook tĩnh nằm tại `docs/index.html` và giải thích reference-first flow, business workbenches, virtual person, makeup, camera/light/composition, provider routing, prompt contract, QA và production loop. Giao diện có i18n VI/EN, dùng font hỗ trợ đầy đủ dấu tiếng Việt và contact sheet liên kết về các post Instagram gốc.

```powershell
python -m http.server 8000 --directory docs
```

Mở `http://localhost:8000`. Handbook có thư viện 17+ reference preview với filter makeup, pose, candid, full-body, editorial và lighting; mỗi ảnh liên kết về post gốc. Gallery output hiển thị packshot, beauty campaign, artistic key visual và fashion look đã render. Ảnh Instagram chỉ dùng để phân tích thuộc tính thị giác, không ngụ ý endorsement và không mặc nhiên cấp quyền tái sử dụng cho campaign.

Khi edit ảnh người thật, makeup chỉ được đổi pigment/finish trên bề mặt. Skill khóa head shape, eye geometry và spacing, eyelids, nose, lips, jaw, chin, ears, hairline, skin tone, tuổi thể hiện, bất đối xứng, expression và gaze. Outfit edit chỉ thay wardrobe; face, hair, body proportions, pose, hands, camera, crop, light và background vẫn phải giữ nguyên.

## Kiểm tra

```powershell
python -m unittest discover -s marketing-minthep/scripts -p "test_*.py"
python marketing-minthep/scripts/plan_marketing_system.py --input marketing-minthep/assets/examples/all-in-one-product-request.json
python C:\Users\Admin\.codex\skills\.system\skill-creator\scripts\quick_validate.py marketing-minthep
python marketing-minthep/scripts/evaluate_workbench.py
```

Workflow `.github/workflows/deploy-pages.yml` kiểm tra cấu trúc, planner, manifest, unit tests, Python compilation và deploy trực tiếp `docs/` lên GitHub Pages. Repository không còn `marketing-one-page-studio` hoặc `web-studio`.

## Giới hạn vận hành

- Platform specs thay đổi; skill phải kiểm tra nguồn chính thức live trước export/upload.
- Kết quả ảnh phụ thuộc provider, reference hợp lệ và khả năng render hiện có; prompt không đồng nghĩa ảnh đã được tạo hoặc QA.
- PR, legal, health, finance, comparative và regulated claims cần bằng chứng/chủ sở hữu phê duyệt phù hợp.
- Skill hỗ trợ lập kế hoạch và tạo artifact; publishing, media buying, outreach và production deployment cần ủy quyền riêng.
