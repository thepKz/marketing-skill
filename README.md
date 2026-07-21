# Marketing Skill

Bộ project gồm hai Codex skill và một website vận hành thử campaign.

## Folder nào là skill cần thiết?

### `marketing-creative-director/` — skill chính

Đây là skill đầy đủ và nên dùng mặc định. Gọi bằng:

```text
$marketing-creative-director
```

Skill xử lý Brand DNA, nghiên cứu reference, campaign strategy, ba creative lane, ảnh sản phẩm, ảnh người, image edit, prompt theo provider, asset manifest, QA, thử nghiệm và learning loop.

Nếu chỉ muốn giữ hoặc cài **một skill**, hãy chọn folder này.

### `marketing-one-page-studio/` — skill compact, tùy chọn

Đây là phiên bản rút gọn cho tình huống cần đi thật nhanh từ một brief sang một trang campaign hoàn chỉnh hoặc JSON để đưa vào website.

Gọi bằng:

```text
$marketing-one-page-studio
```

Nó trả về đúng bảy khối: truth, campaign core, ba lane, asset plan, image prompt, cấu trúc one-page website và QA/export. Skill này không thay thế skill chính; nó là lối tắt cho tác vụ nhỏ và tích hợp giao diện.

### `web-studio/` — website, không phải skill

Đây là ứng dụng React/Vite để nhập brief, chọn provider/lane/subject và xuất campaign, prompt, manifest, Brand DNA, pre-flight QA, Markdown, JSON và CSV.

Folder này được deploy lên GitHub Pages. Không copy nó vào thư mục Codex skills.

## Cấu trúc còn lại

- `PRODUCT.md`: mục tiêu và nguyên tắc sản phẩm của website.
- `DESIGN.md`: visual system của FIELD Studio.
- `.impeccable/`: cấu hình thiết kế và live preview, không phải skill.

## Chạy website local

```powershell
cd web-studio
npm install
npm run dev
```

## Deploy GitHub Pages

Workflow `.github/workflows/deploy-pages.yml` tự build `web-studio` khi push lên `main` và deploy thư mục `web-studio/dist`.

Trong GitHub, mở `Settings > Pages`, chọn `Source: GitHub Actions`, sau đó push branch `main`. Với repository hiện tại, URL dự kiến là:

```text
https://thepKz.github.io/marketing-skill/
```
