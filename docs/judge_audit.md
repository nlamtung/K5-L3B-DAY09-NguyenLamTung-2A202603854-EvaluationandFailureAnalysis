# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.8 | Có (κ=0.757≥0.6, P=0.857≥0.8, R=0.8≥0.7) | dùng |
| helpful | 100 | 0.375 | 1.0 | 0.3 | Không (κ=0.375<0.6, R=0.3<0.7) | loại |

- **Tỉ lệ lỗi hiệu chỉnh (Rogan-Gladen):**
  - `tone_ok`: observed fail rate `0.28` → corrected `0.30` (confusion: `tp=24, fp=4, fn=6, tn=66`).
  - `helpful`: observed fail rate `0.09` → corrected `0.30` (confusion: `tp=9, fp=0, fn=21, tn=70`).

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`) | PASS | FAIL | Người đúng | Câu `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` dùng ngôn ngữ thân mật quá mức ("anh check giúp em", "rồi nha"). Sửa rubric `tone_ok`: cấm từ ngữ suồng sã ("nha", "check giúp"), bắt buộc kính ngữ chuẩn CSKH ("Dạ", "anh/chị", "kiểm tra"). |
| 2 | `H-017` (`tone_ok`) | PASS | FAIL | Người đúng | `"Dạ, bạn ơi LogiX đã hoàn 25.000đ..."` xưng hô "bạn ơi" + "rồi nha" không chuẩn mực. Sửa rubric: quy định rõ xưng hô chuẩn ("anh/chị" hoặc "quý khách"), không dùng "bạn ơi". |
| 3 | `H-029` (`tone_ok`) | PASS | FAIL | Người đúng | `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` giọng cộc lốc, thiếu lịch sự ("không cần nhắn thêm"). Sửa rubric: bổ sung tiêu chí không ra lệnh/đuổi khéo khách hàng. |
| 4 | `H-042` (`tone_ok`) | PASS | PASS (judge FAIL) | Người đúng | `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` lịch sự, rõ ràng nhưng judge đánh FAIL nhầm. Sửa rubric: nêu ví dụ tích cực (positive few-shot) cho câu trả lời ngắn gọn, đủ thông tin. |
| 5 | `H-051` (`tone_ok`) | PASS | PASS (judge FAIL) | Người đúng | `"Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ."` bị judge phạt vì dùng từ tiếng Anh `"refund"`. Cần làm rõ trong rubric: có chấp nhận thuật ngữ quen thuộc `"refund"` hay bắt buộc tiếng Việt `"hoàn tiền"`. |
| 6 | `HL-016` (`helpful`) | PASS | FAIL | Người đúng | `"Dạ, LogiX thành thật xin lỗi anh/chị vì sự bất tiện này..."` chỉ xin lỗi chung chung, không trả lời trạng thái đơn hay hướng xử lý tiếp theo. Sửa rubric `helpful`: bắt buộc có hành động/trạng thái cụ thể (số tiền, lý do từ chối, hoặc bước tiếp theo), xin lỗi suông = FAIL. |

## Kết luận
- **Tiêu chí bị loại:** `helpful` bị loại, **không được dùng làm gate** vì `κ = 0.375 < 0.6` và `Recall = 0.30 < 0.7`. Từ ma trận nhầm lẫn (`tp=9, fp=0, fn=21, tn=70`), judge bỏ sót tới 21/30 trường hợp không hữu ích (`FN = 21`), chỉ phát hiện được 30% lỗi thật (tỉ lệ lỗi quan sát chỉ 0.09 trong khi tỉ lệ thật sau hiệu chỉnh Rogan-Gladen là 0.30).
- **Tiêu chí được giữ:** `tone_ok` đạt cả 3 ngưỡng (`κ = 0.757`, `P = 0.857`, `R = 0.80`), có thể dùng để theo dõi chất lượng văn phong sau khi bổ sung ví dụ ranh giới vào rubric.
- **Rủi ro còn lại:** Judge chỉ được kiểm trên dữ liệu replay đã công khai (`judge_tone_public.csv`, `judge_helpful_public.csv`); cần nhãn người mới trên tập held-out thật trước khi áp dụng ngoài thực tế.
