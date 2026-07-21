# Phần bổ sung Decision Log — Day 5

| ID    | Quyết định                                                         | Trạng thái                |
| -------| --------------------------------------------------------------------| ---------------------------|
| D5-01 | Tiền xử lý chỉ chạy sau QC gate                                    | Chốt                      |
| D5-02 | Offline MVP dùng `sosfiltfilt` zero-phase                          | Chốt                      |
| D5-03 | Butterworth band-pass 20–400 Hz, order 4 là mặc định kỹ thuật v0.1 | Tạm thời; cần site review |
| D5-04 | Notch 50 Hz chỉ chạy khi QC có `POWERLINE_NOISE_HIGH`              | Chốt cho MVP-0            |
| D5-05 | Không resample trong MVP-0                                         | Chốt                      |
| D5-06 | Không rectify/envelope trên spectral analysis path                 | Chốt                      |
| D5-07 | Không tự nội suy NaN/Inf                                           | Chốt                      |
| D5-08 | Tạo output hash và edge guard                                      | Chốt                      |
| D5-09 | Causal/streaming filter được hoãn                                  | Chốt                      |
