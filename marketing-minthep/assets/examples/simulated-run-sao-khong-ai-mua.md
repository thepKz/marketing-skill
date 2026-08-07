# Run mô phỏng: "sao không ai mua"

**Người dùng gõ (giả lập ngày 07/08/2026):** *"shop mình bán serum trên web mà chẳng ai mua,
tháng được 3 đơn, chán quá"* — kèm số liệu trang: 2.100 lượt truy cập/tháng, giá bán 189.000đ.

**Skill đọc ask:** hàng `sao-khong-ai-mua` trong `data/ask-diagnosis.csv` — việc thật là chẩn
đoán 4 chặng traffic → offer → trust → price, gọi tên đúng chặng đang rò với con số chứng minh,
rồi 1 việc sửa xếp trước.

---

## Deliverable: chẩn đoán phễu — shop serum, tháng 07/2026

Chặng rò là **trust**, không phải traffic: theo số liệu trang tháng 07/2026, 2.100 lượt vào
(observed) sinh ra 3 đơn (observed) — tỷ lệ chuyển đổi 0,14%, trong khi khoảng ngành mỹ phẩm
online theo các báo cáo e-commerce nằm quanh 1–2% (inferred). Traffic hiện tại đủ nuôi 20–40
đơn/tháng nếu trang giữ được lòng tin; quảng cáo thêm lúc này là đổ nước vào xô thủng.

| Chặng | Số đo | Nhãn | Kết luận |
|---|---|---|---|
| Traffic | 2.100 lượt/tháng | observed | Đủ — không phải chỗ rò |
| Offer | 189.000đ, không quà, không cam kết | observed | Yếu nhưng chưa phải nút thắt |
| Trust | 0 đánh giá, 0 ảnh khách thật, không COD | observed | **Chỗ rò — sửa trước** |
| Price | 189.000đ vs 150.000–250.000đ cùng phân khúc | inferred | Trong khoảng, chưa đụng |

### Một việc sửa, xếp trước

Bật COD và đưa 3 đánh giá có ảnh khách thật lên đầu trang sản phẩm trong 14 ngày tới. Serum
189.000đ bôi lên mặt là hàng cần lòng tin: người mua lạ cần đường lui (COD) và bằng chứng người
thật (review ảnh) trước khi cần thêm bất kỳ chữ nào. Hai thứ đó tốn 0đ. Chưa tìm nổi 3 khách cũ
chịu gửi ảnh thì đó là phát hiện quan trọng hơn cả chẩn đoán — sản phẩm chưa có người bảo chứng
thì marketing chưa cứu được.

**Điểm đo lại:** hết 14 ngày, cùng lượng truy cập, đếm đơn. Vượt 10 đơn/tháng → chặng trust xác
nhận là chỗ rò cũ; vẫn dưới 5 → mở lại hồ sơ, nghi phạm kế tiếp là offer (thêm cam kết hoàn tiền
7 ngày trước khi nghĩ đến giảm giá).

---

## Gate readout (chạy thật ngày 07/08/2026, không dàn dựng)

```
check_output_shape --check  → verdict: clean — the document is shaped like an answer (exit 0)
check_specificity  --check  → verdict passed — 15 checkable things in 12 sentences,
                              6/6 gates passed, brand-swap 25% ≤ 50% (exit 0)
```

Bản nháp đầu của file này trượt 2 gate: brand-swap 53% và sourced-number — 2 con số 0,14% với
1–2% đứng không nguồn. Sau khi gắn nguồn vào cùng câu và siết chữ, đo lại thì 6/6 sạch. Gate
không viết hộ; gate chỉ không cho số đứng một mình.
