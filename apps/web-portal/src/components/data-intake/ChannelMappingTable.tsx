import type { ChannelMapping } from "../../schemas/channel-mapping.schema";

export interface ChannelMappingTableProps {
  readonly mappings: readonly ChannelMapping[];
  readonly completeness: number;
}

export const ChannelMappingTable = ({ mappings, completeness }: ChannelMappingTableProps): JSX.Element => (
  <section aria-labelledby="mapping-title">
    <h2 id="mapping-title">Ánh xạ kênh</h2>
    <p>Độ đầy đủ: {Math.round(completeness * 100)}%</p>
    <table>
      <caption>Kênh nguồn sang kênh chuẩn, cơ, bên, đơn vị và vai trò</caption>
      <thead><tr><th>Kênh nguồn</th><th>Kênh chuẩn</th><th>Cơ</th><th>Bên</th><th>Đơn vị</th><th>Vai trò</th></tr></thead>
      <tbody>{mappings.map((item) => (
        <tr key={item.sourceChannel}>
          <td>{item.sourceChannel}</td><td>{item.canonicalChannelId}</td><td>{item.muscle}</td><td>{item.side}</td><td>{item.unit}</td><td>{item.functionalRole}</td>
        </tr>
      ))}</tbody>
    </table>
  </section>
);
