import { Alert } from '@/components/ui/Alert';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';

export default function UC4FeasibilityPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC4 — HMI vô trùng research demo</h1>
          <p className="page-subtitle">Nghiên cứu vocabulary và sequence task bằng dữ liệu mô phỏng.</p>
        </div>
      </div>

      <Alert variant="warning" title="Nghiên cứu khả thi — cần wearable mới">
        Chưa dùng trong phòng mổ, không điều khiển thiết bị y tế và không tuyên bố dịch
        hoàn chỉnh ngôn ngữ ký hiệu.
      </Alert>

      <Card padding="lg">
        <CardHeader>
          <h2>Kịch bản nghiên cứu</h2>
        </CardHeader>
        <CardContent>
          <ul>
            <li>Simulated sterile-command vocabulary.</li>
            <li>Sign-sequence token labeling, không phải phân loại một cử chỉ đơn.</li>
            <li>Đánh giá nhiễu môi trường và điều kiện wearable.</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
