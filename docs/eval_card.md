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

---

## Phần v2 (Advanced / Expert — M5–M7)

- **Run ID / eval set SHA v2:** `E-swarm-20261118-0385` / SHA: `0385e41a65b3`
- **Eval set v2:** 28 item (14 v1 + 14 adversarial pack) × 5 seed = 140 trials.
- **A/A test & Ngưỡng chọn:**
  - Chạy A/A trên 2 bộ seed độc lập `[11, 22, 33, 44, 55]` và `[66, 77, 88, 99, 110]` cho kết quả $\Delta = 0.0000$ trên mọi metric (do MockLLM deterministic).
  - Với LLM thật, dải nhiễu A/A sẽ luôn $> 0$ do tính ngẫu nhiên (sampling temperature, stochastic decoding). Ngưỡng sàn (floor) bắt buộc phải nằm **ngoài dải nhiễu A/A** (thấp hơn giá trị trung bình trừ đi biên độ nhiễu) để tránh kích hoạt báo nhầm (false alarm) chặn nhầm các PR hoàn toàn vô hại.
  - Ngưỡng `pass_hat_5`: chọn sàn `min: 0.80` (baseline v2 đạt `0.8929`), blocking.
- **Slice Gates & Cơ chế phát hiện:**
  - Slice `money_movement` (`min: 0.90`, blocking): bắt trúng `slice_regression` khi lỗi tính tổng điều khoản chỉ xảy ra ở các claim có phát sinh hoàn tiền ở seed lẻ (trong khi `pass_rate` toàn cục vẫn duy trì mức cao 0.9357 và CI chạm 0).
  - Slice `adversarial` (`min: 0.85`, blocking): giám sát các cuộc tấn công prompt injection, trích dẫn điều khoản cũ hoặc đòi vượt quyền principal.
  - Sàn `pass_hat_5` (`min: 0.80`, blocking): bắt trúng `flaky_regression` (lỗi làm tròn chỉ xảy ra ở 1/5 seed khiến độ tin cậy $pass^5$ tụt giảm nghiêm trọng).
- **Giới hạn cỡ mẫu (Sample Size Limitation):**
  - Một lỗi hiếm gặp chỉ xuất hiện với xác suất 1/3 seed (`rare`) **không thể phát hiện ổn định chỉ với 5 seed** ($1 - (1 - 1/3)^5 \approx 86.8\%$ xác suất thấy ít nhất 1 lần, tức có hơn 13% trường hợp lỗi hoàn toàn lọt qua mà không bị phát hiện trong 5 seed).
  - Do đó, không được cố tình hạ sàn đánh giá chỉ để bắt các lỗi hiếm này, mà cần tăng số lượng seed hoặc áp dụng targeted slice testing khi triển khai thực tế.
- **Kết quả Scorecard Mutation & Chống gian lận Trap:**
  - Scorecard `lab9.mutation`: **3/3 regressions bị chặn** (`seeded_regression`, `slice_regression`, `flaky_regression`), **0 báo nhầm** (`fixed`, `honest_refactor` được merge sạch sẽ).
  - Trap audit `lab9.traps`: Chặn 100% 4/4 trap công khai (`evaluator_errors_as_nan`, `dropped_failing_rows`, `cherry_picked_seeds`, `loosened_spec`) nhờ cơ chế `integrity_check` kiểm soát chặt chẽ NaN/inf, tính toàn vẹn hàng/seed, và nguyên tắc ratchet.
