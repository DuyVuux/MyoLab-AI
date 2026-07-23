import { Card } from "../../../components/ui/Card";

export const SessionCreatePage = (): JSX.Element => (
  <Card>
    <h1>Tạo phiên đánh giá</h1>
    <p>Nhập mã đối tượng ẩn danh, use case, protocol, bên, cơ mục tiêu, consent và nguồn dữ liệu dự kiến.</p>
    <p role="status">Prototype không nhận tên, MRN, email hoặc số điện thoại.</p>
    <button type="button">Lưu draft an toàn</button>
    <button type="button">Tạo session và tiếp tục</button>
  </Card>
);
