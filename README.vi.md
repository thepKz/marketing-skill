# Marketing-Minthep

<p align="right">
  <a href="README.md"><kbd> &nbsp; English &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; <b>Tiếng Việt</b> &nbsp; </kbd></a>
</p>

Skill marketing cho Claude Code và GPT/Codex. Bạn gõ đúng câu một chủ quán sẽ gõ — *"làm cái poster khai trương"*, *"sao không ai mua"* — skill tìm ra quyết định marketing đang trốn trong câu chữ, quyết nó, rồi giao đúng một deliverable đã chốt với mọi dữ kiện gắn nhãn `confirmed / observed / inferred / unknown`. Nó không bao giờ bịa giá, review, hay số liệu.

```text
$marketing-minthep
```

<table>
  <tr>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-packshot.png"><img src="docs/assets/generated/minthep-serum-packshot.png" alt="Packshot serum, bao bì concept" /></a></td>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-key-visual.png"><img src="docs/assets/generated/minthep-serum-key-visual.png" alt="Key visual serum" /></a></td>
    <td width="25%"><a href="docs/assets/generated/bun-bo-menu-quiet-editorial.svg"><img src="docs/assets/generated/bun-bo-menu-quiet-editorial.svg" alt="Menu vẽ bằng code, hướng quiet editorial" /></a></td>
    <td width="25%"><a href="docs/assets/generated/refsheet-palettes.svg"><img src="docs/assets/generated/refsheet-palettes.svg" alt="Bảng palette với tương phản đo thật" /></a></td>
  </tr>
</table>

Hai tấm ảnh ra từ pipeline ảnh; menu và bảng palette do script vẽ, mọi con số tương phản in trên đó là số đo thật. Xem thêm ở [trang demo](https://thepkz.github.io/marketing-skill/).

## Output, trước và sau

Cùng một đoạn giới thiệu quán bằng tiếng Việt, bản nháp và bản viết lại qua skill. Cả hai đoạn giữ nguyên văn trong [`rewrite-human-worked-example.md`](marketing-minthep/assets/examples/rewrite-human-worked-example.md), nên bạn tự chạy lại gate trên chính hai đoạn đó được — bản đầu trượt, bản sau đậu:

| Số đo | Nháp | Viết lại | Chuẩn |
|---|--:|--:|---|
| Dữ kiện kiểm chứng được | 1 | 8 | ≥ 3 |
| Câu mà đối thủ đăng lại được nguyên văn | 3/4 | 2/8 | ≤ 50% |
| Độ dao động độ dài câu (CV) | 0,10 | 0,85 | ≥ 0,45 |
| Tính từ rỗng trên 150 âm tiết | 1,55 | 0,0 | ≤ 1,0 |
| Dấu vết dịch máy tiếng Việt | 4 | 0 | 0 |
| **Kết luận** | **trượt, 6 lỗi chặn** | **đậu** | |

Mọi con số đều do script in ra — chạy được trên chính bản nháp của bạn. Dữ kiện trong bản viết lại đến từ quán, không phải từ model — đó là toàn bộ khác biệt, và là lý do gate là phép tính chứ không phải gu.

## Hai run đầy đủ, giữ nguyên văn

Tin nhắn người dùng mô phỏng, chạy từ đầu đến cuối, kết quả gate thật nằm cuối mỗi file — kể cả vòng mà bản nháp đầu tiên trượt:

- [`làm cái poster khai trương`](marketing-minthep/assets/examples/simulated-run-khai-truong-poster.md) — câu hỏi không chứa ưu đãi nào, nên skill dựng ưu đãi trước (đồng giá 19K, trần 200 ly, có ngày) và poster chỉ còn 4 dòng. Nháp đầu trượt brand-swap ở 76%; bản cuối đậu 6/6.
- [`sao không ai mua`](marketing-minthep/assets/examples/simulated-run-sao-khong-ai-mua.md) — 2.100 lượt vào, 3 đơn: chẩn đoán phễu gọi tên *trust* là chỗ rò kèm phép tính, xếp một việc sửa 0đ trước mọi đồng quảng cáo. Nháp đầu để 2 con số phần trăm đứng không nguồn; gate bắt cả hai.

## Hỏi được những gì

25 kiểu hỏi đã map trong [`data/ask-diagnosis.csv`](marketing-minthep/data/ask-diagnosis.csv) — mỗi hàng gọi tên việc thật trốn sau câu chữ, output tốt trông ra sao, và kiểu hỏng phải tránh. Vài hàng:

| Bạn gõ | Nó thực sự làm |
|---|---|
| "làm cái poster" | Ưu đãi trước; poster có tiêu đề LÀ ưu đãi, đọc được từ 5 m |
| "viết content đi" | Bài nào cũng mang 1 dữ kiện kiểm được — không phải 10 bài trơn tru ai đăng cũng được |
| "sao không ai mua" | Chẩn đoán phễu 4 chặng, chốt bằng 1 việc sửa xếp trước |
| "để giá bao nhiêu" | Một mức giá kèm phép tính sàn biên lợi nhuận |
| "lên kế hoạch marketing" | Một `plan.md` 10–30 dòng sống trên đĩa kèm nhịp review, không phải deck |

Câu hỏi không chứa quyết định marketing nào — resize ảnh, dịch một dòng — được làm thẳng, không qua pipeline.

## Bắt đầu nhanh

```powershell
python marketing-minthep/scripts/install_global.py     # cài cho Claude Code + Codex
```

Tạo folder làm việc từ một câu, rồi gate bản nháp trước khi giao:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi mở shop mỹ phẩm nhỏ ở Gò Vấp, không biết gì về marketing" --root .
python marketing-minthep/scripts/check_specificity.py --check draft.md
python marketing-minthep/scripts/check_output_shape.py --check draft.md
```

Gate thoát `0` sạch, `2` trượt, `3` chưa ngã ngũ, `4` không chạy được — crash không bao giờ là kết luận.

## Bên trong có gì

```
marketing-minthep/
  SKILL.md            router: 12 luật, đọc câu hỏi trước khi đụng tool nào
  references/         51 file doctrine — nạp theo việc, không bao giờ nạp hết
  data/               43 bảng tra — palette, công thức copy, dấu hiệu slop, bảng ask
  scripts/            52 tool — 11 gate chỉ đo; kết luận thuộc về model
  assets/examples/    input chạy được + hai run mô phỏng ở trên
```

Script đo, không viết hộ. Cố ý không có test suite phía sau: gate chính là bài test, và nó chạy trên bản nháp của bạn đúng lúc cần — mỗi lần chạy là một lần test. Script hỏng thì thoát `4` chứ không đậu hộ, nên crash không bao giờ ra được kết luận. Chi tiết trong [ARCHITECTURE.md](ARCHITECTURE.md).

## Những việc nó từ chối

- Bịa claim, giá, review, số liệu, chứng nhận, hay chiêu khan hiếm giả.
- Sao chép nhận diện người nổi tiếng, phong cách nghệ sĩ còn sống, hay một campaign cụ thể. Reference được tách thành thuộc tính hoặc không dùng.
- Bóp dáng, sửa body người thật trong ảnh.
- Gọi prompt là ảnh, storyboard là video, kế hoạch là kết quả.
- Đăng bài, mua quảng cáo, liên hệ ai — mấy việc đó vẫn là của bạn.

<p align="center">
  <a href="README.md"><kbd> &nbsp; English &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; <b>Tiếng Việt</b> &nbsp; </kbd></a>
</p>
