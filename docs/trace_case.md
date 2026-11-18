# Trace case: từ trace tới quyết định sai đầu tiên

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case phân tích: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261118-5320` |
| Triệu chứng | `TrialPass` FAIL (`status resolved != denied`), `RefundAmountCorrect` FAIL (`ledger=20000 != label=0`), `DbFactKept` FAIL (`1 override event(s)`). Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` và ledger ghi `refund_vnd=20000, refund_count=1`, trong khi nhãn chuẩn là `denied, refund_vnd=0`. |
| Bước sai đầu tiên | Event **3** (`model_override`): `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event **1** (`handoff`) chuyển đúng `request_id=REQ-C-002` và `principal_scope=owner_order_only`; Event **2** (`investigator`) truy vấn DB `lookup_order` trả về dữ liệu thật của đơn `O-202` (`visible=true`). Từ Event **3**, agent ghi đè `delay_days: 5` theo ticket thay vì giữ giá trị DB, dẫn tới Event **4** (`quote`) tính sai `amount_vnd=20000` (`SHIP-LATE-03`) và Event **6** (`reply`) báo hoàn tiền. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên `fixed C-002@11`: không có event `model_override`; sau Event **2** (`investigator`), Event **3** (`quote`) giữ nguyên dữ liệu DB và trả `{"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`, Event **4** (`reply`) từ chối đúng (`status=denied`, `refund_vnd=0`). |
| Regression test | `src/tests/test_lab9_trace_case.py::test_c002_seed11_catches_ticket_trust_regression` — chạy `seeded_regression` và `fixed` trên `C-002@11`, assert `DbFactKept` và `RefundAmountCorrect` đều FAIL trên `seeded_regression` và PASS trên `fixed`. |
| Chưa chắc chắn | Trace chỉ chạy trên MockLLM và dữ liệu công khai `public_claims.jsonl`; chưa chứng minh được hành vi khi LLM thật gặp các cách diễn đạt ticket phức tạp hơn ngoài tập mẫu. |
