import { ChannelMappingTable } from "../../../components/data-intake/ChannelMappingTable";
import { goldenMappings } from "../../../mocks/day20ScenarioRegistry";
import { validateChannelMappings } from "../../../schemas/channel-mapping.schema";

export const SessionMappingPage = (): JSX.Element => {
  const validation = validateChannelMappings(goldenMappings, ["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"]);
  return <main><h1>Metadata & Channel Mapping</h1><ChannelMappingTable mappings={goldenMappings} completeness={validation.completeness} /><p>Không suy đoán đơn vị từ amplitude.</p></main>;
};
