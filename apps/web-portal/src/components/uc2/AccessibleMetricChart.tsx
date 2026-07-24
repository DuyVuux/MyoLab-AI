export interface MetricPoint {
  readonly label: string;
  readonly value: number;
}

export interface AccessibleMetricChartProps {
  readonly title: string;
  readonly unit: string;
  readonly points: readonly MetricPoint[];
}

export function AccessibleMetricChart({
  title,
  unit,
  points,
}: AccessibleMetricChartProps): JSX.Element {
  if (points.length === 0) {
    return <p role="status">Không có dữ liệu để dựng biểu đồ.</p>;
  }

  const max = Math.max(1, ...points.map((point) => point.value));

  return (
    <figure>
      <figcaption>{title}</figcaption>
      <svg
        role="img"
        aria-label={`${title}. Bảng dữ liệu đi kèm sau biểu đồ.`}
        viewBox="0 0 420 140"
      >
        {points.map((point, index) => (
          <rect
            key={`${point.label}-${index}`}
            x={20 + index * 90}
            y={120 - (point.value / max) * 100}
            width="50"
            height={(point.value / max) * 100}
            fill="currentColor"
          />
        ))}
      </svg>
      <table>
        <caption>Dữ liệu thay thế cho {title}</caption>
        <thead>
          <tr>
            <th>Mốc</th>
            <th>
              Giá trị ({unit})
            </th>
          </tr>
        </thead>
        <tbody>
          {points.map((point) => (
            <tr key={point.label}>
              <td>{point.label}</td>
              <td>{point.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
