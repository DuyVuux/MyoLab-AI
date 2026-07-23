"use client";

import { useState } from "react";
import { DataSourceSelector } from "../../../components/data-intake/DataSourceSelector";
import type { DataSourceIntent } from "../../../schemas/session-intake.schema";

export const SessionDataSourcePage = (): JSX.Element => {
  const [selected, setSelected] = useState<DataSourceIntent | null>(null);
  return <main><h1>Chọn nguồn dữ liệu</h1><DataSourceSelector selected={selected} onSelect={setSelected} /></main>;
};
