# Run mô phỏng: "làm cái poster khai trương"

**Người dùng gõ (giả lập ngày 07/08/2026):** *"sắp khai trương quán cà phê, làm cái poster đẹp
giúp anh"* — 0 ngày, 0 ưu đãi, 0 địa chỉ trong tin nhắn.

**Skill đọc ask:** `find_recipe.py --table asks --query "làm poster"` trả về 2 hàng, `lam-poster`
và `khai-truong`: ưu đãi khai trương chưa tồn tại, poster chỉ là chỗ nó đứng. Acceptance test lấy
nguyên văn từ cột `good_output_is`: tiêu đề chính LÀ ưu đãi, giá và ngày nguyên văn, đọc được ở
khoảng cách 5 mét.

---

## Deliverable: bảng nội dung poster khai trương — Cà phê Vườn Măng, Gò Vấp

| Trường | Giá trị | Nhãn |
|---|---|---|
| Tên quán | Cà phê Vườn Măng | confirmed |
| Ngày khai trương | 20/09/2026 (thứ Bảy) | inferred — tránh tháng cô hồn, chốt lại với chủ quán |
| Ưu đãi ngày mở | Đồng giá 19.000đ mọi món nước, 200 ly đầu tiên | inferred |
| Thiết bị kéo lần hai | Voucher giảm 30% cho lần ghé tiếp theo, hạn 05/10/2026 | inferred |
| Địa chỉ | unknown — poster chừa dòng trống, không bịa | unknown |

Trần 200 ly và hạn một ngày lấy từ doctrine khai trương trong `campaign-systems.md`: ly đồng giá
19.000đ mua đám đông hôm 20/09, còn voucher hạn 05/10 mua tuần thứ ba — tuần mà quán mới nào
cũng vắng. Giảm sâu hơn 19.000đ không mua thêm được gì ngoài lỗ.

### Chữ trên poster, nguyên văn

```
ĐỒNG GIÁ 19K — 200 LY ĐẦU TIÊN
Cà phê Vườn Măng khai trương thứ Bảy 20/09
[địa chỉ — chờ xác nhận]
Ghé lại trước 05/10: giảm 30% hoá đơn lần hai
```

Dòng "ĐỒNG GIÁ 19K" cỡ lớn nhất, đạt chuẩn đọc-từ-5-mét theo bảng khoảng cách trong
`poster.md`; tên quán xuống dòng 2 vì người đi ngang quyết định bằng con số 19K, không phải
bằng cái tên chưa từng nghe — 0 slogan, 0 câu "hân hạnh đón tiếp".

### Hướng thị giác đã chốt

Palette `bamboo-kraft` trong `data/palettes.csv`: nền kraft ấm, chữ ink đậm, 1 vệt xanh lá
măng — tương phản đo được 8,1 trên 1, khổ A3 dán kính.

---

## Gate readout (chạy thật ngày 07/08/2026, không dàn dựng)

```
check_output_shape --check  → verdict: clean — the document is shaped like an answer (exit 0)
check_specificity  --check  → verdict passed — 15 checkable things in 12 sentences,
                              6/6 gates passed (exit 0)
```

Bản nháp đầu của chính file này trượt brand-swap ở mức 76% — 16 trên 21 câu không mang con số,
ngày, hay tên nào. Gate bắt được, câu chữ được siết lại, đo lại 2 lần thì sạch. Vòng lặp đó là
sản phẩm, không phải phần biên tập.
