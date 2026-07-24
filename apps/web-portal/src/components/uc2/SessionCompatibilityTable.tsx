import type { LongitudinalCompatibility } from '../../schemas/uc2-assessment.schema';

export interface SessionCompatibilityTableProps {
  readonly result: LongitudinalCompatibility;
}

export function SessionCompatibilityTable({ result }: SessionCompatibilityTableProps): JSX.Element {
  return (
    <section>
      <h2>Khả năng so sánh dọc</h2>
      <p>
        Kết luận: {result.conclusionAllowed ? 'được phép diễn giải kỹ thuật' : 'đã bị chặn'}
      </p>
      <table>
        <caption>Kiểm tra compatibility</caption>
        <thead>
          <tr>
            <th>Trường</th>
            <th>Trạng thái</th>
            <th>Mã lý do</th>
          </tr>
        </thead>
        <tbody>
          {result.checks.map((check, index) => (
            <tr key={`${check.field}-${index}`}>
              <td>{check.field}</td>
              <td>{check.status}</td>
              <td>{check.reasonCode ?? '—'}</td>
            </tr>
          ))}
          {result.checks.length === 0 && (
            <tr>
              <td colSpan={3}>Không có bản ghi so sánh.</td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
