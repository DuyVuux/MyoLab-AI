import { Alert } from '@/components/ui/Alert';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';

export default function UC3FeasibilityPage() {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="page-header__left">
          <h1 className="page-title">UC3 — Điều khiển chi giả cơ điện</h1>
          <p className="page-subtitle">Offline feasibility và replay mô phỏng.</p>
        </div>
      </div>

      <Alert variant="warning" title="Nghiên cứu khả thi — không điều khiển thiết bị thật">
        Màn hình chỉ đánh giá command mapping, safety interlock và điều kiện phần cứng.
        Không gửi lệnh tới actuator.
      </Alert>

      <Card padding="lg">
        <CardHeader>
          <h2>Điều kiện cần đánh giá</h2>
        </CardHeader>
        <CardContent>
          <ul>
            <li>Embedded EMG phù hợp trong socket.</li>
            <li>Đối tác và giao thức phần cứng được xác nhận.</li>
            <li>False-command severity và fail-safe.</li>
            <li>Latency, packet loss và recovery behavior.</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
