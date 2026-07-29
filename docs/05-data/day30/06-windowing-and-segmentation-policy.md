# Windowing và segmentation

## Primary

- 200 ms;
- hop 100 ms.

## Sensitivity

- 150/75 ms;
- 250/125 ms.

## Quy tắc

Split trước windowing. Không window nào được vượt repetition/trial boundary. Test partition không được đọc.

Window size theo mẫu:

\[
N_w=\left\lfloor f_srac{T_w}{1000}+0.5ightfloor
\]
