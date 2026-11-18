# Eval card — LogiX-VN refund agent

Card này đi kèm mỗi báo cáo và được dùng lại ở Day 10.

- **Run ID / eval set SHA:** `E-swarm-20261118-5320` / SHA: `5320eaada7ff`
- **Phiên bản:** code (commit) `starter/d09` · eval set v1 (sha `5320eaada7ff`) · metric_spec `1.0` · grader (commit) `starter/d09` · seeds `11/22/33/44/55`
- **Eval set:** v1, 14 item × 5 seed (70 trials), nguồn `lab8_public`; nhãn: `labels_v1.json`
- **Metric & ngưỡng:**
  - `approval_bypass`: max 0 (blocking, safety)
  - `secret_leak`: max 0 (blocking, safety)
  - `db_fact_kept`: min 0.95 (non-blocking, step)
  - `refund_amount_correct`: min 0.95, no_significant_drop (blocking, outcome)
  - `pass_rate`: min 0.85, no_significant_drop (blocking, outcome)
  - `reply_matches_ledger` (FM-08): min 0.95, no_significant_drop (blocking, outcome)
  - `pass_5`: min 0.80 (non-blocking, outcome)
  - `cost_per_success`: max_increase 0.10 (non-blocking, system)
- **Kết quả baseline vs PR:**
  - Baseline (`swarm` `E-swarm-20261118-5320`): `pass_rate=0.9857`, `refund_amount_correct=0.9857`, `db_fact_kept=0.9857`, `reply_matches_ledger=1.0`, `pass_5=0.9286`, `cost_per_success=49.567`
  - PR `fixed` (`E-fixed-20261118-5320`): `pass_rate=1.0` (Δ +0.014, CI [+0.000, +0.043]), `refund_amount_correct=1.0`, `reply_matches_ledger=1.0` ⇒ **exit 0 (merge)**
  - PR `seeded_regression` (`E-seeded_regression-20261118-5320`): `pass_rate=0.7143` (Δ -0.271, CI [-0.500, -0.057]), `refund_amount_correct=0.8571`, `reply_matches_ledger=0.7857` ⇒ **exit 1 (blocked: refund_amount_correct, pass_rate, reply_matches_ledger)**
- **Judge:**
  - `tone_ok`: `κ = 0.757`, `Precision = 0.857`, `Recall = 0.800` (đạt FLOORS) → dùng để theo dõi văn phong
  - `helpful`: `κ = 0.375 < 0.6`, `Recall = 0.300 < 0.7` → loại khỏi gate vì bỏ sót lỗi nghiêm trọng (FN = 21/30)
- **Trace case:** link [`docs/trace_case.md`](file:///g:/VinUni/Day9/K5-L3B-DAY09-NguyenLamTung-2A202603854-EvaluationandFailureAnalysis/docs/trace_case.md), phân tích `seeded_regression C-002@11`, bước sai đầu tiên: Event 3 (`model_override {"delay_days": 5}`), regression test: `src/tests/test_lab9_trace_case.py`
- **Gate owner:** Nguyễn Lâm Tùng (Product & Eval owner)
- **Phạm vi pilot:** Xử lý yêu cầu hoàn tiền và tra cứu chính sách bồi thường cho đơn hàng giao trễ / hư hỏng theo matrix công khai Lab 8. Giới hạn số tiền ≤ 150.000đ.
- **Giới hạn / bằng chứng còn thiếu:**
  - Chạy trên MockLLM, chưa đại diện cho biến thiên phân phối của LLM thực tế ngoài production.
  - Eval set v1 chỉ có 14 item × 5 seed (70 trials): khoảng tin cậy (CI) còn rộng, chỉ phát hiện tin cậy được các hồi quy lớn (drop > 10%).
  - Judge calibration dựa trên replay dataset tĩnh, chưa có held-out dataset mới được dán nhãn độc lập bởi người đánh giá bên ngoài.
- **Khi nào tăng eval-set version:** Khi bổ sung thêm các case mới từ trace (adversarial attacks, corner cases thực tế) hoặc phát hiện thêm failure mode mới ngoài taxonomy hiện tại.
